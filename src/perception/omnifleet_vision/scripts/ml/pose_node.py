#!/usr/bin/env python3
"""YOLOv8 Pose 人体关键点解析与 ROS2 发布节点。"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np

try:
    from .onnx_yolo_core import _restore_xyxy, non_max_suppression, normalize_output, preprocess_image
except ImportError:
    from onnx_yolo_core import _restore_xyxy, non_max_suppression, normalize_output, preprocess_image


# COCO 17 关键点骨架，仅用于教学调试图显示。
POSE_EDGES = (
    (5, 7), (7, 9), (6, 8), (8, 10),
    (5, 6), (5, 11), (6, 12), (11, 12),
    (11, 13), (13, 15), (12, 14), (14, 16),
    (0, 1), (0, 2), (1, 3), (2, 4),
)


def decode_pose_output(
    output: np.ndarray | Sequence[np.ndarray],
    original_shape: tuple[int, int],
    ratio: float,
    padding: tuple[float, float],
    confidence_threshold: float = 0.4,
    keypoint_threshold: float = 0.5,
    nms_threshold: float = 0.45,
) -> list[dict]:
    """解析 YOLOv8 Pose 的边界框、人体置信度和关键点。"""

    matrix = normalize_output(output)
    boxes: list[tuple[int, int, int, int]] = []
    scores: list[float] = []
    poses: list[list[dict]] = []
    height, width = original_shape
    pad_x, pad_y = padding
    for row in matrix:
        if row.size < 8 or (row.size - 5) % 3 != 0:
            continue
        score = float(row[4])
        if score < confidence_threshold:
            continue
        center_x, center_y, box_width, box_height = (float(item) for item in row[:4])
        box = _restore_xyxy(
            (
                center_x - box_width / 2.0,
                center_y - box_height / 2.0,
                center_x + box_width / 2.0,
                center_y + box_height / 2.0,
            ),
            ratio,
            padding,
            original_shape,
        )
        keypoints = []
        for x, y, visibility in row[5:].reshape(-1, 3):
            restored_x = max(0.0, min(float(width - 1), (float(x) - pad_x) / ratio))
            restored_y = max(0.0, min(float(height - 1), (float(y) - pad_y) / ratio))
            keypoints.append(
                {
                    "x": round(restored_x, 2),
                    "y": round(restored_y, 2),
                    "confidence": round(float(visibility), 6),
                    "visible": bool(float(visibility) >= keypoint_threshold),
                }
            )
        boxes.append(box)
        scores.append(score)
        poses.append(keypoints)

    kept = non_max_suppression(
        boxes,
        scores,
        [0] * len(boxes),
        confidence_threshold,
        nms_threshold,
    )
    results = []
    for index in kept:
        results.append(
            {
                "class_id": 0,
                "label": "person",
                "confidence": round(scores[index], 6),
                "bbox": list(boxes[index]),
                "keypoints": poses[index],
            }
        )
    return results


def draw_poses(image: np.ndarray, poses: Sequence[dict]) -> np.ndarray:
    """绘制人体框、可见关键点和骨架。"""

    debug = image.copy()
    for pose in poses:
        x1, y1, x2, y2 = (int(value) for value in pose["bbox"])
        cv2.rectangle(debug, (x1, y1), (x2, y2), (255, 160, 0), 2)
        points = pose["keypoints"]
        for first, second in POSE_EDGES:
            if first >= len(points) or second >= len(points):
                continue
            if points[first]["visible"] and points[second]["visible"]:
                start = (int(points[first]["x"]), int(points[first]["y"]))
                end = (int(points[second]["x"]), int(points[second]["y"]))
                cv2.line(debug, start, end, (0, 220, 220), 2)
        for point in points:
            if point["visible"]:
                cv2.circle(debug, (int(point["x"]), int(point["y"])), 3, (0, 0, 255), -1)
    return debug


class PoseEstimator:
    """OpenCV DNN 人体姿态推理器。"""

    def __init__(
        self,
        model_path: str,
        input_size: tuple[int, int] = (640, 640),
        confidence_threshold: float = 0.4,
        keypoint_threshold: float = 0.5,
        nms_threshold: float = 0.45,
    ) -> None:
        path = Path(model_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"找不到姿态模型：{path}")
        self.network = cv2.dnn.readNetFromONNX(str(path))
        self.input_size = input_size
        self.confidence_threshold = confidence_threshold
        self.keypoint_threshold = keypoint_threshold
        self.nms_threshold = nms_threshold

    def infer(self, image: np.ndarray) -> list[dict]:
        """对单帧图像执行人体关键点推理。"""

        blob, ratio, padding = preprocess_image(image, self.input_size)
        self.network.setInput(blob)
        names = self.network.getUnconnectedOutLayersNames()
        output = self.network.forward(names) if names else self.network.forward()
        return decode_pose_output(
            output,
            image.shape[:2],
            ratio,
            padding,
            self.confidence_threshold,
            self.keypoint_threshold,
            self.nms_threshold,
        )


def main(args=None) -> None:
    """启动人体姿态估计节点。"""

    import rclpy
    from cv_bridge import CvBridge
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image
    from std_msgs.msg import String

    class PoseNode(Node):
        """发布姿态 JSON 与调试图，不控制小车运动。"""

        def __init__(self) -> None:
            super().__init__("pose_estimation")
            model_path = str(self.declare_parameter("model_path", "").value)
            input_topic = str(self.declare_parameter("input", "/camera/color/image_raw").value)
            result_topic = str(self.declare_parameter("result", "/vision/pose").value)
            debug_topic = str(self.declare_parameter("debug", "/vision/pose/debug").value)
            width = int(self.declare_parameter("input_width", 640).value)
            height = int(self.declare_parameter("input_height", 640).value)
            confidence = float(self.declare_parameter("confidence", 0.4).value)
            keypoint_confidence = float(self.declare_parameter("keypoint_confidence", 0.5).value)
            nms = float(self.declare_parameter("nms", 0.45).value)
            self.estimator = PoseEstimator(
                model_path, (width, height), confidence, keypoint_confidence, nms
            )
            self.bridge = CvBridge()
            self.result_publisher = self.create_publisher(String, result_topic, 10)
            self.debug_publisher = self.create_publisher(Image, debug_topic, 10)
            self.subscription = self.create_subscription(
                Image, input_topic, self.on_image, qos_profile_sensor_data
            )

        def on_image(self, message: Image) -> None:
            """解析一帧人体姿态并发布结果。"""

            try:
                image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
                start = time.perf_counter()
                poses = self.estimator.infer(image)
                inference_ms = (time.perf_counter() - start) * 1000.0
                stamp = message.header.stamp.sec + message.header.stamp.nanosec / 1.0e9
                payload = {
                    "task": "pose",
                    "stamp": stamp,
                    "inference_ms": round(inference_ms, 3),
                    "count": len(poses),
                    "poses": poses,
                }
                result_message = String()
                result_message.data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
                self.result_publisher.publish(result_message)
                debug_message = self.bridge.cv2_to_imgmsg(draw_poses(image, poses), encoding="bgr8")
                debug_message.header = message.header
                self.debug_publisher.publish(debug_message)
            except Exception as error:
                self.get_logger().error(f"姿态估计失败：{error}")

    rclpy.init(args=args)
    node = PoseNode()
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

