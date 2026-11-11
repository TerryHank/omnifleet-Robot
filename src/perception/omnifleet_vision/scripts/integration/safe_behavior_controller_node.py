#!/usr/bin/env python3
"""把交通事件转换为受运动开关和超时保护的速度候选。"""

import json

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String

from vision_integration_core import safe_velocity_command


class SafeBehaviorControllerNode(Node):
    """只向视觉候选话题发布速度，绝不直接控制最终底盘话题。"""

    def __init__(self) -> None:
        super().__init__("safe_behavior_controller")
        event_topic = self.declare_parameter("event_topic", "/vision/events").value
        command_topic = self.declare_parameter("command_topic", "/cmd_vel_vision").value
        status_topic = self.declare_parameter(
            "status_topic", "/vision/safe_behavior/status"
        ).value
        if command_topic != "/cmd_vel_vision":
            raise ValueError("速度候选输出只能使用 /cmd_vel_vision")
        self.enable_motion = bool(self.declare_parameter("enable_motion", False).value)
        self.timeout = float(self.declare_parameter("event_timeout", 0.5).value)
        self.cruise_speed = float(self.declare_parameter("cruise_speed", 0.4).value)
        # 生产底盘会把非零线速度提升到 0.40 m/s，因此候选值不能伪装成 0.20。
        self.caution_speed = float(self.declare_parameter("caution_speed", 0.4).value)
        self.max_angular_speed = float(
            self.declare_parameter("max_angular_speed", 0.6).value
        )
        control_rate = float(self.declare_parameter("control_rate", 10.0).value)
        if self.timeout <= 0.0 or control_rate <= 0.0:
            raise ValueError("事件超时和控制频率必须大于零")
        if self.cruise_speed < 0.0 or self.caution_speed < 0.0 or self.max_angular_speed < 0.0:
            raise ValueError("速度参数不能为负数")
        self.latest_event: dict | None = None
        self.last_message_time: float | None = None
        self.command_publisher = self.create_publisher(Twist, command_topic, 10)
        self.status_publisher = self.create_publisher(String, status_topic, 10)
        self.subscription = self.create_subscription(String, event_topic, self.on_event, 10)
        self.timer = self.create_timer(1.0 / control_rate, self.on_timer)

    def now_seconds(self) -> float:
        """返回节点时钟秒数。"""

        return self.get_clock().now().nanoseconds / 1.0e9

    def on_event(self, message: String) -> None:
        """缓存最近一帧合法事件。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError as error:
            self.get_logger().warning(f"忽略非法事件 JSON：{error}")
            return
        if not isinstance(payload, dict):
            return
        self.latest_event = payload
        self.last_message_time = self.now_seconds()

    def on_timer(self) -> None:
        """固定频率发布速度候选，关闭或超时时持续发布零速。"""

        now = self.now_seconds()
        linear, angular, reason = safe_velocity_command(
            self.latest_event,
            self.enable_motion,
            now,
            self.last_message_time,
            self.timeout,
            self.cruise_speed,
            self.caution_speed,
            self.max_angular_speed,
        )
        command = Twist()
        command.linear.x = linear
        command.angular.z = angular
        self.command_publisher.publish(command)
        status = String()
        status.data = json.dumps(
            {
                "stamp": now,
                "enable_motion": self.enable_motion,
                "linear_x": linear,
                "angular_z": angular,
                "reason": reason,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        self.status_publisher.publish(status)

    def destroy_node(self):
        """退出前主动发布一次零速候选。"""

        self.command_publisher.publish(Twist())
        return super().destroy_node()


def main(args=None) -> None:
    """启动安全行为控制节点。"""

    rclpy.init(args=args)
    node = SafeBehaviorControllerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
