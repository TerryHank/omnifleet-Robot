#!/usr/bin/env python3
"""在对齐 RGB 上显示 YOLO 目标，并读取目标中心的滤波深度。"""

from __future__ import annotations

import json
import time

import cv2
import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import String

try:
    from .algorithms import measure_target_depth
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import measure_target_depth
    from ros_support import ClassicalVisionNode


class DepthMeasurementNode(ClassicalVisionNode):
    """融合对齐彩色图、YOLO 框和对齐深度图。"""

    def __init__(self) -> None:
        super().__init__("depth_measurement", "/camera/color/image_raw")
        self.declare_parameter("depth_topic", "/camera/depth/image_raw")
        self.declare_parameter("detection_topic", "/vision/depth/yolo")
        self.declare_parameter("depth_scale_16u", 0.001)
        self.declare_parameter("minimum_depth", 0.1)
        self.declare_parameter("maximum_depth", 3.5)
        self.declare_parameter("center_patch_radius", 7)
        self.declare_parameter("minimum_inlier_count", 9)
        self.declare_parameter("absolute_outlier_tolerance", 0.08)
        self.declare_parameter("mad_scale", 3.5)
        self.declare_parameter("maximum_depth_age", 4.0)
        self.declare_parameter("maximum_yolo_age", 4.0)
        self.declare_parameter("maximum_processing_rate", 10.0)

        self.latest_color = None
        self.latest_color_message = None
        self.latest_depth = None
        self.latest_depth_encoding = ""
        self.latest_depth_received_at = 0.0
        self.latest_target = None
        self.latest_yolo_received_at = 0.0
        self.last_published_at = 0.0

        depth_topic = str(self.get_parameter("depth_topic").value)
        detection_topic = str(self.get_parameter("detection_topic").value)
        self.depth_subscription = self.create_subscription(
            Image, depth_topic, self.depth_callback, qos_profile_sensor_data
        )
        self.detection_subscription = self.create_subscription(
            String, detection_topic, self.detection_callback, 10
        )
        self.get_logger().info(
            f"RGB+YOLO 中心测距：RGB={self.input_topic}，深度={depth_topic}，"
            f"YOLO={detection_topic}，飞点过滤=范围+中值MAD"
        )

    @staticmethod
    def _select_target(payload):
        """从 YOLO 结果中选择置信度最高的一个有效目标。"""

        detections = payload.get("detections", []) if isinstance(payload, dict) else []
        candidates = []
        for item in detections:
            if not isinstance(item, dict):
                continue
            bbox = item.get("bbox")
            if not isinstance(bbox, (list, tuple)) or len(bbox) < 4:
                continue
            try:
                _, _, width, height = (float(value) for value in bbox[:4])
                confidence = float(item.get("confidence", 0.0))
            except (TypeError, ValueError):
                continue
            if width <= 0.0 or height <= 0.0:
                continue
            candidates.append((confidence, width * height, item))
        return max(candidates, default=(0.0, 0.0, None), key=lambda value: value[:2])[2]

    def detection_callback(self, message: String) -> None:
        """缓存最新 YOLO 目标并刷新 RGB 窗口。"""

        try:
            payload = json.loads(message.data)
            self.latest_target = self._select_target(payload)
            self.latest_yolo_received_at = time.monotonic()
            self._publish_latest()
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            self.get_logger().warning(f"忽略无效 YOLO 结果：{error}")

    def depth_callback(self, message: Image) -> None:
        """缓存对齐深度图并刷新目标距离。"""

        try:
            depth = self.bridge.imgmsg_to_cv2(message, desired_encoding="passthrough")
            self.latest_depth = depth.copy()
            self.latest_depth_encoding = str(message.encoding)
            self.latest_depth_received_at = time.monotonic()
            self._publish_latest()
        except Exception as error:
            self.get_logger().error(f"读取对齐深度失败：{error}")

    def image_callback(self, message: Image) -> None:
        """缓存对齐 RGB；GUI 始终以这一图层作为主画面。"""

        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            self.latest_color = image.copy()
            self.latest_color_message = message
            self._publish_latest()
        except Exception as error:
            self.get_logger().error(f"读取对齐 RGB 失败：{error}")

    def _publish_latest(self) -> None:
        """绘制唯一 YOLO 目标、中心采样区和滤波距离。"""

        if self.latest_color is None or self.latest_color_message is None:
            return
        now = time.monotonic()
        maximum_rate = max(
            0.1, float(self.get_parameter("maximum_processing_rate").value)
        )
        if now - self.last_published_at < 1.0 / maximum_rate:
            return
        self.last_published_at = now

        debug = self.latest_color.copy()
        image_height, image_width = debug.shape[:2]
        yolo_age = now - self.latest_yolo_received_at
        depth_age = now - self.latest_depth_received_at
        yolo_fresh = (
            self.latest_target is not None
            and yolo_age <= float(self.get_parameter("maximum_yolo_age").value)
        )
        depth_fresh = (
            self.latest_depth is not None
            and depth_age <= float(self.get_parameter("maximum_depth_age").value)
        )

        target_output = None
        filter_result = None
        status = "waiting for YOLO target"
        if yolo_fresh:
            target = dict(self.latest_target)
            x, y, width, height = (float(value) for value in target["bbox"][:4])
            x1 = int(max(0, min(round(x), image_width - 1)))
            y1 = int(max(0, min(round(y), image_height - 1)))
            x2 = int(max(x1 + 1, min(round(x + width), image_width)))
            y2 = int(max(y1 + 1, min(round(y + height), image_height)))
            center_x = int(round((x1 + x2) * 0.5))
            center_y = int(round((y1 + y2) * 0.5))
            confidence = float(target.get("confidence", 0.0))
            label = str(target.get("label", target.get("class", "object")))

            target_output = {
                **target,
                "bbox": [x1, y1, x2 - x1, y2 - y1],
                "center_rgb": [center_x, center_y],
                "depth_m": None,
            }
            if depth_fresh:
                depth_height, depth_width = self.latest_depth.shape[:2]
                depth_x = int(round(center_x * (depth_width - 1) / max(1, image_width - 1)))
                depth_y = int(round(center_y * (depth_height - 1) / max(1, image_height - 1)))
                filter_result = measure_target_depth(
                    self.latest_depth,
                    self.latest_depth_encoding,
                    (depth_x, depth_y),
                    sample_radius=int(self.get_parameter("center_patch_radius").value),
                    depth_scale_16u=float(self.get_parameter("depth_scale_16u").value),
                    minimum_depth=float(self.get_parameter("minimum_depth").value),
                    maximum_depth=float(self.get_parameter("maximum_depth").value),
                    minimum_inlier_count=int(
                        self.get_parameter("minimum_inlier_count").value
                    ),
                    absolute_outlier_tolerance=float(
                        self.get_parameter("absolute_outlier_tolerance").value
                    ),
                    mad_scale=float(self.get_parameter("mad_scale").value),
                )
                target_output["center_depth"] = [depth_x, depth_y]
                target_output["depth_m"] = filter_result["depth_m"]
                sample_x, sample_y, sample_width, sample_height = filter_result[
                    "sample_roi_depth"
                ]
                sample_rgb_x1 = int(round(sample_x * image_width / depth_width))
                sample_rgb_y1 = int(round(sample_y * image_height / depth_height))
                sample_rgb_x2 = int(
                    round((sample_x + sample_width) * image_width / depth_width)
                )
                sample_rgb_y2 = int(
                    round((sample_y + sample_height) * image_height / depth_height)
                )
                cv2.rectangle(
                    debug,
                    (sample_rgb_x1, sample_rgb_y1),
                    (sample_rgb_x2, sample_rgb_y2),
                    (255, 255, 0),
                    2,
                )

            distance = target_output["depth_m"]
            if distance is not None:
                status = f"{label} {confidence:.2f} | center={distance:.3f} m"
                box_color = (0, 255, 0)
            elif depth_fresh:
                status = f"{label} {confidence:.2f} | no depth inliers"
                box_color = (0, 165, 255)
            else:
                status = f"{label} {confidence:.2f} | waiting aligned depth"
                box_color = (0, 165, 255)
            cv2.rectangle(debug, (x1, y1), (x2, y2), box_color, 3)
            cv2.drawMarker(
                debug,
                (center_x, center_y),
                (255, 255, 0),
                markerType=cv2.MARKER_CROSS,
                markerSize=20,
                thickness=2,
            )
            text_y = y1 - 8 if y1 >= 78 else min(image_height - 8, y2 + 24)
            cv2.putText(
                debug,
                status,
                (x1, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                box_color,
                2,
                cv2.LINE_AA,
            )

        cv2.rectangle(debug, (0, 0), (image_width, 64), (0, 0, 0), -1)
        cv2.putText(
            debug,
            "RGB + YOLO target center depth",
            (12, 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.68,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            debug,
            f"{status} | filter=range+median/MAD",
            (12, 54),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.56,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        detections = [target_output] if target_output is not None else []
        self.publish_result(
            self.latest_color_message,
            debug,
            {
                "task": "rgb_yolo_target_depth",
                "pipeline": "aligned_rgb_yolo_then_filtered_center_depth",
                "count": len(detections),
                "detections": detections,
                "target": target_output,
                "depth_filter": filter_result,
                "rgb_size": [image_width, image_height],
                "depth_size": (
                    [int(self.latest_depth.shape[1]), int(self.latest_depth.shape[0])]
                    if self.latest_depth is not None
                    else None
                ),
                "yolo_age_s": round(yolo_age, 3) if self.latest_yolo_received_at else None,
                "depth_age_s": round(depth_age, 3) if self.latest_depth_received_at else None,
            },
        )


def main(args=None) -> None:
    """启动 RGB+YOLO 目标中心测距节点。"""

    rclpy.init(args=args)
    node = DepthMeasurementNode()
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
