#!/usr/bin/env python3
"""基于 OpenCV Haar 特征的人脸检测 ROS2 节点。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np


def load_face_cascade(cascade_path: str = "") -> cv2.CascadeClassifier:
    """加载指定 Haar 分类器，空路径使用 OpenCV 自带的人脸分类器。"""

    path = Path(cascade_path).expanduser() if cascade_path else Path(
        cv2.data.haarcascades
    ) / "haarcascade_frontalface_default.xml"
    classifier = cv2.CascadeClassifier(str(path))
    if classifier.empty():
        raise FileNotFoundError(f"无法加载人脸分类器：{path}")
    return classifier


def detect_faces(
    image: np.ndarray,
    classifier: cv2.CascadeClassifier,
    scale_factor: float = 1.1,
    min_neighbors: int = 5,
    min_size: int = 30,
) -> list[dict]:
    """检测正面人脸并返回统一边界框格式。"""

    if image is None or image.size == 0:
        raise ValueError("输入图像不能为空")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    boxes = classifier.detectMultiScale(
        gray,
        scaleFactor=float(scale_factor),
        minNeighbors=int(min_neighbors),
        minSize=(int(min_size), int(min_size)),
    )
    return [
        {
            "class_id": 0,
            "label": "face",
            "confidence": None,
            "bbox": [int(x), int(y), int(x + width), int(y + height)],
        }
        for x, y, width, height in boxes
    ]


def draw_faces(image: np.ndarray, detections: Sequence[dict]) -> np.ndarray:
    """绘制人脸边界框和类别标签。"""

    debug = image.copy()
    for item in detections:
        x1, y1, x2, y2 = item["bbox"]
        cv2.rectangle(debug, (x1, y1), (x2, y2), (255, 180, 0), 2)
        cv2.putText(
            debug, "face", (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (255, 180, 0), 2, cv2.LINE_AA,
        )
    return debug


def main(args=None) -> None:
    """启动人脸检测节点。"""

    import rclpy
    from cv_bridge import CvBridge
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image
    from std_msgs.msg import String

    class FaceDetectionNode(Node):
        """订阅彩色图像并发布人脸检测结果。"""

        def __init__(self) -> None:
            super().__init__("face_detection")
            input_topic = str(self.declare_parameter("input", "/camera/color/image_raw").value)
            result_topic = str(self.declare_parameter("result", "/vision/faces").value)
            debug_topic = str(self.declare_parameter("debug", "/vision/faces/debug").value)
            cascade_path = str(self.declare_parameter("cascade_path", "").value)
            self.scale_factor = float(self.declare_parameter("scale_factor", 1.1).value)
            self.min_neighbors = int(self.declare_parameter("min_neighbors", 5).value)
            self.min_size = int(self.declare_parameter("min_size", 30).value)
            self.classifier = load_face_cascade(cascade_path)
            self.bridge = CvBridge()
            self.result_publisher = self.create_publisher(String, result_topic, 10)
            self.debug_publisher = self.create_publisher(Image, debug_topic, 10)
            self.subscription = self.create_subscription(
                Image, input_topic, self.on_image, qos_profile_sensor_data
            )

        def on_image(self, message: Image) -> None:
            """检测一帧图像中的人脸并发布结果。"""

            try:
                image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
                detections = detect_faces(
                    image, self.classifier, self.scale_factor, self.min_neighbors, self.min_size
                )
                stamp = message.header.stamp.sec + message.header.stamp.nanosec / 1.0e9
                payload = {
                    "task": "face_detection",
                    "stamp": stamp,
                    "count": len(detections),
                    "detections": detections,
                }
                result_message = String()
                result_message.data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
                self.result_publisher.publish(result_message)
                debug_message = self.bridge.cv2_to_imgmsg(
                    draw_faces(image, detections), encoding="bgr8"
                )
                debug_message.header = message.header
                self.debug_publisher.publish(debug_message)
            except Exception as error:
                self.get_logger().error(f"人脸检测失败：{error}")

    rclpy.init(args=args)
    node = FaceDetectionNode()
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
