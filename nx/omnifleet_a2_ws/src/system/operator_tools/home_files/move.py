import sys, time, rclpy
from geometry_msgs.msg import Twist

direction = sys.argv[1]
dist = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
speed = 0.15
duration = dist / speed

rclpy.init()
node = rclpy.create_node("_mover")
pub = node.create_publisher(Twist, "/cmd_vel", 10)

# 等 DDS 发现订阅者
time.sleep(0.3)
rclpy.spin_once(node, timeout_sec=0.1)

m = Twist()
if direction == "w":   m.linear.x = speed
elif direction == "s": m.linear.x = -speed
elif direction == "a": m.linear.y = speed
elif direction == "d": m.linear.y = -speed

pub.publish(m)
rclpy.spin_once(node, timeout_sec=0.1)
time.sleep(duration)

m.linear.x = 0.0; m.linear.y = 0.0
pub.publish(m)
rclpy.spin_once(node, timeout_sec=0.1)

node.destroy_node()
rclpy.shutdown()
