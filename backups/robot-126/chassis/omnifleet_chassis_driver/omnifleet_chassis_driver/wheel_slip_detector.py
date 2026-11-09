#!/usr/bin/env python3
import math

import rclpy
from rclpy.executors import ExternalShutdownException
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Bool, Float32


class WheelSlipDetector(Node):
    def __init__(self):
        super().__init__('omnifleet_t2_wheel_slip_detector')
        self.declare_parameter('wheel_odom_topic', '/omnifleet_t2/chassis/wheel_odometry')
        self.declare_parameter('primary_odom_topic', '/odom')
        self.declare_parameter('minimum_wheel_speed', 0.12)
        self.declare_parameter('slip_ratio_threshold', 0.35)
        self.declare_parameter('hold_time_sec', 0.6)
        self.minimum_speed = float(self.get_parameter('minimum_wheel_speed').value)
        self.threshold = float(self.get_parameter('slip_ratio_threshold').value)
        self.hold_ns = int(float(self.get_parameter('hold_time_sec').value) * 1.0e9)
        self.wheel_speed = 0.0
        self.primary_speed = 0.0
        self.last_primary = None
        self.suspect_since = None
        self.slip_pub = self.create_publisher(Bool, '/diagnostics/wheel_slip', 10)
        self.ratio_pub = self.create_publisher(Float32, '/diagnostics/wheel_speed_ratio', 10)
        self.create_subscription(
            Odometry, self.get_parameter('wheel_odom_topic').value,
            self.on_wheel, qos_profile_sensor_data)
        self.create_subscription(
            Odometry, self.get_parameter('primary_odom_topic').value,
            self.on_primary, qos_profile_sensor_data)
        self.create_timer(0.1, self.evaluate)

    def on_wheel(self, msg):
        v = msg.twist.twist.linear
        self.wheel_speed = math.hypot(v.x, v.y)

    def on_primary(self, msg):
        stamp = int(msg.header.stamp.sec) * 1_000_000_000 + int(msg.header.stamp.nanosec)
        p = msg.pose.pose.position
        if self.last_primary is not None:
            last_stamp, x, y = self.last_primary
            dt = (stamp - last_stamp) / 1.0e9
            if 0.01 < dt < 1.0:
                speed = math.hypot(p.x - x, p.y - y) / dt
                self.primary_speed = 0.7 * self.primary_speed + 0.3 * speed
        self.last_primary = (stamp, p.x, p.y)

    def evaluate(self):
        ratio = self.primary_speed / max(self.wheel_speed, 1.0e-3)
        now = self.get_clock().now().nanoseconds
        suspect = self.wheel_speed >= self.minimum_speed and ratio < self.threshold
        if suspect:
            if self.suspect_since is None:
                self.suspect_since = now
        else:
            self.suspect_since = None
        slipping = self.suspect_since is not None and now - self.suspect_since >= self.hold_ns
        self.ratio_pub.publish(Float32(data=float(ratio)))
        self.slip_pub.publish(Bool(data=slipping))


def main():
    rclpy.init()
    node = WheelSlipDetector()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
