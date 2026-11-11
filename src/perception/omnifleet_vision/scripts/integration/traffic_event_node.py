#!/usr/bin/env python3
"""把目标检测结果转换为防抖后的交通课程事件。"""

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from vision_integration_core import EventDebouncer


class TrafficEventNode(Node):
    """统一行人、信号灯、路标和车辆事件的优先级。"""

    def __init__(self) -> None:
        super().__init__("traffic_event")
        input_topic = self.declare_parameter("input_topic", "/vision/targets_3d").value
        output_topic = self.declare_parameter("output_topic", "/vision/events").value
        activate_frames = int(self.declare_parameter("activate_frames", 3).value)
        release_frames = int(self.declare_parameter("release_frames", 2).value)
        self.min_confidence = float(self.declare_parameter("min_confidence", 0.4).value)
        self.debouncer = EventDebouncer(activate_frames, release_frames)
        self.publisher = self.create_publisher(String, output_topic, 10)
        self.subscription = self.create_subscription(String, input_topic, self.on_targets, 10)

    def on_targets(self, message: String) -> None:
        """对目标类别做事件映射、防抖和优先级排序。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError as error:
            self.get_logger().warning(f"忽略非法目标 JSON：{error}")
            return
        if isinstance(payload, dict):
            raw_detections = payload.get("detections", payload.get("tracks", []))
            stamp = payload.get(
                "stamp", self.get_clock().now().nanoseconds / 1.0e9
            )
        elif isinstance(payload, list):
            raw_detections = payload
            stamp = self.get_clock().now().nanoseconds / 1.0e9
        else:
            return
        if not isinstance(raw_detections, list):
            raw_detections = []
        filtered = []
        for detection in raw_detections:
            if not isinstance(detection, dict):
                continue
            try:
                confidence = float(detection.get("confidence", detection.get("score", 1.0)))
            except (TypeError, ValueError):
                continue
            if confidence >= self.min_confidence:
                filtered.append(detection)
        events = self.debouncer.update(filtered)
        result = {
            "stamp": stamp,
            "active_events": events,
            "primary_event": events[0] if events else None,
        }
        output = String()
        output.data = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        self.publisher.publish(output)


def main(args=None) -> None:
    """启动交通事件节点。"""

    rclpy.init(args=args)
    node = TrafficEventNode()
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
