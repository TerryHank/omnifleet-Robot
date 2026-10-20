#!/usr/bin/env python3
import json
import math
import os
import copy
import time
import shutil
import signal
from dataclasses import dataclass
from pathlib import Path

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Pose, PoseStamped
from nav_msgs.msg import Path as NavPath
from nav2_msgs.action import ComputePathThroughPoses
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.signals import SignalHandlerOptions
from std_msgs.msg import Empty, String
from visualization_msgs.msg import Marker, MarkerArray


MAP_SAVE_TOPIC = "/omnifleet_t2/waypoints/map_save"
MAP_LOAD_TOPIC = "/omnifleet_t2/waypoints/map_load"


@dataclass
class SemanticWaypoint:
    name: str
    pose: Pose
    kind: str = "pass"
    dwell_seconds: float = 0.0


def validate_waypoint_options(kind, dwell):
    if kind not in ("pass", "stop"):
        raise ValueError("航点类型只能是途经或停靠")
    if isinstance(dwell, bool) or not isinstance(dwell, (int, float)) or not math.isfinite(dwell) or not 0 <= dwell <= 600:
        raise ValueError("停靠等待时间必须在0到600秒之间")
    return kind, float(dwell)


def load_pass_radius(path):
    radius = json.loads(path.read_text()).get("pass_radius", 0.25) if path.is_file() else 0.25
    if isinstance(radius, bool) or not isinstance(radius, (int, float)) or not math.isfinite(radius) or not .05 <= radius <= .5:
        raise ValueError("途经半径必须在0.05到0.50米之间")
    return float(radius)


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


def map_sidecar_path(map_path: object) -> Path:
    """Return the waypoint sidecar path for a MOLA map prefix."""
    value = str(map_path).strip()
    for suffix in (".mm", ".simplemap"):
        if value.lower().endswith(suffix):
            value = value[: -len(suffix)]
            break
    prefix = Path(value).expanduser()
    if not value or prefix.name in {"", ".", ".."}:
        raise ValueError("地图路径前缀不能为空")
    return Path(f"{prefix}.waypoints.json")


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
            kind, dwell = validate_waypoint_options(record.get("kind", "stop"), record.get("dwell_seconds", 0.0))
            waypoints.append(
                SemanticWaypoint(
                    name=waypoint_name(record.get("name"), index),
                    pose=record_to_pose(record["pose"]),
                    kind=kind, dwell_seconds=dwell,
                )
            )
        return waypoints

    poses = data.get("poses", [])
    if not isinstance(poses, list):
        raise ValueError("路线文件格式不正确")
    return [
        SemanticWaypoint(name=waypoint_name("", index), pose=record_to_pose(record), kind="stop")
        for index, record in enumerate(poses, start=1)
    ]


def save_route(path: Path, frame_id: str, waypoints: list[SemanticWaypoint], pass_radius=.25) -> None:
    if isinstance(pass_radius, bool) or not math.isfinite(pass_radius) or not .05 <= pass_radius <= .5:
        raise ValueError("途经半径必须在0.05到0.50米之间")
    for waypoint in waypoints:
        validate_waypoint_options(waypoint.kind, waypoint.dwell_seconds)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 2,
        "frame_id": frame_id,
        "pass_radius": pass_radius,
        "waypoints": [
            {"name": waypoint.name, "pose": pose_to_record(waypoint.pose), "kind": waypoint.kind, "dwell_seconds": waypoint.dwell_seconds}
            for waypoint in waypoints
        ],
    }
    if path.is_file():
        shutil.copy2(path, path.with_name(path.name + f".backup-{time.time_ns()}"))
    temporary = path.with_suffix(f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


class WaypointUiBridge(Node):
    def __init__(self) -> None:
        super().__init__("omnifleet_t2_waypoint_ui")
        self.declare_parameter("frame_id", "map")
        self.declare_parameter(
            "route_file", "/home/iecme/omnifleet_data/missions/waypoints.json"
        )
        self.frame_id = str(self.get_parameter("frame_id").value)
        self.route_file = Path(
            str(self.get_parameter("route_file").value)
        ).expanduser()
        self.waypoints = []
        self.pass_radius = .25
        self.pending_name = ""
        self.nav2_ready = False
        self.navigation_active = False
        self.edit_navigation_state = None
        self.edit_navigation_time = 0.0
        self.preview_planner_id = "GridBased"
        self.preview_effective_planner = "GridBased"
        self.preview_ready = False
        self.preview_revision = 0
        self.preview_in_flight = False
        self.preview_dirty = False
        self.preview_state = "empty"
        self.preview_pose_count = 0
        self.preview_waypoint_count = 0
        self.preview_goal_handle = None
        self.execution = None

        latched = QoSProfile(depth=1)
        latched.reliability = ReliabilityPolicy.RELIABLE
        latched.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.status_pub = self.create_publisher(
            String, "/omnifleet_t2/waypoints/status", latched
        )
        self.path_pub = self.create_publisher(
            NavPath, "/omnifleet_t2/waypoints/path", latched
        )
        self.markers_pub = self.create_publisher(
            MarkerArray, "/omnifleet_t2/waypoints/markers", latched
        )
        self.catalog_pub = self.create_publisher(
            String, "/omnifleet_t2/waypoints/catalog", latched
        )
        self.preview_client = ActionClient(
            self, ComputePathThroughPoses, "compute_path_through_poses"
        )

        self.create_subscription(
            PoseStamped,
            "/omnifleet_t2/waypoints/add_pose",
            self.on_add_pose,
            10,
        )
        self.create_subscription(
            String, "/omnifleet_t2/waypoints/next_name", self.on_next_name, 10
        )
        self.create_subscription(
            String, "/omnifleet_t2/waypoints/rename", self.on_rename, 10
        )
        self.create_subscription(
            Empty, "/omnifleet_t2/waypoints/start", self.on_start, 10
        )
        self.create_subscription(
            String,
            "/omnifleet_t2/waypoints/navigate_to",
            self.on_navigate_to,
            10,
        )
        self.create_subscription(
            Empty, "/omnifleet_t2/waypoints/stop", self.on_stop, 10
        )
        self.create_subscription(
            Empty, "/omnifleet_t2/waypoints/undo", self.on_undo, 10
        )
        self.create_subscription(
            Empty, "/omnifleet_t2/waypoints/clear", self.on_clear, 10
        )
        self.create_subscription(String, MAP_SAVE_TOPIC, self.on_map_save, 10)
        self.create_subscription(String, MAP_LOAD_TOPIC, self.on_map_load, 10)
        from .map_bundle import install_map_bundle
        install_map_bundle(self)
        self.create_subscription(
            String, "/planner_selector", self.on_planner_selector, latched
        )
        update_topic = ('/'+self.frame_id.rpartition('/')[0] if '/' in self.frame_id else '')+'/omnifleet_t2/waypoints/update'
        self.create_subscription(String, update_topic, self.on_update_options, 10)
        self.create_subscription(String, "/navigation/status", self.on_edit_navigation_state, 10)
        from omnifleet_local_navigation.client import NavigationClient
        self.execution = NavigationClient(self)
        self.create_timer(1.0, self.refresh_nav2_ready)

        try:
            self.waypoints = load_route(self.route_file)
            self.pass_radius = load_pass_radius(self.route_file)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            self.get_logger().warning(f"无法加载已有路线：{error}")
        from .map_lifecycle import install_map_lifecycle
        install_map_lifecycle(self)
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
        save_route(self.route_file, self.frame_id, self.waypoints, self.pass_radius)

    def on_edit_navigation_state(self, message):
        try:
            state = json.loads(message.data)
            if isinstance(state, dict) and isinstance(state.get("navigation_active"), bool):
                self.edit_navigation_state = state
                self.edit_navigation_time = time.monotonic()
                self.map_lifecycle.observe_status(state)
        except (ValueError, TypeError):
            pass

    def on_update_options(self, message):
        if getattr(getattr(self, "map_lifecycle", None), "blocked", False):
            self.publish_status("地图正在切换或旧航点清除未确认，暂不能操作航点")
            return
        if self.navigation_active:
            self.publish_status("正在执行或取消任务，不能修改路线")
            return
        try:
            request = json.loads(message.data)
            if not isinstance(request, dict):
                raise ValueError("航点更新必须是对象")
            waypoints = copy.deepcopy(self.waypoints)
            radius = self.pass_radius
            if request.get("convert_intermediate") is True:
                for point in waypoints[:-1]:
                    point.kind, point.dwell_seconds = "pass", 0.0
            elif "pass_radius" in request:
                radius = request["pass_radius"]
                if isinstance(radius, bool) or not isinstance(radius, (int, float)) or not math.isfinite(radius) or not .05 <= radius <= .5:
                    raise ValueError("途经半径必须在0.05到0.50米之间")
            else:
                index = request["index"]
                if type(index) is not int or not 1 <= index <= len(waypoints):
                    raise ValueError("航点序号不存在")
                point = waypoints[index-1]
                if "position" in request:
                    if self.edit_navigation_state is None or time.monotonic() - self.edit_navigation_time > 2.0:
                        raise ValueError("导航状态过期，暂不能移动航点")
                    if self.edit_navigation_state["navigation_active"]:
                        raise ValueError("正在执行导航，不能移动航点")
                    if request.get("frame_id") != self.frame_id:
                        raise ValueError("航点坐标系不匹配")
                    position = request["position"]
                    previous = request.get("previous_position")
                    if not isinstance(position, dict) or not isinstance(previous, dict):
                        raise ValueError("缺少位置或原位置")
                    for values in (position, previous):
                        if any(type(values.get(k)) not in (int, float) or not math.isfinite(values[k]) for k in ("x", "y")):
                            raise ValueError("航点坐标必须是有限数值")
                    if request.get("name") != point.name or abs(previous["x"] - point.pose.position.x) > 1e-4 or abs(previous["y"] - point.pose.position.y) > 1e-4:
                        raise ValueError("航点已被其他操作修改，请重新拖动")
                    point.pose.position.x = float(position["x"])
                    point.pose.position.y = float(position["y"])
                point.kind, point.dwell_seconds = validate_waypoint_options(request.get("kind", point.kind), request.get("dwell_seconds", point.dwell_seconds))
            save_route(self.route_file, self.frame_id, waypoints, radius)
            self.waypoints, self.pass_radius = waypoints, radius
            self.publish_visuals()
            self.publish_status("航点位置已保存" if "position" in request else "航点类型、等待时间和途经半径已保存")
        except (ValueError, KeyError, TypeError, OSError) as error:
            self.publish_status(f"航点设置未保存：{error}")

    def on_map_save(self, message: String) -> None:
        try:
            sidecar = map_sidecar_path(message.data)
            save_route(sidecar, self.frame_id, self.waypoints, self.pass_radius)
        except (OSError, ValueError) as error:
            self.publish_status(f"地图航点保存失败：{error}")
            return
        self.route_file = sidecar
        self.publish_status(
            f"地图航点已保存：{sidecar}（共 {len(self.waypoints)} 个点）"
        )

    def on_map_load(self, message: String) -> None:
        if self.navigation_active:
            self.publish_status("正在导航，必须先点击停止才能加载地图航点")
            return
        try:
            sidecar = map_sidecar_path(message.data)
            loaded = load_route(sidecar)
            radius = load_pass_radius(sidecar)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            self.publish_status(f"地图航点加载失败：{error}")
            return
        self.route_file = sidecar
        self.waypoints = loaded
        self.pass_radius = radius
        self.pending_name = ""
        self.publish_visuals()
        if sidecar.is_file():
            self.publish_status(
                f"地图航点已加载：{sidecar}（共 {len(self.waypoints)} 个点）"
            )
        else:
            self.publish_status(f"该地图没有航点文件：{sidecar}")

    def publish_catalog(self) -> None:
        catalog = {
            "version": 2,
            "pass_radius": self.pass_radius,
            "execution": self.execution.catalog() if self.execution else {},
            "frame_id": self.frame_id,
            "map_valid": not getattr(getattr(self, "map_lifecycle", None), "blocked", False),
            "route_file": str(self.route_file),
            "pending_name": self.pending_name,
            "nav2_ready": self.nav2_ready,
            "navigation_active": self.navigation_active,
            "route_preview": {
                "state": self.preview_state,
                "planner_id": self.preview_effective_planner if self.preview_state == 'ready' else self.preview_planner_id,
                "pose_count": self.preview_pose_count,
                "waypoint_count": self.preview_waypoint_count,
            },
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
                    "kind": waypoint.kind,
                    "dwell_seconds": waypoint.dwell_seconds,
                    "effective_kind": "stop" if index == len(self.waypoints) else waypoint.kind,
                }
            )
        message = String()
        message.data = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
        self.catalog_pub.publish(message)

    def publish_visuals(self) -> None:
        if self.execution and not self.navigation_active:
            self.execution.states = []
            self.execution.phase = 'idle'
        now = self.get_clock().now().to_msg()
        markers = MarkerArray()
        clear = Marker()
        clear.action = Marker.DELETEALL
        markers.markers.append(clear)
        for index, waypoint in enumerate(self.waypoints):
            pose = waypoint.pose
            point = Marker()
            point.header.frame_id = self.frame_id
            point.header.stamp = now
            point.ns = "omnifleet_t2_waypoints"
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
            label.ns = "omnifleet_t2_waypoint_labels"
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
        self.request_route_preview()
        self.publish_catalog()

    def publish_empty_preview(self) -> None:
        path = NavPath()
        path.header.frame_id = self.frame_id
        path.header.stamp = self.get_clock().now().to_msg()
        self.path_pub.publish(path)

    def request_route_preview(self) -> None:
        self.preview_revision += 1
        self.preview_pose_count = 0
        self.preview_waypoint_count = 0
        self.publish_empty_preview()
        if not self.waypoints:
            self.preview_state = "empty"
            self.preview_dirty = False
            return
        self.preview_state = "waiting" if not self.preview_ready else "pending"
        self.preview_dirty = True
        self.dispatch_route_preview()

    def dispatch_route_preview(self) -> None:
        if (
            self.navigation_active
            or self.preview_in_flight
            or not self.preview_dirty
            or not self.preview_ready
            or not self.nav2_ready
            or not self.waypoints
        ):
            return

        revision = self.preview_revision
        planner_id = self.preview_planner_id
        waypoint_count = len(self.waypoints)
        stamp = self.get_clock().now().to_msg()
        goal = ComputePathThroughPoses.Goal()
        goal.planner_id = planner_id
        goal.use_start = False
        from omnifleet_local_navigation.route_execution import oriented_route
        initial_yaw = None
        if self.execution and self.execution.pose:
            from omnifleet_local_navigation.route_execution import yaw
            initial_yaw = yaw(self.execution.pose[1].pose.pose)
        for waypoint in oriented_route(self.waypoints, initial_yaw):
            pose = PoseStamped()
            pose.header.frame_id = self.frame_id
            pose.header.stamp = stamp
            pose.pose = waypoint.pose
            goal.goals.append(pose)

        self.preview_in_flight = True
        self.preview_dirty = False
        self.preview_state = "planning"
        future = self.preview_client.send_goal_async(goal)
        future.add_done_callback(
            lambda result: self.on_preview_goal_response(
                result, revision, planner_id, waypoint_count
            )
        )

    def on_preview_goal_response(
        self, future, revision: int, planner_id: str, waypoint_count: int
    ) -> None:
        try:
            goal_handle = future.result()
        except Exception as error:
            self.finish_route_preview(
                revision, planner_id, waypoint_count, error=str(error)
            )
            return
        if not goal_handle.accepted:
            self.finish_route_preview(
                revision, planner_id, waypoint_count, error="规划器拒绝请求"
            )
            return
        if revision != self.preview_revision or self.navigation_active:
            goal_handle.cancel_goal_async()
            return
        self.preview_goal_handle = goal_handle
        result = goal_handle.get_result_async()
        result.add_done_callback(
            lambda response: self.on_preview_result(
                response, revision, planner_id, waypoint_count
            )
        )

    def on_preview_result(
        self, future, revision: int, planner_id: str, waypoint_count: int
    ) -> None:
        try:
            wrapped = future.result()
            status = int(wrapped.status)
            path = wrapped.result.path
        except Exception as error:
            self.finish_route_preview(
                revision, planner_id, waypoint_count, error=str(error)
            )
            return
        if status != GoalStatus.STATUS_SUCCEEDED or not path.poses:
            self.finish_route_preview(
                revision,
                planner_id,
                waypoint_count,
                error=f"规划未成功，状态码 {status}",
            )
            return
        self.finish_route_preview(
            revision, planner_id, waypoint_count, path=path
        )

    def finish_route_preview(
        self,
        revision: int,
        planner_id: str,
        waypoint_count: int,
        *,
        path: NavPath | None = None,
        error: str = "",
    ) -> None:
        self.preview_in_flight = False
        self.preview_goal_handle = None
        if revision == self.preview_revision:
            if path is not None:
                self.path_pub.publish(path)
                self.preview_state = "ready"
                self.preview_effective_planner = planner_id
                self.preview_pose_count = len(path.poses)
                self.preview_waypoint_count = waypoint_count
                self.publish_status(
                    f"路线预览已按 {planner_id} 规划："
                    f"{waypoint_count} 个航点，{len(path.poses)} 个路径点"
                )
            else:
                self.publish_empty_preview()
                self.preview_state = "failed"
                self.preview_pose_count = 0
                self.preview_waypoint_count = 0
                self.publish_status(f"路线预览规划失败：{error}")
            self.publish_catalog()
        self.dispatch_route_preview()

    def on_planner_selector(self, message: String) -> None:
        planner_id = message.data.strip()
        if not planner_id or planner_id == self.preview_planner_id:
            return
        self.preview_planner_id = planner_id
        if not self.navigation_active:
            self.request_route_preview()
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
        if getattr(getattr(self, "map_lifecycle", None), "blocked", False):
            self.publish_status("地图正在切换或旧航点清除未确认，暂不能操作航点")
            return
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
        updated = self.waypoints + [SemanticWaypoint(name=name, pose=pose)]
        try:
            save_route(self.route_file, self.frame_id, updated, self.pass_radius)
        except OSError as error:
            self.publish_status(f"添加失败：路线保存失败：{error}")
            return
        self.pending_name = ""
        self.waypoints = updated
        self.publish_visuals()
        self.publish_status(
            f"已添加第 {index} 个点“{name}”："
            f"x={pose.position.x:.2f}, y={pose.position.y:.2f}"
        )




    def on_start(self, _message: Empty) -> None:
        if getattr(getattr(self, "map_lifecycle", None), "blocked", False):
            self.publish_status("地图正在切换或旧航点清除未确认，暂不能操作航点")
            return
        self.publish_catalog()
        self.execution.start(self.waypoints)

    def on_navigate_to(self, message: String) -> None:
        if getattr(getattr(self, "map_lifecycle", None), "blocked", False):
            self.publish_status("地图正在切换或旧航点清除未确认，暂不能操作航点")
            return
        try:
            _index, waypoint = resolve_waypoint(self.waypoints, message.data)
        except ValueError as error:
            self.publish_status(f"指定语义点失败：{error}")
            return
        self.publish_catalog()
        self.execution.start([waypoint], single_point=True)

    def on_stop(self, _message: Empty) -> None:
        self.execution.stop("用户停止本车导航")



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
        ready = self.execution.navigator.server_is_ready() and self.execution.inputs_ready()
        preview_ready = self.preview_client.server_is_ready()
        changed = ready != self.nav2_ready or preview_ready != self.preview_ready
        self.nav2_ready = ready
        self.preview_ready = preview_ready
        if preview_ready:
            self.dispatch_route_preview()
        self.publish_catalog()
        if not ready and not self.navigation_active:
            self.publish_status("等待导航就绪："+self.execution.health.reason)
        if changed:
            self.publish_catalog()
            if ready and not self.navigation_active:
                self.publish_status(
                    f"系统已就绪；{self.execution.health.reason}；"
                    + (f"已选 {len(self.waypoints)} 个点，可以点击开始整条路线" if self.waypoints else "当前无航点，请先在地图中添加")
                )






def main(args=None) -> None:
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = WaypointUiBridge()
    stopping = [False]
    previous = {sig: signal.signal(sig, lambda *_: stopping.__setitem__(0, True)) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        while rclpy.ok() and not stopping[0]:
            rclpy.spin_once(node, timeout_sec=.1)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok() and node.navigation_active:
            node.on_stop(Empty())
            deadline = time.monotonic()+5
            while rclpy.ok() and node.navigation_active and time.monotonic()<deadline:
                rclpy.spin_once(node, timeout_sec=.05)
            if node.navigation_active:
                node.get_logger().error("关闭前未确认取消导航；请停止整个导航栈")
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
