#!/usr/bin/env python3
"""WSAD 键盘遥控: w前进 s后退 a左转 d右转 空格停止 q退出"""
import sys, termios, tty, rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class WSAD(Node):
    def __init__(self):
        super().__init__("wsad_control")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.speed = 0.15
        self.turn = 0.4
        self.get_logger().info("w/s/a/d 控制, 空格停, q退出")
        self.create_timer(0.1, self.read_key)

    def read_key(self):
        try:
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            tty.setraw(fd)
            c = sys.stdin.read(1)
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except:
            return

        msg = Twist()
        if c == 'w':
            msg.linear.x = self.speed
        elif c == 's':
            msg.linear.x = -self.speed
        elif c == 'a':
            msg.angular.z = self.turn
        elif c == 'd':
            msg.angular.z = -self.turn
        elif c == ' ':
            msg.linear.x = 0.0
        elif c == 'q':
            raise SystemExit
        self.pub.publish(msg)


def main():
    rclpy.init(); node = WSAD()
    try: rclpy.spin(node)
    except: pass
    node.destroy_node(); rclpy.shutdown()


if __name__ == "__main__":
    main()
