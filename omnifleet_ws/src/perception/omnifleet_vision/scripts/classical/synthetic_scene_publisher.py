#!/usr/bin/env python3
"""生成无品牌、水印和隐私信息的课程测试图像。"""

from __future__ import annotations

import cv2
import numpy as np


def build_scene(mode: str, width: int = 640, height: int = 480, text: str = "OMNIFLEET") -> np.ndarray:
    """生成颜色、二维码、标签、巡线、灯态或课程假车牌场景。"""

    if width < 160 or height < 120:
        raise ValueError("测试图像尺寸过小")
    mode = mode.strip().lower()
    image = np.full((height, width, 3), 235, dtype=np.uint8)
    if mode == "color":
        colors = [(0, 0, 255), (0, 255, 255), (0, 200, 0), (255, 0, 0)]
        block = width // 5
        for index, color in enumerate(colors):
            left = (index + 1) * block - block // 2
            cv2.rectangle(image, (left, height // 3), (left + block // 2, 2 * height // 3), color, -1)
    elif mode == "lane":
        image[:] = 35
        points = np.array(
            [[width // 2 - 25, height], [width // 2 - 10, height // 2],
             [width // 2 + 10, height // 2], [width // 2 + 25, height]], dtype=np.int32,
        )
        cv2.fillPoly(image, [points], (255, 255, 255))
    elif mode == "apriltag":
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
        size = min(width, height) // 2
        marker = (
            cv2.aruco.generateImageMarker(dictionary, 0, size)
            if hasattr(cv2.aruco, "generateImageMarker")
            else cv2.aruco.drawMarker(dictionary, 0, size)
        )
        start_x, start_y = (width - size) // 2, (height - size) // 2
        image[start_y : start_y + size, start_x : start_x + size] = cv2.cvtColor(
            marker, cv2.COLOR_GRAY2BGR
        )
    elif mode == "qr":
        import qrcode

        qr = np.array(qrcode.make(text).convert("RGB"))[:, :, ::-1]
        size = min(width, height) // 2
        qr = cv2.resize(qr, (size, size), interpolation=cv2.INTER_NEAREST)
        start_x, start_y = (width - size) // 2, (height - size) // 2
        image[start_y : start_y + size, start_x : start_x + size] = qr
    elif mode == "traffic_light":
        image[:] = 40
        state = text.strip().lower()
        centers = [(width // 2, height // 4), (width // 2, height // 2), (width // 2, 3 * height // 4)]
        colors = [(0, 0, 255), (0, 255, 255), (0, 255, 0)]
        names = ["red", "yellow", "green"]
        for center, color, name in zip(centers, colors, names):
            cv2.circle(image, center, min(width, height) // 12, color if state == name else (80, 80, 80), -1)
    elif mode == "license_plate":
        image[:] = 70
        left, top, right, bottom = width // 5, height // 3, 4 * width // 5, 2 * height // 3
        cv2.rectangle(image, (left, top), (right, bottom), (190, 80, 20), -1)
        cv2.putText(
            image, text[:10].upper(), (left + 20, (top + bottom) // 2 + 20),
            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3,
        )
    elif mode == "blank":
        pass
    else:
        raise ValueError(f"未知测试场景：{mode}")
    return image


def main(args=None) -> None:
    """启动测试图像发布节点。"""

    import rclpy
    from cv_bridge import CvBridge
    from rclpy.node import Node
    from sensor_msgs.msg import Image

    class SyntheticScenePublisher(Node):
        """以固定频率发布生成图像，不读取厂商截图或真实隐私素材。"""

        def __init__(self) -> None:
            super().__init__("synthetic_scene_publisher")
            mode = str(self.declare_parameter("mode", "color").value)
            width = int(self.declare_parameter("width", 640).value)
            height = int(self.declare_parameter("height", 480).value)
            text = str(self.declare_parameter("text", "OMNIFLEET").value)
            topic = str(self.declare_parameter("output_topic", "/vision/test/image").value)
            rate = float(self.declare_parameter("publish_rate", 5.0).value)
            if rate <= 0.0:
                raise ValueError("发布频率必须大于零")
            self.image = build_scene(mode, width, height, text)
            self.bridge = CvBridge()
            self.publisher = self.create_publisher(Image, topic, 10)
            self.timer = self.create_timer(1.0 / rate, self.publish_image)

        def publish_image(self) -> None:
            """发布一帧带当前 ROS 时间戳的测试图像。"""

            message = self.bridge.cv2_to_imgmsg(self.image, encoding="bgr8")
            message.header.stamp = self.get_clock().now().to_msg()
            message.header.frame_id = "vision_test_frame"
            self.publisher.publish(message)

    rclpy.init(args=args)
    node = SyntheticScenePublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
