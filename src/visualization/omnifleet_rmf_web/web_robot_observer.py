import base64
import hashlib
import io
from PIL import Image
import json
import math
import os
from pathlib import Path
import socket
import time

config_path = Path('/home/zhangwnag/workspaces/omnifleet_ws/src/system/omnifleet_rmf_adapter/config/framework.json')
config = json.loads(config_path.read_text())
robot_id = 'robot_104'
registry = config_path.parents[4] / 'data/discovery.json'
def discovered_profile():
    if not registry.exists():return None
    state=json.loads(registry.read_text())
    if not 0<=time.monotonic()-state.get('updated_monotonic',0)<6:return None
    return state.get('robots',{}).get(robot_id)

while discovered_profile() is None:
    time.sleep(1)
discovered = discovered_profile()
profile = {**config['robots'][robot_id], **discovered}
if not profile['enabled'] or profile['domain_id'] is None:
    raise RuntimeError('robot_104 observation is disabled in framework.json')
os.environ.update(ROS_DOMAIN_ID=str(profile['domain_id']), RMW_IMPLEMENTATION=profile['rmw'], ROS_LOCALHOST_ONLY='0', ZENOH_SESSION_CONFIG_URI=str(config_path.parent / profile['zenoh_config']))

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy
from rclpy.signals import SignalHandlerOptions
from nav_msgs.msg import Odometry, OccupancyGrid
from std_msgs.msg import Float32, String


class WebRobotObserver(Node):
    def __init__(self):
        super().__init__('omnifleet_web_read_only_robot104')
        self.map = None
        self.map_count = 0
        self.samples = {}
        self.counts = {}
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.socket.setblocking(False)
        self.target = '/home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web/run/robot104.sock'
        prefix = profile['observed_namespace']
        self.create_subscription(String, prefix + '/navigation/status', lambda m: self.status('navigation', m), qos_profile_sensor_data)
        self.create_subscription(String, prefix + '/navigation/local_status', lambda m: self.status('control', m), qos_profile_sensor_data)
        self.create_subscription(Odometry, prefix + '/lidar_odometry/pose', self.pose, qos_profile_sensor_data)
        self.create_subscription(Float32, prefix + '/voltage', lambda m: self.record('voltage', m.data) if math.isfinite(m.data) else None, qos_profile_sensor_data)
        self.create_subscription(OccupancyGrid, prefix + '/map', self.receive_map, QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.create_timer(1.0, self.emit)

    def record(self, kind, value):
        self.samples[kind] = (time.monotonic(), value)
        self.counts[kind] = self.counts.get(kind, 0) + 1

    def status(self, kind, message):
        try:
            value = json.loads(message.data)
            if isinstance(value, dict):
                self.record(kind, value)
        except ValueError:
            pass

    def pose(self, message):
        p = message.pose.pose
        q = p.orientation
        if not all(math.isfinite(v) for v in (p.position.x, p.position.y, q.x, q.y, q.z, q.w)):
            return
        self.record('pose', {'x': p.position.x, 'y': p.position.y, 'yaw': math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)), 'frame_id': message.header.frame_id, 'stamp_seconds': message.header.stamp.sec + message.header.stamp.nanosec * 1e-9})

    def receive_map(self, message):
        info = message.info
        if info.width == 0 or info.height == 0 or len(message.data) != info.width * info.height:
            return
        pixels = bytes(205 if value < 0 else round(255 * (1 - min(value, 100) / 100)) for value in message.data)
        image = Image.frombytes('L', (info.width, info.height), pixels).transpose(Image.FLIP_TOP_BOTTOM)
        known = Image.frombytes('L', (info.width, info.height), bytes(255 if value >= 0 else 0 for value in message.data)).transpose(Image.FLIP_TOP_BOTTOM)
        bounds = known.getbbox()
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        png = buffer.getvalue()
        q = info.origin.orientation
        self.map_count += 1
        self.map = {'bounds': bounds, 'frame_id': message.header.frame_id, 'width': info.width, 'height': info.height,
                    'resolution': info.resolution, 'origin': {'x': info.origin.position.x, 'y': info.origin.position.y,
                    'yaw': math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))},
                    'stamp_seconds': message.header.stamp.sec + message.header.stamp.nanosec*1e-9,
                    'sample_monotonic': time.monotonic(), 'message_count': self.map_count,
                    'hash': hashlib.sha256(png).hexdigest(), 'image_base64': base64.b64encode(png).decode()}

    def emit(self):
        if discovered_profile() != discovered:
            raise RuntimeError('Vehicle broadcast expired or endpoint changed; rediscovering')
        now = time.monotonic()
        assignment = config['central']['assignments']['robot_104']
        payload = {'map': self.map, 'schema': 1, 'robot_id': 'robot_104', 'domain_id': profile['domain_id'], 'assigned_robot_name': assignment['robot_name'], 'assigned_namespace': assignment['namespace'], 'sample_monotonic': now, 'ipc_age_seconds': 0.0, 'read_only': True, 'dispatch_enabled': False, 'rmf_registered': False, 'battery_soc': None, 'message_counts': self.counts, 'samples': {k: {'age_seconds': now - stamp, 'value': value} for k, (stamp, value) in self.samples.items()}}
        try:
            packet = json.dumps(payload, allow_nan=False).encode()
            if len(packet) > 180000:
                payload['map'] = {'error': '地图图像超过本机状态通道大小限制'}
                packet = json.dumps(payload, allow_nan=False).encode()
            self.socket.sendto(packet, self.target)
        except (FileNotFoundError, ConnectionRefusedError, BlockingIOError):
            pass


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = WebRobotObserver()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.socket.close()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
