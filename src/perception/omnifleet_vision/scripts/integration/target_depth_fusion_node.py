#!/usr/bin/env python3
"""融合检测框与对齐深度图，输出目标近似三维位置。"""

import json

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

from vision_integration_core import depth_at_pixel, fuse_detections_with_depth


class TargetDepthFusionNode(Node):
    """使用标准图像消息和 JSON 检测结果完成轻量深度融合。"""

    def __init__(self) -> None:
        super().__init__("target_depth_fusion")
        detection_topic = self.declare_parameter("detection_topic", "/vision/tracks").value
        depth_topic = self.declare_parameter(
            "depth_topic", "/camera/depth/image_raw"
        ).value
        output_topic = self.declare_parameter("output_topic", "/vision/targets_3d").value
        # 默认内参和分辨率来自 OmniFleet 的 MV-DT01SNU 标定配置。
        self.fx = float(self.declare_parameter("fx", 1019.1704230044749).value)
        self.fy = float(self.declare_parameter("fy", 1044.3850797624254).value)
        self.cx = float(self.declare_parameter("cx", 767.5).value)
        self.cy = float(self.declare_parameter("cy", 639.5).value)
        self.color_width = float(self.declare_parameter("color_width", 1536.0).value)
        self.color_height = float(self.declare_parameter("color_height", 1280.0).value)
        self.sample_grid = int(self.declare_parameter("sample_grid", 5).value)
        self.min_depth = float(self.declare_parameter("min_depth", 0.1).value)
        self.max_depth = float(self.declare_parameter("max_depth", 3.5).value)
        self.scale_16u = float(self.declare_parameter("depth_scale_16u", 0.001).value)
        self.scale_32f = float(self.declare_parameter("depth_scale_32f", 1.0).value)
        self.detection_timeout = float(
            self.declare_parameter("detection_timeout", 2.0).value
        )
        if min(self.fx, self.fy, self.color_width, self.color_height, self.detection_timeout) <= 0.0:
            raise ValueError("相机内参、彩色尺寸和检测超时必须大于零")
        self.latest_payload: dict | list | None = None
        self.latest_detection_time: float | None = None
        self.publisher = self.create_publisher(String, output_topic, 10)
        self.detection_subscription = self.create_subscription(
            String, detection_topic, self.on_detection, 10
        )
        self.depth_subscription = self.create_subscription(Image, depth_topic, self.on_depth, 10)

    def now_seconds(self) -> float:
        """返回节点时钟秒数。"""

        return self.get_clock().now().nanoseconds / 1.0e9

    def on_detection(self, message: String) -> None:
        """缓存最近一帧检测结果。"""

        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError as error:
            self.get_logger().warning(f"忽略非法检测 JSON：{error}")
            return
        if not isinstance(payload, (dict, list)):
            self.get_logger().warning("检测 JSON 根节点必须是对象或数组")
            return
        self.latest_payload = payload
        self.latest_detection_time = self.now_seconds()

    def on_depth(self, image: Image) -> None:
        """收到深度图后计算每个目标的三维近似值。"""

        now = self.now_seconds()
        if self.latest_payload is None or self.latest_detection_time is None:
            return
        if now - self.latest_detection_time > self.detection_timeout:
            return

        def reader(x: int, y: int) -> float | None:
            # 检测框位于 1536x1280 彩色坐标系，深度图通常为 640x480，读取前必须缩放。
            depth_x = round(x * image.width / self.color_width)
            depth_y = round(y * image.height / self.color_height)
            return depth_at_pixel(
                image.data,
                image.width,
                image.height,
                image.step,
                image.encoding,
                bool(image.is_bigendian),
                depth_x,
                depth_y,
                self.scale_16u,
                self.scale_32f,
            )

        targets = fuse_detections_with_depth(
            self.latest_payload,
            reader,
            self.fx,
            self.fy,
            self.cx,
            self.cy,
            self.sample_grid,
            self.min_depth,
            self.max_depth,
        )
        result = {
            "stamp": now,
            "frame_id": image.header.frame_id,
            "depth_encoding": image.encoding,
            "detections": targets,
        }
        message = String()
        message.data = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        self.publisher.publish(message)


def main(args=None) -> None:
    """启动目标深度融合节点。"""

    rclpy.init(args=args)
    node = TargetDepthFusionNode()
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
