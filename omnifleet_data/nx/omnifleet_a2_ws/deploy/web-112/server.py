import json
import math
import socket
from collections import OrderedDict
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import rclpy
from geometry_msgs.msg import Twist
from omnifleet_interfaces.srv import ServoCommand
from rclpy.executors import ExternalShutdownException
from std_srvs.srv import Trigger
from navigation_parameters import NavigationParameters
from navigation_display import NavigationDisplay

class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def setup(self):
        super().setup()
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/opt/foxglove-studio-cn-122/site", **kwargs)

    def do_POST(self):
        if self.path == '/api/nav2/parameters':
            try:
                size = int(self.headers.get('Content-Length', 0))
                if not 0 < size <= 1024 or self.headers.get_content_type() != 'application/json':
                    raise ValueError("无效参数请求")
                request = json.loads(self.rfile.read(size))
                result = self.server.navigation_parameters.set(request['id'], request['value'])
                self.send_json(result)
            except (ValueError, KeyError, TypeError) as error:
                self.send_json({"error": str(error)}, status=400)
            except OSError as error:
                self.send_json({"error": str(error)}, status=503)
            return
        if self.path == '/api/steering-limit':
            self.steering_limit(save=True)
            return
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
            # angular_z follows ROS. The older Foxglove panel sent right-positive angular.
            angular = float(command['angular_z']) if 'angular_z' in command else -float(command['angular'])
            if not math.isfinite(linear) or not math.isfinite(angular):
                raise ValueError
            source = command.get("stream")
            sequence = command.get("sequence")
            if source is not None and (not isinstance(source, str) or len(source) > 64
                                       or type(sequence) is not int or sequence < 0):
                raise ValueError
        except (ValueError, TypeError, KeyError, OSError):
            self.send_error(400)
            return
        twist = Twist()
        twist.linear.x = max(-1.0, min(1.0, linear))
        twist.angular.z = max(-3.1, min(3.1, angular))
        if source is None:
            self.server.drive.publish(twist)
        else:
            with self.server.drive_lock:
                order = self.server.drive_order
                if sequence > order.get(source, -1):
                    order[source] = sequence
                    order.move_to_end(source)
                    while len(order) > 64:
                        order.popitem(last=False)
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
                if angle is not None:
                    # STM32 has one RX command buffer: let the save/flash finish
                    # before sending the read request. Do not block the driver timer.
                    time.sleep(0.1)
                    if not self.call_steering_center(0).success:
                        self.send_error(502)
                        return
                deadline = time.monotonic() + 1
                next_read = time.monotonic() + 0.15
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
                    if time.monotonic() >= next_read:
                        self.call_steering_center(0)
                        next_read = time.monotonic() + 0.15
                    time.sleep(0.05)
            except ConnectionError:
                self.send_error(503)
                return
            except TimeoutError:
                pass
        self.send_error(504)

    def steering_limit(self, save=False):
        value = 0
        if save:
            try:
                if self.headers.get_content_type() != 'application/json':
                    self.send_error(415)
                    return
                size = int(self.headers.get('Content-Length', 0))
                if not 0 < size <= 256:
                    raise ValueError
                self.connection.settimeout(1.0)
                value = json.loads(self.rfile.read(size))['max_angle_deg']
                if type(value) is not int or not 0 <= value <= 60:
                    raise ValueError
            except (ValueError, TypeError, KeyError, OSError):
                self.send_error(400)
                return
        try:
            reply = self.call_steering_center(4 if save else 3, value)
            if not reply.success:
                self.send_error(502)
                return
            body = json.dumps({'max_angle_deg': reply.value0}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionError, TimeoutError):
            self.send_error(503)

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

    def send_json(self, value, status=200):
        content = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path == '/api/nav2/parameters':
            try:
                self.send_json(self.server.navigation_parameters.read())
            except (OSError, ValueError, StopIteration) as error:
                self.send_json({"error": str(error)}, status=503)
            return
        if self.path == '/api/steering-limit':
            self.steering_limit()
            return
        if self.path == '/api/steering-center':
            self.steering_center()
            return
        if self.path.split('?', 1)[0] == '/dashboard':
            self.send_response(302)
            self.send_header('Location', '/')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, *_):
        pass


def main():
    rclpy.init()
    node = rclpy.create_node('omnifleet_112_web')
    with ThreadingHTTPServer(('127.0.0.1', 8781), Handler) as server:
        server.heading_reset = node.create_client(Trigger, '/vr/reset_heading')
        server.drive = node.create_publisher(Twist, '/cmd_vel', 1)
        server.drive_lock = threading.Lock()
        server.drive_order = OrderedDict()
        server.navigation_parameters = NavigationParameters(node)
        server.navigation_display = NavigationDisplay(node)
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
