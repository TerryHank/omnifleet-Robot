#!/usr/bin/env python3
import sys, select, termios, tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

BINDINGS = {
    "\x1b[A":  ( 0.15,  0.0,  0.0),
    "\x1b[B":  (-0.15,  0.0,  0.0),
    "\x1b[D":  ( 0.0,   0.15, 0.0),
    "\x1b[C":  ( 0.0,  -0.15, 0.0),
}

class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__("keyboard_teleop")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.vx = 0.0; self.vy = 0.0; self.vz = 0.0
        self.settings = termios.tcgetattr(sys.stdin)
        print("\n  ↑前进  ↓后退  ←左移  →右移  空格急停  q退出")
        self.timer = self.create_timer(0.05, self.publish_cmd)

    def publish_cmd(self):
        t = Twist()
        t.linear.x = self.vx; t.linear.y = self.vy; t.angular.z = self.vz
        self.pub.publish(t)

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        r, _, _ = select.select([sys.stdin], [], [], 0.05)
        key = ""
        if r:
            key = sys.stdin.read(1)
            if key == "\x1b":
                more = sys.stdin.read(2)
                key += more if len(more) == 2 else ""
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

def main():
    rclpy.init()
    node = KeyboardTeleop()

    # Use rclpy.spin_once in a loop + keyboard handling
    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.01)
        key = node.get_key()
        if key in BINDINGS:
            node.vx, node.vy, node.vz = BINDINGS[key]
            print(f"\r  vx={node.vx:+.2f}  vy={node.vy:+.2f}  ", end="", flush=True)
        elif key == " ":
            node.vx = node.vy = node.vz = 0.0
            print("\r  急停!                    ", flush=True)
        elif key == "q" or key == "\x03":
            node.vx = node.vy = node.vz = 0.0
            break
        else:
            node.vx = node.vy = node.vz = 0.0

    node.publish_cmd()
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)
    print("\n退出")
    rclpy.shutdown()

if __name__ == "__main__":
    main()
