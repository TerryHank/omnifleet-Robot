import math
import time
from copy import deepcopy

import numpy as np
import rclpy
from grid_map_msgs.msg import GridMap
from nav_msgs.msg import OccupancyGrid
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Float32MultiArray, MultiArrayDimension

from omnifleet_terrain_analysis.terrain_analysis import TERRAIN_LAYERS, analyze_terrain


class TerrainMapper(Node):
    """Generate GridMap terrain layers and a Nav2-compatible terrain cost map."""

    def __init__(self):
        super().__init__("omnifleet_t2_terrain_mapper")
        defaults = (
            ("input_cloud_topic", "/rslidar_points"),
            ("static_map_topic", "/map"),
            ("output_grid_map_topic", "/omnifleet_t2/terrain/grid_map"),
            ("output_costmap_topic", "/omnifleet_t2/terrain/costmap"),
            ("max_update_rate", 0.20),
            ("max_input_points", 2000000),
            ("min_points_per_cell", 1),
            ("ground_band", 0.12),
            ("hole_fill_iterations", 2),
            ("max_slope_deg", 15.0),
            ("max_roughness", 0.05),
            ("max_step_height", 0.10),
        )
        for name, value in defaults:
            self.declare_parameter(name, value)

        self.static_map = None
        self.global_points = np.empty((0, 3), dtype=np.float32)
        self.cloud_frame = ""
        self.last_update = 0.0
        self.min_period = 1.0 / max(
            float(self.get_parameter("max_update_rate").value), 1e-6
        )

        latched = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.grid_map_publisher = self.create_publisher(
            GridMap, self.get_parameter("output_grid_map_topic").value, latched
        )
        self.costmap_publisher = self.create_publisher(
            OccupancyGrid, self.get_parameter("output_costmap_topic").value, latched
        )
        self.static_map_subscription = self.create_subscription(
            OccupancyGrid,
            self.get_parameter("static_map_topic").value,
            self.on_static_map,
            latched,
        )
        self.global_cloud_subscription = self.create_subscription(
            PointCloud2,
            self.get_parameter("input_cloud_topic").value,
            self.on_global_cloud,
            latched,
        )

    def on_static_map(self, message):
        self.static_map = message
        self.try_publish()

    def on_global_cloud(self, message):
        try:
            points = self.decode_cloud(message)
        except (KeyError, ValueError) as error:
            self.get_logger().error(f"无法读取全局点云：{error}")
            return
        self.global_points = self.limit_points(points)
        self.cloud_frame = message.header.frame_id or "map"
        self.try_publish()

    def limit_points(self, points):
        maximum = int(self.get_parameter("max_input_points").value)
        if maximum > 0 and len(points) > maximum:
            stride = int(math.ceil(len(points) / maximum))
            points = points[::stride]
        return points.astype(np.float32, copy=False)

    @staticmethod
    def decode_cloud(message):
        cloud = point_cloud2.read_points(
            message, field_names=("x", "y", "z"), skip_nans=True
        )
        return np.column_stack((cloud["x"], cloud["y"], cloud["z"])).astype(
            np.float32, copy=False
        )

    @staticmethod
    def quaternion_yaw(quaternion):
        return math.atan2(
            2.0 * (
                quaternion.w * quaternion.z + quaternion.x * quaternion.y
            ),
            1.0
            - 2.0
            * (quaternion.y * quaternion.y + quaternion.z * quaternion.z),
        )

    def try_publish(self):
        if self.static_map is None or len(self.global_points) == 0:
            return
        now = time.monotonic()
        if now - self.last_update < self.min_period:
            return
        map_frame = self.static_map.header.frame_id or "map"
        cloud_frame = self.cloud_frame or "map"
        if cloud_frame != map_frame:
            self.get_logger().error(
                f"2.5D输入坐标系不一致：点云={cloud_frame}，静态地图={map_frame}"
            )
            return

        points = self.global_points

        info = self.static_map.info
        origin = info.origin
        try:
            layers, cost = analyze_terrain(
                points,
                width=info.width,
                height=info.height,
                resolution=info.resolution,
                origin_x=origin.position.x,
                origin_y=origin.position.y,
                origin_yaw=self.quaternion_yaw(origin.orientation),
                static_occupancy=self.static_map.data,
                min_points_per_cell=int(
                    self.get_parameter("min_points_per_cell").value
                ),
                ground_band=float(self.get_parameter("ground_band").value),
                hole_fill_iterations=int(
                    self.get_parameter("hole_fill_iterations").value
                ),
                max_slope_deg=float(
                    self.get_parameter("max_slope_deg").value
                ),
                max_roughness=float(
                    self.get_parameter("max_roughness").value
                ),
                max_step_height=float(
                    self.get_parameter("max_step_height").value
                ),
            )
        except ValueError as error:
            self.get_logger().error(f"2.5D地形分析失败：{error}")
            return

        stamp = self.get_clock().now().to_msg()
        grid_map = self.make_grid_map(layers, stamp)
        terrain_costmap = OccupancyGrid()
        terrain_costmap.header.stamp = stamp
        terrain_costmap.header.frame_id = map_frame
        terrain_costmap.info = deepcopy(info)
        terrain_costmap.info.map_load_time = stamp
        terrain_costmap.data = cost.ravel(order="C").tolist()

        self.grid_map_publisher.publish(grid_map)
        self.costmap_publisher.publish(terrain_costmap)
        self.last_update = now
        known = np.isfinite(layers["elevation"])
        lethal = cost == 100
        self.get_logger().info(
            "已发布2.5D地形："
            f"{info.width}x{info.height}，有效地形={int(np.count_nonzero(known))}，"
            f"致命地形={int(np.count_nonzero(lethal))}"
        )

    def make_grid_map(self, layers, stamp):
        info = self.static_map.info
        message = GridMap()
        message.header.stamp = stamp
        message.header.frame_id = self.static_map.header.frame_id or "map"
        message.info.resolution = float(info.resolution)
        message.info.length_x = float(info.width * info.resolution)
        message.info.length_y = float(info.height * info.resolution)

        origin = info.origin
        yaw = self.quaternion_yaw(origin.orientation)
        half_x = message.info.length_x * 0.5
        half_y = message.info.length_y * 0.5
        message.info.pose.position.x = (
            origin.position.x + math.cos(yaw) * half_x - math.sin(yaw) * half_y
        )
        message.info.pose.position.y = (
            origin.position.y + math.sin(yaw) * half_x + math.cos(yaw) * half_y
        )
        message.info.pose.position.z = origin.position.z
        message.info.pose.orientation = origin.orientation
        message.layers = list(TERRAIN_LAYERS)
        message.basic_layers = ["elevation"]
        message.data = [self.layer_message(layers[name]) for name in TERRAIN_LAYERS]
        message.outer_start_index = 0
        message.inner_start_index = 0
        return message

    @staticmethod
    def layer_message(layer):
        height, width = layer.shape
        message = Float32MultiArray()
        message.layout.dim = [
            MultiArrayDimension(
                label="row_index", size=height, stride=height * width
            ),
            MultiArrayDimension(label="column_index", size=width, stride=width),
        ]
        message.layout.data_offset = 0
        message.data = layer.astype(np.float32, copy=False).ravel(order="C").tolist()
        return message


def main():
    rclpy.init()
    node = TerrainMapper()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
