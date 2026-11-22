#!/usr/bin/env python3
"""Experimental VR UDP/TCP adapter for the tracked car.

Network messages are translated into standard ROS 2 messages:
  HEADP/HEADY -> trajectory_msgs/JointTrajectory (radians)
  SPEED/ANGLE -> geometry_msgs/Twist
  POSE         <- nav_msgs/Odometry
  camera       <- sensor_msgs/CompressedImage

The FTServo bridge remains /t2/servo_command; this node converts the standard
joint trajectory to that existing service so the STM32 transport is unchanged.
"""
from collections import deque
import math
from pathlib import Path
import socket
import struct
from statistics import median
import time

import rclpy
from geometry_msgs.msg import Quaternion, Twist, Vector3
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener
from tf_transformations import quaternion_conjugate, quaternion_multiply
from sensor_msgs.msg import CompressedImage, Imu, JointState
from std_msgs.msg import Bool, Float64
from std_srvs.srv import Trigger
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from omnifleet_interfaces.srv import ServoCommand


def clamp(value, low, high):
    return max(low, min(high, value))


def bind_interface(sock, interface):
    if interface:
        socket.if_nametoindex(interface)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE,
                        (interface + '\0').encode('utf-8'))


def rpy_from_quaternion(q):
    roll = math.atan2(2.0 * (q.w * q.x + q.y * q.z),
                      1.0 - 2.0 * (q.x * q.x + q.y * q.y))
    pitch = math.asin(clamp(2.0 * (q.w * q.y - q.z * q.x), -1.0, 1.0))
    yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                     1.0 - 2.0 * (q.y * q.y + q.z * q.z))
    return roll, pitch, yaw


class VrProtocolAdapter(Node):
    def __init__(self):
        super().__init__('vr_protocol_adapter')
        self.declare_parameter('car_id', 'CAR001')
        self.declare_parameter('car_name', 'Tracked-Car')
        self.declare_parameter('ctrl_port', 8888)
        self.declare_parameter('discovery_port', 9100)
        self.declare_parameter('pose_port', 9000)
        self.declare_parameter('video_port', 8090)
        self.declare_parameter('network_interface', '')
        self.declare_parameter('enable_drive', False)
        self.declare_parameter('attitude_topic', '')
        self.declare_parameter('heading_zero_file', '')
        self.declare_parameter('heading_topic', '')
        self.declare_parameter('rep103_attitude', False)
        self.declare_parameter('robot_prefix', '')
        self.declare_parameter('odom_topic', str(self.get_parameter('robot_prefix').value).rstrip('/') + '/lidar_odometry/pose')
        self.declare_parameter('camera_topic', '/camera/image/compressed')
        self.declare_parameter('servo_service', '/t2/servo_command')

        self.car_id = str(self.get_parameter('car_id').value)
        self.car_name = str(self.get_parameter('car_name').value)
        self.ctrl_port = int(self.get_parameter('ctrl_port').value)
        self.discovery_port = int(self.get_parameter('discovery_port').value)
        self.pose_port = int(self.get_parameter('pose_port').value)
        self.video_port = int(self.get_parameter('video_port').value)
        self.network_interface = str(self.get_parameter('network_interface').value)
        self.enable_drive = bool(self.get_parameter('enable_drive').value)
        self.robot_prefix = str(self.get_parameter('robot_prefix').value).rstrip('/')
        odom_topic = str(self.get_parameter('odom_topic').value) or self.robot_prefix + '/lidar_odometry/pose'
        self.cmd_topic = self.robot_prefix + '/cmd_vel'
        self.fire_topic = self.robot_prefix + '/vr/fire'
        self.joint_topic = self.robot_prefix + '/servo/command'
        self.joint_state_topic = self.robot_prefix + '/servo/joint_states'
        self.matched_vr = ''
        self.bound_ip = ''
        self.last_control = time.monotonic()
        self.last_speed = 0.0
        self.last_angle = 0.0
        self.last_odom = None
        self.last_attitude = None
        self.attitude_samples = deque(maxlen=3)
        self.latest_jpeg = None
        self.video_socket = None
        self._pending_servo = None
        self._queued_servo = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bind_interface(self.sock, self.network_interface)
        self.sock.bind(('0.0.0.0', self.ctrl_port))
        self.sock.setblocking(False)

        self.cmd_pub = self.create_publisher(Twist, self.cmd_topic, 10)
        self.fire_pub = self.create_publisher(Bool, self.fire_topic, 10)
        self.joint_cmd_pub = self.create_publisher(JointTrajectory, self.joint_topic, 10)
        self.joint_state_pub = self.create_publisher(JointState, self.joint_state_topic, 10)
        self.servo_client = self.create_client(
            ServoCommand, str(self.get_parameter('servo_service').value))
        self.create_subscription(JointTrajectory, self.joint_topic,
                                 self.joint_command_cb, 10)
        self.rep103_attitude = self.get_parameter('rep103_attitude').value
        self.heading_pub = None
        self.rpy_pub = None
        self.heading_zero = None
        self.heading_yaw = None
        zero_file = self.get_parameter('heading_zero_file').value
        if zero_file:
            self.heading_zero_file = Path(zero_file)
            try:
                self.heading_zero = float(self.heading_zero_file.read_text())
            except FileNotFoundError:
                pass
            self.heading_pub = self.create_publisher(
                Float64, '/vr/heading_rad' if self.rep103_attitude else '/vr/heading_deg', 1)
            if self.rep103_attitude:
                self.rpy_pub = self.create_publisher(Vector3, '/vr/attitude_rpy_rad', 1)
            self.heading_reset_srv = self.create_service(
                Trigger, '/vr/reset_heading', self.reset_heading)
        heading_topic = self.get_parameter('heading_topic').value
        if heading_topic:
            self.create_subscription(Odometry, heading_topic, self.heading_cb, 10)
        self.create_subscription(Odometry, odom_topic, self.odom_cb, 10)
        attitude_topic = self.get_parameter('attitude_topic').value
        if attitude_topic:
            if self.rep103_attitude:
                self.attitude_tf = Buffer()
                self.attitude_tf_listener = TransformListener(self.attitude_tf, self)
            self.create_subscription(Imu, attitude_topic, self.attitude_cb, qos_profile_sensor_data)
        self.create_subscription(CompressedImage, str(self.get_parameter('camera_topic').value), self.camera_cb, 5)
        self.create_timer(0.02, self.poll_udp)
        self.create_timer(1.0, self.broadcast_disc)
        self.create_timer(0.05, self.publish_pose)
        self.create_timer(0.1, self.send_video)
        self.broadcast_disc()
        self.get_logger().info('VR适配层监听 UDP %d，驱动控制=%s，摄像头=%s，网卡=%s' %
                               (self.ctrl_port, self.enable_drive,
                                self.get_parameter('camera_topic').value,
                                self.network_interface or 'auto'))

    def broadcast_disc(self):
        paired = 1 if self.matched_vr else 0
        text = 'DISC|%s,%d,%d,%s,%s' % (self.car_id, self.ctrl_port, paired,
                                        self.matched_vr, self.car_name)
        try:
            self.sock.sendto(text.encode('utf-8'), ('255.255.255.255', self.discovery_port))
        except OSError as error:
            self.get_logger().warning('DISC发送失败: %s' % error)

    def send_reply(self, text, address):
        self.sock.sendto(text.encode('utf-8'), address)

    def poll_udp(self):
        for _ in range(20):
            try:
                raw, address = self.sock.recvfrom(2048)
            except BlockingIOError:
                break
            try:
                self.handle_packet(raw.decode('utf-8').strip(), address)
            except (ValueError, UnicodeDecodeError) as error:
                self.get_logger().warning('忽略非法协议包 %s: %s' % (address, error))
        if self.enable_drive and time.monotonic() - self.last_control > 0.2:
            self.last_speed = self.last_angle = 0.0
            self.publish_drive()

    def handle_packet(self, text, address):
        command, _, value = text.partition('|')
        command = command.upper()
        value = value.strip()
        if command == 'PAIR':
            if not value:
                return
            if not self.matched_vr or self.matched_vr == value:
                self.matched_vr, self.bound_ip = value, address[0]
                self.send_reply('PAIR_ACK|%s,1,%s' % (self.car_id, value), address)
            else:
                self.send_reply('PAIR_ACK|%s,0,%s' % (self.car_id, self.matched_vr), address)
            return
        if command == 'UNPAIR':
            if value == self.matched_vr:
                self.matched_vr = self.bound_ip = ''
                self.close_video()
            return
        if address[0] != self.bound_ip:
            return
        if command in ('HEADP', 'HEADY'):
            self.publish_head(command, float(value))
        elif command == 'SPEED':
            self.last_speed = clamp(float(value), -1.0, 1.0)
            self.last_control = time.monotonic(); self.publish_drive()
        elif command == 'ANGLE':
            self.last_angle = clamp(float(value), -30.0, 30.0)
            self.last_control = time.monotonic(); self.publish_drive()
        elif command == 'RESET':
            self.reset_outputs()
        elif command == 'FIRE':
            message = Bool(); message.data = value == '0' or value.lower() == 'true'
            self.fire_pub.publish(message)

    def publish_head(self, command, degrees):
        degrees = clamp(degrees, -180.0, 180.0)
        name = 'pitch' if command == 'HEADP' else 'yaw'
        msg = JointTrajectory(); msg.header.stamp = self.get_clock().now().to_msg()
        msg.joint_names = [name]
        point = JointTrajectoryPoint(); point.positions = [math.radians(degrees)]
        point.time_from_start.sec = 0; point.time_from_start.nanosec = 100000000
        msg.points = [point]
        self.joint_cmd_pub.publish(msg)

    def joint_command_cb(self, message):
        if not message.points:
            return
        point = message.points[-1]
        for index, name in enumerate(message.joint_names):
            if index >= len(point.positions) or name not in ('pitch', 'yaw'):
                continue
            speed = 300
            accel = 30
            if index < len(point.velocities):
                speed = clamp(round(abs(point.velocities[index]) * 10.0), 0, 3400)
            if index < len(point.accelerations):
                accel = clamp(round(abs(point.accelerations[index]) * 10.0), 0, 255)
            self._send_servo(name, math.degrees(point.positions[index]), speed, accel)

    def _send_servo(self, name, degrees, speed=300, accel=30):
        if self._pending_servo is not None:
            self._queued_servo[name] = degrees, speed, accel
            return
        if not self.servo_client.service_is_ready():
            return
        servo_id, low, high = (1, 1067, 2263) if name == 'pitch' else (2, 2048, 4095)
        position = round((low + high) / 2.0 + degrees / 180.0 * (high - low) / 2.0)
        request = ServoCommand.Request(); request.operation = 3; request.id = servo_id
        request.arg0 = position; request.arg1 = speed; request.arg2 = accel
        self._pending_servo = self.servo_client.call_async(request)
        self._pending_servo.add_done_callback(lambda _: self._servo_done(name, position))

    def _servo_done(self, name, position):
        future = self._pending_servo; self._pending_servo = None
        if self._queued_servo:
            next_axis = next(iter(self._queued_servo))
            self._send_servo(next_axis, *self._queued_servo.pop(next_axis))
        if future is None or not future.result().success:
            self.get_logger().warning('舵机 %s 命令失败' % name); return
        state = JointState(); state.header.stamp = self.get_clock().now().to_msg()
        state.name = ['pitch' if name == 'pitch' else 'yaw']; state.position = [math.radians(position)]
        self.joint_state_pub.publish(state)

    def attitude_cb(self, message):
        q = message.orientation
        norm = math.hypot(q.x, q.y, q.z, q.w)
        if message.orientation_covariance[0] >= 0 and abs(norm - 1.0) < 0.01:
            now = time.monotonic()
            if self.attitude_samples and now - self.attitude_samples[-1][0] >= 0.5:
                self.attitude_samples.clear()
            if self.rep103_attitude:
                try:
                    tf = self.attitude_tf.lookup_transform(
                        'base_link', message.header.frame_id, Time()).transform.rotation
                except TransformException:
                    return
                # world<-base = world<-sensor * inverse(base<-sensor).
                base = quaternion_multiply(
                    (q.x, q.y, q.z, q.w), quaternion_conjugate((tf.x, tf.y, tf.z, tf.w)))
                q = Quaternion(x=float(base[0]), y=float(base[1]), z=float(base[2]), w=float(base[3]))
            roll, pitch, _ = rpy_from_quaternion(q)
            self.attitude_samples.append((now, roll, pitch))
            if len(self.attitude_samples) == self.attitude_samples.maxlen:
                _, rolls, pitches = zip(*self.attitude_samples)
                self.last_attitude = now, median(rolls), median(pitches)

    def save_heading_zero(self, yaw):
        pending = self.heading_zero_file.with_suffix('.tmp')
        pending.write_text(str(yaw))
        pending.replace(self.heading_zero_file)
        self.heading_zero = yaw

    def reset_heading(self, request, response):
        if self.heading_yaw is None:
            response.message = 'No heading received'
            return response
        try:
            self.save_heading_zero(self.heading_yaw)
        except OSError as exc:
            response.message = str(exc)
            return response
        self.publish_pose()
        response.success = True
        return response

    def heading_cb(self, message):
        _, _, yaw = rpy_from_quaternion(message.pose.pose.orientation)
        if self.heading_pub is not None and self.heading_zero is None:
            self.save_heading_zero(yaw)
        self.heading_yaw = yaw

    def odom_cb(self, message):
        self.last_odom = message
        if not self.get_parameter('heading_topic').value and self.heading_pub is not None:
            self.heading_cb(message)

    def publish_drive(self):
        if not self.enable_drive:
            return
        message = Twist(); message.linear.x = self.last_speed
        message.angular.z = self.last_angle / 30.0 * 2.0
        self.cmd_pub.publish(message)

    def reset_outputs(self):
        self.last_speed = self.last_angle = 0.0; self.publish_drive()
        self.publish_head('HEADP', 0.0); self.publish_head('HEADY', 0.0)

    def publish_pose(self):
        if self.last_odom is None:
            return
        pose = self.last_odom.pose.pose
        roll, pitch, yaw = rpy_from_quaternion(pose.orientation)
        heading = -math.degrees(yaw)
        if self.heading_pub is not None:
            if self.heading_yaw is None:
                return
            relative_yaw = self.heading_yaw - self.heading_zero
            if not self.rep103_attitude:
                relative_yaw = -relative_yaw
            relative_yaw = (relative_yaw + math.pi) % math.tau - math.pi
            heading = math.degrees(relative_yaw)
            self.heading_pub.publish(Float64(data=relative_yaw if self.rep103_attitude else heading))
        if self.last_attitude is not None:
            received_at, imu_roll, imu_pitch = self.last_attitude
            if time.monotonic() - received_at < 0.5:
                roll, pitch = (imu_roll, imu_pitch) if self.rep103_attitude else (imu_pitch, imu_roll)
                if self.rpy_pub is not None:
                    self.rpy_pub.publish(Vector3(x=roll, y=pitch, z=relative_yaw))
        if not self.matched_vr:
            return
        # The existing headset POSE protocol uses degrees.
        roll, pitch = map(math.degrees, (roll, pitch))
        text = 'POSE|%.3f,%.3f,%.2f,%.2f,%.2f' % (pose.position.x, pose.position.y, heading, pitch, roll)
        try:
            self.sock.sendto(text.encode('utf-8'), (self.bound_ip, self.pose_port))
        except OSError:
            pass

    def camera_cb(self, message):
        self.latest_jpeg = bytes(message.data)

    def close_video(self):
        if self.video_socket:
            self.video_socket.close()
        self.video_socket = None

    def send_video(self):
        if not self.matched_vr or not self.latest_jpeg:
            return
        try:
            if self.video_socket is None:
                self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.video_socket.settimeout(0.2)
                bind_interface(self.video_socket, self.network_interface)
                self.video_socket.connect((self.bound_ip, self.video_port))
            payload = self.latest_jpeg
            self.video_socket.sendall(struct.pack('<i', len(payload)) + payload)
        except OSError:
            self.close_video()

    def destroy_node(self):
        self.close_video(); self.sock.close(); super().destroy_node()


def main():
    rclpy.init(); node = VrProtocolAdapter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()


if __name__ == '__main__':
    main()
