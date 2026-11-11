"""Read camera/follow state and start recognition with movement disabled."""

import json
import sys
import time
from collections import Counter

import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, CompressedImage, Image
from std_msgs.msg import String


mode = sys.argv[1]
cases = {"objects": "02_07_kcf", "person": "04_09_body_tracking"}
rclpy.init(args=[])
node = rclpy.create_node("vision122_probe")
counts = Counter()
last = {}


def capture(key, data):
    counts[key] += 1
    last[key] = data


for name, topic in (
    ("manager", "/vision/demo/status"),
    ("mobile", "/vision/mobile/detections"),
    ("object", "/omnifleet_vision/kcf/status"),
    ("person", "/vision/body_tracking/status"),
):
    node.create_subscription(String, topic, lambda m, key=name: capture(key, json.loads(m.data)), 1)

node.create_subscription(Image, "/camera/depth/image_raw",
                         lambda m: capture("depth", [m.width, m.height, m.encoding, m.header.frame_id]),
                         qos_profile_sensor_data)
node.create_subscription(CameraInfo, "/camera/color/camera_info",
                         lambda m: capture("intrinsics", [m.width, m.height, m.k[0], m.k[4]]),
                         qos_profile_sensor_data)
node.create_subscription(CompressedImage, "/camera/color/vision_follow/compressed",
                         lambda m: capture("jpeg", [m.format, len(m.data)]), qos_profile_sensor_data)

control = node.create_publisher(String, "/vision/demo/control", 1)
mobile = node.create_publisher(String, "/vision/mobile/control", 1)
request = {"op": "start", "id": f"probe-{mode}", "case_id": cases[mode], "parameters": {"enable_motion": "false"}}
deadline = time.monotonic() + 5
while control.get_subscription_count() == 0 and time.monotonic() < deadline:
    rclpy.spin_once(node, timeout_sec=0.2)
control.publish(String(data=json.dumps(request)))

if mode == "objects":
    mobile.publish(String(data='{"op":"mode","mode":"color","labels":["red","green","blue","yellow"]}'))

expected = "object" if mode == "objects" else "person"
deadline = time.monotonic() + 23
while time.monotonic() < deadline:
    rclpy.spin_once(node, timeout_sec=0.2)
    state = last.get("manager", {})
    if state.get("request_id") == request["id"] and state.get("phase") == "ERROR":
        break
    if counts[expected] >= 3 and counts["jpeg"] and counts["depth"] and counts["intrinsics"]:
        break

for key in ("object", "person", "mobile"):
    data = last.get(key)
    if data:
        last[key] = {k: data[k] for k in
                     ("enable_motion", "motion_enabled", "state", "mode", "depth_m", "person_range_m",
                      "image_width", "image_height", "track_id", "rgb_resolution", "body_tracking")
                     if k in data}
print(json.dumps({"counts": counts, "last": last}, ensure_ascii=False))
node.destroy_node()
rclpy.shutdown()
sys.exit(0 if counts[expected] >= 3 and counts["jpeg"] and counts["depth"] and counts["intrinsics"] else 1)
