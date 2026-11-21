import json
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool, String

from .traffic_light_navigation import TrafficDecision, TrafficLightPolicy


class TrafficLightNavSupervisor(Node):
    """Optional traffic-light gate for the otherwise independent Nav2 stack."""

    def __init__(self):
        super().__init__("omnifleet_t2_traffic_light_supervisor")
        detection_topic = str(
            self.declare_parameter("detection_topic", "/omnifleet_t2/vision/detections").value
        )
        stop_confirmations = int(
            self.declare_parameter("stop_confirmations", 2).value
        )
        go_confirmations = int(
            self.declare_parameter("go_confirmations", 3).value
        )
        self._green_release_delay_sec = float(
            self.declare_parameter("green_release_delay_sec", 0.25).value
        )
        if self._green_release_delay_sec < 0.0:
            raise ValueError("green_release_delay_sec must be non-negative")

        self._policy = TrafficLightPolicy(stop_confirmations, go_confirmations)
        self._release_at = None

        command_qos = QoSProfile(depth=1)
        command_qos.reliability = ReliabilityPolicy.RELIABLE
        command_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self._pause_publisher = self.create_publisher(
            Bool, "/omnifleet_t2/navigation/traffic_light_pause", command_qos
        )
        self._status_publisher = self.create_publisher(
            String, "/omnifleet_t2/navigation/traffic_light_status", 10
        )
        self.create_subscription(String, detection_topic, self._on_detection, 10)
        self.create_timer(0.05, self._resume_after_green_if_ready)

        self._publish_pause(False)
        self.get_logger().info(
            f"独立红绿灯监督器已启用：输入={detection_topic}；"
            "红灯/黄灯停车，稳定绿灯后继续原航点"
        )

    def _on_detection(self, message: String) -> None:
        transition = self._policy.observe(message.data)
        phase = "observing"
        if transition.decision is TrafficDecision.STOP:
            self._release_at = None
            self._publish_pause(True)
            phase = "stopped"
            self.get_logger().warning(
                f"确认{transition.signal}灯：已取消当前导航并保存航点"
            )
        elif transition.decision is TrafficDecision.GO:
            self._release_at = time.monotonic() + self._green_release_delay_sec
            phase = "resuming"
            self.get_logger().info("确认绿灯：延时后恢复原航点")
        self._publish_status(transition, phase)

    def _resume_after_green_if_ready(self) -> None:
        if self._release_at is None or time.monotonic() < self._release_at:
            return
        self._release_at = None
        self._publish_pause(False)

    def _publish_pause(self, paused: bool) -> None:
        message = Bool()
        message.data = bool(paused)
        self._pause_publisher.publish(message)

    def _publish_status(self, transition, phase: str) -> None:
        payload = {
            "mode": "separate_launch",
            "phase": phase,
            "signal": transition.signal,
            "stopped": transition.stopped,
            "decision": transition.decision.value,
            "consecutive_count": transition.consecutive_count,
        }
        message = String()
        message.data = json.dumps(payload, sort_keys=True)
        self._status_publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = TrafficLightNavSupervisor()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
