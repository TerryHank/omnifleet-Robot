#!/usr/bin/env python3
"""相机频率、画面冻结和状态监测节点。"""

import cv2
import numpy as np
import rclpy
from sensor_msgs.msg import Image

try:
    from .algorithms import CameraHealthMonitor
    from .ros_support import ClassicalVisionNode
except ImportError:
    from algorithms import CameraHealthMonitor
    from ros_support import ClassicalVisionNode


class CameraMonitorNode(ClassicalVisionNode):
    """持续检查相机图像是否正常更新。"""

    def __init__(self) -> None:
        super().__init__("omnifleet_a2_camera_monitor", "/tof/color/image_raw")
        self.declare_parameter("minimum_fps", 10.0)
        self.declare_parameter("freeze_frame_count", 5)
        self.declare_parameter("freeze_difference", 0.5)
        self.declare_parameter("depth_topic", "")
        self.monitor = CameraHealthMonitor(
            minimum_fps=float(self.get_parameter("minimum_fps").value),
            freeze_frame_count=int(self.get_parameter("freeze_frame_count").value),
            freeze_difference=float(self.get_parameter("freeze_difference").value),
        )
        self.depth_debug = None
        self.depth_valid_ratio = 0.0
        depth_topic = str(self.get_parameter("depth_topic").value)
        self.depth_subscription = None
        if depth_topic:
            self.depth_subscription = self.create_subscription(
                Image, depth_topic, self.depth_callback, 10
            )
            self.get_logger().info(f"RGB-D 双画面监控：深度={depth_topic}")

    def depth_callback(self, message: Image) -> None:
        """缓存对齐深度伪彩，只用于 03_01 双话题可视化。"""

        try:
            raw = self.bridge.imgmsg_to_cv2(message, desired_encoding="passthrough")
            depth_m = raw.astype(np.float32)
            if str(message.encoding).upper() in {"16UC1", "MONO16"}:
                depth_m *= 0.001
            valid = np.isfinite(depth_m) & (depth_m >= 0.1) & (depth_m <= 3.5)
            self.depth_valid_ratio = float(np.count_nonzero(valid) / max(1, valid.size))
            normalized = np.zeros(depth_m.shape, dtype=np.uint8)
            normalized[valid] = np.clip(
                (depth_m[valid] - 0.1) * (255.0 / 3.4), 0.0, 255.0
            ).astype(np.uint8)
            color = cv2.applyColorMap(255 - normalized, cv2.COLORMAP_TURBO)
            color[~valid] = 0
            self.depth_debug = color
        except Exception as error:
            self.get_logger().warning(f"对齐深度预览失败：{error}")

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
            if self.depth_subscription is not None:
                if self.depth_debug is None:
                    depth_debug = np.zeros_like(debug)
                    cv2.putText(
                        depth_debug, "WAITING ALIGNED DEPTH", (25, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2,
                    )
                else:
                    depth_debug = cv2.resize(
                        self.depth_debug, (debug.shape[1], debug.shape[0])
                    )
                debug = cv2.hconcat([debug, depth_debug])
                cv2.putText(debug, "RGB", (15, debug.shape[0] - 16), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(
                    debug, "ALIGNED DEPTH", (image.shape[1] + 15, debug.shape[0] - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
                )
                result.update(
                    {
                        "layout": "rgb_left_aligned_depth_right",
                        "depth_received": self.depth_debug is not None,
                        "depth_valid_ratio": round(self.depth_valid_ratio, 6),
                    }
                )
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
