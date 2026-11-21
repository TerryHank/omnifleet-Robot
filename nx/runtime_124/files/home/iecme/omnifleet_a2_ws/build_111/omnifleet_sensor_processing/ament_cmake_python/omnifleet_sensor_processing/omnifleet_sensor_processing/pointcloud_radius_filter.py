#!/usr/bin/env python3
"""Drop lidar returns whose Euclidean distance from the lidar origin is < 5 cm."""

import math
import threading

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


class PointCloudRadiusFilter(Node):
    def __init__(self):
        super().__init__('pointcloud_radius_filter')
        self.declare_parameter('input_topic', '/rslidar_points')
        self.declare_parameter('output_topic', '/rslidar_points_filtered')
        self.declare_parameter('min_radius_m', 0.05)
        input_topic = str(self.get_parameter('input_topic').value)
        output_topic = str(self.get_parameter('output_topic').value)
        self.min_radius_sq = float(self.get_parameter('min_radius_m').value) ** 2
        self._latest = None
        self._condition = threading.Condition()
        self._stopping = False
        self.publisher = self.create_publisher(PointCloud2, output_topic, qos_profile_sensor_data)
        self.subscription = self.create_subscription(
            PointCloud2, input_topic, self.callback, qos_profile_sensor_data)
        self._worker = threading.Thread(target=self._run_filter, name='radius_filter_worker', daemon=True)
        self._worker.start()
        self.get_logger().info(
            f'filtering {input_topic} -> {output_topic}, '
            f'removing points with radius < {math.sqrt(self.min_radius_sq):.3f} m')

    def callback(self, message):
        # Do not let an expensive frame transform block the ROS receive callback.
        # A bounded latest-only mailbox prevents stale clouds from accumulating.
        with self._condition:
            self._latest = message
            self._condition.notify()

    def _run_filter(self):
        while True:
            with self._condition:
                self._condition.wait_for(lambda: self._stopping or self._latest is not None)
                if self._stopping:
                    return
                message = self._latest
                self._latest = None

            points = point_cloud2.read_points(message, skip_nans=True)
            xyz = points[['x', 'y', 'z']]
            keep = (xyz['x'] * xyz['x'] + xyz['y'] * xyz['y'] + xyz['z'] * xyz['z']) >= self.min_radius_sq
            self.publisher.publish(point_cloud2.create_cloud(message.header, message.fields, points[keep]))


def main():
    rclpy.init()
    node = PointCloudRadiusFilter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        with node._condition:
            node._stopping = True
            node._condition.notify()
        node._worker.join(timeout=2.0)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
