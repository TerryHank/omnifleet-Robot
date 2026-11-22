#!/usr/bin/env python3
"""
慢速直走测试: 用更低速度减少电池/摩擦波动
"""
import math, time, rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

SPEED = 0.10               # 慢速 m/s
DISTANCE = 1.0
DURATION = DISTANCE / SPEED

class SlowMove(Node):
    def __init__(self):
        super().__init__("slow_move")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.get_logger().info(f"速度={SPEED}m/s, 运行{DURATION:.1f}s, 预期{DISTANCE}m")
        self.start = time.monotonic()
        self.create_timer(0.05, self.control)
    def control(self):
        elapsed = time.monotonic() - self.start
        msg = Twist()
        if elapsed < DURATION:
            msg.linear.x = SPEED
        else:
            msg.linear.x = 0.0
            self.get_logger().info(f"停止! 实测走了多少cm?")
            rclpy.shutdown()
            return
        self.pub.publish(msg)

def main():
    rclpy.init(); node = SlowMove()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    node.destroy_node(); rclpy.shutdown()

if __name__ == "__main__":
    main()
