#!/usr/bin/env python3
"""把目标像素和深度转换为导航候选位姿，不发送导航动作。"""

import json
import math

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from std_msgs.msg import String

from vision_integration_core import navigation_candidate


class VisionNavTargetNode(Node):
    """发布供上层审核或转换的位姿候选。"""

    def __init__(self) -> None:
        super().__init__("vision_nav_target")
        input_topic = self.declare_parameter("input_topic", "/vision/nav_target").value
        output_topic = self.declare_parameter(
            "output_topic", "/vision_nav_target_candidate"
        ).value
        if output_topic in {"/goal_pose", "goal_pose"}:
            raise ValueError("本节点只能发布候选位姿，不能直接发布导航目标")
        self.frame_id = self.declare_parameter("frame_id", "base_link").value
        self.fx = float(self.declare_parameter("fx", 1019.1704230044749).value)
        self.cx = float(self.declare_parameter("cx", 767.5).value)
        self.min_depth = float(self.declare_parameter("min_depth", 0.2).value)
        self.max_depth = float(self.declare_parameter("max_depth", 3.5).value)
        self.publisher = self.create_publisher(PoseStamped, output_topic, 10)
        self.subscription = self.create_subscription(String, input_topic, self.on_target, 10)

    @staticmethod
    def select_target(payload: object) -> dict | None:
        """从根对象、指定目标或目标数组中选择一条候选。"""

        if not isinstance(payload, dict):
            return None
        if isinstance(payload.get("target"), dict):
            return payload["target"]
        detections = payload.get("detections", payload.get("tracks"))
        if isinstance(detections, list):
            valid = [item for item in detections if isinstance(item, dict)]
            if not valid:
                return None
            return max(valid, key=lambda item: float(item.get("confidence", 0.0)))
        return payload

    def on_target(self, message: String) -> None:
        """解析目标并发布近似平面位姿。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError as error:
            self.get_logger().warning(f"忽略非法目标 JSON：{error}")
            return
        target = self.select_target(payload)
        if target is None:
            return
        if "pixel_x" not in target and "u" not in target:
            center = target.get("pixel_center")
            if isinstance(center, list) and center:
                target = dict(target)
                target["pixel_x"] = center[0]
        candidate = navigation_candidate(
            target, self.fx, self.cx, self.min_depth, self.max_depth
        )
        if candidate is None:
            return
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = str(payload.get("frame_id", self.frame_id))
        pose.pose.position.x = candidate["x"]
        pose.pose.position.y = candidate["y"]
        half_yaw = candidate["yaw"] * 0.5
        pose.pose.orientation.z = math.sin(half_yaw)
        pose.pose.orientation.w = math.cos(half_yaw)
        self.publisher.publish(pose)


def main(args=None) -> None:
    """启动视觉导航候选节点。"""

    rclpy.init(args=args)
    node = VisionNavTargetNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
