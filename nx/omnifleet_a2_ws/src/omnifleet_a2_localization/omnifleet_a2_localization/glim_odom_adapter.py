#!/usr/bin/env python3
"""Expose GLIM's native base TF as a REP-105 Odometry message.

GLIM remains the only pose estimator and TF broadcaster. This node only fixes
the message-level child frame: GLIM's native odometry describes the IMU pose,
while Nav2 and diagnostics expect the configured robot base frame.
"""

import rclpy
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener

from .vector_math import rotate_vector_inverse


class GlimOdomAdapter(Node):
    def __init__(self):
        super().__init__("omnifleet_a2_glim_odom_adapter")
        self.declare_parameter("input_topic", "/glim_ros/odom")
        self.declare_parameter("output_topic", "/odom")
        self.declare_parameter("odom_frame", "odom")
        self.declare_parameter("base_frame", "base_link")

        self.odom_frame = str(self.get_parameter("odom_frame").value)
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.publisher = self.create_publisher(
            Odometry, self.get_parameter("output_topic").value, 20
        )
        self.subscription = self.create_subscription(
            Odometry,
            self.get_parameter("input_topic").value,
            self.on_odometry,
            qos_profile_sensor_data,
        )

    def on_odometry(self, source):
        try:
            transform = self.tf_buffer.lookup_transform(
                self.odom_frame, self.base_frame, Time()
            )
        except TransformException as exc:
            self.get_logger().warning(
                f"等待 GLIM 原生 {self.odom_frame} -> {self.base_frame} TF：{exc}",
                throttle_duration_sec=5.0,
            )
            return

        target = Odometry()
        target.header = source.header
        target.header.frame_id = self.odom_frame
        target.child_frame_id = self.base_frame
        target.pose.pose.position.x = transform.transform.translation.x
        target.pose.pose.position.y = transform.transform.translation.y
        target.pose.pose.position.z = transform.transform.translation.z
        target.pose.pose.orientation = transform.transform.rotation
        target.pose.covariance = source.pose.covariance

        quaternion = (
            transform.transform.rotation.x,
            transform.transform.rotation.y,
            transform.transform.rotation.z,
            transform.transform.rotation.w,
        )
        linear = rotate_vector_inverse(
            (
                source.twist.twist.linear.x,
                source.twist.twist.linear.y,
                source.twist.twist.linear.z,
            ),
            quaternion,
        )
        target.twist.twist.linear.x = linear[0]
        target.twist.twist.linear.y = linear[1]
        target.twist.twist.linear.z = linear[2]
        target.twist.twist.angular = source.twist.twist.angular
        target.twist.covariance = source.twist.covariance
        self.publisher.publish(target)


def main():
    rclpy.init()
    node = GlimOdomAdapter()
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
