#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String


class VoltageDisplayNode(Node):
    def __init__(self) -> None:
        super().__init__("rrc_voltage_display")
        self._publisher = self.create_publisher(String, "/voltage/display", 10)
        self._subscription = self.create_subscription(
            Float32, "/voltage", self._on_voltage, 10
        )

    def _on_voltage(self, message: Float32) -> None:
        display = String()
        display.data = f"{float(message.data):.1f} V"
        self._publisher.publish(display)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VoltageDisplayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
