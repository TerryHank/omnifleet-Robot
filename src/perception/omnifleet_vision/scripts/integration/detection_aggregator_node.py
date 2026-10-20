#!/usr/bin/env python3
"""合并多个检测器的最近结果，避免不同模型轮流覆盖同一话题。"""

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class DetectionAggregatorNode(Node):
    """在输入超时窗口内合并 COCO 与红绿灯检测结果。"""

    def __init__(self) -> None:
        super().__init__("detection_aggregator")
        input_topics = list(
            self.declare_parameter(
                "input_topics", ["/vision/detections/coco", "/vision/detections/traffic_light"]
            ).value
        )
        output_topic = str(self.declare_parameter("output_topic", "/vision/detections").value)
        self.timeout = float(self.declare_parameter("input_timeout", 1.5).value)
        rate = float(self.declare_parameter("publish_rate", 5.0).value)
        if not input_topics or self.timeout <= 0.0 or rate <= 0.0:
            raise ValueError("输入话题、超时和发布频率必须有效")
        self.latest = {}
        self.publisher = self.create_publisher(String, output_topic, 10)
        self.input_subscriptions = [
            self.create_subscription(
                String,
                topic,
                lambda message, source=topic: self.on_detection(source, message),
                10,
            )
            for topic in input_topics
        ]
        self.timer = self.create_timer(1.0 / rate, self.on_timer)

    def now_seconds(self) -> float:
        """返回 ROS 时钟秒数。"""

        return self.get_clock().now().nanoseconds / 1.0e9

    def on_detection(self, source: str, message: String) -> None:
        """缓存一个来源的最近检测。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            return
        if isinstance(payload, dict):
            self.latest[source] = (self.now_seconds(), payload)

    def on_timer(self) -> None:
        """合并仍在有效期内的检测并发布。"""

        now = self.now_seconds()
        detections = []
        sources = []
        for source, (stamp, payload) in self.latest.items():
            if now - stamp > self.timeout:
                continue
            values = payload.get("detections", [])
            if not isinstance(values, list):
                continue
            for detection in values:
                if isinstance(detection, dict):
                    item = dict(detection)
                    item["source"] = source
                    detections.append(item)
            sources.append(source)
        output = String()
        output.data = json.dumps(
            {"stamp": now, "sources": sources, "detections": detections},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        self.publisher.publish(output)


def main(args=None) -> None:
    """启动检测结果合并节点。"""

    rclpy.init(args=args)
    node = DetectionAggregatorNode()
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
