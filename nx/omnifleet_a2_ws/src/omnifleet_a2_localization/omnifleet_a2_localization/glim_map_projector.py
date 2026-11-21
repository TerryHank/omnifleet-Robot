#!/usr/bin/env python3
"""Project GLIM geometry directly into a lightweight 2-D occupancy grid."""

import math
import threading
import time

import numpy as np
import rclpy
from nav_msgs.msg import OccupancyGrid
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from tf2_ros import Buffer, TransformException, TransformListener


class GlimMapProjector(Node):
    """Apply every observation immediately; no neighbor or history filter."""

    def __init__(self):
        super().__init__("omnifleet_a2_glim_map_projector")
        self.declare_parameter("input_topic", "/glim_ros/map")
        self.declare_parameter("bootstrap_input_topic", "/rslidar_points")
        self.declare_parameter("bootstrap_max_rate_hz", 0.5)
        self.declare_parameter("bootstrap_raytrace_max_range", 6.0)
        self.declare_parameter("output_topic", "/map")
        self.declare_parameter("resolution", 0.08)
        self.declare_parameter("padding", 1.0)
        self.declare_parameter("ground_relative_min", -0.03)
        self.declare_parameter("ground_relative_max", 0.03)
        self.declare_parameter("obstacle_relative_min", 0.06)
        self.declare_parameter("obstacle_relative_max", 1.80)
        self.declare_parameter("clear_robot_footprint", True)
        self.declare_parameter("robot_base_frame", "base_link")
        self.declare_parameter("ground_z_offset_from_base", 0.0)
        self.declare_parameter("robot_footprint_x_min", -0.06)
        self.declare_parameter("robot_footprint_x_max", 0.42)
        self.declare_parameter("robot_footprint_y_min", -0.16)
        self.declare_parameter("robot_footprint_y_max", 0.16)
        self.declare_parameter("max_grid_cells", 800)
        self.declare_parameter("tf_latest_tolerance_sec", 0.02)

        self.resolution = float(self.get_parameter("resolution").value)
        self.padding = float(self.get_parameter("padding").value)
        self.ground_min = float(self.get_parameter("ground_relative_min").value)
        self.ground_max = float(self.get_parameter("ground_relative_max").value)
        self.obstacle_min = float(
            self.get_parameter("obstacle_relative_min").value
        )
        self.obstacle_max = float(
            self.get_parameter("obstacle_relative_max").value
        )
        self.clear_robot_footprint = bool(
            self.get_parameter("clear_robot_footprint").value
        )
        self.robot_base_frame = str(self.get_parameter("robot_base_frame").value)
        self.ground_z_offset = float(
            self.get_parameter("ground_z_offset_from_base").value
        )
        self.robot_x_min = float(self.get_parameter("robot_footprint_x_min").value)
        self.robot_x_max = float(self.get_parameter("robot_footprint_x_max").value)
        self.robot_y_min = float(self.get_parameter("robot_footprint_y_min").value)
        self.robot_y_max = float(self.get_parameter("robot_footprint_y_max").value)
        self.max_cells = int(self.get_parameter("max_grid_cells").value)
        bootstrap_rate = float(
            self.get_parameter("bootstrap_max_rate_hz").value
        )
        self.bootstrap_raytrace_max_range = float(
            self.get_parameter("bootstrap_raytrace_max_range").value
        )
        tf_latest_tolerance = float(
            self.get_parameter("tf_latest_tolerance_sec").value
        )
        if not (
            0.0 < self.resolution
            and self.ground_min < self.ground_max < self.obstacle_min < self.obstacle_max
            and self.robot_x_min < self.robot_x_max
            and self.robot_y_min < self.robot_y_max
            and self.max_cells > 0
            and bootstrap_rate > 0.0
            and self.bootstrap_raytrace_max_range > 0.0
            and 0.0 <= tf_latest_tolerance <= 0.1
        ):
            raise ValueError("invalid direct map projection parameters")
        self.tf_latest_tolerance_ns = int(tf_latest_tolerance * 1.0e9)
        self.bootstrap_min_period = 1.0 / bootstrap_rate
        self.last_bootstrap_attempt = float("-inf")
        self.official_map_active = False
        self.map_state_lock = threading.Lock()
        self.last_global_stamp = None
        self.pending_global_map = None
        self.map_frame = "map"
        self.official_occupied_cells = set()
        self.current_occupied_cells = set()
        self.occupied_cells = set()
        self.free_cells = set()

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        latched = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        latest_cloud = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.publisher = self.create_publisher(
            OccupancyGrid, self.get_parameter("output_topic").value, latched
        )
        self.create_subscription(
            PointCloud2,
            self.get_parameter("input_topic").value,
            self.on_global_cloud,
            latched,
        )
        self.create_subscription(
            PointCloud2,
            self.get_parameter("bootstrap_input_topic").value,
            self.on_bootstrap_cloud,
            latest_cloud,
        )
        self.create_timer(0.5, self.retry_global_map)

    @staticmethod
    def decode(msg):
        cloud = point_cloud2.read_points(
            msg, field_names=("x", "y", "z"), skip_nans=True
        )
        return np.column_stack((cloud["x"], cloud["y"], cloud["z"])).astype(
            np.float32, copy=False
        )

    def point_cells(self, points):
        if len(points) == 0:
            return set()
        indices = np.floor(points[:, :2] / self.resolution).astype(np.int64)
        return {tuple(cell) for cell in indices}

    @staticmethod
    def ray_cells(start, end):
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        step_x = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        step_y = 1 if y0 < y1 else -1
        error = dx + dy
        cells = []
        while True:
            cells.append((x0, y0))
            if x0 == x1 and y0 == y1:
                return cells
            doubled = 2 * error
            if doubled >= dy:
                error += dy
                x0 += step_x
            if doubled <= dx:
                error += dx
                y0 += step_y

    def visible_free_cells(self, sensor_xy, occupied_cells, ground_cells):
        sensor_cell = tuple(
            np.floor(np.asarray(sensor_xy) / self.resolution).astype(np.int64)
        )
        visible = set()
        for endpoint in occupied_cells:
            visible.update(self.ray_cells(sensor_cell, endpoint)[:-1])
        for endpoint in ground_cells:
            visible.update(self.ray_cells(sensor_cell, endpoint))
        visible.difference_update(occupied_cells)
        return visible

    def on_global_cloud(self, msg):
        stamp = (msg.header.stamp.sec, msg.header.stamp.nanosec)
        if self.last_global_stamp is not None and stamp <= self.last_global_stamp:
            return
        self.pending_global_map = msg
        self.try_apply_global_map()

    def retry_global_map(self):
        if self.pending_global_map is not None:
            self.try_apply_global_map()

    def try_apply_global_map(self):
        msg = self.pending_global_map
        if msg is None:
            return
        map_frame = msg.header.frame_id or "map"
        if map_frame != "map":
            self.get_logger().error(
                f"拒绝非 map 坐标系的 GLIM 全局地图：{map_frame}",
                throttle_duration_sec=5.0,
            )
            return
        base_transform = self.lookup_frame_transform(
            map_frame, self.robot_base_frame, msg
        )
        if base_transform is None and not (self.occupied_cells or self.free_cells):
            base_transform = self.lookup_bootstrap_transform(
                map_frame, self.robot_base_frame
            )
        if base_transform is None:
            return
        try:
            xyz = self.decode(msg)
        except (AssertionError, KeyError, ValueError) as exc:
            self.get_logger().warning(
                f"无法读取GLIM全局地图：{exc}", throttle_duration_sec=5.0
            )
            return
        if len(xyz) < 20:
            return
        _ground_mask, obstacle_mask = self.height_masks(xyz, base_transform)
        occupied_cells = self.point_cells(xyz[obstacle_mask])
        with self.map_state_lock:
            first_official_map = not self.official_map_active
            unchanged = occupied_cells == self.official_occupied_cells
            self.official_map_active = True
            self.last_global_stamp = (
                msg.header.stamp.sec,
                msg.header.stamp.nanosec,
            )
            self.pending_global_map = None
            self.official_occupied_cells = occupied_cells
            self.occupied_cells = (
                self.official_occupied_cells | self.current_occupied_cells
            )
            self.free_cells.difference_update(self.occupied_cells)
        if first_official_map:
            self.get_logger().info(
                "首张完整GLIM子图已到达，正式障碍地图已接管；"
                "当前单帧继续提供可见自由区"
            )
        if unchanged and not first_official_map:
            return
        self.publish_map(msg, "正式GLIM障碍+当前可见自由区")

    def on_bootstrap_cloud(self, msg):
        now = time.monotonic()
        if now - self.last_bootstrap_attempt < self.bootstrap_min_period:
            return
        self.last_bootstrap_attempt = now
        cloud_frame = msg.header.frame_id
        if not cloud_frame:
            self.get_logger().error(
                "拒绝无坐标系的Airy当前帧",
                throttle_duration_sec=5.0,
            )
            return
        map_frame = "map"
        cloud_transform = self.lookup_frame_transform(
            map_frame, cloud_frame, msg
        )
        base_transform = self.lookup_frame_transform(
            map_frame, self.robot_base_frame, msg
        )
        if cloud_transform is None or base_transform is None:
            return
        try:
            xyz = self.decode(msg)
        except (AssertionError, KeyError, ValueError) as exc:
            self.get_logger().warning(
                f"无法读取Airy当前帧：{exc}", throttle_duration_sec=5.0
            )
            return
        if len(xyz) < 20:
            return
        cloud_rotation = self.quaternion_matrix(
            cloud_transform.transform.rotation
        )
        cloud_translation = cloud_transform.transform.translation
        sensor_xyz = np.asarray(
            [cloud_translation.x, cloud_translation.y, cloud_translation.z],
            dtype=np.float64,
        )
        xyz_map = xyz.astype(np.float64) @ cloud_rotation.T + sensor_xyz
        planar_delta = xyz_map[:, :2] - sensor_xyz[:2]
        in_range = (
            np.sum(planar_delta * planar_delta, axis=1)
            <= self.bootstrap_raytrace_max_range ** 2
        )
        xyz_map = xyz_map[in_range]
        if len(xyz_map) < 20:
            return
        ground_mask, obstacle_mask = self.height_masks(xyz_map, base_transform)
        observed_occupied = self.point_cells(xyz_map[obstacle_mask])
        ground_cells = self.point_cells(xyz_map[ground_mask]) - observed_occupied
        observed_free = self.visible_free_cells(
            sensor_xyz[:2], observed_occupied, ground_cells
        )
        if not (observed_occupied or observed_free):
            return
        with self.map_state_lock:
            # The latest accepted frame replaces the previous frame in full.
            # No occupied or free cell from an older Airy frame is retained.
            self.current_occupied_cells = observed_occupied
            self.occupied_cells = (
                self.official_occupied_cells | self.current_occupied_cells
            )
            self.free_cells = observed_free - self.occupied_cells
            source = (
                "正式GLIM障碍+Airy当前单帧可见区"
                if self.official_map_active
                else "Airy启动单帧可见区"
            )
            self.publish_map(msg, source)

    @staticmethod
    def quaternion_matrix(rotation):
        quaternion = np.asarray(
            [rotation.x, rotation.y, rotation.z, rotation.w], dtype=np.float64
        )
        norm = np.linalg.norm(quaternion)
        if norm == 0.0:
            raise ValueError("zero-length transform quaternion")
        x, y, z, w = quaternion / norm
        return np.asarray(
            [
                [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
                [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
                [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
            ]
        )

    def height_masks(self, xyz, base_transform):
        translation = base_transform.transform.translation
        map_from_base = self.quaternion_matrix(base_transform.transform.rotation)
        delta = xyz.astype(np.float64) - np.asarray(
            [translation.x, translation.y, translation.z], dtype=np.float64
        )
        relative_height = delta @ map_from_base[:, 2] - self.ground_z_offset
        ground = (relative_height >= self.ground_min) & (
            relative_height <= self.ground_max
        )
        obstacle = (relative_height >= self.obstacle_min) & (
            relative_height <= self.obstacle_max
        )
        return ground, obstacle

    def publish_map(self, msg, source):
        all_cells = self.occupied_cells | self.free_cells
        if not all_cells:
            return
        indices = np.asarray(list(all_cells), dtype=np.int64)
        padding_cells = int(math.ceil(self.padding / self.resolution))
        lower = np.min(indices, axis=0) - padding_cells
        upper = np.max(indices, axis=0) + padding_cells
        base_span = np.maximum(1, upper - lower + 1)
        scale = max(1, int(math.ceil(float(np.max(base_span)) / self.max_cells)))
        resolution = self.resolution * scale
        width, height = np.maximum(1, np.ceil(base_span / scale).astype(np.int64))
        grid = np.full((height, width), -1, dtype=np.int8)

        def output_cells(cells):
            if not cells:
                return np.empty((0, 2), dtype=np.int64)
            values = np.asarray(list(cells), dtype=np.int64)
            values = np.floor_divide(values - lower, scale)
            valid = (
                (values[:, 0] >= 0)
                & (values[:, 0] < width)
                & (values[:, 1] >= 0)
                & (values[:, 1] < height)
            )
            return values[valid]

        free_cells = output_cells(self.free_cells)
        grid[free_cells[:, 1], free_cells[:, 0]] = 0
        obstacle_cells = output_cells(self.occupied_cells)
        grid[obstacle_cells[:, 1], obstacle_cells[:, 0]] = 100
        xy_min = lower.astype(np.float64) * self.resolution
        map_frame = "map"
        if self.clear_robot_footprint:
            self.clear_current_robot_footprint(grid, xy_min, resolution, map_frame)

        output = OccupancyGrid()
        output.header = msg.header
        output.header.frame_id = map_frame
        output.info.map_load_time = self.get_clock().now().to_msg()
        output.info.resolution = resolution
        output.info.width = int(width)
        output.info.height = int(height)
        output.info.origin.position.x = float(xy_min[0])
        output.info.origin.position.y = float(xy_min[1])
        output.info.origin.position.z = 0.0
        output.info.origin.orientation.w = 1.0
        output.data = grid.ravel().tolist()
        self.publisher.publish(output)
        self.get_logger().info(
            f"已发布{source} {width}x{height}，分辨率 {resolution:.3f}m "
            f"（障碍={len(self.occupied_cells)}，自由={len(self.free_cells)}）",
            throttle_duration_sec=5.0,
        )

    def lookup_frame_transform(self, target_frame, source_frame, msg):
        stamp = Time.from_msg(msg.header.stamp)
        if stamp.nanoseconds == 0:
            self.get_logger().warning(
                f"丢弃零时间戳点云，不能匹配 {target_frame}->{source_frame} 位姿",
                throttle_duration_sec=5.0,
            )
            return None
        try:
            return self.tf_buffer.lookup_transform(
                target_frame,
                source_frame,
                stamp,
                timeout=Duration(seconds=0.02),
            )
        except TransformException as exact_error:
            try:
                latest = self.tf_buffer.lookup_transform(
                    target_frame,
                    source_frame,
                    Time(),
                    timeout=Duration(seconds=0.03),
                )
            except TransformException:
                latest = None
            if latest is not None:
                latest_stamp = Time.from_msg(latest.header.stamp)
                skew_ns = abs(latest_stamp.nanoseconds - stamp.nanoseconds)
                if skew_ns <= self.tf_latest_tolerance_ns:
                    return latest
            self.get_logger().warning(
                f"丢弃无法匹配时间戳的点云 {target_frame}->{source_frame}：{exact_error}",
                throttle_duration_sec=5.0,
            )
            return None

    def lookup_bootstrap_transform(self, target_frame, source_frame):
        try:
            return self.tf_buffer.lookup_transform(
                target_frame,
                source_frame,
                Time(),
                timeout=Duration(seconds=0.15),
            )
        except TransformException as exc:
            self.get_logger().warning(
                f"先验地图等待 {target_frame}->{source_frame} TF：{exc}",
                throttle_duration_sec=5.0,
            )
            return None

    def clear_current_robot_footprint(self, grid, xy_min, resolution, map_frame):
        try:
            transform = self.tf_buffer.lookup_transform(
                map_frame,
                self.robot_base_frame,
                Time(),
                timeout=Duration(seconds=0.03),
            )
        except TransformException:
            return
        translation = transform.transform.translation
        rotation = transform.transform.rotation
        yaw = math.atan2(
            2.0 * (rotation.w * rotation.z + rotation.x * rotation.y),
            1.0 - 2.0 * (rotation.y * rotation.y + rotation.z * rotation.z),
        )
        radius = math.hypot(
            max(abs(self.robot_x_min), abs(self.robot_x_max)),
            max(abs(self.robot_y_min), abs(self.robot_y_max)),
        )
        min_cell = np.floor(
            (np.asarray([translation.x - radius, translation.y - radius]) - xy_min)
            / resolution
        ).astype(np.int64)
        max_cell = np.ceil(
            (np.asarray([translation.x + radius, translation.y + radius]) - xy_min)
            / resolution
        ).astype(np.int64)
        height, width = grid.shape
        min_x, min_y = np.maximum(min_cell, 0)
        max_x = min(width - 1, int(max_cell[0]))
        max_y = min(height - 1, int(max_cell[1]))
        if min_x > max_x or min_y > max_y:
            return
        gx, gy = np.meshgrid(
            np.arange(min_x, max_x + 1), np.arange(min_y, max_y + 1)
        )
        world_x = xy_min[0] + (gx + 0.5) * resolution - translation.x
        world_y = xy_min[1] + (gy + 0.5) * resolution - translation.y
        cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
        local_x = cos_yaw * world_x + sin_yaw * world_y
        local_y = -sin_yaw * world_x + cos_yaw * world_y
        inside = (
            (local_x >= self.robot_x_min)
            & (local_x <= self.robot_x_max)
            & (local_y >= self.robot_y_min)
            & (local_y <= self.robot_y_max)
        )
        region = grid[min_y : max_y + 1, min_x : max_x + 1]
        region[inside] = 0


def main():
    rclpy.init()
    node = GlimMapProjector()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        while rclpy.ok():
            executor.spin_once(timeout_sec=0.2)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        executor.shutdown()
        executor.remove_node(node)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
