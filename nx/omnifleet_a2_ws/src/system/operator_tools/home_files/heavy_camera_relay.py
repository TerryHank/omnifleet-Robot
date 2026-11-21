#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image, PointCloud2


class HeavyCameraRelay(Node):
    def __init__(self):
        super().__init__('heavy_camera_relay')
        self.points_pub = self.create_publisher(
            PointCloud2, '/tof/points', qos_profile_sensor_data
        )
        self.depth_pub = self.create_publisher(
            Image, '/tof/aligned_depth_to_color/image_raw', qos_profile_sensor_data
        )
        self.depth_info_pub = self.create_publisher(
            CameraInfo,
            '/tof/aligned_depth_to_color/camera_info',
            qos_profile_sensor_data,
        )
        self.color_pub = self.create_publisher(
            Image, '/tof/color/image_raw', qos_profile_sensor_data
        )
        self.color_info_pub = self.create_publisher(
            CameraInfo, '/tof/color/camera_info', qos_profile_sensor_data
        )
        self.create_subscription(
            PointCloud2,
            '/camera/depth_registered/points',
            self.points_pub.publish,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_pub.publish,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            CameraInfo,
            '/camera/depth/camera_info',
            self.depth_info_pub.publish,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.color_pub.publish,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            CameraInfo,
            '/camera/color/camera_info',
            self.color_info_pub.publish,
            qos_profile_sensor_data,
        )


def main():
    rclpy.init()
    node = HeavyCameraRelay()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
