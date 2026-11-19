#!/usr/bin/env python3
"""Query native Gemini depth for tracked RGB boxes without an aligned image."""
import json
from collections import deque

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image, Range
from std_msgs.msg import String
from orbbec_camera_msgs.msg import Extrinsics
from omnifleet_hikrobot_rgbd.depth_foreground import depth_foreground
from omnifleet_hikrobot_rgbd.aligned_depth import aligned_depth_foreground
from omnifleet_hikrobot_rgbd.foreground_tracking import summary


class TargetSparseDepthNode(Node):
    def __init__(self):
        super().__init__("target_sparse_depth")
        p = lambda name, default: self.declare_parameter(name, default).value
        self.minimum = float(p("min_depth", .2))
        self.maximum = float(p("max_depth", 3.5))
        self.depths = deque(maxlen=4)
        self.color_info = self.depth_info = self.transform = self.mask = None
        self.publisher = self.create_publisher(String, str(p("output_topic", "/vision/targets_3d")), 10)
        range_topic = str(p("range_topic", ""))
        self.range_pub = self.create_publisher(Range, range_topic, 10) if range_topic else None
        self.create_subscription(String, str(p("input_topic", "/vision/tracks")), self.on_target, 1)
        self.create_subscription(CameraInfo, "/camera/color/camera_info", self.on_color_info, qos_profile_sensor_data)
        self.native_subscriptions=None

    def subscribe_native(self):
        # Foreground tracks already carry measured calibrated XYZ. Receiving a
        # second1280x800 depth stream here adds traffic without using its pixels.
        # Retain native querying for legacy producers that have no foreground.
        self.native_subscriptions=[
            self.create_subscription(Image,'/camera/depth/image_raw',self.depths.append,QoSProfile(depth=1,reliability=ReliabilityPolicy.BEST_EFFORT)),
            self.create_subscription(CameraInfo,'/camera/depth/camera_info',self.on_depth_info,qos_profile_sensor_data),
            self.create_subscription(Extrinsics,'/camera/depth_to_color',self.on_extrinsics,QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL))]

    def on_color_info(self, info):
        if info.k[0] > 0 and info.k[4] > 0:
            self.color_info = info
            if self.mask is None or self.mask.shape != (info.height, info.width):
                self.mask = np.ones((info.height, info.width), dtype=bool)

    def on_depth_info(self, info):
        if info.k[0] > 0 and info.k[4] > 0:
            self.depth_info = info

    def on_extrinsics(self, message):
        self.transform = np.eye(4)
        self.transform[:3, :3] = np.asarray(message.rotation).reshape(3, 3)
        self.transform[:3, 3] = message.translation

    @staticmethod
    def stamp(message):
        return message.header.stamp.sec + message.header.stamp.nanosec * 1e-9

    def on_target(self, message):
        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            return
        source_stamp = float(payload.get("source_stamp", payload.get("stamp", 0.)))
        targets = payload.get("tracks", [])
        if self.native_subscriptions is None and any('foreground' not in t for t in targets):
            self.subscribe_native()
        depth = min(self.depths, key=lambda value: abs(self.stamp(value) - source_stamp)) if self.depths else None
        ready = (depth is not None and depth.encoding == "16UC1" and
                 abs(self.stamp(depth) - source_stamp) <= .2 and
                 self.color_info is not None and self.depth_info is not None and self.transform is not None)
        results = []
        for target in targets:
            item = dict(target, depth_m=None, position_3d=None)
            foreground=target.get('foreground')
            if foreground is not None:
                # Reuse exactly the component used by the tracker, not a second
                # box median with a different foreground and background mix.
                when=foreground.get('depth_stamp')
                if foreground.get('depth_m') is not None and when is not None and abs(when-source_stamp)<=.2:
                    item.update(depth_m=foreground['depth_m'],
                        position_3d=dict(zip(('x','y','z'),foreground['rgb_xyz_m'])),
                        sampled_count=foreground['sampled_count'],inlier_count=foreground['sampled_count'])
            elif ready:
                native = np.ndarray((depth.height, depth.width), dtype=">u2" if depth.is_bigendian else "<u2",
                                    buffer=depth.data, strides=(depth.step, 2))
                info = self.color_info
                if depth.header.frame_id==info.header.frame_id:
                    sample=aligned_depth_foreground(native,target['bbox'],(info.width,info.height),
                        np.asarray(info.k).reshape(3,3),min_depth_m=self.minimum,
                        max_depth_m=self.maximum,rgb_distortion=info.d)
                else:
                    sample = depth_foreground(native, target['bbox'], (info.width, info.height),
                        np.asarray(self.depth_info.k).reshape(3, 3), np.asarray(info.k).reshape(3, 3),
                        self.transform, min_depth_m=self.minimum,
                        max_depth_m=self.maximum, rgb_distortion=info.d)
                if sample is not None:
                    xyz = sample["rgb_xyz_m"]
                    item.update(depth_m=sample["depth_m"], position_3d=dict(zip(("x", "y", "z"), map(float, xyz))),
                                sampled_count=sample['depth_sample_count'],inlier_count=sample['depth_sample_count'],
                                foreground=summary(sample,source_stamp,self.stamp(depth)))
            results.append(item)
        now = self.get_clock().now().nanoseconds * 1e-9
        result = dict(stamp=now, source_stamp=source_stamp, detections=results,
                      frame_id=self.color_info.header.frame_id if self.color_info else '',
                      image_width=self.color_info.width if self.color_info else payload.get("image_width", 640),
                      depth_method="foreground_aligned_16x16" if any(
                          item.get('foreground',{}).get('projection_backend')=='aligned_depth_direct' for item in results)
                          else "foreground_native_16x16", calibration_ready=bool(payload.get('foreground_depth_ready',ready)))
        self.publisher.publish(String(data=json.dumps(result, separators=(",", ":"))))
        if self.range_pub:
            value = Range()
            measured_stamp=source_stamp
            if results and results[0]['depth_m'] is not None:
                measured_stamp=results[0].get('foreground',{}).get('depth_stamp',
                    self.stamp(depth) if depth is not None else source_stamp)
            value.header.stamp.sec, value.header.stamp.nanosec = divmod(round(measured_stamp * 1e9), 1000000000)
            value.min_range, value.max_range = self.minimum, self.maximum
            value.range = float(results[0]["depth_m"]) if results and results[0]["depth_m"] is not None else float("nan")
            self.range_pub.publish(value)


def main(args=None):
    rclpy.init(args=args)
    node = TargetSparseDepthNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
