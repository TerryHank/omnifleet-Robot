#!/usr/bin/env python3
"""融合视觉深度和点云最近距离，输出统一风险状态。"""

import json

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import String

from vision_integration_core import (
    minimum_visual_distance,
    multimodal_risk,
    point_cloud_min_distance,
)


class MultimodalRiskNode(Node):
    """按最保守距离融合视觉与点云障碍信息。"""

    def __init__(self) -> None:
        super().__init__("multimodal_risk")
        visual_topic = self.declare_parameter("visual_topic", "/vision/targets_3d").value
        cloud_topic = self.declare_parameter("cloud_topic", "/livox/lidar").value
        output_topic = self.declare_parameter("output_topic", "/vision/risk").value
        self.input_timeout = float(self.declare_parameter("input_timeout", 0.5).value)
        self.stop_distance = float(self.declare_parameter("stop_distance", 0.6).value)
        self.danger_distance = float(self.declare_parameter("danger_distance", 1.0).value)
        self.caution_distance = float(
            self.declare_parameter("caution_distance", 2.0).value
        )
        self.min_height = float(self.declare_parameter("min_height", -1.0).value)
        self.max_height = float(self.declare_parameter("max_height", 1.5).value)
        publish_rate = float(self.declare_parameter("publish_rate", 10.0).value)
        if self.input_timeout <= 0.0 or publish_rate <= 0.0:
            raise ValueError("输入超时和发布频率必须大于零")
        self.visual_distance: float | None = None
        self.cloud_distance: float | None = None
        self.visual_time: float | None = None
        self.cloud_time: float | None = None
        self.publisher = self.create_publisher(String, output_topic, 10)
        self.visual_subscription = self.create_subscription(
            String, visual_topic, self.on_visual, 10
        )
        self.cloud_subscription = self.create_subscription(
            PointCloud2, cloud_topic, self.on_cloud, 10
        )
        self.timer = self.create_timer(1.0 / publish_rate, self.on_timer)

    def now_seconds(self) -> float:
        """返回节点时钟秒数。"""

        return self.get_clock().now().nanoseconds / 1.0e9

    def on_visual(self, message: String) -> None:
        """更新视觉目标最近距离。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError as error:
            self.get_logger().warning(f"忽略非法视觉 JSON：{error}")
            return
        self.visual_distance = minimum_visual_distance(payload)
        self.visual_time = self.now_seconds()

    def on_cloud(self, cloud: PointCloud2) -> None:
        """解析标准点云消息并更新前向最近距离。"""

        fields = {
            field.name: (int(field.offset), int(field.datatype)) for field in cloud.fields
        }
        self.cloud_distance = point_cloud_min_distance(
            cloud.data,
            cloud.width,
            cloud.height,
            cloud.point_step,
            cloud.row_step,
            fields,
            bool(cloud.is_bigendian),
            self.min_height,
            self.max_height,
            True,
        )
        self.cloud_time = self.now_seconds()

    def on_timer(self) -> None:
        """周期发布风险，过期输入按未知处理。"""

        now = self.now_seconds()
        visual = (
            self.visual_distance
            if self.visual_time is not None and now - self.visual_time <= self.input_timeout
            else None
        )
        cloud = (
            self.cloud_distance
            if self.cloud_time is not None and now - self.cloud_time <= self.input_timeout
            else None
        )
        risk = multimodal_risk(
            visual,
            cloud,
            self.stop_distance,
            self.danger_distance,
            self.caution_distance,
        )
        risk["stamp"] = now
        output = String()
        output.data = json.dumps(risk, ensure_ascii=False, separators=(",", ":"))
        self.publisher.publish(output)


def main(args=None) -> None:
    """启动多模态风险节点。"""

    rclpy.init(args=args)
    node = MultimodalRiskNode()
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
