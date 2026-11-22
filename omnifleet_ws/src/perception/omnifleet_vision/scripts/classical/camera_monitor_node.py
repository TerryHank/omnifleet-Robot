#!/usr/bin/env python3
"""相机频率、画面冻结和状态监测节点。"""

import cv2
import rclpy

try:
    from .algorithms import CameraHealthMonitor
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import CameraHealthMonitor
    from ros_support import ClassicalVisionNode


class CameraMonitorNode(ClassicalVisionNode):
    """持续检查相机图像是否正常更新。"""

    def __init__(self) -> None:
        super().__init__("camera_monitor", "/camera/color/image_raw")
        self.declare_parameter("minimum_fps", 10.0)
        self.declare_parameter("freeze_frame_count", 5)
        self.declare_parameter("freeze_difference", 0.5)
        self.monitor = CameraHealthMonitor(
            minimum_fps=float(self.get_parameter("minimum_fps").value),
            freeze_frame_count=int(self.get_parameter("freeze_frame_count").value),
            freeze_difference=float(self.get_parameter("freeze_difference").value),
        )

    def image_callback(self, message) -> None:
        """统计频率和帧差，并在原图上标记状态。"""
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            timestamp = message.header.stamp.sec + message.header.stamp.nanosec * 1.0e-9
            if timestamp <= 0.0:
                timestamp = self.get_clock().now().nanoseconds * 1.0e-9
            result = self.monitor.update(image, timestamp)
            debug = image.copy()
            color = (0, 255, 0) if result["status"] == "ok" else (0, 0, 255)
            cv2.putText(debug, f"{result['status']}  {result['fps']:.1f} FPS", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            self.publish_result(message, debug, result)
        except Exception as error:
            self.get_logger().error(f"相机状态处理失败：{error}")


def main(args=None) -> None:
    """启动相机状态监测节点。"""
    rclpy.init(args=args)
    node = CameraMonitorNode()
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
