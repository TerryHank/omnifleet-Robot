import json
import math
import time
from copy import deepcopy
from functools import partial

import rclpy
from geometry_msgs.msg import PoseArray, PoseStamped, Twist
from nav2_msgs.action import NavigateThroughPoses
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool, String
from std_srvs.srv import Trigger

from .goal_transactions import Decision, GoalTransaction, GoalTransactions


class HoldToStopDetector:
    """区分中键持续零速与方向键松开时的单次零速。"""

    def __init__(self, required_messages=3, window_sec=0.35):
        if required_messages < 2:
            raise ValueError("required_messages必须至少为2")
        if window_sec <= 0.0:
            raise ValueError("window_sec必须大于0")
        self.required_messages = int(required_messages)
        self.window_sec = float(window_sec)
        self._zero_timestamps = []
        self._latched = False

    def observe(self, is_zero, timestamp):
        if not is_zero:
            self.reset()
            return False
        if self._latched:
            return False

        cutoff = float(timestamp) - self.window_sec
        self._zero_timestamps = [
            value for value in self._zero_timestamps if value >= cutoff
        ]
        self._zero_timestamps.append(float(timestamp))
        if len(self._zero_timestamps) < self.required_messages:
            return False

        self._latched = True
        return True

    def reset(self):
        self._zero_timestamps.clear()
        self._latched = False


def _approach_xy(goal_x, goal_y, goal_yaw, approach_distance):
    """返回目标箭头反方向上的阿克曼直线进场点。"""

    return (
        goal_x - approach_distance * math.cos(goal_yaw),
        goal_y - approach_distance * math.sin(goal_yaw),
    )


def _yaw_from_pose(pose):
    orientation = pose.pose.orientation
    norm = math.sqrt(
        orientation.x * orientation.x
        + orientation.y * orientation.y
        + orientation.z * orientation.z
        + orientation.w * orientation.w
    )
    if not math.isfinite(norm) or norm < 1.0e-6:
        raise ValueError("目标箭头的四元数无效")
    x = orientation.x / norm
    y = orientation.y / norm
    z = orientation.z / norm
    w = orientation.w / norm
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


class FoxgloveNavBridge(Node):
    def __init__(self):
        super().__init__("foxglove_nav_bridge")
        self.declare_parameter("goal_topic", "/goal_pose")
        self.declare_parameter("waypoints_topic", "/waypoint_poses")
        self.declare_parameter("stamp_backdate_sec", 0.2)
        self.declare_parameter("goal_approach_distance", 1.26)
        self.declare_parameter("manual_stop_topic", "/cmd_vel_teleop")
        self.declare_parameter(
            "manual_stop_service", "/rrc_system/stop_manual_stack"
        )
        self.declare_parameter("manual_stop_hold_messages", 3)
        self.declare_parameter("manual_stop_window_sec", 0.35)

        goal_topic = self.get_parameter("goal_topic").value
        waypoints_topic = self.get_parameter("waypoints_topic").value
        self._goal_approach_distance = float(
            self.get_parameter("goal_approach_distance").value
        )
        if self._goal_approach_distance <= 0.0:
            raise ValueError("goal_approach_distance必须大于0")
        through_poses_client = ActionClient(
            self, NavigateThroughPoses, "navigate_through_poses"
        )
        self._action_clients = {
            "single": through_poses_client,
            "multi": through_poses_client,
        }
        self._transactions = GoalTransactions()
        self._active_goal_handle = None
        self._manual_stop_service = str(
            self.get_parameter("manual_stop_service").value
        )
        self._manual_stop_detector = HoldToStopDetector(
            required_messages=int(
                self.get_parameter("manual_stop_hold_messages").value
            ),
            window_sec=float(self.get_parameter("manual_stop_window_sec").value),
        )
        self._manual_stop_future = None
        self._localization_ready = False
        self._lifecycle_ready = False
        self._manual_stop_client = self.create_client(
            Trigger, self._manual_stop_service
        )
        self._approach_pose_publisher = self.create_publisher(
            PoseStamped, "/rrc_nav/parking_approach_pose", 10
        )
        self._feedback_publisher = self.create_publisher(
            String, "/rrc_nav/feedback", 10
        )
        self._result_publisher = self.create_publisher(String, "/rrc_nav/result", 10)
        self.create_subscription(PoseStamped, goal_topic, self._on_goal_pose, 10)
        self.create_subscription(PoseArray, waypoints_topic, self._on_waypoint_poses, 10)
        readiness_qos = QoSProfile(depth=1)
        readiness_qos.reliability = ReliabilityPolicy.RELIABLE
        readiness_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.create_subscription(
            Bool,
            "/omnifleet/localization_ready",
            lambda message: setattr(self, "_localization_ready", message.data),
            readiness_qos,
        )
        self.create_subscription(
            Bool,
            "/omnifleet/lifecycle_ready",
            lambda message: setattr(self, "_lifecycle_ready", message.data),
            readiness_qos,
        )
        self.create_subscription(
            Twist,
            str(self.get_parameter("manual_stop_topic").value),
            self._on_teleop_command,
            10,
        )
        self.get_logger().info(
            f"正在将 {goal_topic} 和 {waypoints_topic} 转发为 Nav2 动作目标；"
            f"单点目标保留 {self._goal_approach_distance:.2f} m 直线进场段；"
            "遥控中键持续零速将关闭手动启动栈"
        )

    @staticmethod
    def _is_zero_twist(message):
        values = (
            message.linear.x,
            message.linear.y,
            message.linear.z,
            message.angular.x,
            message.angular.y,
            message.angular.z,
        )
        return all(math.isfinite(value) and abs(value) <= 1.0e-9 for value in values)

    def _on_teleop_command(self, message):
        if not self._manual_stop_detector.observe(
            self._is_zero_twist(message), time.monotonic()
        ):
            return
        if self._manual_stop_future is not None:
            return
        if not self._manual_stop_client.service_is_ready():
            self.get_logger().error(
                f"中键停止失败：{self._manual_stop_service} 服务不可用"
            )
            self._manual_stop_detector.reset()
            return

        self.get_logger().warning(
            "检测到遥控中键持续零速：正在锁定零速度并关闭手动启动栈"
        )
        self._manual_stop_future = self._manual_stop_client.call_async(
            Trigger.Request()
        )
        self._manual_stop_future.add_done_callback(self._on_manual_stop_response)

    def _on_manual_stop_response(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().warning(response.message)
            else:
                self.get_logger().error(f"关闭手动启动栈失败：{response.message}")
                self._manual_stop_future = None
                self._manual_stop_detector.reset()
        except Exception as error:
            self.get_logger().error(f"关闭手动启动栈服务异常：{error}")
            self._manual_stop_future = None
            self._manual_stop_detector.reset()

    def _default_stamp(self):
        backdate = max(0.0, float(self.get_parameter("stamp_backdate_sec").value))
        return (self.get_clock().now() - Duration(seconds=backdate)).to_msg()

    def _on_goal_pose(self, pose: PoseStamped) -> None:
        if not self._navigation_is_ready("single"):
            return
        final_pose = deepcopy(pose)
        if not final_pose.header.frame_id:
            final_pose.header.frame_id = "map"
        if final_pose.header.stamp.sec == 0 and final_pose.header.stamp.nanosec == 0:
            final_pose.header.stamp = self._default_stamp()
        try:
            goal_yaw = _yaw_from_pose(final_pose)
        except ValueError as error:
            self._publish_result("", "single", "rejected", str(error))
            return

        approach_pose = deepcopy(final_pose)
        approach_x, approach_y = _approach_xy(
            final_pose.pose.position.x,
            final_pose.pose.position.y,
            goal_yaw,
            self._goal_approach_distance,
        )
        approach_pose.pose.position.x = approach_x
        approach_pose.pose.position.y = approach_y
        self._approach_pose_publisher.publish(approach_pose)

        goal = NavigateThroughPoses.Goal()
        goal.poses = [approach_pose, final_pose]
        self.get_logger().info(
            "精确停车目标："
            f"进场点=({approach_x:.2f}, {approach_y:.2f})，"
            f"终点=({final_pose.pose.position.x:.2f}, "
            f"{final_pose.pose.position.y:.2f})，"
            f"目标朝向={goal_yaw:.2f} rad"
        )
        self._submit("single", goal)

    def _on_waypoint_poses(self, poses: PoseArray) -> None:
        if not self._navigation_is_ready("multi"):
            return
        if not poses.poses:
            self._publish_result("", "multi", "rejected", "航点数组为空")
            return
        frame_id = poses.header.frame_id or "map"
        stamp = poses.header.stamp
        if stamp.sec == 0 and stamp.nanosec == 0:
            stamp = self._default_stamp()
        goal = NavigateThroughPoses.Goal()
        for pose in poses.poses:
            stamped = PoseStamped()
            stamped.header.frame_id = frame_id
            stamped.header.stamp = stamp
            stamped.pose = pose
            goal.poses.append(stamped)
        self._submit("multi", goal)

    def _navigation_is_ready(self, kind):
        if self._localization_ready and self._lifecycle_ready:
            return True
        missing = []
        if not self._localization_ready:
            missing.append("map/cloud localization")
        if not self._lifecycle_ready:
            missing.append("Nav2 lifecycle")
        detail = "navigation is locked; waiting for " + " and ".join(missing)
        self.get_logger().warning(detail)
        self._publish_result("", kind, "rejected", detail)
        return False

    def _submit(self, kind, goal):
        transaction, decision = self._transactions.submit(kind, goal)
        self._publish_feedback(transaction, "queued")
        if decision is Decision.START:
            self._start(transaction)
        elif decision is Decision.CANCEL:
            self._cancel_active(transaction.transaction_id)

    def _start(self, transaction: GoalTransaction):
        client = self._action_clients[transaction.kind]
        if not client.server_is_ready():
            self._publish_result(
                transaction.transaction_id,
                transaction.kind,
                "rejected",
                "Nav2 动作服务器不可用",
            )
            promoted, decision = self._transactions.goal_rejected(
                transaction.transaction_id
            )
            if decision is Decision.START:
                self._start(promoted)
            return
        self._publish_feedback(transaction, "sending")
        future = client.send_goal_async(
            transaction.payload,
            feedback_callback=partial(self._on_action_feedback, transaction),
        )
        future.add_done_callback(partial(self._on_goal_response, transaction))

    def _on_goal_response(self, transaction, future):
        try:
            goal_handle = future.result()
        except Exception as error:
            self._reject_and_promote(transaction, str(error))
            return
        if not goal_handle.accepted:
            self._reject_and_promote(transaction, "Nav2 拒绝了动作目标")
            return
        self._active_goal_handle = goal_handle
        decision = self._transactions.goal_response(
            transaction.transaction_id, accepted=True
        )
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(partial(self._on_action_result, transaction))
        self._publish_feedback(transaction, "accepted")
        if decision is Decision.CANCEL:
            self._cancel_active(transaction.transaction_id)

    def _reject_and_promote(self, transaction, message):
        self._publish_result(
            transaction.transaction_id, transaction.kind, "rejected", message
        )
        promoted, decision = self._transactions.goal_rejected(
            transaction.transaction_id
        )
        if decision is Decision.START:
            self._start(promoted)

    def _cancel_active(self, replacement_transaction_id):
        if self._active_goal_handle is None:
            return
        current = self._transactions.current
        self._publish_feedback(
            current,
            "cancel_requested",
            replacement_transaction_id=replacement_transaction_id,
        )
        future = self._active_goal_handle.cancel_goal_async()
        future.add_done_callback(partial(self._on_cancel_response, current))

    def _on_cancel_response(self, transaction, future):
        try:
            response = future.result()
            goals_canceling = len(response.goals_canceling)
            message = f"已确认取消 {goals_canceling} 个目标"
        except Exception as error:
            message = f"取消请求失败：{error}"
        self._transactions.cancel_response(transaction.transaction_id)
        self._publish_feedback(transaction, "waiting_for_result", message=message)

    def _on_action_feedback(self, transaction, feedback_message):
        self._publish_feedback(
            transaction, "active", feedback=str(feedback_message.feedback)
        )

    def _on_action_result(self, transaction, future):
        try:
            wrapped = future.result()
            status = int(wrapped.status)
            detail = str(wrapped.result)
        except Exception as error:
            status = -1
            detail = str(error)
        self._active_goal_handle = None
        self._publish_result(
            transaction.transaction_id,
            transaction.kind,
            "finished",
            detail,
            action_status=status,
        )
        promoted, decision = self._transactions.result(transaction.transaction_id)
        if decision is Decision.START:
            self._start(promoted)

    def _publish_feedback(self, transaction, state, **fields):
        payload = {
            "transaction_id": transaction.transaction_id,
            "kind": transaction.kind,
            "state": state,
            **fields,
        }
        message = String()
        message.data = json.dumps(payload, sort_keys=True)
        self._feedback_publisher.publish(message)

    def _publish_result(self, transaction_id, kind, state, detail, **fields):
        payload = {
            "transaction_id": transaction_id,
            "kind": kind,
            "state": state,
            "detail": detail,
            **fields,
        }
        message = String()
        message.data = json.dumps(payload, sort_keys=True)
        self._result_publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = FoxgloveNavBridge()
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
