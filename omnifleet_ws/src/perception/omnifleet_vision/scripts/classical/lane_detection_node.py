#!/usr/bin/env python3
"""灰度与 HSV 融合车道线检测节点。"""

import rclpy

try:
    from .algorithms import detect_lane
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import detect_lane
    from ros_support import ClassicalVisionNode


class LaneDetectionNode(ClassicalVisionNode):
    """检测下方区域的车道中心和横向偏差。"""

    def __init__(self) -> None:
        super().__init__("lane_detection", "/camera/color/image_raw")
        self.declare_parameter("roi_start_ratio", 0.55)
        self.declare_parameter("white_threshold", 180)
        self.declare_parameter("minimum_area", 100.0)

    def image_callback(self, message) -> None:
        """检测车道并发布中心偏差，不发送运动指令。"""
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            debug, result = detect_lane(
                image,
                float(self.get_parameter("roi_start_ratio").value),
                int(self.get_parameter("white_threshold").value),
                float(self.get_parameter("minimum_area").value),
            )
            self.publish_result(message, debug, result)
        except Exception as error:
            self.get_logger().error(f"车道检测失败：{error}")


def main(args=None) -> None:
    """启动车道检测节点。"""
    rclpy.init(args=args)
    node = LaneDetectionNode()
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
