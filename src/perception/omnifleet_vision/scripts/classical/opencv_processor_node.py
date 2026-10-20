#!/usr/bin/env python3
"""灰度、模糊和边缘处理节点。"""

import rclpy

try:
    from .algorithms import process_opencv_image
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import process_opencv_image
    from ros_support import ClassicalVisionNode


class OpenCvProcessorNode(ClassicalVisionNode):
    """按参数选择一种基础图像处理操作。"""

    def __init__(self) -> None:
        super().__init__("opencv_processor", "/camera/color/image_raw")
        self.declare_parameter("operation", "canny")
        self.declare_parameter("blur_size", 5)
        self.declare_parameter("canny_low", 50)
        self.declare_parameter("canny_high", 150)

    def image_callback(self, message) -> None:
        """处理单帧图像并发布统计结果。"""
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            debug, result = process_opencv_image(
                image,
                str(self.get_parameter("operation").value),
                int(self.get_parameter("blur_size").value),
                int(self.get_parameter("canny_low").value),
                int(self.get_parameter("canny_high").value),
            )
            self.publish_result(message, debug, result)
        except Exception as error:
            self.get_logger().error(f"基础图像处理失败：{error}")


def main(args=None) -> None:
    """启动基础图像处理节点。"""
    rclpy.init(args=args)
    node = OpenCvProcessorNode()
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
