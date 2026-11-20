"""Publish Ranger feedback to the 104 chassis topics."""

import json
import math
import struct
import time
from pathlib import Path

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float32, String

from ranger_protocol import ACKERMANN, CRAB, FEEDBACK, PARK, SPIN, body_twist
from ranger_protocol import decode_feedback, open_can, unpack_frame


class RangerReceiver(Node):
    def __init__(self, bus):
        super().__init__("omnifleet_t2_driver")
        self.bus = bus
        self.bus.setblocking(False)
        self.odom = self.create_publisher(Odometry, "/odom", 20)
        self.velocity = self.create_publisher(Twist, "/vel_raw", 20)
        self.voltage = self.create_publisher(Float32, "/voltage", 10)
        self.feedback = self.create_publisher(String, "/ranger_can/feedback", 10)
        self.pending = {}
        self.mode = None
        self.previous_sample = None
        self.x = self.y = self.yaw = 0.0
        self.create_timer(0.005, self.read_bus)
        self.create_timer(0.1, self.publish_feedback)

    def read_bus(self):
        for _ in range(256):
            try:
                frame = unpack_frame(self.bus.recv(16))
            except BlockingIOError:
                break
            if frame is None:
                continue
            can_id, data = frame
            if can_id not in FEEDBACK:
                continue
            try:
                decoded = decode_feedback(can_id, data)
            except struct.error:
                continue
            self.pending[f"{can_id:03X}"] = decoded
            if can_id == 0x211:
                self.voltage.publish(Float32(data=decoded["voltage_dV"] / 10))
            elif can_id == 0x291:
                self.mode = decoded["motion_mode"]
            elif can_id == 0x221 and self.mode in (ACKERMANN, CRAB, SPIN, PARK):
                self.publish_odometry(decoded)

    def publish_feedback(self):
        if self.pending:
            self.feedback.publish(String(data=json.dumps(self.pending, separators=(",", ":"))))
            self.pending.clear()

    def publish_odometry(self, motion):
        vx, vy, wz = body_twist(self.mode, motion)
        now = time.monotonic()
        if self.previous_sample is not None:
            dt = now - self.previous_sample
            if dt < 0.5:
                heading = self.yaw + wz * dt / 2
                self.x += (vx * math.cos(heading) - vy * math.sin(heading)) * dt
                self.y += (vx * math.sin(heading) + vy * math.cos(heading)) * dt
                self.yaw += wz * dt
        self.previous_sample = now
        message = Odometry()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = "odom"
        message.child_frame_id = "base_link"
        message.pose.pose.position.x = self.x
        message.pose.pose.position.y = self.y
        message.pose.pose.orientation.z = math.sin(self.yaw / 2)
        message.pose.pose.orientation.w = math.cos(self.yaw / 2)
        message.twist.twist.linear.x = vx
        message.twist.twist.linear.y = vy
        message.twist.twist.angular.z = wz
        self.odom.publish(message)
        self.velocity.publish(message.twist.twist)


def main():
    interface = Path("/run/omnifleet-ranger-can/interface").read_text().strip()
    with open_can(interface) as bus:
        rclpy.init()
        node = RangerReceiver(bus)
        node.get_logger().info(f"Ranger feedback on {interface}, receive only")
        try:
            rclpy.spin(node)
        except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
            pass
        finally:
            node.destroy_node()
            rclpy.try_shutdown()


if __name__ == "__main__":
    main()
