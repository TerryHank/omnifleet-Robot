#!/usr/bin/env python3
"""统计视觉推理耗时和结果发布频率的 ROS2 节点。"""

from __future__ import annotations

import json
import math
from collections import deque

import numpy as np


class InferenceStatistics:
    """维护固定窗口内的推理耗时和消息到达时间。"""

    def __init__(self, window_size: int = 60) -> None:
        if window_size < 2:
            raise ValueError("统计窗口至少需要 2 个样本")
        self.durations_ms: deque[float] = deque(maxlen=int(window_size))
        self.arrival_times: deque[float] = deque(maxlen=int(window_size))
        self.invalid_count = 0

    def update(self, inference_ms: float, arrival_time: float) -> None:
        """加入一个有效样本；非法或负耗时只计入异常数量。"""

        if not math.isfinite(inference_ms) or inference_ms < 0.0:
            self.invalid_count += 1
            return
        self.durations_ms.append(float(inference_ms))
        self.arrival_times.append(float(arrival_time))

    def snapshot(self) -> dict:
        """生成平均值、P95、最大值和实际到达频率。"""

        durations = np.asarray(self.durations_ms, dtype=np.float64)
        frequency = 0.0
        if len(self.arrival_times) >= 2:
            elapsed = self.arrival_times[-1] - self.arrival_times[0]
            if elapsed > 0.0:
                frequency = (len(self.arrival_times) - 1) / elapsed
        return {
            "sample_count": int(durations.size),
            "invalid_count": self.invalid_count,
            "frequency_hz": round(float(frequency), 3),
            "inference_mean_ms": round(float(np.mean(durations)), 3) if durations.size else None,
            "inference_p95_ms": round(float(np.percentile(durations, 95)), 3) if durations.size else None,
            "inference_max_ms": round(float(np.max(durations)), 3) if durations.size else None,
        }


def extract_inference_ms(payload: object) -> float | None:
    """从统一视觉 JSON 中提取推理耗时。"""

    if not isinstance(payload, dict) or "inference_ms" not in payload:
        return None
    try:
        value = float(payload["inference_ms"])
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def main(args=None) -> None:
    """启动推理状态统计节点。"""

    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String

    class InferenceStatusNode(Node):
        """订阅推理 JSON 并周期发布性能统计。"""

        def __init__(self) -> None:
            super().__init__("inference_status")
            input_topic = str(self.declare_parameter("input", "/vision/detections").value)
            result_topic = str(self.declare_parameter("result", "/vision/inference_status").value)
            window_size = int(self.declare_parameter("window_size", 60).value)
            publish_period = float(self.declare_parameter("publish_period", 1.0).value)
            self.statistics = InferenceStatistics(window_size)
            self.publisher = self.create_publisher(String, result_topic, 10)
            self.subscription = self.create_subscription(String, input_topic, self.on_result, 10)
            self.timer = self.create_timer(publish_period, self.publish_status)

        def on_result(self, message: String) -> None:
            """读取一条推理结果并加入统计窗口。"""

            try:
                payload = json.loads(message.data)
            except json.JSONDecodeError:
                self.statistics.invalid_count += 1
                return
            inference_ms = extract_inference_ms(payload)
            if inference_ms is None:
                self.statistics.invalid_count += 1
                return
            arrival_time = self.get_clock().now().nanoseconds / 1.0e9
            self.statistics.update(inference_ms, arrival_time)

        def publish_status(self) -> None:
            """发布当前滑动窗口统计。"""

            message = String()
            message.data = json.dumps(
                self.statistics.snapshot(), ensure_ascii=False, separators=(",", ":")
            )
            self.publisher.publish(message)

    rclpy.init(args=args)
    node = InferenceStatusNode()
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
