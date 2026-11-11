#!/usr/bin/env python3
"""Publish the navigation height band for visualization only."""
import numpy as np
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2

INPUT = '/navigation/deskewed_points'
OUTPUT = '/navigation/height_filtered_points'
MIN_Z = -0.03
MAX_Z = 0.5
VOXEL_SIZE = 0.08
MAX_RATE_HZ = 2.0


def filter_cloud(message):
    fields = {field.name: field for field in message.fields}
    endian = '>' if message.is_bigendian else '<'
    formats = {7: 'f4', 8: 'f8'}
    dtype = np.dtype({
        'names': ['x', 'y', 'z'],
        'formats': [endian + formats[fields[k].datatype] for k in ('x', 'y', 'z')],
        'offsets': [fields[k].offset for k in ('x', 'y', 'z')],
        'itemsize': message.point_step,
    })
    points = np.ndarray((message.height, message.width), dtype=dtype,
                        buffer=message.data, strides=(message.row_step, message.point_step))
    valid = np.isfinite(points['x']) & np.isfinite(points['y']) & np.isfinite(points['z'])
    valid &= (points['z'] >= MIN_Z) & (points['z'] <= MAX_Z)
    records = np.ndarray((message.height, message.width, message.point_step), dtype=np.uint8,
                         buffer=message.data, strides=(message.row_step, message.point_step, 1))
    selected = records[valid]
    if len(selected):
        xyz = np.column_stack([points[name][valid] for name in ('x', 'y', 'z')])
        _, indices = np.unique(np.floor(xyz / VOXEL_SIZE).astype(np.int64), axis=0, return_index=True)
        selected = selected[indices]
    result = PointCloud2()
    result.header = message.header
    result.fields = message.fields
    result.is_bigendian = message.is_bigendian
    result.point_step = message.point_step
    result.height = 1
    result.width = len(selected)
    result.row_step = result.width * result.point_step
    result.is_dense = True
    result.data = selected.tobytes()
    return result


class HeightFilteredCloud(Node):
    def __init__(self):
        super().__init__('navigation_height_cloud_visualizer')
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.publisher = self.create_publisher(PointCloud2, OUTPUT, qos)
        self.subscription = self.create_subscription(PointCloud2, INPUT, self.on_cloud, qos)
        self.last_publish = 0.
        self.get_logger().info(f'{INPUT} -> {OUTPUT}: map Z in [{MIN_Z}, {MAX_Z}] m')

    def on_cloud(self, message):
        if not self.publisher.get_subscription_count():
            return
        now = time.monotonic()
        if now-self.last_publish < 1./MAX_RATE_HZ:
            return
        if message.header.frame_id.lstrip('/') != 'map':
            self.get_logger().warning(
                'Expected map-frame cloud; refusing to apply map-height limits in another frame',
                throttle_duration_sec=5.0)
            return
        self.publisher.publish(filter_cloud(message))
        self.last_publish = now


def main():
    rclpy.init()
    node = HeightFilteredCloud()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
