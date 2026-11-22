#!/usr/bin/env python3
"""
简单直走测试: 用 /cmd_vel 让车走 1 米后停止
用法: python3 move_1m.py
原理: 开环控制, 速度=v, 时间=t, 距离=v*t
      先估算: v=0.15m/s, 轮径4cm, 轮周长=0.1257m
      rps = v / 周长 = 0.15 / 0.1257 ≈ 1.19 rps
      时间 = 1m / 0.15m/s = 6.67s
"""
import math
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

WHEEL_DIAMETER = 0.04      # 4cm
WHEEL_CIRC = math.pi * WHEEL_DIAMETER  # 0.1257m
SPEED = 0.15               # m/s
DISTANCE = 1.0             # m
DURATION = DISTANCE / SPEED  # 6.67s
RPS = SPEED / WHEEL_CIRC   # 1.19 rps

class MoveTest(Node):
    def __init__(self):
        super().__init__("move_test")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.get_logger().info(
            f"轮径={WHEEL_DIAMETER*100:.0f}cm 周长={WHEEL_CIRC:.4f}m "
            f"速度={SPEED}m/s rps={RPS:.2f} 时间={DURATION:.2f}s 距离={DISTANCE}m"
        )
        self.start_time = time.monotonic()
        self.create_timer(0.05, self.control)

    def control(self):
        elapsed = time.monotonic() - self.start_time
        msg = Twist()
        if elapsed < DURATION:
            msg.linear.x = SPEED
        else:
            msg.linear.x = 0.0
            self.get_logger().info(f"停止! 运行 {elapsed:.2f}s, 预期行驶 {DISTANCE}m")
            self.get_logger().info("请测量实际距离, 告诉我要修正")
            rclpy.shutdown()
            return
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = MoveTest()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
