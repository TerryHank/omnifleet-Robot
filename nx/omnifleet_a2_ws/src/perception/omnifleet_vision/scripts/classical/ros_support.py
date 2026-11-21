"""经典视觉 ROS2 节点共用的发布与参数逻辑。"""

import json
import os
from typing import Dict

import cv2
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


class ClassicalVisionNode(Node):
    """统一图像订阅、调试图像和 JSON 结果输出。"""

    def __init__(self, node_name: str, default_input_topic: str) -> None:
        super().__init__(node_name)
        self.declare_parameter("input_topic", default_input_topic)
        self.declare_parameter("debug_topic", "~/debug_image")
        self.declare_parameter("result_topic", "~/result")
        self.declare_parameter("qos_depth", 10)
        self.declare_parameter("use_gui", False)
        self.declare_parameter("window_name", f"OmniFleet {node_name.replace('_', ' ')}")
        self.input_topic = str(self.get_parameter("input_topic").value)
        debug_topic = str(self.get_parameter("debug_topic").value)
        result_topic = str(self.get_parameter("result_topic").value)
        qos_depth = max(1, int(self.get_parameter("qos_depth").value))
        requested_gui = bool(self.get_parameter("use_gui").value)
        self.window_name = str(self.get_parameter("window_name").value)
        self.use_gui = requested_gui and bool(os.environ.get("DISPLAY"))
        if requested_gui and not self.use_gui:
            self.get_logger().warning("use_gui=true，但当前没有 DISPLAY；仅发布调试图话题。")
        self.bridge = CvBridge()
        self.debug_publisher = self.create_publisher(Image, debug_topic, qos_depth)
        self.result_publisher = self.create_publisher(String, result_topic, qos_depth)
        self.subscription = self.create_subscription(Image, self.input_topic, self.image_callback, qos_depth)
        self.get_logger().info(
            f"已启动：输入={self.input_topic}，调试图={debug_topic}，结果={result_topic}，"
            f"实时窗口={'开启' if self.use_gui else '关闭'}"
        )

    def image_callback(self, message: Image) -> None:
        """由具体节点实现图像处理。"""
        raise NotImplementedError

    def publish_result(self, message: Image, debug_image, result: Dict[str, object]) -> None:
        """保持原始时间戳发布调试图和 JSON 结果。"""
        debug_message = self.bridge.cv2_to_imgmsg(debug_image, encoding="bgr8")
        debug_message.header = message.header
        self.debug_publisher.publish(debug_message)
        if self.use_gui:
            cv2.imshow(self.window_name, debug_image)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                cv2.destroyWindow(self.window_name)
                self.use_gui = False
        payload = {
            "node": self.get_name(),
            "frame_id": message.header.frame_id,
            "stamp": {
                "sec": int(message.header.stamp.sec),
                "nanosec": int(message.header.stamp.nanosec),
            },
            **result,
        }
        output = String()
        output.data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        self.result_publisher.publish(output)

    def destroy_node(self):
        """节点退出时关闭本进程创建的实时窗口。"""
        if self.use_gui:
            cv2.destroyWindow(self.window_name)
            self.use_gui = False
        return super().destroy_node()
