#!/usr/bin/env python3
"""Publish current map pose using source-time-aligned wheel displacement."""
import copy
import signal
from pathlib import Path
import numpy as np
import yaml
import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from scipy.spatial.transform import Rotation
from pose_compensation import PoseCompensator

def stamp(message):
    return message.header.stamp.sec + message.header.stamp.nanosec / 1e9

def pose(message):
    p = message.pose.pose
    return [p.position.x, p.position.y, p.position.z,
            p.orientation.x, p.orientation.y, p.orientation.z, p.orientation.w]

class CurrentPose(Node):
    def __init__(self):
        super().__init__('latency_compensated_pose')
        self.declare_parameter('publish_tf', False)
        config = Path(__file__).parent / 'live-candidate' / 'tracked-state-estimation-simple.yaml'
        age = yaml.safe_load(config.read_text())['params']['max_time_to_use_velocity_model']
        self.compensation = PoseCompensator(float(age))
        self.lidar = None
        self.wheel = None
        self.last_published = float('-inf')
        self.publisher = self.create_publisher(Odometry, '/localization/current_pose', 10)
        self.tf = TransformBroadcaster(self)
        self.create_subscription(Odometry, '/lidar_odometry/pose', self.on_lidar, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/odom', self.on_wheel, qos_profile_sensor_data)

    def on_lidar(self, message):
        values = pose(message)
        if not np.isfinite(values).all() or np.linalg.norm(values[3:]) < 1e-9:
            return
        if self.lidar is not None and stamp(message) <= stamp(self.lidar):
            return
        self.lidar = message
        self.compensation.add_lidar(stamp(message), values)

    def on_wheel(self, message):
        values = pose(message)
        if not np.isfinite(values).all() or np.linalg.norm(values[3:]) < 1e-9:
            return
        self.compensation.add_wheel(stamp(message), values)
        if self.wheel is not None and stamp(message) <= stamp(self.wheel):
            return
        self.wheel = message
        if self.lidar is None or message.child_frame_id != self.lidar.child_frame_id:
            return
        result = self.compensation.current()
        if result is None:
            return
        timestamp, values = result
        if timestamp <= self.last_published:
            return
        output = copy.deepcopy(self.lidar)
        output.header.stamp = copy.deepcopy(message.header.stamp)
        position, rotation = output.pose.pose.position, output.pose.pose.orientation
        position.x, position.y, position.z = map(float, values[:3])
        rotation.x, rotation.y, rotation.z, rotation.w = map(float, values[3:])
        output.twist = copy.deepcopy(message.twist)
        # Include the wheel increment uncertainty in the corrected pose.
        for index in range(6):
            diagonal = index * 7
            output.pose.covariance[diagonal] += max(0., message.pose.covariance[diagonal])
        self.publisher.publish(output)
        if self.get_parameter('publish_tf').value:
            transform = TransformStamped()
            transform.header = copy.deepcopy(output.header)
            # Keep the chassis as the sole owner of odom -> base_link.
            # Use the same source-time wheel pose to derive map -> odom.
            wheel = pose(message)
            map_rotation = Rotation.from_quat(values[3:])
            odom_rotation = Rotation.from_quat(wheel[3:])
            rotation_to_odom = map_rotation * odom_rotation.inv()
            translation = np.asarray(values[:3]) - rotation_to_odom.apply(wheel[:3])
            transform.child_frame_id = message.header.frame_id.lstrip('/')
            transform.transform.translation.x, transform.transform.translation.y, transform.transform.translation.z = map(float, translation)
            rotation = rotation_to_odom.as_quat()
            transform.transform.rotation.x, transform.transform.rotation.y, transform.transform.rotation.z, transform.transform.rotation.w = map(float, rotation)
            self.tf.sendTransform(transform)
        self.last_published = timestamp

def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    def stop(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    node = CurrentPose()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
