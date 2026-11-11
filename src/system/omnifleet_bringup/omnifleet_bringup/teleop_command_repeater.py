import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class TeleopCommandRepeater(Node):
    """Bridge low-rate UI commands to the chassis without weakening its watchdog."""

    def __init__(self):
        super().__init__("teleop_command_repeater")
        input_topic = self.declare_parameter("input_topic", "/cmd_vel_teleop").value
        output_topic = self.declare_parameter(
            "output_topic", "/cmd_vel_teleop_repeated"
        ).value
        publish_rate = float(self.declare_parameter("publish_rate", 20.0).value)
        self.input_timeout = float(self.declare_parameter("input_timeout", 0.60).value)
        if publish_rate <= 0.0 or self.input_timeout <= 0.0:
            raise ValueError("publish_rate and input_timeout must be positive")
        self.publisher = self.create_publisher(Twist, output_topic, 10)
        self.subscription = self.create_subscription(Twist, input_topic, self.on_command, 10)
        self.latest = Twist()
        self.last_received = None
        self.timeout_stop_sent = True
        self.create_timer(1.0 / publish_rate, self.on_timer)

    def on_command(self, message):
        self.latest = message
        self.last_received = time.monotonic()
        self.timeout_stop_sent = False

    def on_timer(self):
        if self.last_received is None:
            return
        if time.monotonic() - self.last_received <= self.input_timeout:
            self.publisher.publish(self.latest)
            return
        if not self.timeout_stop_sent:
            self.publisher.publish(Twist())
            self.timeout_stop_sent = True


def main():
    rclpy.init()
    node = TeleopCommandRepeater()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
