#!/usr/bin/env python3
"""
旋转标定: 原地旋转 90° (左转)
"""
import math, time, rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

SPEED = 0.4                # rad/s
ANGLE = math.radians(90)   # 90° → rad
DURATION = ANGLE / SPEED   # ~3.93s

class RotateTest(Node):
    def __init__(self):
        super().__init__("rotate_test")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.get_logger().info(
            f"角速度={SPEED}rad/s, 运行{DURATION:.2f}s, 预期{math.degrees(ANGLE):.0f}°"
        )
        self.start = time.monotonic()
        self.create_timer(0.05, self.control)

    def control(self):
        elapsed = time.monotonic() - self.start
        msg = Twist()
        if elapsed < DURATION:
            msg.angular.z = SPEED   # 正=左转
        else:
            msg.angular.z = 0.0
            self.get_logger().info(f"停止! 实际转了多少度?")
            rclpy.shutdown()
            return
        self.pub.publish(msg)

def main():
    rclpy.init(); node = RotateTest()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    node.destroy_node(); rclpy.shutdown()

if __name__ == "__main__":
    main()
