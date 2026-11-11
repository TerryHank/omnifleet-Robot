#!/usr/bin/env python3
"""通用 ONNX YOLO 目标检测 ROS2 节点。"""

from __future__ import annotations

import json
import time

try:
    from .onnx_yolo_core import OnnxYoloDetector, draw_detections
except ImportError:
    from onnx_yolo_core import OnnxYoloDetector, draw_detections


def make_result(task: str, detections: list[dict], inference_ms: float, stamp: float) -> dict:
    """构造下游联调节点可直接读取的统一 JSON 数据。"""

    return {
        "task": task,
        "stamp": float(stamp),
        "inference_ms": round(float(inference_ms), 3),
        "count": len(detections),
        "detections": detections,
    }


def _parse_class_ids(value: str) -> list[int] | None:
    """把逗号分隔类别编号转换为整数列表，空字符串表示不过滤。"""

    values = [item.strip() for item in value.split(",") if item.strip()]
    return [int(item) for item in values] if values else None


def main(args=None) -> None:
    """启动通用 ONNX 检测节点。"""

    import rclpy
    from cv_bridge import CvBridge
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image
    from std_msgs.msg import String

    class OnnxDetectorNode(Node):
        """订阅图像并发布检测 JSON 和调试图，不发布任何运动指令。"""

        def __init__(self) -> None:
            super().__init__("onnx_detector")
            model_path = str(self.declare_parameter("model_path", "").value)
            labels = str(self.declare_parameter("labels", "").value)
            self.task = str(self.declare_parameter("task", "object_detection").value)
            input_topic = str(self.declare_parameter("input", "/camera/color/image_raw").value)
            result_topic = str(self.declare_parameter("result", "/vision/detections").value)
            debug_topic = str(self.declare_parameter("debug", "/vision/detections/debug").value)
            input_width = int(self.declare_parameter("input_width", 640).value)
            input_height = int(self.declare_parameter("input_height", 640).value)
            confidence = float(self.declare_parameter("confidence", 0.4).value)
            nms = float(self.declare_parameter("nms", 0.45).value)
            class_ids = _parse_class_ids(str(self.declare_parameter("class_ids", "").value))
            self.detector = OnnxYoloDetector(
                model_path,
                labels,
                (input_width, input_height),
                confidence,
                nms,
                class_ids,
            )
            self.bridge = CvBridge()
            self.result_publisher = self.create_publisher(String, result_topic, 10)
            self.debug_publisher = self.create_publisher(Image, debug_topic, 10)
            self.subscription = self.create_subscription(
                Image, input_topic, self.on_image, qos_profile_sensor_data
            )
            self.get_logger().info(f"ONNX 检测已启动：任务={self.task}，输入={input_topic}")

        def on_image(self, message: Image) -> None:
            """推理一帧图像并发布结构化结果和可视化图像。"""

            try:
                image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
                start = time.perf_counter()
                detections = self.detector.detect(image)
                inference_ms = (time.perf_counter() - start) * 1000.0
                stamp = message.header.stamp.sec + message.header.stamp.nanosec / 1.0e9
                payload = make_result(self.task, detections, inference_ms, stamp)
                result_message = String()
                result_message.data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
                self.result_publisher.publish(result_message)
                debug_message = self.bridge.cv2_to_imgmsg(
                    draw_detections(image, detections), encoding="bgr8"
                )
                debug_message.header = message.header
                self.debug_publisher.publish(debug_message)
            except Exception as error:
                self.get_logger().error(f"ONNX 检测失败：{error}")

    rclpy.init(args=args)
    node = OnnxDetectorNode()
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
