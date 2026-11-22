#!/usr/bin/env python3
"""Manually save /map to PGM+YAML with correct QoS"""
import rclpy, time, yaml, numpy as np
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy
from nav_msgs.msg import OccupancyGrid
from PIL import Image

rclpy.init()
node = Node("map_saver_manual")

qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                 reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST)

msg = None
def cb(m):
    global msg; msg = m

node.create_subscription(OccupancyGrid, "/map", cb, qos)

start = time.time()
while msg is None and time.time() - start < 30:
    rclpy.spin_once(node, timeout_sec=1.0)

if msg is None:
    print("ERROR: No /map data in 30s")
else:
    path = "/home/iecme/omnifleet_data/maps/robot_maps/nav2/active/map"
    w, h = msg.info.width, msg.info.height
    data = np.array(msg.data, dtype=np.int8).reshape(h, w)
    # Convert: -1(unknown)→205, 100(occupied)→0, 0(free)→254
    img = np.full((h, w), 205, dtype=np.uint8)
    img[data == 100] = 0
    img[data == 0] = 254
    Image.fromarray(img).save(path + ".pgm")
    origin = msg.info.origin.position
    info = {"image": path + ".pgm", "resolution": msg.info.resolution,
            "origin": [origin.x, origin.y, 0.0],
            "negate": 0, "occupied_thresh": 0.65, "free_thresh": 0.196}
    with open(path + ".yaml", "w") as f:
        yaml.dump(info, f)
    print(f"Saved: {path}.pgm ({w}x{h}) + {path}.yaml")

node.destroy_node()
rclpy.shutdown()
