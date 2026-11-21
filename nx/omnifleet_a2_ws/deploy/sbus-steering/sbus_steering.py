"""Use the 121 receiver forwarded by the STM32 serial driver."""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float32, UInt16MultiArray

from xbox_steering import STEERING_DEGREES, motion_command


SBUS_MIN = 192
SBUS_MAX = 1792
CH1_CENTER = 992
CH3_CENTER = 972
MIN_SPEED = 0.05
MAX_SPEED = 1.0
SPEED_STEP = 0.05
SBUS_INPUT_TOPIC = '/stm32/sbus'
SBUS_DRIVE_TOPIC = '/stm32/sbus/cmd_vel'


def stick_axis(value, center):
    delta = value - center
    # Ignore the receiver's measured variation around the trimmed center.
    if abs(delta) <= 24:
        return 0
    span = SBUS_MAX - center if delta > 0 else center - SBUS_MIN
    return round(32767 * max(-1.0, min(1.0, delta / span)))


def speed_limit(value):
    fraction = max(0.0, min(1.0, (value - SBUS_MIN) / (SBUS_MAX - SBUS_MIN)))
    steps = round(fraction * (MAX_SPEED - MIN_SPEED) / SPEED_STEP)
    return round(MIN_SPEED + steps * SPEED_STEP, 2)


class SbusSteering(Node):
    def __init__(self):
        super().__init__('sbus_steering_121')
        self.publisher = self.create_publisher(Twist, SBUS_DRIVE_TOPIC, 1)
        self.create_subscription(UInt16MultiArray, SBUS_INPUT_TOPIC, self.on_sbus, 10)
        self.create_subscription(Float32, '/omnifleet_a2/chassis/steering_limit',
                                 self.on_steering_limit, 10)
        self.steering_limit = STEERING_DEGREES
        self.requested_speed = None
        self.was_active = False

    def on_steering_limit(self, message):
        self.steering_limit = message.data

    def on_sbus(self, message):
        channels = message.data
        if len(channels) != 20:
            return
        if channels[18] or channels[19] or tuple(channels[:4]) == (992, 992, 32, 992):
            if self.was_active:
                self.publisher.publish(Twist())
                self.was_active = False
            return

        limit = speed_limit(channels[8])
        if limit != self.requested_speed:
            self.get_logger().info(f'CH9 speed limit: {limit:.2f} m/s (raw {channels[8]})')
            self.requested_speed = limit
        command = motion_command(stick_axis(channels[0], CH1_CENTER),
                                 -stick_axis(channels[2], CH3_CENTER),
                                 self.steering_limit, limit)
        active = bool(command.linear.x or command.linear.y)
        if active or self.was_active:
            self.publisher.publish(command)
        self.was_active = active


def main():
    rclpy.init()
    node = SbusSteering()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
