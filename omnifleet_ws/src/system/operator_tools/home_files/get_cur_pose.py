import rclpy
from rclpy.node import Node
import tf2_ros
from rclpy.time import Time
import math
import time

rclpy.init()
node = Node("current_pose_listener")
tf_buffer = tf2_ros.Buffer()
tf_listener = tf2_ros.TransformListener(tf_buffer, node)

start = time.time()
found = False
for i in range(25):
    rclpy.spin_once(node, timeout_sec=0.2)
    try:
        t = tf_buffer.lookup_transform("map", "base_link", Time())
        tr = t.transform.translation
        rot = t.transform.rotation
        siny_cosp = 2 * (rot.w * rot.z + rot.x * rot.y)
        cosy_cosp = 1 - 2 * (rot.y * rot.y + rot.z * rot.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        print(f"CURRENT_POSE: x={tr.x:.4f}, y={tr.y:.4f}, z={tr.z:.4f}, yaw={math.degrees(yaw):.2f} deg, yaw_rad={yaw:.4f}")
        found = True
        break
    except Exception as e:
        pass

node.destroy_node()
rclpy.shutdown()
if not found:
    print("FAILED to lookup map -> base_link")
