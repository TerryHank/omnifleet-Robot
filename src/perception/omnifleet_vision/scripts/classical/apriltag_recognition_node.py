#!/usr/bin/env python3
"""36h11 标签识别节点。"""

import rclpy
import numpy as np
import sys
from ament_index_python.packages import get_package_prefix
sys.path.insert(0, get_package_prefix('omnifleet_vision')+'/lib/omnifleet_vision')
from marker_follow import MarkerFollow
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo

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
        self.tag_size_m = float(self.declare_parameter("tag_size_m", 0.21).value)
        self.target_id = int(self.declare_parameter("target_id", 0).value)
        topic = str(self.declare_parameter("camera_info_topic", "/camera/color/camera_info").value)
        self.camera_info = None
        self.follow = MarkerFollow(self, 'apriltag')
        self.info_subscription = self.create_subscription(CameraInfo, topic, self.info_callback, qos_profile_sensor_data)
        self.get_logger().info(f"tag36h11 ID={self.target_id}; black border={self.tag_size_m * 1000:.0f}mm; CameraInfo={topic}")

    def info_callback(self, message):
        self.camera_info = message

    def image_callback(self, message) -> None:
        """识别标签并发布结构化结果。"""
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            info = self.camera_info
            calibrated = info is not None and (info.width, info.height) == (message.width, message.height)
            matrix = np.array(info.k).reshape(3, 3) if calibrated else None
            distortion = np.array(info.d) if calibrated else None
            debug, result = recognize_apriltags(image, self.tag_size_m, self.target_id, matrix, distortion)
            result["pose_available"] = any("position_m" in item for item in result["detections"])
            result["camera_info_received"] = calibrated
            debug, result = self.follow.process(image, message, result, debug)
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
