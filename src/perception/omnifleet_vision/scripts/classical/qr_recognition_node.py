#!/usr/bin/env python3
"""二维码识别节点。"""

import rclpy

try:
    from .algorithms import recognize_qr_codes
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import recognize_qr_codes
    from ros_support import ClassicalVisionNode


class QrRecognitionNode(ClassicalVisionNode):
    """识别二维码文字和角点。"""

    def __init__(self) -> None:
        super().__init__("qr_recognition", "/camera/color/image_raw")

    def image_callback(self, message) -> None:
        """识别二维码并发布结构化结果。"""
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            debug, result = recognize_qr_codes(image)
            self.publish_result(message, debug, result)
        except Exception as error:
            self.get_logger().error(f"二维码识别失败：{error}")


def main(args=None) -> None:
    """启动二维码识别节点。"""
    rclpy.init(args=args)
    node = QrRecognitionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
