import hashlib
import math
import time
from functools import partial
from pathlib import Path

import signal

import rclpy
from rclpy.executors import ExternalShutdownException
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Pose, PoseStamped
from nav2_msgs.action import FollowWaypoints, NavigateThroughPoses, NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from std_srvs.srv import Trigger

from omnifleet_behaviors.goal_transactions import Decision, GoalTransactions
from omnifleet_interfaces.msg import MissionStatus, SlamStatus
from omnifleet_interfaces.srv import Capability, LoadMission, RunMission, StoreMission

from .storage import MissionStore


class MissionManagerNode(Node):
    def __init__(self):
        super().__init__("rrc_mission_manager")
        self.store = MissionStore(
            self.declare_parameter("storage_root", "~/robot_missions").value
        )
        self.map_root = Path(
            self.declare_parameter("map_root", "~/robot_maps").value
        ).expanduser()
        self.tof_calibration_manifest = Path(
            self.declare_parameter(
                "tof_calibration_manifest", "~/robot_calibration/tof.yaml"
            ).value
        ).expanduser()
        self.frontier_min_distance = float(
            self.declare_parameter("frontier_min_distance", 0.75).value
        )
        self.frontier_min_hold_sec = float(
            self.declare_parameter("frontier_min_hold_sec", 5.0).value
        )

        self._slam_status = None
        self._loaded = None
        self._transactions = GoalTransactions()
        self._active_goal_handle = None
        self._exploration_active = False
        self._last_frontier = None
        self._last_frontier_time = 0.0
        self._action_clients = {
            "through_poses": ActionClient(
                self, NavigateThroughPoses, "navigate_through_poses"
            ),
            "waypoints": ActionClient(self, FollowWaypoints, "follow_waypoints"),
            "single": ActionClient(self, NavigateToPose, "navigate_to_pose"),
        }
        self.status_publisher = self.create_publisher(
            MissionStatus, "/rrc_mission/status", 10
        )
        self.create_subscription(SlamStatus, "/rrc_slam/status", self._on_slam, 10)
        self.create_subscription(
            PoseStamped,
            "/rrc_exploration/frontier_goal",
            self._on_frontier_goal,
            10,
        )
        self.create_service(StoreMission, "/rrc_mission/store", self._store)
        self.create_service(LoadMission, "/rrc_mission/load", self._load)
        self.create_service(RunMission, "/rrc_mission/start", self._start)
        self.create_service(Trigger, "/rrc_mission/cancel", self._cancel)
        self.create_service(
            Capability, "/rrc_mission/start_exploration", self._exploration
        )
        self.create_service(
            Capability, "/rrc_mission/final_approach", self._final_approach
        )
        self._publish_status("idle", message="任务管理器已就绪")

    def _on_slam(self, status):
        self._slam_status = status
        if status.state != "RUNNING":
            self._exploration_active = False

    def _store(self, request, response):
        try:
            map_id, map_sha = self._current_map_identity()
            document = self.store.save(
                request.mission_id,
                map_id=map_id,
                map_sha256=map_sha,
                frame="map",
                poses=[self._pose_to_dict(pose) for pose in request.poses],
                loop=request.loop,
            )
            response.accepted = True
            response.revision = document["revision"]
            response.map_id = map_id
            response.map_sha256 = map_sha
            response.message = "任务已保存"
        except Exception as error:
            response.message = str(error)
        return response

    def _load(self, request, response):
        try:
            map_id, map_sha = self._current_map_identity()
            document = self.store.load(
                request.mission_id, map_id=map_id, map_sha256=map_sha
            )
            self._loaded = document
            response.accepted = True
            response.revision = document["revision"]
            response.map_id = document["map_id"]
            response.map_sha256 = document["map_sha256"]
            response.frame = document["frame"]
            response.poses = [self._dict_to_pose(pose) for pose in document["poses"]]
            response.loop = document["loop"]
            response.message = "任务已加载；请显式调用 /rrc_mission/start 启动"
            self._publish_status("loaded", document=document)
        except Exception as error:
            response.message = str(error)
        return response

    def _start(self, request, response):
        try:
            if self._loaded is None or self._loaded["mission_id"] != request.mission_id:
                raise RuntimeError("启动前必须先加载任务")
            if self._loaded["revision"] != request.revision:
                raise RuntimeError("任务版本不匹配")
            map_id, map_sha = self._current_map_identity()
            if self._loaded["map_id"] != map_id or self._loaded["map_sha256"] != map_sha:
                raise RuntimeError("任务加载后当前地图发生了变化")
            policy = request.policy or "through_poses"
            if policy not in {"through_poses", "waypoints"}:
                raise ValueError("policy 必须为 through_poses 或 waypoints")
            transaction, decision = self._submit_document(self._loaded, policy)
            response.accepted = True
            response.transaction_id = transaction.transaction_id
            response.message = {
                Decision.START: "任务已开始",
                Decision.CANCEL: "正在取消旧任务并切换到新任务",
                Decision.WAIT: "任务已进入等待队列",
            }[decision]
        except Exception as error:
            response.message = str(error)
        return response

    def _cancel(self, _, response):
        self._exploration_active = False
        if self._transactions.request_cancel() is Decision.CANCEL:
            self._cancel_active()
            response.success = True
            response.message = "已请求取消，正在等待动作结果"
        else:
            response.success = True
            response.message = "当前没有正在执行的任务"
        return response

    def _exploration(self, request, response):
        response.available = True
        if request.capability not in {"", "exploration"}:
            response.message = "capability 必须为 exploration"
            return response
        if self._slam_status is None or self._slam_status.state != "RUNNING":
            response.message = "SLAM 模式运行异常"
            return response
        if self._slam_status.operation != "mapping":
            response.message = "只有在 mapping 操作中才能使用自主探索"
            return response
        self._exploration_active = True
        response.accepted = True
        response.transaction_id = f"explore-{int(time.time())}"
        response.message = "自主探索入口已启用，正在等待前沿目标"
        self._publish_status("exploring", message=response.message)
        return response

    def _final_approach(self, request, response):
        response.available = False
        if request.capability not in {"", "final_approach"}:
            response.message = "capability 必须为 final_approach"
            return response
        topics = {name for name, _ in self.get_topic_names_and_types()}
        if "/sensors/tof/points" not in topics:
            response.message = "ToF 点云话题不可用"
            return response
        if not self.tof_calibration_manifest.is_file():
            response.message = "ToF 标定清单不可用"
            return response
        response.message = "尚未安装最终接近控制器"
        return response

    def _on_frontier_goal(self, pose):
        if not self._exploration_active:
            return
        now = time.monotonic()
        if now - self._last_frontier_time < self.frontier_min_hold_sec:
            self._publish_status("exploring", message="前沿目标保持间隔尚未结束")
            return
        if self._last_frontier is not None:
            dx = pose.pose.position.x - self._last_frontier.pose.position.x
            dy = pose.pose.position.y - self._last_frontier.pose.position.y
            if math.hypot(dx, dy) < self.frontier_min_distance:
                self._publish_status("exploring", message="前沿目标因距离迟滞规则被拒绝")
                return
        pose.header.frame_id = pose.header.frame_id or "map"
        goal = NavigateToPose.Goal()
        goal.pose = pose
        document = {
            "mission_id": "exploration",
            "revision": 0,
            "map_id": self._slam_status.map_id,
            "poses": [self._pose_to_dict(pose.pose)],
            "loop": False,
        }
        transaction, decision = self._transactions.submit(
            "single", {"goal": goal, "document": document, "policy": "single"}
        )
        if decision is Decision.START:
            self._send(transaction)
        elif decision is Decision.CANCEL:
            self._cancel_active()
        self._last_frontier = pose
        self._last_frontier_time = now

    def _submit_document(self, document, policy):
        stamped = []
        for pose in document["poses"]:
            message = PoseStamped()
            message.header.frame_id = document["frame"]
            message.header.stamp = self.get_clock().now().to_msg()
            message.pose = self._dict_to_pose(pose)
            stamped.append(message)
        if policy == "waypoints":
            goal = FollowWaypoints.Goal()
        else:
            goal = NavigateThroughPoses.Goal()
        goal.poses = stamped
        transaction, decision = self._transactions.submit(
            policy, {"goal": goal, "document": document, "policy": policy}
        )
        if decision is Decision.START:
            self._send(transaction)
        elif decision is Decision.CANCEL:
            self._cancel_active()
        self._publish_status("queued", transaction=transaction, document=document)
        return transaction, decision

    def _send(self, transaction):
        payload = transaction.payload
        client = self._action_clients[payload["policy"]]
        if not client.server_is_ready():
            self._publish_status(
                "rejected",
                transaction=transaction,
                document=payload["document"],
                message="Nav2 动作服务器不可用",
            )
            promoted, decision = self._transactions.goal_rejected(
                transaction.transaction_id
            )
            if decision is Decision.START:
                self._send(promoted)
            return
        future = client.send_goal_async(
            payload["goal"],
            feedback_callback=partial(self._feedback, transaction),
        )
        future.add_done_callback(partial(self._goal_response, transaction))

    def _goal_response(self, transaction, future):
        try:
            handle = future.result()
        except Exception as error:
            self._goal_rejected(transaction, str(error))
            return
        if not handle.accepted:
            self._goal_rejected(transaction, "Nav2 拒绝了任务")
            return
        self._active_goal_handle = handle
        decision = self._transactions.goal_response(transaction.transaction_id, True)
        handle.get_result_async().add_done_callback(partial(self._result, transaction))
        self._publish_status(
            "active", transaction=transaction, document=transaction.payload["document"]
        )
        if decision is Decision.CANCEL:
            self._cancel_active()

    def _goal_rejected(self, transaction, message):
        self._publish_status(
            "rejected",
            transaction=transaction,
            document=transaction.payload["document"],
            message=message,
        )
        promoted, decision = self._transactions.goal_rejected(
            transaction.transaction_id
        )
        if decision is Decision.START:
            self._send(promoted)

    def _cancel_active(self):
        if self._active_goal_handle is not None:
            self._active_goal_handle.cancel_goal_async()

    def _feedback(self, transaction, feedback):
        document = transaction.payload["document"]
        remaining = int(getattr(feedback.feedback, "number_of_poses_remaining", 0))
        current = max(0, len(document["poses"]) - remaining)
        self._publish_status(
            "active",
            transaction=transaction,
            document=document,
            current_index=current,
        )

    def _result(self, transaction, future):
        try:
            wrapped = future.result()
            succeeded = wrapped.status == GoalStatus.STATUS_SUCCEEDED
            message = str(wrapped.result)
        except Exception as error:
            succeeded = False
            message = str(error)
        self._active_goal_handle = None
        document = transaction.payload["document"]
        self._publish_status(
            "succeeded" if succeeded else "finished",
            transaction=transaction,
            document=document,
            message=message,
        )
        promoted, decision = self._transactions.result(transaction.transaction_id)
        if decision is Decision.START:
            self._send(promoted)
        elif succeeded and document.get("loop"):
            self._submit_document(document, transaction.payload["policy"])

    def _current_map_identity(self):
        if self._slam_status is None or self._slam_status.state != "RUNNING":
            raise RuntimeError("当前没有运行正常的 SLAM 模式")
        if not self._slam_status.map_id or not self._slam_status.mode:
            raise RuntimeError("当前 SLAM 状态中没有地图标识")
        manifest = (
            self.map_root
            / self._slam_status.mode
            / self._slam_status.map_id
            / "manifest.yaml"
        )
        if not manifest.is_file():
            raise FileNotFoundError(manifest)
        digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
        return self._slam_status.map_id, digest

    def _publish_status(
        self,
        state,
        *,
        transaction=None,
        document=None,
        current_index=0,
        message="",
    ):
        status = MissionStatus()
        status.stamp = self.get_clock().now().to_msg()
        status.state = state
        status.message = message
        if transaction is not None:
            status.transaction_id = transaction.transaction_id
        if document is not None:
            status.mission_id = document["mission_id"]
            status.revision = document["revision"]
            status.total = len(document["poses"])
            status.map_id = document["map_id"]
        status.current_index = current_index
        self.status_publisher.publish(status)

    @staticmethod
    def _pose_to_dict(pose):
        return {
            "position": {
                "x": float(pose.position.x),
                "y": float(pose.position.y),
                "z": float(pose.position.z),
            },
            "orientation": {
                "x": float(pose.orientation.x),
                "y": float(pose.orientation.y),
                "z": float(pose.orientation.z),
                "w": float(pose.orientation.w),
            },
        }

    @staticmethod
    def _dict_to_pose(data):
        pose = Pose()
        pose.position.x = data["position"]["x"]
        pose.position.y = data["position"]["y"]
        pose.position.z = data["position"]["z"]
        pose.orientation.x = data["orientation"]["x"]
        pose.orientation.y = data["orientation"]["y"]
        pose.orientation.z = data["orientation"]["z"]
        pose.orientation.w = data["orientation"]["w"]
        return pose


def main(args=None):
    rclpy.init(args=args)
    node = MissionManagerNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
