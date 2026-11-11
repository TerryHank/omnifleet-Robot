#!/usr/bin/env python3
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

import rclpy
from action_msgs.msg import GoalStatus
from action_msgs.srv import CancelGoal
from geometry_msgs.msg import Pose, PoseStamped
from nav_msgs.msg import Path as NavPath
from nav2_msgs.action import NavigateThroughPoses
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Empty, String
from visualization_msgs.msg import Marker, MarkerArray


@dataclass
class SemanticWaypoint:
    name: str
    pose: Pose


def normalized_pose(pose: Pose) -> Pose:
    values = (
        pose.position.x,
        pose.position.y,
        pose.position.z,
        pose.orientation.x,
        pose.orientation.y,
        pose.orientation.z,
        pose.orientation.w,
    )
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("点位包含无效数字")
    norm = math.sqrt(
        pose.orientation.x * pose.orientation.x
        + pose.orientation.y * pose.orientation.y
        + pose.orientation.z * pose.orientation.z
        + pose.orientation.w * pose.orientation.w
    )
    result = Pose()
    result.position.x = float(pose.position.x)
    result.position.y = float(pose.position.y)
    result.position.z = float(pose.position.z)
    if norm < 1.0e-8:
        result.orientation.w = 1.0
    else:
        result.orientation.x = float(pose.orientation.x) / norm
        result.orientation.y = float(pose.orientation.y) / norm
        result.orientation.z = float(pose.orientation.z) / norm
        result.orientation.w = float(pose.orientation.w) / norm
    return result


def pose_to_record(pose: Pose) -> dict:
    pose = normalized_pose(pose)
    return {
        "position": {
            "x": pose.position.x,
            "y": pose.position.y,
            "z": pose.position.z,
        },
        "orientation": {
            "x": pose.orientation.x,
            "y": pose.orientation.y,
            "z": pose.orientation.z,
            "w": pose.orientation.w,
        },
    }


def record_to_pose(record: dict) -> Pose:
    pose = Pose()
    position = record.get("position", {})
    orientation = record.get("orientation", {})
    pose.position.x = float(position.get("x", 0.0))
    pose.position.y = float(position.get("y", 0.0))
    pose.position.z = float(position.get("z", 0.0))
    pose.orientation.x = float(orientation.get("x", 0.0))
    pose.orientation.y = float(orientation.get("y", 0.0))
    pose.orientation.z = float(orientation.get("z", 0.0))
    pose.orientation.w = float(orientation.get("w", 1.0))
    return normalized_pose(pose)


def waypoint_name(value: object, index: int) -> str:
    if not isinstance(value, str):
        value = ""
    name = " ".join(value.split())
    return name or f"航点{index}"


def resolve_waypoint(
    waypoints: list[SemanticWaypoint], request_text: str
) -> tuple[int, SemanticWaypoint]:
    try:
        request = json.loads(request_text)
    except json.JSONDecodeError:
        request = request_text

    if isinstance(request, dict):
        index = request.get("index")
        if isinstance(index, bool) or not isinstance(index, int):
            raise ValueError("语义点序号必须是整数")
        if index < 1 or index > len(waypoints):
            raise ValueError("语义点序号不存在")
        return index, waypoints[index - 1]

    if not isinstance(request, str):
        raise ValueError("语义点名称格式不正确")
    name = " ".join(request.split())
    if not name:
        raise ValueError("语义点名称不能为空")
    matches = [
        (index, waypoint)
        for index, waypoint in enumerate(waypoints, start=1)
        if waypoint.name == name
    ]
    if not matches:
        raise ValueError(f"找不到语义点“{name}”")
    if len(matches) > 1:
        raise ValueError(f"存在多个同名语义点“{name}”，请在界面点击目标点")
    return matches[0]


def load_route(path: Path) -> list[SemanticWaypoint]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("路线文件格式不正确")
    records = data.get("waypoints")
    if records is not None:
        if not isinstance(records, list):
            raise ValueError("路线文件格式不正确")
        waypoints = []
        for index, record in enumerate(records, start=1):
            if not isinstance(record, dict) or not isinstance(record.get("pose"), dict):
                raise ValueError("路线文件格式不正确")
            waypoints.append(
                SemanticWaypoint(
                    name=waypoint_name(record.get("name"), index),
                    pose=record_to_pose(record["pose"]),
                )
            )
        return waypoints

    poses = data.get("poses", [])
    if not isinstance(poses, list):
        raise ValueError("路线文件格式不正确")
    return [
        SemanticWaypoint(name=waypoint_name("", index), pose=record_to_pose(record))
        for index, record in enumerate(poses, start=1)
    ]


def save_route(path: Path, frame_id: str, waypoints: list[SemanticWaypoint]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 2,
        "frame_id": frame_id,
        "waypoints": [
            {"name": waypoint.name, "pose": pose_to_record(waypoint.pose)}
            for waypoint in waypoints
        ],
    }
    temporary = path.with_suffix(f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


class WaypointUiBridge(Node):
    def __init__(self) -> None:
        super().__init__("omnifleet_a2_waypoint_ui")
        self.declare_parameter("frame_id", "map")
        self.declare_parameter(
            "route_file", "/var/lib/omnifleet_a2/missions/waypoints.json"
        )
        self.frame_id = str(self.get_parameter("frame_id").value)
        self.route_file = Path(
            str(self.get_parameter("route_file").value)
        ).expanduser()
        self.waypoints = []
        self.pending_name = ""
        self.nav2_ready = False
        self.navigation_active = False
        self.active_route_names = []
        self.active_goal_handle = None
        self.cancel_after_accept = False
        self.last_remaining = None

        latched = QoSProfile(depth=1)
        latched.reliability = ReliabilityPolicy.RELIABLE
        latched.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.status_pub = self.create_publisher(
            String, "/omnifleet_a2/waypoints/status", latched
        )
        self.path_pub = self.create_publisher(
            NavPath, "/omnifleet_a2/waypoints/path", latched
        )
        self.markers_pub = self.create_publisher(
            MarkerArray, "/omnifleet_a2/waypoints/markers", latched
        )
        self.catalog_pub = self.create_publisher(
            String, "/omnifleet_a2/waypoints/catalog", latched
        )
        self.action_client = ActionClient(
            self, NavigateThroughPoses, "navigate_through_poses"
        )
        self.cancel_clients = (
            (
                "单点",
                self.create_client(
                    CancelGoal, "/navigate_to_pose/_action/cancel_goal"
                ),
            ),
            (
                "多点",
                self.create_client(
                    CancelGoal, "/navigate_through_poses/_action/cancel_goal"
                ),
            ),
        )
        self.pending_cancel_responses = 0
        self.cancelled_goal_count = 0
        self.cancel_errors = []

        self.create_subscription(
            PoseStamped,
            "/omnifleet_a2/waypoints/add_pose",
            self.on_add_pose,
            10,
        )
        self.create_subscription(
            String, "/omnifleet_a2/waypoints/next_name", self.on_next_name, 10
        )
        self.create_subscription(
            String, "/omnifleet_a2/waypoints/rename", self.on_rename, 10
        )
        self.create_subscription(
            Empty, "/omnifleet_a2/waypoints/start", self.on_start, 10
        )
        self.create_subscription(
            String,
            "/omnifleet_a2/waypoints/navigate_to",
            self.on_navigate_to,
            10,
        )
        self.create_subscription(
            Empty, "/omnifleet_a2/waypoints/stop", self.on_stop, 10
        )
        self.create_subscription(
            Empty, "/omnifleet_a2/waypoints/undo", self.on_undo, 10
        )
        self.create_subscription(
            Empty, "/omnifleet_a2/waypoints/clear", self.on_clear, 10
        )
        self.create_timer(1.0, self.refresh_nav2_ready)

        try:
            self.waypoints = load_route(self.route_file)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            self.get_logger().warning(f"无法加载已有路线：{error}")
        self.publish_visuals()
        self.publish_status(
            f"面板已启动，当前有 {len(self.waypoints)} 个语义点；等待导航就绪"
        )

    def publish_status(self, text: str) -> None:
        message = String()
        message.data = text
        self.status_pub.publish(message)
        self.get_logger().info(text)

    def persist(self) -> None:
        save_route(self.route_file, self.frame_id, self.waypoints)

    def publish_catalog(self) -> None:
        catalog = {
            "version": 1,
            "frame_id": self.frame_id,
            "pending_name": self.pending_name,
            "nav2_ready": self.nav2_ready,
            "navigation_active": self.navigation_active,
            "waypoints": [],
        }
        for index, waypoint in enumerate(self.waypoints, start=1):
            pose = waypoint.pose
            sin_yaw = 2.0 * (
                pose.orientation.w * pose.orientation.z
                + pose.orientation.x * pose.orientation.y
            )
            cos_yaw = 1.0 - 2.0 * (
                pose.orientation.y * pose.orientation.y
                + pose.orientation.z * pose.orientation.z
            )
            catalog["waypoints"].append(
                {
                    "index": index,
                    "name": waypoint.name,
                    "x": pose.position.x,
                    "y": pose.position.y,
                    "yaw_deg": math.degrees(math.atan2(sin_yaw, cos_yaw)),
                }
            )
        message = String()
        message.data = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
        self.catalog_pub.publish(message)

    def publish_visuals(self) -> None:
        now = self.get_clock().now().to_msg()
        path = NavPath()
        path.header.frame_id = self.frame_id
        path.header.stamp = now
        for waypoint in self.waypoints:
            stamped = PoseStamped()
            stamped.header.frame_id = self.frame_id
            stamped.header.stamp = now
            stamped.pose = waypoint.pose
            path.poses.append(stamped)
        self.path_pub.publish(path)

        markers = MarkerArray()
        clear = Marker()
        clear.action = Marker.DELETEALL
        markers.markers.append(clear)
        for index, waypoint in enumerate(self.waypoints):
            pose = waypoint.pose
            point = Marker()
            point.header.frame_id = self.frame_id
            point.header.stamp = now
            point.ns = "omnifleet_a2_waypoints"
            point.id = index * 2
            point.type = Marker.ARROW
            point.action = Marker.ADD
            point.pose = pose
            point.scale.x = 0.45
            point.scale.y = 0.10
            point.scale.z = 0.10
            point.color.r = 0.10
            point.color.g = 0.85
            point.color.b = 0.25
            point.color.a = 1.0
            markers.markers.append(point)

            label = Marker()
            label.header.frame_id = self.frame_id
            label.header.stamp = now
            label.ns = "omnifleet_a2_waypoint_labels"
            label.id = index * 2 + 1
            label.type = Marker.TEXT_VIEW_FACING
            label.action = Marker.ADD
            label.pose.position.x = pose.position.x
            label.pose.position.y = pose.position.y
            label.pose.position.z = 0.35
            label.pose.orientation.w = 1.0
            label.scale.z = 0.24
            label.color.r = 1.0
            label.color.g = 0.85
            label.color.b = 0.05
            label.color.a = 1.0
            label.text = waypoint.name
            markers.markers.append(label)
        self.markers_pub.publish(markers)
        self.publish_catalog()

    def on_next_name(self, message: String) -> None:
        if self.navigation_active:
            self.publish_status("正在导航，必须先点击停止才能设置点位名称")
            return
        self.pending_name = " ".join(message.data.split())
        self.publish_catalog()
        if self.pending_name:
            self.publish_status(f"下一个点将命名为：{self.pending_name}")
        else:
            self.publish_status(
                f"下一个点未命名，将自动使用：航点{len(self.waypoints) + 1}"
            )

    def on_rename(self, message: String) -> None:
        if self.navigation_active:
            self.publish_status("正在导航，必须先点击停止才能重命名点位")
            return
        try:
            request = json.loads(message.data)
            index = request.get("index")
            if isinstance(index, bool) or not isinstance(index, int):
                raise ValueError("序号必须是整数")
            if index < 1 or index > len(self.waypoints):
                raise ValueError("序号不存在")
            name = waypoint_name(request.get("name"), index)
        except (AttributeError, json.JSONDecodeError, ValueError) as error:
            self.publish_status(f"重命名失败：{error}")
            return
        self.waypoints[index - 1].name = name
        self.persist()
        self.publish_visuals()
        self.publish_status(f"第 {index} 个点已命名为：{name}")

    def on_add_pose(self, message: PoseStamped) -> None:
        if self.navigation_active:
            self.publish_status("正在导航，必须先点击停止才能修改路线")
            return
        frame_id = message.header.frame_id or self.frame_id
        if frame_id != self.frame_id:
            self.publish_status(f"添加失败：点位坐标系必须是 {self.frame_id}")
            return
        try:
            pose = normalized_pose(message.pose)
        except ValueError as error:
            self.publish_status(f"添加失败：{error}")
            return
        index = len(self.waypoints) + 1
        name = waypoint_name(self.pending_name, index)
        self.pending_name = ""
        self.waypoints.append(SemanticWaypoint(name=name, pose=pose))
        self.persist()
        self.publish_visuals()
        self.publish_status(
            f"已添加第 {index} 个点“{name}”："
            f"x={pose.position.x:.2f}, y={pose.position.y:.2f}"
        )

    def navigation_blockers(self) -> list[str]:
        return [] if self.action_client.server_is_ready() else ["Nav2"]

    def begin_navigation(self, waypoints: list[SemanticWaypoint]) -> None:
        goal = NavigateThroughPoses.Goal()
        stamp = self.get_clock().now().to_msg()
        for waypoint in waypoints:
            pose = PoseStamped()
            pose.header.frame_id = self.frame_id
            pose.header.stamp = stamp
            pose.pose = waypoint.pose
            goal.poses.append(pose)
        self.active_route_names = [waypoint.name for waypoint in waypoints]
        self.navigation_active = True
        self.active_goal_handle = None
        self.cancel_after_accept = False
        self.last_remaining = None
        self.publish_catalog()
        future = self.action_client.send_goal_async(
            goal, feedback_callback=self.on_action_feedback
        )
        future.add_done_callback(self.on_goal_response)

    def on_start(self, _message: Empty) -> None:
        if self.navigation_active:
            self.publish_status("路线已经在执行，请勿重复点击开始")
            return
        if not self.waypoints:
            self.publish_status("不能开始：请先在地图上添加至少一个点")
            return
        missing = self.navigation_blockers()
        if missing:
            self.publish_status("不能开始：等待" + "和".join(missing) + "就绪")
            return
        self.begin_navigation(self.waypoints)
        names = " → ".join(waypoint.name for waypoint in self.waypoints)
        self.publish_status(
            f"已发送 {len(self.waypoints)} 个语义点，路线：{names}"
        )

    def on_navigate_to(self, message: String) -> None:
        if self.navigation_active:
            self.publish_status("导航已经在执行，请先点击停止导航")
            return
        try:
            _index, waypoint = resolve_waypoint(self.waypoints, message.data)
        except ValueError as error:
            self.publish_status(f"指定语义点失败：{error}")
            return
        missing = self.navigation_blockers()
        if missing:
            self.publish_status("不能开始：等待" + "和".join(missing) + "就绪")
            return
        self.begin_navigation([waypoint])
        self.publish_status(f"已发送单点语义目标：{waypoint.name}")

    def on_stop(self, _message: Empty) -> None:
        if self.pending_cancel_responses:
            self.publish_status("停止全部导航请求正在处理……")
            return

        missing = [
            label for label, client in self.cancel_clients if not client.service_is_ready()
        ]
        if missing:
            self.publish_status(
                "停止失败：等待Nav2取消服务（" + "、".join(missing) + "）就绪"
            )
            return

        if self.navigation_active and self.active_goal_handle is None:
            self.cancel_after_accept = True

        self.pending_cancel_responses = len(self.cancel_clients)
        self.cancelled_goal_count = 0
        self.cancel_errors = []
        for _label, client in self.cancel_clients:
            future = client.call_async(CancelGoal.Request())
            future.add_done_callback(self.on_cancel_all_response)
        self.publish_status("正在停止全部导航……")

    def on_cancel_all_response(self, future) -> None:
        try:
            self.cancelled_goal_count += len(future.result().goals_canceling)
        except Exception as error:
            self.cancel_errors.append(str(error))
        self.pending_cancel_responses -= 1
        if self.pending_cancel_responses:
            return
        if self.cancel_errors:
            self.publish_status(
                "停止请求部分失败：" + "；".join(self.cancel_errors)
            )
            return
        self.publish_status(
            f"停止全部导航请求已确认，取消目标数：{self.cancelled_goal_count}"
        )

    def on_cancel_response(self, future) -> None:
        try:
            count = len(future.result().goals_canceling)
            self.publish_status(f"停止请求已确认，取消目标数：{count}")
        except Exception as error:
            self.publish_status(f"停止请求失败：{error}")

    def on_undo(self, _message: Empty) -> None:
        if self.navigation_active:
            self.publish_status("正在导航，必须先点击停止才能撤销点位")
            return
        if not self.waypoints:
            self.publish_status("路线为空，没有可以撤销的点")
            return
        removed = self.waypoints.pop()
        self.persist()
        self.publish_visuals()
        self.publish_status(
            f"已撤销“{removed.name}”，剩余 {len(self.waypoints)} 个点"
        )

    def on_clear(self, _message: Empty) -> None:
        if self.navigation_active:
            self.publish_status("正在导航，必须先点击停止才能清空路线")
            return
        self.waypoints.clear()
        self.pending_name = ""
        self.persist()
        self.publish_visuals()
        self.publish_status("路线已经清空")

    def refresh_nav2_ready(self) -> None:
        ready = self.action_client.server_is_ready()
        if ready == self.nav2_ready:
            return
        self.nav2_ready = ready
        self.publish_catalog()
        if ready and not self.navigation_active:
            self.publish_status(
                f"系统已就绪；已选 {len(self.waypoints)} 个点，可以点击开始整条路线"
            )

    def on_goal_response(self, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as error:
            self.finish_navigation(f"Nav2目标提交失败：{error}")
            return
        if not goal_handle.accepted:
            self.finish_navigation("Nav2拒绝了这条路线")
            return
        self.active_goal_handle = goal_handle
        result = goal_handle.get_result_async()
        result.add_done_callback(self.on_action_result)
        if self.cancel_after_accept:
            cancel = goal_handle.cancel_goal_async()
            cancel.add_done_callback(self.on_cancel_response)
            return
        if len(self.active_route_names) == 1:
            self.publish_status(f"Nav2 已接受语义目标：{self.active_route_names[0]}")
        else:
            self.publish_status(f"Nav2 已接受 {len(self.active_route_names)} 点路线")

    def on_action_feedback(self, feedback_message) -> None:
        feedback = feedback_message.feedback
        remaining = getattr(feedback, "number_of_poses_remaining", None)
        if remaining is None or remaining == self.last_remaining:
            return
        self.last_remaining = remaining
        self.publish_status(f"路线执行中，剩余 {remaining} 个目标点")

    def on_action_result(self, future) -> None:
        try:
            wrapped = future.result()
            status = int(wrapped.status)
            detail = str(wrapped.result)
        except Exception as error:
            self.finish_navigation(f"读取导航结果失败：{error}")
            return
        names = self.active_route_names
        if status == GoalStatus.STATUS_SUCCEEDED:
            text = (
                f"已到达语义点：{names[0]}"
                if len(names) == 1
                else f"路线完成：共 {len(names)} 个点"
            )
        elif status == GoalStatus.STATUS_CANCELED:
            text = "导航已停止"
        else:
            text = f"路线未完成：状态码 {status}，{detail}"
        self.finish_navigation(text)

    def finish_navigation(self, text: str) -> None:
        self.navigation_active = False
        self.active_route_names = []
        self.active_goal_handle = None
        self.cancel_after_accept = False
        self.last_remaining = None
        self.publish_catalog()
        self.publish_status(text)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = WaypointUiBridge()
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
