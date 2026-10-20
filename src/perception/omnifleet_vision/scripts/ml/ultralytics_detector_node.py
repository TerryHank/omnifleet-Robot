#!/usr/bin/env python3
"""Jetson 上使用完整 PyTorch CUDA 的 Ultralytics 检测与姿态节点。"""

from __future__ import annotations

import json
import time
from typing import Any


def parse_class_ids(value: str) -> list[int] | None:
    """把逗号分隔的类别编号转换为整数列表。"""

    values = [item.strip() for item in value.split(",") if item.strip()]
    return [int(item) for item in values] if values else None


def box_to_detection(xyxy, confidence: float, class_id: int, label: str) -> dict[str, Any]:
    """把左上右下框转换为课程统一的左上宽高框。"""

    x1, y1, x2, y2 = (float(value) for value in xyxy)
    return {
        "class_id": int(class_id),
        "class": str(label),
        "label": str(label),
        "confidence": round(float(confidence), 6),
        "bbox": [round(x1, 2), round(y1, 2), round(max(0.0, x2 - x1), 2), round(max(0.0, y2 - y1), 2)],
    }


def main(args=None) -> None:
    """启动 PyTorch CUDA 检测节点。"""

    import rclpy
    import torch
    from cv_bridge import CvBridge
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image
    from std_msgs.msg import String
    from ultralytics import YOLO

    class UltralyticsDetectorNode(Node):
        """统一执行目标检测或人体姿态，输出 JSON 与无品牌调试图。"""

        def __init__(self) -> None:
            super().__init__("ultralytics_detector")
            model_path = str(self.declare_parameter("model_path", "").value)
            self.task = str(self.declare_parameter("task", "object_detection").value)
            input_topic = str(self.declare_parameter("input", "/camera/color/image_raw").value)
            result_topic = str(self.declare_parameter("result", "/vision/detections").value)
            debug_topic = str(self.declare_parameter("debug", "/vision/detections/debug").value)
            self.image_size = int(self.declare_parameter("image_size", 640).value)
            self.confidence = float(self.declare_parameter("confidence", 0.4).value)
            self.class_ids = parse_class_ids(str(self.declare_parameter("class_ids", "").value))
            requested_device = str(self.declare_parameter("device", "0").value)
            if requested_device != "cpu" and not torch.cuda.is_available():
                raise RuntimeError("请求 CUDA 推理，但当前 PyTorch CUDA 不可用")
            self.device = requested_device
            self.model = YOLO(model_path)
            self.bridge = CvBridge()
            self.result_publisher = self.create_publisher(String, result_topic, 10)
            self.debug_publisher = self.create_publisher(Image, debug_topic, 10)
            self.subscription = self.create_subscription(
                Image, input_topic, self.on_image, qos_profile_sensor_data
            )
            self.get_logger().info(
                f"PyTorch 视觉节点已启动：任务={self.task}，设备={self.device}，模型={model_path}"
            )

        def on_image(self, message: Image) -> None:
            """在 GPU 上处理一帧并发布统一检测或姿态结果。"""

            try:
                image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
                started = time.perf_counter()
                result = self.model.predict(
                    image, device=self.device, imgsz=self.image_size,
                    conf=self.confidence, classes=self.class_ids, verbose=False,
                )[0]
                inference_ms = (time.perf_counter() - started) * 1000.0
                detections = []
                boxes = result.boxes
                if boxes is not None:
                    names = result.names
                    xyxy_values = boxes.xyxy.detach().cpu().numpy()
                    confidence_values = boxes.conf.detach().cpu().numpy()
                    class_values = boxes.cls.detach().cpu().numpy().astype(int)
                    for index, (xyxy, confidence, class_id) in enumerate(
                        zip(xyxy_values, confidence_values, class_values)
                    ):
                        detection = box_to_detection(xyxy, confidence, class_id, names[class_id])
                        if result.keypoints is not None:
                            xy = result.keypoints.xy[index].detach().cpu().numpy()
                            confidence_points = result.keypoints.conf[index].detach().cpu().numpy()
                            detection["keypoints"] = [
                                {"x": round(float(point[0]), 2), "y": round(float(point[1]), 2),
                                 "confidence": round(float(score), 6)}
                                for point, score in zip(xy, confidence_points)
                            ]
                        detections.append(detection)
                stamp = message.header.stamp.sec + message.header.stamp.nanosec / 1.0e9
                output = String()
                output.data = json.dumps(
                    {"task": self.task, "stamp": stamp, "inference_ms": round(inference_ms, 3),
                     "backend": "pytorch_cuda" if self.device != "cpu" else "pytorch_cpu",
                     "count": len(detections), "detections": detections},
                    ensure_ascii=False, separators=(",", ":"),
                )
                self.result_publisher.publish(output)
                debug_message = self.bridge.cv2_to_imgmsg(result.plot(labels=True, conf=True), encoding="bgr8")
                debug_message.header = message.header
                self.debug_publisher.publish(debug_message)
            except Exception as error:
                self.get_logger().error(f"PyTorch CUDA 推理失败：{error}")

    rclpy.init(args=args)
    node = UltralyticsDetectorNode()
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
