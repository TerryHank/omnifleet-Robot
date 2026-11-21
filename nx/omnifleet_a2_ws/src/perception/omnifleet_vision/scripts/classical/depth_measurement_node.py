#!/usr/bin/env python3
"""深度中位数和有效率测量节点。"""

import rclpy

try:
    from .algorithms import measure_depth
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import measure_depth
    from ros_support import ClassicalVisionNode


class DepthMeasurementNode(ClassicalVisionNode):
    """兼容毫米整数深度和米制浮点深度。"""

    def __init__(self) -> None:
        super().__init__("depth_measurement", "/tof/aligned_depth_to_color/image_raw")
        self.declare_parameter("roi_x", -1)
        self.declare_parameter("roi_y", -1)
        self.declare_parameter("roi_width", 0)
        self.declare_parameter("roi_height", 0)
        self.declare_parameter("depth_scale_16u", 0.001)
        self.declare_parameter("minimum_depth", 0.1)
        self.declare_parameter("maximum_depth", 3.5)

    def image_callback(self, message) -> None:
        """读取原始深度编码并发布米制统计结果。"""
        try:
            depth = self.bridge.imgmsg_to_cv2(message, desired_encoding="passthrough")
            roi_width = int(self.get_parameter("roi_width").value)
            roi_height = int(self.get_parameter("roi_height").value)
            roi = None
            if roi_width > 0 and roi_height > 0:
                roi = (
                    int(self.get_parameter("roi_x").value),
                    int(self.get_parameter("roi_y").value),
                    roi_width,
                    roi_height,
                )
            debug, result = measure_depth(
                depth,
                message.encoding,
                roi,
                float(self.get_parameter("depth_scale_16u").value),
                float(self.get_parameter("minimum_depth").value),
                float(self.get_parameter("maximum_depth").value),
            )
            self.publish_result(message, debug, result)
        except Exception as error:
            self.get_logger().error(f"深度测量失败：{error}")


def main(args=None) -> None:
    """启动深度测量节点。"""
    rclpy.init(args=args)
    node = DepthMeasurementNode()
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
