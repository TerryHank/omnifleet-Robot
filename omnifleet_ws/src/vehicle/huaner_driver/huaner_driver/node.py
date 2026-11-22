import math
import struct
import time

import rclpy
import serial
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from ros_robot_controller.ros_robot_controller_sdk import checksum_crc8
from std_msgs.msg import Float32, UInt8, UInt8MultiArray


HEADER = b"\xaa\x55"


def signed_tick_delta(current, previous):
    return (current - previous + 2**31) % 2**32 - 2**31


def stick_axis(raw):
    delta = raw - 1002
    if abs(delta) <= 60:
        return 0.0
    return math.copysign(min(1.0, (abs(delta) - 60) / 660), delta)


class HuanerDriver(Node):
    def __init__(self):
        super().__init__("huaner_driver")
        self.declare_parameter("body_dimensions_m", [0.50, 0.37, 0.33])
        self.declare_parameter("track_separation_m", 0.33)
        self.declare_parameter("drive_sprocket_diameter_m", 0.054)
        self.declare_parameter("left_motor_sign", -1.0)
        self.declare_parameter("right_motor_sign", 1.0)
        self.declare_parameter("encoder_ticks_per_rev", 1980.0)
        self.declare_parameter("input_topic", "/navigation/cmd_vel_safe")
        self.declare_parameter(
            "serial_port", "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5C67041434-if00"
        )
        self.half_track = self.get_parameter("track_separation_m").value / 2
        self.circumference = math.pi * self.get_parameter("drive_sprocket_diameter_m").value
        self.metres_per_tick = self.circumference / self.get_parameter("encoder_ticks_per_rev").value
        self.left_sign = self.get_parameter("left_motor_sign").value
        self.right_sign = self.get_parameter("right_motor_sign").value
        self.port = serial.Serial(
            self.get_parameter("serial_port").value, 115200, timeout=0,
            write_timeout=0.2, exclusive=True,
        )
        self.buffer = bytearray()
        self.target = (0.0, 0.0)
        self.last_command = None
        self.encoder_sample = None
        self.sbus_motion = False
        self.last_sbus = None
        self.sbus = self.create_publisher(UInt8MultiArray, "/huaner_driver/sbus_raw", 10)
        self.manual = self.create_publisher(Twist, "/cmd_vel", 1)
        self.x = self.y = self.yaw = 0.0
        self.odom = self.create_publisher(Odometry, '/odom', 20)
        self.velocity = self.create_publisher(Twist, '/vel_raw', 20)
        self.ack = self.create_publisher(UInt8, "~/motor_ack", 10)
        self.telemetry = self.create_publisher(UInt8MultiArray, "~/telemetry_raw", 10)
        self.voltage = self.create_publisher(Float32, "/voltage", 10)
        self.create_subscription(Twist, self.get_parameter("input_topic").value, self.on_command, 1)
        self.create_timer(0.05, self.update)
        self.send_motor(bytes([3, 15]))

    def send_motor(self, payload):
        body = bytes([3, len(payload)]) + payload
        self.port.write(HEADER + body + bytes([checksum_crc8(body)]))

    def on_command(self, msg):
        linear, angular = msg.linear.x, msg.angular.z
        if not (math.isfinite(linear) and math.isfinite(angular)):
            self.target = (0.0, 0.0)
            self.last_command = None
            self.send_motor(bytes([3, 15]))
            return
        turn = angular * self.half_track
        left = (linear - turn) / self.circumference
        right = (linear + turn) / self.circumference
        self.target = (self.left_sign * left, self.right_sign * right)
        self.last_command = time.monotonic()

    def update(self):
        if self.last_command is not None:
            if time.monotonic() - self.last_command > 0.35:
                self.send_motor(bytes([3, 15]))
                self.last_command = None
            else:
                left, right = self.target
                self.send_motor(struct.pack("<BBBfBf", 1, 2, 0, left, 1, right))
        if self.sbus_motion and time.monotonic() - self.last_sbus > 0.2:
            self.publish_sbus_velocity(Twist())
        latest_telemetry = None
        self.buffer.extend(self.port.read(self.port.in_waiting))
        while len(self.buffer) >= 5:
            start = self.buffer.find(HEADER)
            if start < 0:
                del self.buffer[:-1]
                break
            del self.buffer[:start]
            if len(self.buffer) < 5:
                break
            end = 5 + self.buffer[3]
            if len(self.buffer) < end:
                break
            frame = self.buffer[:end]
            if checksum_crc8(frame[2:-1]) != frame[-1]:
                del self.buffer[0]
                continue
            del self.buffer[:end]
            payload = frame[4:-1]
            if frame[2] == 9 and len(payload) == 36:
                self.on_sbus(payload)
            elif frame[2] == 0 and len(payload) == 4 and payload[:3] == b"ROS":
                self.ack.publish(UInt8(data=payload[3]))
            elif frame[2] == 0 and len(payload) == 88 and payload[:4] == b"RRC\x01":
                self.telemetry.publish(UInt8MultiArray(data=list(payload)))
                latest_telemetry = payload
        if latest_telemetry is not None:
            self.publish_odometry(latest_telemetry)
            battery_mv = struct.unpack_from("<H", latest_telemetry, 6)[0]
            if 0 < battery_mv <= 20000:
                self.voltage.publish(Float32(data=battery_mv / 1000.0))

    def on_sbus(self, payload):
        *channels, _, _, frame_lost, failsafe = struct.unpack("<16H4B", payload)
        self.sbus.publish(UInt8MultiArray(data=list(payload)))
        self.last_sbus = time.monotonic()
        command = Twist()
        if not (frame_lost or failsafe) and all(value <= 2047 for value in channels):
            gear = channels[4]
            if gear >= 642:
                gear_scale = 1.0 if gear < 1362 else 3.0
                command.linear.x = gear_scale * 0.5 * stick_axis(channels[2])
                command.angular.z = gear_scale * 0.60 * stick_axis(channels[0])
                if command.linear.x and command.angular.z:
                    # Reserve differential speed for steering when driving and turning.
                    linear_budget = max(0.0, 0.45 - abs(command.angular.z) * self.half_track)
                    command.linear.x = math.copysign(
                        min(abs(command.linear.x), linear_budget), command.linear.x
                    )
        self.publish_sbus_velocity(command)

    def publish_sbus_velocity(self, command):
        moving = bool(command.linear.x or command.angular.z)
        if moving or self.sbus_motion:
            self.manual.publish(command)
        self.sbus_motion = moving

    def publish_odometry(self, payload):
        # RRC v1 has a little-endian signed tick counter at byte 24 of M1
        # and byte 44 of M2 (right). Each motor record is 20 bytes.
        left_ticks = struct.unpack_from("<i", payload, 24)[0]
        right_ticks = struct.unpack_from("<i", payload, 44)[0]
        now = time.monotonic()
        previous = self.encoder_sample
        self.encoder_sample = (now, left_ticks, right_ticks)
        if previous is None:
            return
        elapsed = now - previous[0]
        left = signed_tick_delta(left_ticks, previous[1]) * self.left_sign * self.metres_per_tick
        right = signed_tick_delta(right_ticks, previous[2]) * self.right_sign * self.metres_per_tick
        distance = (left + right) / 2
        turn = (right - left) / (2 * self.half_track)
        self.x += distance * math.cos(self.yaw + turn / 2)
        self.y += distance * math.sin(self.yaw + turn / 2)
        self.yaw += turn

        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "odom"
        msg.child_frame_id = "base_link"
        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y
        msg.pose.pose.orientation.z = math.sin(self.yaw / 2)
        msg.pose.pose.orientation.w = math.cos(self.yaw / 2)
        msg.twist.twist.linear.x = distance / elapsed
        msg.twist.twist.angular.z = turn / elapsed
        self.odom.publish(msg)
        self.velocity.publish(msg.twist.twist)

    def close(self):
        try:
            self.send_motor(bytes([3, 15]))
            self.port.flush()
        finally:
            self.port.close()


def main():
    rclpy.init()
    node = None
    try:
        node = HuanerDriver()
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        try:
            if node is not None:
                try:
                    node.close()
                finally:
                    node.destroy_node()
        finally:
            rclpy.try_shutdown()
