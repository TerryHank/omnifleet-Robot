#!/usr/bin/env python3
"""为视觉课程调试图提供统一的实时 OpenCV 窗口。"""

from __future__ import annotations

import os

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class ImageDisplayNode(Node):
    """订阅课程调试图；无桌面时自动退回话题模式。"""

    def __init__(self) -> None:
        super().__init__("image_display")
        input_topic = str(self.declare_parameter("input_topic", "/vision/debug").value)
        self.window_name = str(self.declare_parameter("window_name", "OmniFleet Vision").value)
        requested_gui = bool(self.declare_parameter("use_gui", True).value)
        self.enabled = requested_gui and bool(os.environ.get("DISPLAY"))
        self.bridge = CvBridge()
        if self.enabled:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, 960, 720)
            self.subscription = self.create_subscription(
                Image, input_topic, self.on_image, qos_profile_sensor_data
            )
            self.get_logger().info(
                f"实时窗口已开启：窗口={self.window_name}，输入={input_topic}"
            )
        else:
            self.subscription = None
            self.get_logger().warning(
                f"实时窗口未开启：use_gui={requested_gui}，DISPLAY={os.environ.get('DISPLAY', '')!r}；"
                f"调试图仍由原节点发布到 {input_topic}"
            )

    def on_image(self, message: Image) -> None:
        """显示一帧调试图；q 或 Esc 只关闭窗口。"""
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            cv2.imshow(self.window_name, image)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                cv2.destroyWindow(self.window_name)
                self.enabled = False
                self.destroy_subscription(self.subscription)
                self.subscription = None
        except Exception as error:
            self.get_logger().error(f"实时图像显示失败：{error}")

    def destroy_node(self):
        """退出时关闭本节点窗口。"""
        if self.enabled:
            cv2.destroyWindow(self.window_name)
            self.enabled = False
        return super().destroy_node()


def main(args=None) -> None:
    """启动统一实时显示节点。"""
    rclpy.init(args=args)
    node = ImageDisplayNode()
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
