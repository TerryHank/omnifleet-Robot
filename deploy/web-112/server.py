import base64
import json
import math
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
import rclpy
from geometry_msgs.msg import Twist, Vector3
from nav_msgs.msg import OccupancyGrid, Odometry
from omnifleet_interfaces.srv import ServoCommand
from rclpy.executors import ExternalShutdownException
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Imu, PointCloud2
from sensor_msgs_py.point_cloud2 import read_points
from std_msgs.msg import Float32, Float64, String
from std_srvs.srv import Trigger

state = {}
jpeg = b''
cloud_at = 0.0
page = Path(__file__).with_name('index.html').read_bytes()


def update(key, value):
    state[key] = {'value': value, 'at': time.monotonic()}


def odometry(msg, key="odom"):
    p, q = msg.pose.pose.position, msg.pose.pose.orientation
    yaw = math.atan2(2 * (q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
    update(key, [p.x, p.y, yaw, msg.twist.twist.linear.x])


def occupancy(msg):
    i = msg.info
    q = i.origin.orientation
    yaw = math.atan2(2 * (q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
    update('map', {
        'width': i.width, 'height': i.height, 'resolution': i.resolution,
        'origin': [i.origin.position.x, i.origin.position.y, yaw],
        'cells': base64.b64encode(bytes(msg.data)).decode(),
    })


def camera(msg):
    global jpeg
    jpeg = bytes(msg.data)


def cloud(msg):
    global cloud_at
    now = time.monotonic()
    if now - cloud_at < 0.4:
        return
    cloud_at = now
    records = read_points(msg, field_names=('x', 'y', 'z'), skip_nans=False)
    xyz = np.column_stack([records[field] for field in ('x', 'y', 'z')])
    xyz = xyz[::max(1, (len(xyz) + 2499)//2500)]
    xyz = xyz[np.isfinite(xyz).all(axis=1)]
    update('points', xyz.round(2).tolist())


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/opt/foxglove-studio-cn-122/site", **kwargs)

    def do_POST(self):
        if self.path == '/api/steering-center':
            self.save_steering_center()
            return
        if self.path == '/api/heading/reset':
            self.reset_heading()
            return
        if self.path != '/api/drive':
            self.send_error(404)
            return
        if self.headers.get_content_type() != 'application/json':
            self.send_error(415)
            return
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size <= 256:
                raise ValueError
            self.connection.settimeout(1.0)
            command = json.loads(self.rfile.read(size))
            linear = float(command['linear'])
            angular = float(command['angular'])
            if not math.isfinite(linear) or not math.isfinite(angular):
                raise ValueError
        except (ValueError, TypeError, KeyError, OSError):
            self.send_error(400)
            return
        twist = Twist()
        twist.linear.x = max(-0.4, min(0.4, linear))
        twist.angular.z = max(-0.3, min(0.3, angular))
        self.server.drive.publish(twist)
        self.send_response(204)
        self.end_headers()
    def reset_heading(self):
        if self.headers.get_content_type() != 'application/json':
            self.send_error(415)
            return
        client = self.server.heading_reset
        if not client.service_is_ready():
            self.send_error(503)
            return
        done = threading.Event()
        future = client.call_async(Trigger.Request())
        future.add_done_callback(lambda _: done.set())
        if not done.wait(2):
            client.remove_pending_request(future)
            self.send_error(504)
            return
        if not future.result().success:
            self.send_error(503)
            return
        self.send_response(204)
        self.end_headers()

    def call_steering_center(self, operation, angle=0):
        client = self.server.steering_center
        if not client.service_is_ready():
            raise ConnectionError("Steering center service unavailable")
        request = ServoCommand.Request()
        request.operation = operation
        request.arg0 = angle
        future = client.call_async(request)
        done = threading.Event()
        future.add_done_callback(lambda _: done.set())
        if not done.wait(0.5):
            client.remove_pending_request(future)
            raise TimeoutError("Steering center service timed out")
        return future.result()

    def steering_center(self, angle=None):
        with self.server.steering_center_lock:
            try:
                start = self.call_steering_center(0 if angle is None else 1, angle or 0)
                if not start.success:
                    self.send_error(502)
                    return
                deadline = time.monotonic() + 1
                while time.monotonic() < deadline:
                    reply = self.call_steering_center(2)
                    if reply.success:
                        if angle is not None and reply.value0 != angle:
                            self.send_error(502)
                            return
                        body = json.dumps({'offset_deg': reply.value0 - 90}).encode()
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Cache-Control', 'no-store')
                        self.send_header('Content-Length', str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)
                        return
                    time.sleep(0.05)
            except ConnectionError:
                self.send_error(503)
                return
            except TimeoutError:
                pass
        self.send_error(504)

    def save_steering_center(self):
        if self.headers.get_content_type() != 'application/json':
            self.send_error(415)
            return
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size <= 256:
                raise ValueError
            self.connection.settimeout(1.0)
            offset = json.loads(self.rfile.read(size))['offset_deg']
            if type(offset) is not int or not -90 <= offset <= 90:
                raise ValueError
        except (ValueError, TypeError, KeyError, OSError):
            self.send_error(400)
            return
        self.steering_center(90 + offset)

    def do_GET(self):
        if self.path == '/api/steering-center':
            self.steering_center()
            return
        if self.path == '/dashboard':
            body, kind = page, 'text/html; charset=utf-8'
        elif self.path == '/api/state':
            now = time.monotonic()
            body = json.dumps({k: {'value': v['value'], 'age': round(now-v['at'], 2)}
                               for k, v in state.copy().items() if k != 'map'}, ensure_ascii=False).encode()
            kind = 'application/json'
        elif self.path == '/api/map' and 'map' in state:
            grid = state['map']
            body = json.dumps({'value': grid['value'], 'age': round(time.monotonic()-grid['at'], 2)}).encode()
            kind = 'application/json'
        elif self.path.split('?', 1)[0] == '/camera.jpg' and jpeg:
            body, kind = jpeg, 'image/jpeg'
        else:
            super().do_GET()
            return
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


def main():
    rclpy.init()
    node = rclpy.create_node('omnifleet_112_web')
    subscriptions = [
        (Float64, '/vr/heading_rad', lambda m: update('heading', m.data)),
        (Vector3, '/vr/attitude_rpy_rad', lambda m: update('attitude', [m.x, m.y, m.z])),
        (Odometry, '/odom', odometry),
        (Odometry, '/lidar_odometry/pose', lambda m: odometry(m, 'localization')),
        (Imu, '/rslidar_imu_data_corrected', lambda m: update('angular', m.angular_velocity.z)),
        (Float32, '/omnifleet_a2/chassis/voltage', lambda m: update('voltage', m.data)),
        (String, '/omnifleet_a2/waypoints/status', lambda m: update('waypoints', m.data)),
        (PointCloud2, '/rslidar_points', cloud),
        (CompressedImage, '/tof/color/image_raw/compressed', camera),
    ]
    for msg, topic, callback in subscriptions:
        node.create_subscription(msg, topic, callback, qos_profile_sensor_data)
    node.create_subscription(OccupancyGrid, '/map', occupancy,
                             QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    with ThreadingHTTPServer(('0.0.0.0', 80), Handler) as server:
        server.heading_reset = node.create_client(Trigger, '/vr/reset_heading')
        server.drive = node.create_publisher(Twist, '/cmd_vel', 1)
        server.steering_center = node.create_client(ServoCommand, '/omnifleet_a2/chassis/steering_center')
        server.steering_center_lock = threading.Lock()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            rclpy.spin(node)
        except ExternalShutdownException:
            pass
        finally:
            server.shutdown()
            node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()


if __name__ == '__main__':
    main()
