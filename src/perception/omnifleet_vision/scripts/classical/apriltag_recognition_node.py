#!/usr/bin/env python3
"""36h11 标签识别节点。"""

import rclpy

try:
    from .algorithms import recognize_apriltags
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import recognize_apriltags
    from ros_support import ClassicalVisionNode


class AprilTagRecognitionNode(ClassicalVisionNode):
    """识别标签编号、中心和四个角点。"""

    def __init__(self) -> None:
        super().__init__("apriltag_recognition", "/camera/color/image_raw")

    def image_callback(self, message) -> None:
        """识别标签并发布结构化结果。"""
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            debug, result = recognize_apriltags(image)
            self.publish_result(message, debug, result)
        except Exception as error:
            self.get_logger().error(f"标签识别失败：{error}")


def main(args=None) -> None:
    """启动标签识别节点。"""
    rclpy.init(args=args)
    node = AprilTagRecognitionNode()
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
