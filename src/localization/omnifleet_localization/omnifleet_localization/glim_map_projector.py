#!/usr/bin/env python3
"""Build a stable 2D map from GLIM scans using temporal occupancy evidence."""

import math
import time

import numpy as np
import rclpy
from nav_msgs.msg import OccupancyGrid
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
    qos_profile_sensor_data,
)
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from tf2_ros import Buffer, TransformException, TransformListener

from .conservative_projection import (
    bridge_small_obstacle_gaps,
    clip_ray_at_guards,
    conservative_scan_segments,
    expand_cells,
    mask_for_cells,
    obstacle_support_cells,
    rasterize_segment,
)
from .occupancy_evidence import OccupancyEvidence


class GlimMapProjector(Node):
    def __init__(self):
        super().__init__("glim_map_projector")
        self.declare_parameter("input_topic", "/glim_ros/map")
        self.declare_parameter("aligned_points_topic", "/glim_ros/aligned_points")
        self.declare_parameter("accumulate_aligned_points", True)
        self.declare_parameter("output_topic", "/map")
        self.declare_parameter("resolution", 0.025)
        self.declare_parameter("padding", 1.0)
        self.declare_parameter("ground_relative_min", -0.03)
        self.declare_parameter("ground_relative_max", 0.03)
        self.declare_parameter("obstacle_relative_min", 0.06)
        self.declare_parameter("obstacle_relative_max", 1.80)
        self.declare_parameter("free_expansion_radius", 0.0)
        self.declare_parameter("clear_robot_footprint", True)
        self.declare_parameter("robot_base_frame", "base_link")
        self.declare_parameter("ground_z_offset_from_base", 0.0)
        self.declare_parameter("sensor_frame", "rslidar")
        self.declare_parameter("robot_footprint_x_min", -0.06)
        self.declare_parameter("robot_footprint_x_max", 0.42)
        self.declare_parameter("robot_footprint_y_min", -0.16)
        self.declare_parameter("robot_footprint_y_max", 0.16)
        self.declare_parameter("max_grid_cells", 1200)
        self.declare_parameter("accumulation_window_sec", 1.0)
        self.declare_parameter("max_aligned_rate", 3.0)

        self.declare_parameter("quality_hit_required", 5)
        self.declare_parameter("quality_hit_window", 10)
        self.declare_parameter("strong_hit_required", 3)
        self.declare_parameter("strong_hit_window", 4)
        self.declare_parameter("persistent_hit_required", 8)
        self.declare_parameter("persistent_hit_window", 12)
        self.declare_parameter("free_confirmation_scans", 3)
        self.declare_parameter("candidate_ttl", 3.0)
        self.declare_parameter("free_candidate_ttl", 2.0)
        self.declare_parameter("hit_spatial_tolerance_cells", 1)
        self.declare_parameter("quality_intensity_min", 1.0)
        self.declare_parameter("vertical_structure_min_span", 0.20)
        self.declare_parameter("structural_min_points", 3)
        self.declare_parameter("obstacle_support_radius_cells", 1)
        self.declare_parameter("confirmed_guard_timeout", 3.0)
        self.declare_parameter("wall_continuity_max_gap_cells", 2)
        self.declare_parameter("raytrace_max_range", 8.0)
        self.declare_parameter("ray_angular_resolution_deg", 0.4)
        self.declare_parameter("wall_stop_margin", 0.075)
        self.declare_parameter("wall_guard_cells", 2)
        self.declare_parameter("bootstrap_global_map", True)

        self.resolution = float(self.get_parameter("resolution").value)
        self.padding = float(self.get_parameter("padding").value)
        self.ground_min = float(self.get_parameter("ground_relative_min").value)
        self.ground_max = float(self.get_parameter("ground_relative_max").value)
        self.obstacle_min = float(self.get_parameter("obstacle_relative_min").value)
        self.obstacle_max = float(self.get_parameter("obstacle_relative_max").value)
        self.free_radius = float(self.get_parameter("free_expansion_radius").value)
        self.clear_robot_footprint = bool(
            self.get_parameter("clear_robot_footprint").value
        )
        self.robot_base_frame = str(self.get_parameter("robot_base_frame").value)
        self.ground_z_offset = float(
            self.get_parameter("ground_z_offset_from_base").value
        )
        self.fixed_ground_z = None
        self.sensor_frame = str(self.get_parameter("sensor_frame").value)
        self.robot_x_min = float(self.get_parameter("robot_footprint_x_min").value)
        self.robot_x_max = float(self.get_parameter("robot_footprint_x_max").value)
        self.robot_y_min = float(self.get_parameter("robot_footprint_y_min").value)
        self.robot_y_max = float(self.get_parameter("robot_footprint_y_max").value)
        if not (
            self.robot_x_min < self.robot_x_max
            and self.robot_y_min < self.robot_y_max
        ):
            raise ValueError("robot footprint bounds must be strictly increasing")
        self.max_cells = int(self.get_parameter("max_grid_cells").value)
        self.accumulation_window = float(
            self.get_parameter("accumulation_window_sec").value
        )
        aligned_rate = float(self.get_parameter("max_aligned_rate").value)
        self.aligned_min_period = 1.0 / aligned_rate if aligned_rate > 0.0 else 0.0
        self.raytrace_max_range = float(
            self.get_parameter("raytrace_max_range").value
        )
        self.ray_angle = math.radians(
            float(self.get_parameter("ray_angular_resolution_deg").value)
        )
        self.wall_stop_margin = float(
            self.get_parameter("wall_stop_margin").value
        )
        self.wall_guard_cells = int(
            self.get_parameter("wall_guard_cells").value
        )
        self.quality_intensity_min = float(
            self.get_parameter("quality_intensity_min").value
        )
        self.vertical_structure_min_span = float(
            self.get_parameter("vertical_structure_min_span").value
        )
        self.structural_min_points = int(
            self.get_parameter("structural_min_points").value
        )
        self.obstacle_support_radius = int(
            self.get_parameter("obstacle_support_radius_cells").value
        )
        self.confirmed_guard_timeout = float(
            self.get_parameter("confirmed_guard_timeout").value
        )
        self.wall_continuity_gap = int(
            self.get_parameter("wall_continuity_max_gap_cells").value
        )
        if not (
            self.ground_min < self.ground_max
            and self.ground_max < self.obstacle_min
            and self.obstacle_min < self.obstacle_max
        ):
            raise ValueError("ground and obstacle relative-height bands must be ordered")
        if self.accumulation_window <= 0.0:
            raise ValueError("accumulation_window_sec must be positive")
        if self.ray_angle <= 0.0 or self.wall_stop_margin < 0.0:
            raise ValueError("ray angle must be positive and wall margin non-negative")
        if self.wall_guard_cells < 0:
            raise ValueError("wall_guard_cells must be non-negative")
        if self.quality_intensity_min < 0.0:
            raise ValueError("quality_intensity_min must be non-negative")
        if self.vertical_structure_min_span <= 0.0:
            raise ValueError("vertical_structure_min_span must be positive")
        if self.structural_min_points < 1 or self.obstacle_support_radius < 0:
            raise ValueError("obstacle support settings are invalid")
        if self.confirmed_guard_timeout <= 0.0 or self.wall_continuity_gap < 0:
            raise ValueError("wall guard timeout and continuity gap are invalid")
        self.bootstrap_global_map = bool(
            self.get_parameter("bootstrap_global_map").value
        )
        self.evidence = OccupancyEvidence(
            hit_threshold=self.get_parameter("quality_hit_required").value,
            hit_window_size=self.get_parameter("quality_hit_window").value,
            strong_hit_threshold=self.get_parameter("strong_hit_required").value,
            strong_hit_window_size=self.get_parameter("strong_hit_window").value,
            persistent_hit_threshold=self.get_parameter(
                "persistent_hit_required"
            ).value,
            persistent_hit_window_size=self.get_parameter(
                "persistent_hit_window"
            ).value,
            miss_threshold=self.get_parameter("free_confirmation_scans").value,
            candidate_ttl=self.get_parameter("candidate_ttl").value,
            free_threshold=self.get_parameter("free_confirmation_scans").value,
            free_candidate_ttl=self.get_parameter("free_candidate_ttl").value,
            hit_tolerance_cells=self.get_parameter(
                "hit_spatial_tolerance_cells"
            ).value,
        )
        self.last_update = 0.0
        self.last_aligned_input = 0.0
        self.window_started = None
        self.pending_scans = []
        self.pending_map_frame = None
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        latched = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
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
        if bool(self.get_parameter("accumulate_aligned_points").value):
            self.create_subscription(
                PointCloud2,
                self.get_parameter("aligned_points_topic").value,
                self.on_aligned_cloud,
                qos_profile_sensor_data,
            )

    @staticmethod
    def decode(msg):
        cloud = point_cloud2.read_points(
            msg, field_names=("x", "y", "z", "intensity"), skip_nans=True
        )
        xyz = np.column_stack((cloud["x"], cloud["y"], cloud["z"])).astype(
            np.float32, copy=False
        )
        return xyz, np.asarray(cloud["intensity"], dtype=np.float32)

    def point_cells(self, points):
        if len(points) == 0:
            return set()
        indices = np.floor(points[:, :2] / self.resolution).astype(np.int64)
        return {tuple(cell) for cell in indices}

    def on_global_cloud(self, msg):
        """Use an existing GLIM map only as a restart/localization bootstrap."""
        if not self.bootstrap_global_map or self.evidence.has_data:
            return
        try:
            xyz, intensities = self.decode(msg)
        except (KeyError, ValueError) as exc:
            self.get_logger().warning(
                f"无法读取 GLIM 全局地图：{exc}", throttle_duration_sec=5.0
            )
            return
        if len(xyz) < 20:
            return
        map_frame = msg.header.frame_id or "map"
        base_transform = self.lookup_frame_transform(
            map_frame, self.robot_base_frame, msg
        )
        if base_transform is None:
            return
        ground_mask, obstacle_mask, relative_heights = self.height_masks(
            xyz, base_transform
        )
        strong_cells, _ = obstacle_support_cells(
            xyz,
            obstacle_mask,
            relative_heights,
            intensities,
            self.resolution,
            self.obstacle_support_radius,
            self.vertical_structure_min_span,
            self.quality_intensity_min,
            self.structural_min_points,
        )
        self.evidence.seed_confirmed(
            strong_cells,
            self.point_cells(xyz[ground_mask]),
            now=time.monotonic(),
        )
        self.get_logger().info(
            "已从 GLIM 全局地图恢复二维占用证据；后续由实时扫描负责清除动态残影"
        )
        self.publish_map(msg)

    def on_aligned_cloud(self, msg):
        now = time.monotonic()
        if (
            self.aligned_min_period
            and self.last_aligned_input
            and now - self.last_aligned_input < self.aligned_min_period
        ):
            return
        self.last_aligned_input = now
        try:
            xyz, intensities = self.decode(msg)
        except (KeyError, ValueError) as exc:
            self.get_logger().warning(
                f"无法读取 GLIM 对齐扫描：{exc}", throttle_duration_sec=5.0
            )
            return
        if len(xyz) < 20:
            return

        map_frame = msg.header.frame_id or "map"
        origin = self.lookup_sensor_origin(map_frame, msg)
        base_transform = self.lookup_frame_transform(
            map_frame, self.robot_base_frame, msg
        )
        if origin is None or base_transform is None:
            return
        ground_mask, obstacle_mask, relative_heights = self.height_masks(
            xyz, base_transform
        )

        if self.pending_map_frame not in {None, map_frame}:
            self.pending_scans.clear()
            self.window_started = None
        self.pending_map_frame = map_frame
        if self.window_started is None:
            self.window_started = now
        self.pending_scans.append(
            (
                xyz,
                intensities,
                relative_heights,
                ground_mask,
                obstacle_mask,
                origin,
            )
        )
        if now - self.window_started < self.accumulation_window:
            return
        self.process_scan_window(msg, now)

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
        base_z = delta @ map_from_base[:, 2]
        relative_height = base_z - self.ground_z_offset
        ground = (relative_height >= self.ground_min) & (
            relative_height <= self.ground_max
        )
        obstacle = (relative_height >= self.obstacle_min) & (
            relative_height <= self.obstacle_max
        )
        return ground, obstacle, relative_height

    def process_scan_window(self, msg, now):
        """Fuse one second of non-repetitive Airy scans conservatively."""
        occupied = set()
        strong_observations = set()
        quality_observations = set()
        segments = set()

        combined_xyz = np.concatenate(
            [scan[0] for scan in self.pending_scans], axis=0
        )
        combined_intensities = np.concatenate(
            [scan[1] for scan in self.pending_scans], axis=0
        )
        combined_heights = np.concatenate(
            [scan[2] for scan in self.pending_scans], axis=0
        )
        combined_obstacles = np.concatenate(
            [scan[4] for scan in self.pending_scans], axis=0
        )
        strong_cells, quality_cells = obstacle_support_cells(
            combined_xyz,
            combined_obstacles,
            combined_heights,
            combined_intensities,
            self.resolution,
            self.obstacle_support_radius,
            self.vertical_structure_min_span,
            self.quality_intensity_min,
            self.structural_min_points,
        )

        for (
            xyz,
            _intensities,
            _relative_heights,
            ground_mask,
            obstacle_mask,
            origin,
        ) in self.pending_scans:
            scan_occupied, _ = conservative_scan_segments(
                xyz,
                ground_mask,
                obstacle_mask,
                origin,
                self.resolution,
                self.ray_angle,
                0.10,
                self.raytrace_max_range,
                self.wall_stop_margin,
            )
            occupied.update(scan_occupied)

            # Only a spatially supported vertical structure is allowed to
            # block a free ray before temporal confirmation.  Low, isolated
            # candidates remain evidence candidates but cannot cast a gray
            # wall shadow.
            structural_mask = obstacle_mask & mask_for_cells(
                xyz, self.resolution, strong_cells
            )
            _, scan_segments = conservative_scan_segments(
                xyz,
                ground_mask,
                structural_mask,
                origin,
                self.resolution,
                self.ray_angle,
                0.10,
                self.raytrace_max_range,
                self.wall_stop_margin,
            )
            segments.update(scan_segments)

        strong_observations = occupied & strong_cells
        quality_observations = occupied & quality_cells

        active_confirmed = self.evidence.active_wall_guards(
            now, self.confirmed_guard_timeout
        )
        active_walls = bridge_small_obstacle_gaps(
            active_confirmed | strong_observations,
            self.wall_continuity_gap,
        )
        guards = expand_cells(
            active_walls, self.wall_guard_cells
        )
        free = set()
        for segment in segments:
            origin_cell = segment[0]
            ray = rasterize_segment(segment)
            free.update(clip_ray_at_guards(ray, guards, origin_cell))
        free.difference_update(guards)
        self.evidence.observe(
            occupied,
            free,
            now,
            strong_cells=strong_observations,
            quality_cells=quality_observations,
        )
        self.pending_scans.clear()
        self.window_started = now
        self.publish_map(msg)

    def publish_map(self, msg):
        if not self.evidence.confirmed and not self.evidence.known_free:
            return

        rendered_obstacles = bridge_small_obstacle_gaps(
            self.evidence.confirmed, self.wall_continuity_gap
        )
        all_cells = rendered_obstacles | self.evidence.known_free
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

        free_cells = output_cells(self.evidence.known_free)
        radius = max(0, int(math.ceil(self.free_radius / resolution)))
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy > radius * radius:
                    continue
                gx = free_cells[:, 0] + dx
                gy = free_cells[:, 1] + dy
                valid = (gx >= 0) & (gx < width) & (gy >= 0) & (gy < height)
                grid[gy[valid], gx[valid]] = 0

        obstacle_cells = output_cells(rendered_obstacles)
        grid[obstacle_cells[:, 1], obstacle_cells[:, 0]] = 100

        map_frame = msg.header.frame_id or "map"
        xy_min = lower.astype(np.float64) * self.resolution
        if self.clear_robot_footprint:
            self.clear_current_robot_footprint(grid, xy_min, resolution, map_frame)

        ground_z = self.lookup_robot_ground_z(map_frame)
        if ground_z is None:
            return

        output = OccupancyGrid()
        output.header = msg.header
        output.header.frame_id = map_frame
        output.info.map_load_time = self.get_clock().now().to_msg()
        output.info.resolution = resolution
        output.info.width = int(width)
        output.info.height = int(height)
        output.info.origin.position.x = float(xy_min[0])
        output.info.origin.position.y = float(xy_min[1])
        output.info.origin.position.z = ground_z
        output.info.origin.orientation.w = 1.0
        output.data = grid.ravel().tolist()
        self.publisher.publish(output)
        self.last_update = time.monotonic()
        self.get_logger().info(
            f"已发布证据化二维地图 {width}x{height}，分辨率 {resolution:.3f}m "
            f"（确认障碍={len(self.evidence.confirmed)}，连续墙格={len(rendered_obstacles)}，"
            f"候选={len(self.evidence.candidates)}，"
            f"确认自由={len(self.evidence.known_free)}，"
            f"自由候选={len(self.evidence.free_candidates)}）"
        )

    def lookup_sensor_origin(self, map_frame, msg):
        transform = self.lookup_frame_transform(map_frame, self.sensor_frame, msg)
        if transform is None:
            return None
        translation = transform.transform.translation
        return (translation.x, translation.y, translation.z)

    def lookup_frame_transform(self, target_frame, source_frame, msg):
        """Use only the transform matching the cloud stamp; never latest TF."""
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
                # GLIM publishes the aligned cloud and its transform very close
                # together.  A dedicated executor thread must be able to ingest
                # that TF while this callback waits; the recorded P95 arrival
                # difference on this vehicle is about 0.20 s.
                timeout=Duration(seconds=0.35),
            )
        except TransformException as exc:
            self.get_logger().warning(
                f"丢弃无法匹配点云时间戳的帧 {target_frame}->{source_frame}：{exc}",
                throttle_duration_sec=5.0,
            )
            return None

    def lookup_robot_ground_z(self, map_frame):
        if self.fixed_ground_z is not None:
            return self.fixed_ground_z

        try:
            transform = self.tf_buffer.lookup_transform(
                map_frame,
                self.robot_base_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
        except TransformException as exc:
            self.get_logger().warning(
                f"无法确定 {map_frame} 中的地面高度：{exc}",
                throttle_duration_sec=5.0,
            )
            return None

        base_z = float(transform.transform.translation.z)
        self.fixed_ground_z = base_z + self.ground_z_offset
        self.get_logger().info(
            f"已固定二维栅格地面高度 z={self.fixed_ground_z:.4f}m "
            f"（首次 {map_frame}->{self.robot_base_frame}.z={base_z:.4f}m，"
            f"地面偏移={self.ground_z_offset:.4f}m）"
        )
        return self.fixed_ground_z

    def clear_current_robot_footprint(self, grid, xy_min, resolution, map_frame):
        try:
            transform = self.tf_buffer.lookup_transform(
                map_frame,
                self.robot_base_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
        except TransformException as exc:
            self.get_logger().warning(
                f"无法在 {map_frame} 中清除机器人轮廓：{exc}",
                throttle_duration_sec=5.0,
            )
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
            (np.array([translation.x - radius, translation.y - radius]) - xy_min)
            / resolution
        ).astype(np.int64)
        max_cell = np.ceil(
            (np.array([translation.x + radius, translation.y + radius]) - xy_min)
            / resolution
        ).astype(np.int64)

        height, width = grid.shape
        min_x = max(0, int(min_cell[0]))
        min_y = max(0, int(min_cell[1]))
        max_x = min(width - 1, int(max_cell[0]))
        max_y = min(height - 1, int(max_cell[1]))
        if min_x > max_x or min_y > max_y:
            return

        gx, gy = np.meshgrid(
            np.arange(min_x, max_x + 1), np.arange(min_y, max_y + 1)
        )
        world_x = xy_min[0] + (gx + 0.5) * resolution - translation.x
        world_y = xy_min[1] + (gy + 0.5) * resolution - translation.y
        cos_yaw = math.cos(yaw)
        sin_yaw = math.sin(yaw)
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
    # TransformListener uses a re-entrant callback group.  Two executor threads
    # let /tf enter its buffer while an aligned-cloud callback waits for the
    # transform at the exact cloud stamp.  With a single-threaded executor the
    # wait itself blocked /tf, causing repeated multi-second frame drops.
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
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
