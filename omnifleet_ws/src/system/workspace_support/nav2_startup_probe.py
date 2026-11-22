"""Verify a usable ROS/Zenoh context before starting the Nav2 children."""
import time
import rclpy
from rclpy.node import Node

started=time.monotonic()
rclpy.init()
node=None
try:
    node=Node('nav2_startup_transport_probe')
    print(f'Nav2 startup transport ready in {time.monotonic()-started:.3f}s',flush=True)
finally:
    if node is not None:node.destroy_node()
    if rclpy.ok():rclpy.shutdown()
