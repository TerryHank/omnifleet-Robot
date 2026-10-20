#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class FreshPointCloudFilter(Node):
    def __init__(self):
        super().__init__('fresh_pointcloud_filter')
        self.dropped = 0
        self.tf = TransformBroadcaster(self)
        self.pub = self.create_publisher(PointCloud2, '/rslidar_points_fresh', qos_profile_sensor_data)
        input_qos = QoSProfile(depth=5, reliability=ReliabilityPolicy.RELIABLE)
        self.sub = self.create_subscription(PointCloud2, '/rslidar_points', self.on_cloud, input_qos)
        self.create_timer(0.05, self.publish_tf)

    def publish_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'rslidar'
        t.transform.translation.x = -0.041
        t.transform.translation.z = 0.150
        t.transform.rotation.w = 1.0
        self.tf.sendTransform(t)

    def on_cloud(self, msg):
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        age = self.get_clock().now().nanoseconds * 1e-9 - stamp
        if age > 0.6 or age < -0.2:
            self.dropped += 1
            return
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = FreshPointCloudFilter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
