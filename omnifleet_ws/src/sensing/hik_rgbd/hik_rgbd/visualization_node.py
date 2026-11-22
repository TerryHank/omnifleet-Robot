"""On-demand gray depth display; never modify camera raw topics."""
import json
import math
import os
import array
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import cv2
import numpy as np
cv2.setNumThreads(1)
import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import String
from tf2_ros import StaticTransformBroadcaster
from tf2_msgs.msg import TFMessage
from omnifleet_hikrobot_rgbd.camera_node import load_calibration


def depth_array(message):
    return np.ndarray((message.height, message.width),
                      dtype='>u2' if message.is_bigendian else '<u2',
                      buffer=message.data, strides=(message.step, 2)).astype(np.uint16)


def clean_depth(depth):
    """Reject isolated jumps; retain original measured Z for accepted pixels."""
    median = cv2.medianBlur(depth, 5)
    valid = ((depth > 0) & (depth < 65535) & (median > 0) & (median < 65535) &
             (np.abs(depth.astype(float) - median) <= np.maximum(30., depth * .02)))
    return np.where(valid, depth, 0).astype(np.uint16)


def smooth_small_holes(depth):
    """Edge-limited median smoothing and local holes; full operation in OpenCV/NumPy."""
    valid = (depth > 0) & (depth < 65535)
    measured = np.where(valid, depth, 0).astype(np.uint16)
    median = cv2.medianBlur(measured, 3)
    kernel = np.ones((3, 3), np.uint8)
    neighbours = cv2.filter2D(valid.astype(np.uint8), -1, kernel)
    lower = cv2.erode(np.where(valid, depth, 65535).astype(np.uint16), kernel)
    upper = cv2.dilate(measured, kernel)
    consistent = upper.astype(np.int32)-lower.astype(np.int32) <= np.maximum(30., lower*.02)
    accepted = valid & (median > 0) & (np.abs(depth.astype(np.int32)-median.astype(np.int32)) <= np.maximum(30., depth*.02))
    result = np.where(accepted, median, measured).astype(np.uint16)
    fill = ~valid & (neighbours >= 5) & consistent & (median > 0)
    result[fill] = median[fill]
    return result


class Visualization(Node):
    def __init__(self):
        super().__init__('hik_rgbd_visualization')
        self.camera_backend = self.declare_parameter('camera_backend', 'hikrobot').value
        self.display_max_mm = float(self.declare_parameter('display_max_mm', 1500.).value)
        if self.camera_backend == 'hikrobot':
            # A display root with X forward, Y left, Z up. This does not assert a
            # camera-to-vehicle mounting transform. RGB/depth uses factory extrinsics.
            config = Path(get_package_share_directory('omnifleet_hikrobot_rgbd')) / 'config/mv_dt01snu.yaml'
            params = yaml.safe_load(config.read_text())['mv_dt01snu_camera']['ros__parameters']
            _, _, depth_to_rgb, _, _ = load_calibration(params['calibration_file'], params['serial_number'])
            rgb_to_depth = np.linalg.inv(depth_to_rgb)
            optical = TransformStamped()
            optical.header.stamp = self.get_clock().now().to_msg()
            optical.header.frame_id = 'rgbd_view_z_up'
            optical.child_frame_id = 'camera_depth_optical_frame'
            optical.transform.rotation.x, optical.transform.rotation.y = -.5, .5
            optical.transform.rotation.z, optical.transform.rotation.w = -.5, .5
            rgb = TransformStamped()
            rgb.header.stamp = optical.header.stamp
            rgb.header.frame_id = 'camera_depth_optical_frame'
            rgb.child_frame_id = 'camera_color_optical_frame'
            rgb.transform.translation.x, rgb.transform.translation.y, rgb.transform.translation.z = rgb_to_depth[:3, 3]
            rvec = cv2.Rodrigues(rgb_to_depth[:3, :3])[0].reshape(3)
            angle = np.linalg.norm(rvec)
            q = rvec * (math.sin(angle / 2) / angle if angle > 1e-12 else .5)
            rgb.transform.rotation.x, rgb.transform.rotation.y, rgb.transform.rotation.z = q
            rgb.transform.rotation.w = math.cos(angle / 2)
            self.static_tf = StaticTransformBroadcaster(self)
            self.static_tf.sendTransform([optical, rgb])
            # Keep the complete camera subtree available after a Foxglove reconnect:
            # the bridge's last /tf_static message may belong to another publisher.
            self.display_tf = self.create_publisher(
                TFMessage, '/camera/tf_static', QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
            self.display_tf.publish(TFMessage(transforms=[optical, rgb]))
        self.filtered_depth = self.create_publisher(Image, '/camera/depth/image_filtered', qos_profile_sensor_data)
        self.gray_raw = self.create_publisher(Image, '/camera/depth/image_gray', qos_profile_sensor_data)
        self.gray_clean = self.create_publisher(Image, '/camera/depth/image_gray_filtered', qos_profile_sensor_data)
        self.gray_jpeg = {
            self.gray_raw.topic_name: self.create_publisher(CompressedImage, '/camera/depth/image_gray/compressed', qos_profile_sensor_data),
            self.gray_clean.topic_name: self.create_publisher(CompressedImage, '/camera/depth/image_gray_filtered/compressed', qos_profile_sensor_data),
        }
        self.status = self.create_publisher(String, '/camera/rgbd/visualization_status', 1)
        self.depth_input = None
        self.create_timer(.5, self.update_depth_input)

    def requested(self, publisher):
        return publisher.get_subscription_count() or self.gray_jpeg[publisher.topic_name].get_subscription_count()

    def update_depth_input(self):
        needed = self.requested(self.gray_raw) or self.requested(self.gray_clean) or self.filtered_depth.get_subscription_count() or self.status.get_subscription_count()
        if needed and self.depth_input is None:
            self.depth_input = self.create_subscription(Image, '/camera/depth/image_raw', self.depth, qos_profile_sensor_data)
        elif not needed and self.depth_input is not None:
            self.destroy_subscription(self.depth_input)
            self.depth_input = None

    def gray(self, depth, header, publisher):
        compressed = self.gray_jpeg[publisher.topic_name]
        if not publisher.get_subscription_count() and not compressed.get_subscription_count():
            return
        valid = (depth > 0) & (depth < 65535)
        raw_display = publisher is self.gray_raw
        maximum = self.display_max_mm if raw_display else 8000.
        pixels = np.where(valid, np.clip((maximum - depth) * 255. / maximum, 1, 255), 0).astype(np.uint8)
        if publisher.get_subscription_count():
            payload = array.array('B')
            payload.frombytes(memoryview(pixels).cast('B'))
            message = Image(header=header, height=depth.shape[0], width=depth.shape[1],
                            encoding='mono8', is_bigendian=0, step=depth.shape[1])
            message.data = payload
            publisher.publish(message)
        if compressed.get_subscription_count():
            extension = '.png' if raw_display else '.jpg'
            options = [cv2.IMWRITE_PNG_COMPRESSION,1] if raw_display else [cv2.IMWRITE_JPEG_QUALITY,90]
            ok, encoded = cv2.imencode(extension, pixels, options)
            if ok:
                payload = array.array('B')
                payload.frombytes(memoryview(encoded).cast('B'))
                message = CompressedImage(header=header, format='png' if raw_display else 'jpeg')
                message.data = payload
                compressed.publish(message)

    def depth(self, message):
        raw = depth_array(message)
        self.gray(raw, message.header, self.gray_raw)
        if self.requested(self.gray_clean) or self.filtered_depth.get_subscription_count():
            filtered = smooth_small_holes(raw) if self.camera_backend == 'orbbec' else clean_depth(raw)
            self.gray(filtered, message.header, self.gray_clean)
            if self.filtered_depth.get_subscription_count():
                payload = array.array('B'); payload.frombytes(memoryview(filtered).cast('B'))
                result = Image(header=message.header, height=message.height, width=message.width,
                               encoding='16UC1', is_bigendian=0, step=message.width*2)
                result.data = payload; self.filtered_depth.publish(result)
        if self.status.get_subscription_count():
            self.status.publish(String(data=json.dumps(dict(
                depth_unit='millimetres in source 16UC1',
                source_valid_fraction=float(((raw > 0) & (raw < 65535)).mean()),
                source_rated_range_fraction=float(((raw >= 200) & (raw <= self.display_max_mm)).mean()),
                visual_point_clouds_enabled=False,
                gray_display_range_mm=[0, self.display_max_mm], filtered_gray_display_range_mm=[0, 8000],
                rated_range_mm=[200, 1500] if self.camera_backend == 'hikrobot' else None,
                camera_backend=self.camera_backend,
                filtered_preview='edge_limited_median_3x3_small_holes' if self.camera_backend == 'orbbec' else 'outlier_rejection',
                source_topics_unchanged=True))))


def main(args=None):
    rclpy.init(args=args)
    node = Visualization()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
