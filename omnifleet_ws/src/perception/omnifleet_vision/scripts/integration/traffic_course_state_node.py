#!/usr/bin/env python3
"""阶段项目交通状态机，确保行人停车优先于信号灯。"""

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from vision_integration_core import TrafficCourseStateMachine


class TrafficCourseStateNode(Node):
    """把防抖事件转换为便于教学观察的项目状态。"""

    def __init__(self) -> None:
        super().__init__("traffic_course_state")
        input_topic = self.declare_parameter("input_topic", "/vision/events").value
        output_topic = self.declare_parameter(
            "output_topic", "/vision/course_state"
        ).value
        self.input_timeout = float(self.declare_parameter("input_timeout", 0.8).value)
        if self.input_timeout <= 0.0:
            raise ValueError("输入超时时间必须大于零")
        self.machine = TrafficCourseStateMachine()
        self.publisher = self.create_publisher(String, output_topic, 10)
        self.subscription = self.create_subscription(String, input_topic, self.on_event, 10)
        self.last_input_time: float | None = None
        self.timeout_published = False
        self.timer = self.create_timer(min(0.2, self.input_timeout * 0.5), self.on_timer)

    def now_seconds(self) -> float:
        """返回节点时钟秒数。"""

        return self.get_clock().now().nanoseconds / 1.0e9

    def publish_state(self, result: dict) -> None:
        """发布统一阶段项目状态。"""

        result = dict(result)
        result["stamp"] = self.now_seconds()
        output = String()
        output.data = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        self.publisher.publish(output)

    def on_event(self, message: String) -> None:
        """根据活动事件推进状态机。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError as error:
            self.get_logger().warning(f"忽略非法事件 JSON：{error}")
            return
        if not isinstance(payload, dict):
            return
        self.last_input_time = self.now_seconds()
        self.timeout_published = False
        self.publish_state(self.machine.update(payload))

    def on_timer(self) -> None:
        """事件输入超时后回到等待状态，避免保留旧通行状态。"""

        if self.last_input_time is None or self.timeout_published:
            return
        if self.now_seconds() - self.last_input_time <= self.input_timeout:
            return
        result = self.machine.update({"active_events": []})
        result["reason"] = "input_timeout"
        self.publish_state(result)
        self.timeout_published = True


def main(args=None) -> None:
    """启动阶段项目交通状态机。"""

    rclpy.init(args=args)
    node = TrafficCourseStateNode()
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
