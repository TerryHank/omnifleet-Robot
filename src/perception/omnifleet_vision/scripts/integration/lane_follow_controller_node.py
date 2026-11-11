#!/usr/bin/env python3
"""把车道中心误差转换为受超时和风险保护的视觉速度候选。"""

import json

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String

from course_controllers_core import lane_follow_command


class LaneFollowControllerNode(Node):
    """默认禁止运动，只允许向 `/cmd_vel_vision` 发布候选速度。"""

    def __init__(self) -> None:
        super().__init__("lane_follow_controller")
        lane_topic = self.declare_parameter("lane_topic", "/lane_detection/result").value
        risk_topic = self.declare_parameter("risk_topic", "/vision/risk").value
        event_topic = self.declare_parameter("event_topic", "/vision/events").value
        command_topic = self.declare_parameter("command_topic", "/cmd_vel_vision").value
        status_topic = self.declare_parameter("status_topic", "/vision/lane_follow/status").value
        if command_topic != "/cmd_vel_vision":
            raise ValueError("线路控制器只能发布 /cmd_vel_vision")
        self.enable_motion = bool(self.declare_parameter("enable_motion", False).value)
        self.timeout = float(self.declare_parameter("lane_timeout", 0.6).value)
        self.linear_speed = float(self.declare_parameter("linear_speed", 0.4).value)
        self.angular_gain = float(self.declare_parameter("angular_gain", 0.6).value)
        self.max_angular_speed = float(self.declare_parameter("max_angular_speed", 0.3).value)
        rate = float(self.declare_parameter("control_rate", 10.0).value)
        if min(self.timeout, rate, self.linear_speed, self.max_angular_speed) <= 0.0:
            raise ValueError("超时、频率和速度参数必须大于零")
        self.lane_payload = None
        self.risk_payload = None
        self.event_payload = None
        self.last_lane_time = None
        self.command_publisher = self.create_publisher(Twist, command_topic, 10)
        self.status_publisher = self.create_publisher(String, status_topic, 10)
        self.lane_subscription = self.create_subscription(String, lane_topic, self.on_lane, 10)
        self.risk_subscription = self.create_subscription(String, risk_topic, self.on_risk, 10)
        self.event_subscription = self.create_subscription(String, event_topic, self.on_event, 10)
        self.timer = self.create_timer(1.0 / rate, self.on_timer)

    def now_seconds(self) -> float:
        """返回 ROS 时钟秒数。"""

        return self.get_clock().now().nanoseconds / 1.0e9

    def on_lane(self, message: String) -> None:
        """缓存最近一帧线路结果。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            return
        if isinstance(payload, dict):
            self.lane_payload = payload
            self.last_lane_time = self.now_seconds()

    def on_risk(self, message: String) -> None:
        """缓存最近风险状态。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            return
        if isinstance(payload, dict):
            self.risk_payload = payload

    def on_event(self, message: String) -> None:
        """缓存交通事件；行人、红灯和停车标志会覆盖巡线通行。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            return
        if isinstance(payload, dict):
            self.event_payload = payload

    def on_timer(self) -> None:
        """定频发布候选速度和决策原因。"""

        now = self.now_seconds()
        linear, angular, reason = lane_follow_command(
            self.lane_payload,
            self.risk_payload,
            self.enable_motion,
            now,
            self.last_lane_time,
            self.timeout,
            self.linear_speed,
            self.angular_gain,
            self.max_angular_speed,
            self.event_payload,
        )
        command = Twist()
        command.linear.x = linear
        command.angular.z = angular
        self.command_publisher.publish(command)
        status = String()
        status.data = json.dumps(
            {"stamp": now, "linear_x": linear, "angular_z": angular, "reason": reason},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        self.status_publisher.publish(status)

    def destroy_node(self):
        """退出前发布零速。"""

        self.command_publisher.publish(Twist())
        return super().destroy_node()


def main(args=None) -> None:
    """启动线路控制器。"""

    rclpy.init(args=args)
    node = LaneFollowControllerNode()
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
