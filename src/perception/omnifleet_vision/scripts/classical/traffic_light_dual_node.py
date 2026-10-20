#!/usr/bin/env python3
"""先用 YOLO 定位灯体，再在框内使用 OpenCV HSV 判定灯色。"""

from __future__ import annotations

import json
import time

import cv2
import rclpy
from std_msgs.msg import String

try:
    from .algorithms import detect_traffic_light_colors_in_yolo_rois
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import detect_traffic_light_colors_in_yolo_rois
    from ros_support import ClassicalVisionNode


class TrafficLightDualNode(ClassicalVisionNode):
    """在同一调试图展示 YOLO ROI 到 HSV 判色的串联结果。"""

    def __init__(self) -> None:
        super().__init__("traffic_light_dual", "/camera/color/image_raw")
        self.declare_parameter("yolo_topic", "/vision/traffic_light/yolo")
        self.declare_parameter("minimum_area", 9.0)
        self.declare_parameter("maximum_area_ratio", 0.35)
        self.declare_parameter("minimum_circularity", 0.35)
        self.declare_parameter("minimum_color_confidence", 0.60)
        self.declare_parameter("minimum_mean_value", 100.0)
        self.declare_parameter("maximum_yolo_age", 1.5)
        self.declare_parameter("maximum_processing_rate", 10.0)
        self.latest_yolo_detections = []
        self.latest_yolo_received_at = 0.0
        self.last_processed = 0.0
        self.yolo_subscription = self.create_subscription(
            String,
            str(self.get_parameter("yolo_topic").value),
            self.yolo_callback,
            10,
        )

    def yolo_callback(self, message: String) -> None:
        """保存 YOLO 支线的最新灯体框。"""

        try:
            payload = json.loads(message.data)
            detections = payload.get("detections", [])
            self.latest_yolo_detections = [
                item for item in detections if item.get("class") == "traffic light"
            ]
            self.latest_yolo_received_at = time.monotonic()
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            self.get_logger().warning(f"忽略无效 YOLO 结果：{error}")

    def image_callback(self, message) -> None:
        """读取最新 YOLO 框，只在框内运行 HSV 并绘制串联结果。"""

        now = time.monotonic()
        maximum_rate = max(0.1, float(self.get_parameter("maximum_processing_rate").value))
        if now - self.last_processed < 1.0 / maximum_rate:
            return
        self.last_processed = now

        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            maximum_age = float(self.get_parameter("maximum_yolo_age").value)
            if now - self.latest_yolo_received_at <= maximum_age:
                yolo_detections = list(self.latest_yolo_detections)
            else:
                yolo_detections = []
            debug, opencv_result = detect_traffic_light_colors_in_yolo_rois(
                image,
                yolo_detections,
                minimum_area=float(self.get_parameter("minimum_area").value),
                maximum_area_ratio=float(self.get_parameter("maximum_area_ratio").value),
                minimum_circularity=float(self.get_parameter("minimum_circularity").value),
                minimum_confidence=float(
                    self.get_parameter("minimum_color_confidence").value
                ),
                minimum_mean_value=float(self.get_parameter("minimum_mean_value").value),
            )

            for detection in yolo_detections:
                x, y, width, height = (
                    int(round(float(value))) for value in detection["bbox"]
                )
                confidence = float(detection.get("confidence", 0.0))
                cv2.rectangle(debug, (x, y), (x + width, y + height), (255, 0, 255), 3)
                cv2.putText(
                    debug,
                    f"Stage 1 YOLO ROI: traffic light {confidence:.2f}",
                    (x, max(22, y - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.62,
                    (255, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

            counts = opencv_result["counts"]
            cv2.rectangle(debug, (0, 0), (debug.shape[1], 72), (0, 0, 0), -1)
            cv2.putText(
                debug,
                f"Stage 1 YOLO: traffic light ROIs = {len(yolo_detections)}",
                (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.72,
                (255, 0, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                debug,
                "Stage 2 ROI OpenCV HSV: "
                f"RED={counts['red']} YELLOW={counts['yellow']} GREEN={counts['green']}",
                (12, 59),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.68,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

            opencv_detections = list(opencv_result["detections"])
            if counts["red"]:
                fused_state = "red"
            elif counts["yellow"]:
                fused_state = "yellow"
            elif counts["green"]:
                fused_state = "green"
            else:
                fused_state = "unknown"
            if yolo_detections and opencv_detections:
                fusion_status = "cascade_confirmed"
            elif yolo_detections:
                fusion_status = "yolo_no_color"
            else:
                fusion_status = "no_yolo_roi"

            self.publish_result(
                message,
                debug,
                {
                    "task": "traffic_light_cascade",
                    "pipeline": "yolo_roi_then_opencv_hsv",
                    "count": len(opencv_detections),
                    "detections": opencv_detections,
                    "fused_state": fused_state,
                    "fusion_status": fusion_status,
                    "branches": {
                        "yolo": {
                            "count": len(yolo_detections),
                            "detections": yolo_detections,
                        },
                        "opencv": opencv_result,
                    },
                },
            )
        except Exception as error:
            self.get_logger().error(f"红绿灯串联处理失败：{error}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TrafficLightDualNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception:
        if rclpy.ok():
            raise
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == "__main__":
    main()
