#!/usr/bin/env python3
"""Adapt Nav2 yaw commands to the chassis steering sign convention."""

from copy import deepcopy

import rclpy
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


def scale_angular_z(message: Twist, scale: float) -> Twist:
    output = deepcopy(message)
    output.angular.z *= scale
    return output


def adapt_navigation_twist(
    message: Twist,
    angular_scale: float,
    minimum_linear_speed: float,
    maximum_angular_speed: float,
    minimum_turning_radius: float = 0.0,
) -> Twist:
    """Map a Nav2 command into the chassis executable-speed envelope."""
    output = scale_angular_z(message, angular_scale)
    speed = float(output.linear.x)
    if abs(speed) <= 1.0e-6:
        # Nav2 cannot request an in-place turn from an Ackermann chassis.
        output.linear.x = 0.0
        output.angular.z = 0.0
        return output
    if abs(speed) < minimum_linear_speed:
        factor = minimum_linear_speed / abs(speed)
        output.linear.x = minimum_linear_speed if speed > 0.0 else -minimum_linear_speed
        output.angular.z *= factor
    yaw_limit = maximum_angular_speed
    if minimum_turning_radius > 0.0:
        yaw_limit = min(yaw_limit, abs(output.linear.x) / minimum_turning_radius)
    output.angular.z = max(-yaw_limit, min(yaw_limit, output.angular.z))
    return output


class NavSteeringAdapter(Node):
    def __init__(self):
        super().__init__("nav_steering_adapter")
        input_topic = str(
            self.declare_parameter("input_topic", "/cmd_vel_nav_smoothed").value
        )
        output_topic = str(
            self.declare_parameter("output_topic", "/cmd_vel_nav_adjusted").value
        )
        self.angular_scale = float(
            self.declare_parameter("angular_scale", -1.0).value
        )
        self.minimum_linear_speed = max(
            0.0,
            float(self.declare_parameter("minimum_linear_speed", 0.0).value),
        )
        self.maximum_angular_speed = max(
            0.0,
            float(self.declare_parameter("maximum_angular_speed", 0.3).value),
        )
        self.minimum_turning_radius = float(
            self.declare_parameter("minimum_turning_radius", 0.0).value
        )
        self.publisher = self.create_publisher(Twist, output_topic, 10)
        self.fleet_hold=False
        self.hold_subscription=self.create_subscription(Bool,'/navigation/fleet/hold',self.on_fleet_hold,1)
        self.subscription = self.create_subscription(
            Twist, input_topic, self.on_command, 10
        )
        self.get_logger().info(
            "Navigation steering adapter: %s -> %s, angular.z scale=%.1f, "
            "nonzero |v|>=%.2f m/s, |w|<=%.2f rad/s, radius>=%.2f m"
            % (
                input_topic,
                output_topic,
                self.angular_scale,
                self.minimum_linear_speed,
                self.maximum_angular_speed,
                self.minimum_turning_radius,
            )
        )

    def on_fleet_hold(self,message):
        self.fleet_hold=message.data
        if self.fleet_hold:self.publisher.publish(Twist())

    def on_command(self, message: Twist) -> None:
        if self.fleet_hold:
            self.publisher.publish(Twist());return
        self.publisher.publish(
            adapt_navigation_twist(
                message,
                self.angular_scale,
                self.minimum_linear_speed,
                self.maximum_angular_speed,
                self.minimum_turning_radius,
            )
        )


def main():
    rclpy.init()
    node = NavSteeringAdapter()
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
