"""Map left-stick throttle and right-stick steering to Ackermann commands."""

import math
import os
from pathlib import Path
import struct

import rclpy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
from rclpy.node import Node


DEVICE = Path("/dev/input/by-id/usb-\u00a9Microsoft_Corporation_Controller_1DD5F3D-joystick")
EVENT = struct.Struct("<IhBB")
AXIS_EVENT = 0x02
RIGHT_STICK_X = 3
STEERING_DEGREES = 60.0
FORWARD_SPEED = 0.15
MAX_SPEED = 1.0
SPEED_STEP = 0.05
DPAD_Y = 7
WHEELBASE_M = 0.22492


def steering_input(events, previous, selected_axis=RIGHT_STICK_X):
    value = previous
    for _, raw, kind, axis in EVENT.iter_unpack(events):
        if (kind & 0x7F) == AXIS_EVENT and axis == selected_axis:
            value = raw
    return value


def steering_angle(raw):
    return -STEERING_DEGREES * stick_fraction(raw)


def stick_fraction(raw):
    # The Xbox reports -1 at rest on some axes. Round away that one-count offset.
    return round(max(-1.0, min(1.0, raw / 32767.0)), 4)


def speed_input(events, previous_direction, speed):
    for _, raw, kind, axis in EVENT.iter_unpack(events):
        if (kind & 0x7F) != AXIS_EVENT or axis != DPAD_Y:
            continue
        direction = (raw > 0) - (raw < 0)
        if not kind & 0x80 and direction and direction != previous_direction:
            speed = round(max(0.05, min(MAX_SPEED, speed - direction * SPEED_STEP)), 2)
        previous_direction = direction
    return previous_direction, speed


def motion_command(horizontal, vertical, limit=STEERING_DEGREES, speed_limit=FORWARD_SPEED):
    angle = -limit * stick_fraction(horizontal)
    speed = -min(speed_limit, MAX_SPEED) * stick_fraction(vertical)
    command = Twist()
    command.linear.x = speed
    if speed:
        command.angular.z = speed * math.tan(math.radians(angle)) / WHEELBASE_M
    else:
        command.linear.y = angle
    return command


class XboxSteering(Node):
    def __init__(self):
        super().__init__("xbox_steering_121")
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 1)
        self.speed_limit = FORWARD_SPEED
        self.dpad_direction = 0
        self.steering_limit = STEERING_DEGREES
        self.create_subscription(Float32, "/omnifleet_a2/chassis/steering_limit",
                                 self.update_steering_limit, 10)
        self.fd = None
        self.raw = 0
        self.throttle = 0
        self.last_angle = 0.0
        self.last_speed = 0.0
        self.timer = self.create_timer(0.05, self.poll_controller)

    def update_steering_limit(self, message):
        self.steering_limit = message.data

    def poll_controller(self):
        if self.fd is None:
            try:
                self.fd = os.open(DEVICE, os.O_RDONLY | os.O_NONBLOCK)
            except FileNotFoundError:
                return
            self.get_logger().info(f"Xbox 360 connected: {DEVICE}; speed={self.speed_limit:.2f} m/s; D-pad up/down adjusts speed")

        try:
            events = os.read(self.fd, EVENT.size * 64)
            if not events:
                self.disconnect()
                return
            self.raw = steering_input(events, self.raw)
            self.throttle = steering_input(events, self.throttle, 1)
            previous_speed = self.speed_limit
            self.dpad_direction, self.speed_limit = speed_input(
                events, self.dpad_direction, self.speed_limit)
            if self.speed_limit != previous_speed:
                self.get_logger().info(f"Xbox speed limit: {self.speed_limit:.2f} m/s")
        except BlockingIOError:
            pass
        except OSError:
            self.disconnect()
            return

        command = motion_command(self.raw, self.throttle, self.steering_limit, self.speed_limit)
        if command.linear.x or command.linear.y or self.last_angle or self.last_speed:
            self.publisher.publish(command)
        self.last_angle = command.linear.y
        self.last_speed = command.linear.x

    def disconnect(self):
        os.close(self.fd)
        self.fd = None
        self.raw = 0
        self.throttle = 0
        self.dpad_direction = 0
        if self.last_angle or self.last_speed:
            self.publisher.publish(Twist())
        self.last_angle = 0.0
        self.last_speed = 0.0
        self.get_logger().info("Xbox 360 disconnected")


def main():
    rclpy.init()
    node = XboxSteering()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        if node.fd is not None:
            os.close(node.fd)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()

