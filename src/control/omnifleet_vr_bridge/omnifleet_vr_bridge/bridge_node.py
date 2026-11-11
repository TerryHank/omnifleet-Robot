import math
import socket
import struct
import threading
import time

import cv2
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Empty, Float32


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def quaternion_to_euler_degrees(quaternion):
    x = quaternion.x
    y = quaternion.y
    z = quaternion.z
    w = quaternion.w
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    sinp = 2.0 * (w * y - z * x)
    pitch = math.copysign(math.pi / 2.0, sinp) if abs(sinp) >= 1.0 else math.asin(sinp)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return tuple(math.degrees(value) for value in (roll, pitch, yaw))


class VrBridge(Node):
    def __init__(self):
        super().__init__("omnifleet_t2_vr_bridge")
        defaults = {
            "car_id": "CAR-IECME113",
            "display_name": "OmniFleet-Tracked-Airy",
            "ctrl_port": 8888,
            "discovery_target": "255.255.255.255",
            "discovery_port": 9100,
            "discovery_period_sec": 1.0,
            "pose_port": 9000,
            "pose_period_sec": 0.04,
            "video_port": 8090,
            "video_retry_sec": 1.0,
            "jpeg_quality": 70,
            "control_timeout_sec": 0.20,
            "maximum_speed_mps": 0.30,
            "maximum_angular_rps": 0.80,
            "minimum_motion_speed_mps": 0.0,
            "cmd_vel_topic": "/cmd_vel",
            "odometry_topic": "/wheel/odometry",
            "image_topic": "/camera/color/image_raw",
        }
        for name, default in defaults.items():
            self.declare_parameter(name, default)
        for name in defaults:
            setattr(self, name, self.get_parameter(name).value)

        self.ctrl_port = int(self.ctrl_port)
        self.discovery_port = int(self.discovery_port)
        self.pose_port = int(self.pose_port)
        self.video_port = int(self.video_port)
        self.jpeg_quality = int(clamp(int(self.jpeg_quality), 1, 100))
        self.state_lock = threading.Lock()
        self.image_condition = threading.Condition()
        self.stop_event = threading.Event()
        self.matched = False
        self.paired_vr_id = ""
        self.bound_vr_ip = ""
        self.speed_input = 0.0
        self.steering_deg = 0.0
        self.last_control_time = 0.0
        self.zero_sent = True
        self.latest_odometry = None
        self.latest_jpeg = None
        self.image_sequence = 0
        self.video_socket = None

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind(("0.0.0.0", self.ctrl_port))
        self.udp_socket.settimeout(0.5)

        self.cmd_publisher = self.create_publisher(Twist, str(self.cmd_vel_topic), 10)
        self.head_pitch_publisher = self.create_publisher(Float32, "/omnifleet_t2/vr/head_pitch_deg", 10)
        self.head_yaw_publisher = self.create_publisher(Float32, "/omnifleet_t2/vr/head_yaw_deg", 10)
        self.fire_publisher = self.create_publisher(Empty, "/omnifleet_t2/vr/fire", 10)
        self.reset_publisher = self.create_publisher(Empty, "/omnifleet_t2/vr/reset", 10)
        self.create_subscription(Odometry, str(self.odometry_topic), self.odometry_callback, 10)
        self.create_subscription(Image, str(self.image_topic), self.image_callback, 2)
        self.cv_bridge = CvBridge()

        self.create_timer(float(self.discovery_period_sec), self.send_discovery)
        self.create_timer(0.05, self.control_watchdog)
        self.create_timer(float(self.pose_period_sec), self.send_pose)
        self.receiver_thread = threading.Thread(target=self.receive_loop, name="vr-udp-receiver", daemon=True)
        self.video_thread = threading.Thread(target=self.video_loop, name="vr-jpeg-sender", daemon=True)
        self.receiver_thread.start()
        self.video_thread.start()
        self.get_logger().info(
            "VR bridge ready: UDP control=%d, DISC=%s:%d, POSE=: %d, JPEG=: %d"
            % (
                self.ctrl_port,
                self.discovery_target,
                self.discovery_port,
                self.pose_port,
                self.video_port,
            )
        )

    def receive_loop(self):
        while not self.stop_event.is_set():
            try:
                payload, source = self.udp_socket.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                text = payload.decode("utf-8").strip()
                command, value = text.split("|", 1)
                self.handle_packet(command.strip().upper(), value.strip(), source)
            except (UnicodeDecodeError, ValueError) as error:
                self.get_logger().warning("Ignored malformed UDP packet from %s: %s" % (source[0], error))

    def handle_packet(self, command, value, source):
        source_ip, source_port = source
        if command == "PAIR":
            with self.state_lock:
                accepted = not self.matched or self.paired_vr_id == value
                if accepted:
                    self.matched = True
                    self.paired_vr_id = value
                    self.bound_vr_ip = source_ip
                    paired_id = value
                else:
                    paired_id = self.paired_vr_id
                reply = "PAIR_ACK|%s,%d,%s" % (self.car_id, 1 if accepted else 0, paired_id)
            self.udp_socket.sendto(reply.encode("utf-8"), (source_ip, source_port))
            if accepted:
                self.get_logger().info("VR paired: id=%s ip=%s" % (value, source_ip))
            else:
                self.get_logger().warning("Rejected VR pair request from %s; occupied by %s" % (source_ip, paired_id))
            return

        with self.state_lock:
            is_current_vr = self.matched and source_ip == self.bound_vr_ip
            paired_vr_id = self.paired_vr_id
        if command == "UNPAIR":
            if is_current_vr and value == paired_vr_id:
                self.clear_pairing()
                self.publish_zero()
                self.get_logger().info("VR unpaired: id=%s ip=%s" % (value, source_ip))
            return
        if not is_current_vr:
            return

        if command == "HEADP":
            message = Float32()
            message.data = clamp(float(value), -180.0, 180.0)
            self.head_pitch_publisher.publish(message)
        elif command == "HEADY":
            message = Float32()
            message.data = clamp(float(value), -180.0, 180.0)
            self.head_yaw_publisher.publish(message)
        elif command == "SPEED":
            with self.state_lock:
                self.speed_input = clamp(float(value), -1.0, 1.0)
                self.last_control_time = time.monotonic()
                self.zero_sent = False
            self.publish_control()
        elif command == "ANGLE":
            with self.state_lock:
                self.steering_deg = clamp(float(value), -40.0, 40.0)
                self.last_control_time = time.monotonic()
                self.zero_sent = False
            self.publish_control()
        elif command == "FIRE":
            self.fire_publisher.publish(Empty())
        elif command == "RESET":
            with self.state_lock:
                self.speed_input = 0.0
                self.steering_deg = 0.0
                self.last_control_time = 0.0
            self.publish_zero()
            self.reset_publisher.publish(Empty())

    def clear_pairing(self):
        with self.state_lock:
            self.matched = False
            self.paired_vr_id = ""
            self.bound_vr_ip = ""
            self.speed_input = 0.0
            self.steering_deg = 0.0
            self.last_control_time = 0.0
        self.close_video_socket()

    def send_discovery(self):
        with self.state_lock:
            matched = 1 if self.matched else 0
            paired_vr_id = self.paired_vr_id
        text = "DISC|%s,%d,%d,%s,%s" % (
            self.car_id,
            self.ctrl_port,
            matched,
            paired_vr_id,
            self.display_name,
        )
        try:
            self.udp_socket.sendto(
                text.encode("utf-8"),
                (str(self.discovery_target), self.discovery_port),
            )
        except OSError as error:
            self.get_logger().warning("DISC broadcast failed: %s" % error)

    def effective_speed(self, speed_input):
        if abs(speed_input) <= 1.0e-6:
            return 0.0
        requested = abs(speed_input) * float(self.maximum_speed_mps)
        effective = max(requested, float(self.minimum_motion_speed_mps))
        return math.copysign(min(effective, float(self.maximum_speed_mps)), speed_input)

    def publish_control(self):
        with self.state_lock:
            speed = self.effective_speed(self.speed_input)
            steering_deg = self.steering_deg
        command = Twist()
        command.linear.x = speed
        # The VR protocol still calls this field ANGLE, but a tracked base maps
        # it directly to yaw rate and may rotate in place at zero linear speed.
        command.angular.z = (
            clamp(steering_deg / 40.0, -1.0, 1.0)
            * float(self.maximum_angular_rps)
        )
        self.cmd_publisher.publish(command)

    def publish_zero(self):
        self.cmd_publisher.publish(Twist())
        with self.state_lock:
            self.zero_sent = True

    def control_watchdog(self):
        with self.state_lock:
            matched = self.matched
            last_control_time = self.last_control_time
            zero_sent = self.zero_sent
        if not matched:
            return
        if last_control_time and time.monotonic() - last_control_time <= float(self.control_timeout_sec):
            self.publish_control()
        elif not zero_sent:
            self.publish_zero()
            self.get_logger().warning("VR control timeout; published zero motion")

    def odometry_callback(self, message):
        with self.state_lock:
            self.latest_odometry = message

    def send_pose(self):
        with self.state_lock:
            if not self.matched or self.latest_odometry is None:
                return
            vr_ip = self.bound_vr_ip
            odometry = self.latest_odometry
        roll, pitch, heading = quaternion_to_euler_degrees(odometry.pose.pose.orientation)
        position = odometry.pose.pose.position
        text = "POSE|%.3f,%.3f,%.2f,%.2f,%.2f" % (
            position.x,
            position.y,
            heading,
            pitch,
            roll,
        )
        try:
            self.udp_socket.sendto(text.encode("utf-8"), (vr_ip, self.pose_port))
        except OSError as error:
            self.get_logger().warning("POSE send failed: %s" % error)

    def image_callback(self, message):
        with self.state_lock:
            if not self.matched:
                return
        try:
            image = self.cv_bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            encoded, data = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
            if not encoded:
                return
            with self.image_condition:
                self.latest_jpeg = data.tobytes()
                self.image_sequence += 1
                self.image_condition.notify_all()
        except Exception as error:
            self.get_logger().warning("JPEG encode failed: %s" % error)

    def video_loop(self):
        sent_sequence = -1
        while not self.stop_event.is_set():
            with self.state_lock:
                matched = self.matched
                vr_ip = self.bound_vr_ip
            if not matched:
                self.stop_event.wait(0.2)
                continue
            if self.video_socket is None:
                try:
                    connection = socket.create_connection((vr_ip, self.video_port), timeout=2.0)
                    connection.settimeout(2.0)
                    connection.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    self.video_socket = connection
                    self.get_logger().info("JPEG stream connected to %s:%d" % (vr_ip, self.video_port))
                except OSError:
                    self.stop_event.wait(float(self.video_retry_sec))
                    continue
            with self.image_condition:
                self.image_condition.wait_for(
                    lambda: self.stop_event.is_set() or self.image_sequence != sent_sequence,
                    timeout=0.5,
                )
                jpeg = self.latest_jpeg
                sequence = self.image_sequence
            if jpeg is None or sequence == sent_sequence:
                continue
            try:
                self.video_socket.sendall(struct.pack("<I", len(jpeg)) + jpeg)
                sent_sequence = sequence
            except OSError as error:
                self.get_logger().warning("JPEG stream disconnected: %s" % error)
                self.close_video_socket()

    def close_video_socket(self):
        connection = self.video_socket
        self.video_socket = None
        if connection is not None:
            try:
                connection.close()
            except OSError:
                pass

    def close(self):
        self.publish_zero()
        self.stop_event.set()
        with self.image_condition:
            self.image_condition.notify_all()
        self.close_video_socket()
        try:
            self.udp_socket.close()
        except OSError:
            pass
        self.receiver_thread.join(timeout=1.0)
        self.video_thread.join(timeout=1.0)


def main():
    rclpy.init()
    node = VrBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
