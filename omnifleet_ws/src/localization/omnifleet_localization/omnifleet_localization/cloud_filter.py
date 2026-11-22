#!/usr/bin/env python3
import math

import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
    qos_profile_sensor_data,
)
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2


def rpy_matrix(roll, pitch, yaw):
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return np.asarray(
        [
            [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
            [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
            [-sp, cp * sr, cp * cr],
        ],
        dtype=np.float32,
    )


XYZ32_FIELDS = [
    PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
    PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
    PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
]


def xyz32_cloud(header, points):
    # Avoid creating tens of thousands of Python tuples for each output frame.
    points = np.ascontiguousarray(points, dtype="<f4")
    output = PointCloud2()
    output.header = header
    output.height = 1
    output.width = len(points)
    output.fields = XYZ32_FIELDS
    output.is_bigendian = False
    output.point_step = 12
    output.row_step = output.point_step * output.width
    output.is_dense = True
    output.data = points.tobytes()
    return output


class CloudFilter(Node):
    def __init__(self):
        super().__init__("cloud_filter")
        for name, default in (
            ("input_topic", "/points"), ("output_topic", "/points_filtered"),
            ("output_frame", ""), ("translation", [0.0, 0.0, 0.0]),
            ("rotation_rpy", [0.0, 0.0, 0.0]), ("range_min", 0.0),
            ("range_max", 100.0), ("z_min", -100.0), ("z_max", 100.0),
            ("voxel_size", 0.05), ("max_rate", 10.0), ("remove_self", False),
            ("self_min", [-0.30, -0.25, -0.10]), ("self_max", [0.30, 0.25, 0.55]),
        ):
            self.declare_parameter(name, default)
        self.output_frame = self.get_parameter("output_frame").value
        self.translation = np.asarray(self.get_parameter("translation").value, dtype=np.float32)
        self.rotation = rpy_matrix(*self.get_parameter("rotation_rpy").value)
        self.range_min = float(self.get_parameter("range_min").value)
        self.range_max = float(self.get_parameter("range_max").value)
        self.z_min = float(self.get_parameter("z_min").value)
        self.z_max = float(self.get_parameter("z_max").value)
        self.voxel = float(self.get_parameter("voxel_size").value)
        rate = float(self.get_parameter("max_rate").value)
        self.min_period_ns = int(1.0e9 / rate) if rate > 0.0 else 0
        self.remove_self = bool(self.get_parameter("remove_self").value)
        self.self_min = np.asarray(self.get_parameter("self_min").value, dtype=np.float32)
        self.self_max = np.asarray(self.get_parameter("self_max").value, dtype=np.float32)
        self.last_stamp_ns = 0
        self.publisher = self.create_publisher(
            PointCloud2, self.get_parameter("output_topic").value, qos_profile_sensor_data
        )
        # Filtering a dense non-repetitive Livox scan can take longer than one
        # input period. Keep only the latest scan instead of processing an old
        # queue and feeding stale obstacles to Collision Monitor.
        latest_sensor_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.create_subscription(
            PointCloud2,
            self.get_parameter("input_topic").value,
            self.on_cloud,
            latest_sensor_qos,
        )

    def on_cloud(self, msg):
        stamp_ns = int(msg.header.stamp.sec) * 1_000_000_000 + int(msg.header.stamp.nanosec)
        if self.min_period_ns and self.last_stamp_ns and stamp_ns - self.last_stamp_ns < self.min_period_ns:
            return
        try:
            structured = point_cloud2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
            points = np.column_stack((structured["x"], structured["y"], structured["z"])).astype(np.float32, copy=False)
        except (KeyError, ValueError) as exc:
            self.get_logger().warning(f"无法解析 PointCloud2：{exc}", throttle_duration_sec=5.0)
            return
        points = points @ self.rotation.T + self.translation
        range_sq = np.einsum("ij,ij->i", points, points)
        mask = (
            (range_sq >= self.range_min ** 2) & (range_sq <= self.range_max ** 2)
            & (points[:, 2] >= self.z_min) & (points[:, 2] <= self.z_max)
        )
        if self.remove_self:
            mask &= ~np.all((points >= self.self_min) & (points <= self.self_max), axis=1)
        points = points[mask]
        if not len(points):
            return
        if self.voxel > 0.0:
            keys = np.ascontiguousarray(
                np.floor(points / self.voxel).astype(np.int32)
            )
            row_keys = keys.view(
                np.dtype((np.void, keys.dtype.itemsize * keys.shape[1]))
            ).ravel()
            _, indices = np.unique(row_keys, return_index=True)
            points = points[np.sort(indices)]
        header = msg.header
        if self.output_frame:
            header.frame_id = self.output_frame
        self.publisher.publish(xyz32_cloud(header, points))
        self.last_stamp_ns = stamp_ns


def main():
    rclpy.init()
    node = CloudFilter()
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
