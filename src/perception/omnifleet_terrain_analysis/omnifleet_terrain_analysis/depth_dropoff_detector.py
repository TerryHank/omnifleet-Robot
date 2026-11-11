#!/usr/bin/env python3
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from message_filters import ApproximateTimeSynchronizer, Subscriber
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image, PointCloud2
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Bool


class DepthDropoffDetector(Node):
    def __init__(self):
        super().__init__('omnifleet_t2_depth_dropoff_detector')
        self.declare_parameter('depth_topic', '/tof/aligned_depth_to_color/image_raw')
        self.declare_parameter('camera_info_topic', '/tof/aligned_depth_to_color/camera_info')
        self.declare_parameter('output_topic', '/rgbd/dropoff_obstacles')
        self.declare_parameter('status_topic', '/safety/dropoff_detected')
        self.declare_parameter('roi_top_ratio', 0.52)
        self.declare_parameter('roi_bottom_ratio', 0.95)
        self.declare_parameter('pixel_step', 8)
        self.declare_parameter('row_gap', 12)
        self.declare_parameter('depth_jump_m', 0.30)
        self.declare_parameter('minimum_candidates', 10)
        self.declare_parameter('minimum_depth_m', 0.25)
        self.declare_parameter('maximum_depth_m', 3.2)
        self.declare_parameter('virtual_raise_m', 0.12)

        self.roi_top = float(self.get_parameter('roi_top_ratio').value)
        self.roi_bottom = float(self.get_parameter('roi_bottom_ratio').value)
        self.step = int(self.get_parameter('pixel_step').value)
        self.row_gap = int(self.get_parameter('row_gap').value)
        self.jump = float(self.get_parameter('depth_jump_m').value)
        self.min_candidates = int(self.get_parameter('minimum_candidates').value)
        self.min_depth = float(self.get_parameter('minimum_depth_m').value)
        self.max_depth = float(self.get_parameter('maximum_depth_m').value)
        self.raise_m = float(self.get_parameter('virtual_raise_m').value)
        self.cloud_pub = self.create_publisher(
            PointCloud2, self.get_parameter('output_topic').value, qos_profile_sensor_data)
        self.status_pub = self.create_publisher(Bool, self.get_parameter('status_topic').value, 10)
        depth_sub = Subscriber(self, Image, self.get_parameter('depth_topic').value,
                               qos_profile=qos_profile_sensor_data)
        info_sub = Subscriber(self, CameraInfo, self.get_parameter('camera_info_topic').value,
                              qos_profile=qos_profile_sensor_data)
        self.sync = ApproximateTimeSynchronizer([depth_sub, info_sub], 10, 0.03)
        self.sync.registerCallback(self.on_depth)

    def on_depth(self, image, info):
        if image.encoding not in ('16UC1', 'mono16') or image.step < image.width * 2:
            return
        raw = np.frombuffer(image.data, dtype='<u2').reshape((image.height, image.step // 2))
        depth = raw[:, :image.width].astype(np.float32) * 0.001
        top = max(0, int(image.height * self.roi_top))
        bottom = min(image.height - self.row_gap, int(image.height * self.roi_bottom))
        points = []
        fx, fy, cx, cy = info.k[0], info.k[4], info.k[2], info.k[5]
        for v in range(top, bottom, self.step):
            upper = depth[v, ::self.step]
            lower = depth[v + self.row_gap, ::self.step]
            valid = ((upper >= self.min_depth) & (upper <= self.max_depth) &
                     (lower >= self.min_depth) & (lower <= self.max_depth))
            candidates = np.nonzero(valid & ((lower - upper) >= self.jump))[0]
            for column_index in candidates:
                u = column_index * self.step
                z = float(upper[column_index])
                x = (u - cx) * z / fx
                y = (v - cy) * z / fy - self.raise_m
                points.append((x, y, z))
        detected = len(points) >= self.min_candidates
        self.status_pub.publish(Bool(data=detected))
        selected = points if detected else []
        self.cloud_pub.publish(point_cloud2.create_cloud_xyz32(image.header, selected))


def main():
    rclpy.init()
    node = DepthDropoffDetector()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
