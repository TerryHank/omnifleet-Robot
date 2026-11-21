#!/usr/bin/env python3
"""OpenCV KCF tracker with aligned depth and OmniFleet motion output."""

from __future__ import annotations

import json
import time

import cv2
import numpy as np


def median_depth(depth, bbox, color_size, minimum=0.2, maximum=1.5):
    """Read the robust centre depth of a tracked color-image rectangle."""
    x, y, width, height = bbox
    color_width, color_height = color_size
    cx = int(round((x + width / 2) * depth.shape[1] / color_width))
    cy = int(round((y + height / 2) * depth.shape[0] / color_height))
    radius = max(2, int(round(min(width, height) * .05)))
    x0, x1 = max(0, cx - radius), min(depth.shape[1], cx + radius + 1)
    y0, y1 = max(0, cy - radius), min(depth.shape[0], cy + radius + 1)
    values = depth[y0:y1, x0:x1]
    values = values[(values >= minimum * 1000) & (values <= maximum * 1000)]
    return None if values.size == 0 else float(np.median(values)) * .001


def main(args=None):
    import rclpy
    from cv_bridge import CvBridge
    from geometry_msgs.msg import Twist
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image
    from std_msgs.msg import String

    class KcfFollowerNode(Node):
        def __init__(self):
            super().__init__("kcf_follower")
            p = lambda name, default: self.declare_parameter(name, default).value
            self.color_topic = str(p("tracker_color_topic", "/camera/color/image_raw"))
            self.depth_topic = str(p("depth_topic", "/camera/aligned_depth_to_color/image_raw"))
            self.output_topic = str(p("output_image_topic", "/omnifleet_vision/kcf/image"))
            self.command_topic = str(p("cmd_vel_topic", "/cmd_vel"))
            self.enable_motion = bool(p("enable_motion", False))
            self.use_gui = bool(p("use_gui", True))
            self.scale = float(p("tracking_scale", 1.0))
            self.roi = tuple(int(p(name, 0)) for name in
                             ("roi_x", "roi_y", "roi_width", "roi_height"))
            self.target_distance = float(p("target_distance", .8))
            self.tracking_timeout = float(p("tracking_timeout", .5))
            self.depth_timeout = float(p("depth_timeout", 2.5))
            self.linear_kp = float(p("linear_kp", .6))
            self.angular_kp = float(p("angular_kp", .8))
            self.linear_deadband = float(p("linear_deadband", .15))
            self.minimum_linear_speed = float(p("minimum_linear_speed", .10))
            self.max_linear_speed = float(p("max_linear_speed", .25))
            self.max_angular_speed = float(p("max_angular_speed", .5))
            self.bridge = CvBridge()
            self.tracker = None
            self.bbox = None
            self.color_size = (640, 480)
            self.depth = None
            self.last_tracking = 0.0
            self.last_depth = 0.0
            self.pub = self.create_publisher(Image, self.output_topic, qos_profile_sensor_data)
            self.status_pub = self.create_publisher(String, "/omnifleet_vision/kcf/status", 10)
            self.cmd_pub = self.create_publisher(Twist, self.command_topic, 10)
            self.create_subscription(Image, self.color_topic, self.on_color, qos_profile_sensor_data)
            self.create_subscription(Image, self.depth_topic, self.on_depth, qos_profile_sensor_data)
            self.create_timer(.1, self.on_control)
            self.get_logger().info(
                f"OpenCV {cv2.__version__} KCF ready: color={self.color_topic} "
                f"depth={self.depth_topic} output={self.output_topic} motion={self.enable_motion}"
            )

        def now(self):
            return self.get_clock().now().nanoseconds / 1e9

        def on_depth(self, message):
            if message.encoding not in ("16UC1", "mono16"):
                return
            self.depth = np.frombuffer(message.data, dtype="<u2").reshape(
                message.height, message.width).copy()
            self.last_depth = self.now()

        def make_tracker(self, image):
            x, y, width, height = self.roi
            if width <= 1 or height <= 1:
                if not self.use_gui:
                    return False
                x, y, width, height = (int(value) for value in cv2.selectROI(
                    "OmniFleet KCF", image, fromCenter=False, showCrosshair=True))
            x = max(0, min(x, image.shape[1] - 2))
            y = max(0, min(y, image.shape[0] - 2))
            width = max(0, min(width, image.shape[1] - x))
            height = max(0, min(height, image.shape[0] - y))
            if width <= 1 or height <= 1:
                return False
            self.tracker = cv2.TrackerKCF_create()
            self.tracker.init(image, (x, y, width, height))
            self.bbox = (float(x), float(y), float(width), float(height))
            self.last_tracking = self.now()
            return True

        def on_color(self, message):
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            if self.scale < .999:
                image = cv2.resize(image, None, fx=self.scale, fy=self.scale,
                                   interpolation=cv2.INTER_AREA)
            self.color_size = (image.shape[1], image.shape[0])
            if self.tracker is None:
                self.make_tracker(image)
            else:
                ok, bbox = self.tracker.update(image)
                if ok:
                    self.bbox = tuple(float(value) for value in bbox)
                    self.last_tracking = self.now()
                else:
                    self.tracker = None
                    self.bbox = None
            debug = image.copy()
            distance = median_depth(self.depth, self.bbox, self.color_size) if self.depth is not None and self.bbox is not None else None
            self.status_pub.publish(String(data=json.dumps({"bbox": self.bbox, "depth_m": distance,
                "depth_received": self.depth is not None, "depth_topic": self.depth_topic})))
            if self.bbox is not None:
                x, y, width, height = (int(round(value)) for value in self.bbox)
                cv2.rectangle(debug, (x, y), (x + width, y + height), (0, 255, 0), 2)
            cv2.putText(debug, "KCF tracking" if self.bbox else "KCF waiting for ROI",
                        (16, 32), cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 255, 255), 2)
            cv2.putText(debug, f"Aligned depth: {distance:.3f} m" if distance is not None else "Aligned depth: no valid sample",
                        (16, 60), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 255, 255), 2)
            output = self.bridge.cv2_to_imgmsg(debug, encoding="bgr8")
            output.header = message.header
            self.pub.publish(output)
            if self.use_gui:
                cv2.imshow("OmniFleet KCF", debug)
                cv2.waitKey(1)

        def on_control(self):
            if not self.enable_motion:
                return
            command = Twist()
            now = self.now()
            if (self.bbox is not None and self.depth is not None and
                    now - self.last_tracking <= self.tracking_timeout and
                    now - self.last_depth <= self.depth_timeout):
                distance = median_depth(self.depth, self.bbox, self.color_size)
                if distance is not None:
                    error = distance - self.target_distance
                    if abs(error) > self.linear_deadband:
                        command.linear.x = float(np.clip(error * self.linear_kp,
                            -self.max_linear_speed, self.max_linear_speed))
                        if abs(command.linear.x) < self.minimum_linear_speed:
                            command.linear.x = np.copysign(self.minimum_linear_speed,
                                                          command.linear.x)
                    center = self.bbox[0] + self.bbox[2] / 2
                    horizontal = (center - self.color_size[0] / 2) / (self.color_size[0] / 2)
                    command.angular.z = float(np.clip(-horizontal * self.angular_kp,
                        -self.max_angular_speed, self.max_angular_speed))
            self.cmd_pub.publish(command)

        def destroy_node(self):
            if self.enable_motion and rclpy.ok():
                self.cmd_pub.publish(Twist())
            if self.use_gui:
                cv2.destroyAllWindows()
            return super().destroy_node()

    rclpy.init(args=args)
    node = KcfFollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
