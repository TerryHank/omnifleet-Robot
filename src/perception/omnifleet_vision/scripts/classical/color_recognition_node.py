#!/usr/bin/env python3
"""红、黄、绿、蓝 HSV 颜色识别节点。"""

import rclpy

try:
    from .algorithms import recognize_colors
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import recognize_colors
    from ros_support import ClassicalVisionNode


class ColorRecognitionNode(ClassicalVisionNode):
    """识别画面中的主要颜色区域。"""

    def __init__(self) -> None:
        super().__init__("color_recognition", "/camera/color/image_raw")
        self.declare_parameter("minimum_area", 200.0)

    def image_callback(self, message) -> None:
        """识别颜色区域并发布边界框和面积。"""
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            debug, result = recognize_colors(image, float(self.get_parameter("minimum_area").value))
            self.publish_result(message, debug, result)
        except Exception as error:
            self.get_logger().error(f"颜色识别失败：{error}")


def main(args=None) -> None:
    """启动颜色识别节点。"""
    rclpy.init(args=args)
    node = ColorRecognitionNode()
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
