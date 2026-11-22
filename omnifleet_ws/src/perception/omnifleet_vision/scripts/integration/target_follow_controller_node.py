#!/usr/bin/env python3
"""根据带深度的目标结果生成安全跟随候选速度。"""

import json

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String

from course_controllers_core import target_follow_command


class TargetFollowControllerNode(Node):
    """支持颜色、行人或通用物体目标，默认禁止运动。"""

    def __init__(self) -> None:
        super().__init__("target_follow_controller")
        target_topic = self.declare_parameter("target_topic", "/vision/targets_3d").value
        command_topic = self.declare_parameter("command_topic", "/cmd_vel_vision").value
        status_topic = self.declare_parameter("status_topic", "/vision/target_follow/status").value
        if command_topic != "/cmd_vel_vision":
            raise ValueError("目标跟随只能发布 /cmd_vel_vision")
        self.enable_motion = bool(self.declare_parameter("enable_motion", False).value)
        self.timeout = float(self.declare_parameter("target_timeout", 0.8).value)
        self.image_width = float(self.declare_parameter("image_width", 1536.0).value)
        self.target_distance = float(self.declare_parameter("target_distance", 0.8).value)
        self.distance_deadband = float(self.declare_parameter("distance_deadband", 0.15).value)
        self.linear_speed = float(self.declare_parameter("linear_speed", 0.4).value)
        self.angular_gain = float(self.declare_parameter("angular_gain", 0.6).value)
        self.max_angular_speed = float(self.declare_parameter("max_angular_speed", 0.3).value)
        self.class_filter = str(self.declare_parameter("class_filter", "").value)
        rate = float(self.declare_parameter("control_rate", 10.0).value)
        if min(self.timeout, self.image_width, self.target_distance, self.distance_deadband, rate) <= 0.0:
            raise ValueError("目标跟随的距离、超时和频率参数必须大于零")
        if self.linear_speed < 0.0 or self.max_angular_speed < 0.0:
            raise ValueError("速度参数不能为负数")
        self.payload = None
        self.last_target_time = None
        self.command_publisher = self.create_publisher(Twist, command_topic, 10)
        self.status_publisher = self.create_publisher(String, status_topic, 10)
        self.subscription = self.create_subscription(String, target_topic, self.on_target, 10)
        self.timer = self.create_timer(1.0 / rate, self.on_timer)

    def now_seconds(self) -> float:
        """返回 ROS 时钟秒数。"""

        return self.get_clock().now().nanoseconds / 1.0e9

    def on_target(self, message: String) -> None:
        """缓存最近的三维目标。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            return
        if isinstance(payload, dict):
            self.payload = payload
            self.last_target_time = self.now_seconds()

    def on_timer(self) -> None:
        """定频发布跟随候选和状态。"""

        now = self.now_seconds()
        linear, angular, reason = target_follow_command(
            self.payload,
            self.enable_motion,
            now,
            self.last_target_time,
            self.timeout,
            self.image_width,
            self.target_distance,
            self.distance_deadband,
            self.linear_speed,
            self.angular_gain,
            self.max_angular_speed,
            self.class_filter,
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
    """启动目标跟随控制器。"""

    rclpy.init(args=args)
    node = TargetFollowControllerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
