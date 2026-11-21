#!/usr/bin/env python3
"""Publish Nav2 odometry from Cartographer pose and STM32 wheel velocity."""

import copy

import rclpy
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener


class CartographerOdomAdapter(Node):
    def __init__(self):
        super().__init__("omnifleet_t2_cartographer_odom_adapter")
        self.declare_parameter(
            "velocity_topic", "/omnifleet_t2/chassis/wheel_odometry"
        )
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
            self.get_parameter("velocity_topic").value,
            self.on_wheel_odometry,
            qos_profile_sensor_data,
        )

    def on_wheel_odometry(self, source):
        try:
            transform = self.tf_buffer.lookup_transform(
                self.odom_frame, self.base_frame, Time()
            )
        except TransformException as exc:
            self.get_logger().warning(
                f"等待 Cartographer {self.odom_frame} -> {self.base_frame} TF：{exc}",
                throttle_duration_sec=5.0,
            )
            return

        target = Odometry()
        target.header = transform.header
        target.header.frame_id = self.odom_frame
        target.child_frame_id = self.base_frame
        target.pose.pose.position.x = transform.transform.translation.x
        target.pose.pose.position.y = transform.transform.translation.y
        target.pose.pose.position.z = transform.transform.translation.z
        target.pose.pose.orientation = transform.transform.rotation
        target.pose.covariance = copy.deepcopy(source.pose.covariance)
        target.twist = copy.deepcopy(source.twist)
        self.publisher.publish(target)


def main():
    rclpy.init()
    node = CartographerOdomAdapter()
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
