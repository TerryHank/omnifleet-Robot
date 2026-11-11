#!/usr/bin/env python3
"""为检测结果分配短时稳定的多目标编号。"""

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from vision_integration_core import IoUTracker, message_stamp


class DetectionTrackerNode(Node):
    """接收 JSON 检测数组并发布带编号的 JSON 目标数组。"""

    def __init__(self) -> None:
        super().__init__("detection_tracker")
        input_topic = self.declare_parameter("input_topic", "/vision/detections").value
        output_topic = self.declare_parameter("output_topic", "/vision/tracks").value
        iou_threshold = float(self.declare_parameter("iou_threshold", 0.3).value)
        self.timeout = float(self.declare_parameter("track_timeout", 1.0).value)
        self.tracker = IoUTracker(iou_threshold=iou_threshold, timeout=self.timeout)
        self.publisher = self.create_publisher(String, output_topic, 10)
        self.subscription = self.create_subscription(String, input_topic, self.on_detection, 10)
        self.last_input_time: float | None = None
        self.empty_published = False
        self.timer = self.create_timer(min(0.2, self.timeout * 0.5), self.on_timer)

    def now_seconds(self) -> float:
        """返回节点时钟秒数。"""

        return self.get_clock().now().nanoseconds / 1.0e9

    def publish_tracks(self, tracks: list[dict], source_stamp: float, status: str) -> None:
        """发布统一跟踪数据契约。"""

        result = {
            "stamp": self.now_seconds(),
            "source_stamp": source_stamp,
            "status": status,
            "tracks": tracks,
        }
        message = String()
        message.data = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        self.publisher.publish(message)

    def on_detection(self, message: String) -> None:
        """解析一帧检测结果并更新目标编号。"""

        now = self.now_seconds()
        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError as error:
            self.get_logger().warning(f"忽略非法检测 JSON：{error}")
            return
        tracks = self.tracker.update(payload, now)
        source_stamp = message_stamp(payload, now) if isinstance(payload, dict) else now
        self.last_input_time = now
        self.empty_published = False
        self.publish_tracks(tracks, source_stamp, "tracking")

    def on_timer(self) -> None:
        """输入超时后发布一次空结果，防止下游沿用旧目标。"""

        if self.last_input_time is None or self.empty_published:
            return
        now = self.now_seconds()
        if now - self.last_input_time <= self.timeout:
            return
        self.tracker.update([], now)
        self.publish_tracks([], now, "input_timeout")
        self.empty_published = True


def main(args=None) -> None:
    """启动多目标编号节点。"""

    rclpy.init(args=args)
    node = DetectionTrackerNode()
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
