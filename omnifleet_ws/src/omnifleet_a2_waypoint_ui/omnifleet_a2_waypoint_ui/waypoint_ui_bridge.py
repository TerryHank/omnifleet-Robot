#!/usr/bin/env python3
from collections import deque
import json
from copy import deepcopy
import math
import os
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import rclpy
from action_msgs.msg import GoalStatus
from action_msgs.srv import CancelGoal
from geometry_msgs.msg import PointStamped, Pose, PoseStamped
from nav_msgs.msg import Path as NavPath
from nav2_msgs.action import ComputePathThroughPoses, ComputePathToPose, FollowPath, NavigateThroughPoses
from nav2_msgs.srv import GetCostmap, IsPathValid
from rcl_interfaces.msg import Log
from rcl_interfaces.srv import GetParameters
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from std_msgs.msg import Empty, String
from tf2_geometry_msgs import do_transform_point
from tf2_ros import Buffer, TransformException, TransformListener
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


def save_route(path: Path, frame_id: str, waypoints: list[SemanticWaypoint], **map_binding) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 2,
        "frame_id": frame_id,
        **map_binding,
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


POINT_GOAL_TOLERANCE = 0.10
POINT_APPROACH_CLEARANCE = 0.13
POINT_MAX_REPLANS = 2
RPP_COLLISION_MESSAGE = "RegulatedPurePursuitController detected collision ahead!"


def planar_yaw(q) -> float:
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    )


def terminal_approach(poses) -> float:
    end = poses[-1].pose.position
    start = next(
        (p.pose.position for p in reversed(poses[:-1])
         if math.hypot(end.x-p.pose.position.x, end.y-p.pose.position.y) >= 0.30),
        poses[0].pose.position,
    )
    return math.atan2(end.y-start.y, end.x-start.x)


@dataclass
class ClearanceGrid:
    distance: np.ndarray
    origin_x: float
    origin_y: float
    resolution: float
    translation: tuple[float, float]
    yaw: float
    scope: str = ""

    def clearance(self, xy):
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        x = self.translation[0] + c*xy[..., 0] - s*xy[..., 1]
        y = self.translation[1] + s*xy[..., 0] + c*xy[..., 1]
        i = np.floor((x-self.origin_x)/self.resolution).astype(int)
        j = np.floor((y-self.origin_y)/self.resolution).astype(int)
        width, height = self.distance.shape[1], self.distance.shape[0]
        visible = (i >= 0) & (i < width) & (j >= 0) & (j < height)
        result = np.full(i.shape, np.inf)
        result[visible] = np.maximum(
            0., self.distance[j[visible], i[visible]]-self.resolution/math.sqrt(2)
        )
        return result


def route_clearance(poses, sides, grids):
    xy = np.array([(p.pose.position.x, p.pose.position.y) for p in poses])
    yaw = np.unwrap([planar_yaw(p.pose.orientation) for p in poses])
    arc = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]
    samples = np.linspace(0., arc[-1], max(2, math.ceil(arc[-1]/.035)+1))
    xy = np.column_stack([np.interp(samples, arc, xy[:, axis]) for axis in (0, 1)])
    yaw = np.interp(samples, arc, yaw)
    c, s = np.cos(yaw[:, None]), np.sin(yaw[:, None])
    x = xy[:, 0, None] + c*sides[:, 0] - s*sides[:, 1]
    y = xy[:, 1, None] + s*sides[:, 0] + c*sides[:, 1]
    corners = np.stack((x, y), axis=-1)
    distances = np.minimum.reduce([grid.clearance(corners) for grid in grids]).min(axis=1)
    return samples, distances


def route_side_space(poses, sides, grids) -> tuple[float, float]:
    if not grids or not len(sides):
        return POINT_APPROACH_CLEARANCE, 0.0
    samples, distances = route_clearance(poses, sides, grids)
    observed = distances[(samples >= min(.10, samples[-1]/4)) & np.isfinite(distances)]
    room = float(np.quantile(observed, .05)) if len(observed) else POINT_APPROACH_CLEARANCE
    penalty = float(np.mean(np.maximum(0.0, POINT_APPROACH_CLEARANCE-observed))) if len(observed) else 0.0
    return room, penalty


def position_path_score(poses, endpoint_error: float) -> tuple[float, float]:
    length = 0.0
    changes = 0
    previous_direction = None
    for start, end in zip(poses, poses[1:]):
        dx = end.pose.position.x - start.pose.position.x
        dy = end.pose.position.y - start.pose.position.y
        distance = math.hypot(dx, dy)
        if distance < 0.005:
            continue
        q = start.pose.orientation
        forward_x = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        forward_y = 2.0 * (q.w * q.z + q.x * q.y)
        direction = dx * forward_x + dy * forward_y >= 0.0
        if previous_direction is not None and previous_direction != direction:
            changes += 1
        previous_direction = direction
        length += distance
    # An extra shift is worth avoiding when two paths are close in distance.
    return (length + 0.25 * changes, endpoint_error)


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
        self.map_session = None
        self.map_changing = False
        self.pending_name = ""
        self.nav2_ready = False
        self.navigation_active = False
        self.active_route_names = []
        self.active_goal_handle = None
        self.cancel_after_accept = False
        self.last_remaining = None
        self.point_target = None
        self.point_planning = False
        self.point_arrival_cancel = False
        self.point_attempts = []
        self.point_history = deque(maxlen=128)
        self.point_rewind_pending = False
        self.point_rewind_goal = None
        self.point_stable_recovery = False
        self.point_progress_stalled = False
        self.point_progress_replan = False
        self.point_collision_seen = False
        self.point_sent_at = None
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

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
        self.point_navigation = ActionClient(self, FollowPath, "follow_path")
        self.point_via_planner = ActionClient(
            self, ComputePathThroughPoses, "compute_path_through_poses"
        )
        self.point_plan_pub = self.create_publisher(NavPath, "/plan", 1)
        self.point_grid_clients = {
            name: self.create_client(GetCostmap, f"/{name}_costmap/get_costmap")
            for name in ("global", "local")
        }
        self.point_footprint_client = self.create_client(
            GetParameters, "/local_costmap/local_costmap/get_parameters"
        )
        self.create_subscription(Log, "/rosout", self.on_controller_log, 20)
        self.point_planner = ActionClient(
            self, ComputePathToPose, "compute_path_to_pose"
        )
        self.point_path_check = self.create_client(IsPathValid, "is_path_valid")
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
            String, "/omnifleet_a2/waypoints/update", self.on_update, 10
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
        # Volatile so a command published before this node started is never replayed.
        self.create_subscription(PointStamped, "/clicked_point", self.on_clicked_point, 1)
        self.create_timer(0.10, self.check_point_arrival)
        self.create_timer(1.0, self.refresh_nav2_ready)

        from .map_bundle import install_map_bundle
        install_map_bundle(self)
        self.publish_visuals()
        self.publish_status(
            f"面板已启动，当前有 {len(self.waypoints)} 个语义点；等待导航就绪"
        )

    def publish_status(self, text: str) -> None:
        message = String()
        message.data = text
        self.status_pub.publish(message)
        self.get_logger().info(text)

    def sync_map_session(self) -> None:
        publishers = self.get_publishers_info_by_topic("/lidar_odometry/pose")
        identities = {
            bytes(info.endpoint_gid).hex() for info in publishers
            if info.node_name == "mola_integrated_bridge"
        }
        session = next(iter(identities)) if len(identities) == 1 else None
        if session == self.map_session:
            return
        self.map_session = session
        self.map_changing = False
        self.waypoints = []
        self.pending_name = ""
        if session and self.route_file.is_file() and not self.map_changing:
            try:
                route = json.loads(self.route_file.read_text(encoding="utf-8"))
                if route.get("map_session") == session and route.get("frame_id") == self.frame_id:
                    self.waypoints = load_route(self.route_file)
                else:
                    self.persist()
            except (OSError, ValueError, AttributeError) as error:
                self.get_logger().warning(f"航点地图绑定无法恢复：{error}")
        self.publish_visuals()

    def clear_map_waypoints(self) -> None:
        self.waypoints = []
        self.pending_name = ""
        self.persist()
        self.publish_visuals()

    def persist(self) -> None:
        save_route(self.route_file, self.frame_id, self.waypoints, map_session=self.map_session)

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

    def on_update(self, message: String) -> None:
        if self.navigation_active:
            self.publish_status("正在导航，必须先点击停止才能修改路线")
            return
        try:
            request = json.loads(message.data)
            index = request["index"]
            if type(index) is not int or not 1 <= index <= len(self.waypoints):
                raise ValueError("序号不存在")
            waypoint = self.waypoints[index - 1]
            if request["frame_id"] != self.frame_id or request["name"] != waypoint.name:
                raise ValueError("航点已变化，请重新拖动")
            previous, position = request["previous_position"], request["position"]
            old = waypoint.pose.position
            coordinates = [item[axis] for item in (previous, position) for axis in ("x", "y")]
            if any(type(value) not in (int, float) or not math.isfinite(value) for value in coordinates):
                raise ValueError("点位包含无效数字")
            if math.hypot(old.x - previous["x"], old.y - previous["y"]) > 1.e-4:
                raise ValueError("航点已变化，请重新拖动")
        except (KeyError, TypeError, ValueError, OverflowError) as error:
            self.publish_status(f"移动航点失败：{error}")
            return
        updated = deepcopy(waypoint.pose)
        updated.position.x = float(position["x"])
        updated.position.y = float(position["y"])
        self.waypoints[index - 1] = SemanticWaypoint(waypoint.name, updated)
        try:
            self.persist()
        except OSError as error:
            self.waypoints[index - 1] = waypoint
            self.publish_status(f"移动航点失败：{error}")
            return
        self.publish_visuals()
        self.publish_status(f"已保存航点“{waypoint.name}”的新位置")

    def on_add_pose(self, message: PoseStamped) -> None:
        self.sync_map_session()
        if self.map_changing or not self.map_session:
            self.publish_status("请等待当前地图就绪后再保存航点")
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
        self.pending_name = ""
        self.waypoints.append(SemanticWaypoint(name=name, pose=pose))
        self.persist()
        self.publish_visuals()
        self.publish_status(
            f"已添加第 {index} 个点“{name}”："
            f"x={pose.position.x:.2f}, y={pose.position.y:.2f}"
        )

    def on_clicked_point(self, message: PointStamped) -> None:
        if self.navigation_active:
            self.publish_status("导航正在执行，请先点击停止导航")
            return
        point = message.point
        if not all(math.isfinite(value) for value in (point.x, point.y, point.z)):
            self.publish_status("无法导航：点击点坐标无效")
            return
        try:
            frame_id = message.header.frame_id or self.frame_id
            if frame_id != self.frame_id:
                transform = self.tf_buffer.lookup_transform(
                    self.frame_id, frame_id, Time()
                )
                point = do_transform_point(message, transform).point
            base = self.tf_buffer.lookup_transform(
                self.frame_id, "base_link", Time()
            ).transform
        except TransformException as error:
            self.publish_status(f"无法定位点击点：{error}")
            return
        dx = point.x - base.translation.x
        dy = point.y - base.translation.y
        if math.hypot(dx, dy) <= POINT_GOAL_TOLERANCE:
            self.publish_status("已在无方向航点附近")
            return
        if (not self.point_navigation.server_is_ready()
                or not self.point_planner.server_is_ready()
                or not self.point_path_check.service_is_ready()):
            self.publish_status("无法开始无方向导航：等待 Nav2 就绪")
            return

        self.point_target = point
        self.point_history.clear()
        self.navigation_active = True
        self.publish_catalog()
        self.publish_status(f"正在规划无方向航点 x={point.x:.2f}, y={point.y:.2f}")
        self.start_point_planning(point)

    def on_controller_log(self, msg: Log) -> None:
        if (self.point_sent_at is None or msg.name != "controller_server"
                or Time.from_msg(msg.stamp).nanoseconds < self.point_sent_at):
            return
        if RPP_COLLISION_MESSAGE in msg.msg:
            self.point_collision_seen = True
        elif "Failed to make progress" in msg.msg:
            self.point_progress_stalled = True

    def start_point_planning(self, point) -> None:
        self.point_planning = True
        try:
            base = self.tf_buffer.lookup_transform(
                self.frame_id, "base_link", Time()
            ).transform
        except TransformException as error:
            self.finish_navigation(f"无法读取重规划起点：{error}")
            return
        bearing = math.atan2(point.y-base.translation.y, point.x-base.translation.x)
        current = planar_yaw(base.rotation)
        aligned = bearing if math.cos(bearing-current) >= 0.0 else bearing+math.pi
        opposite = aligned + math.pi
        headings = (aligned, current, aligned-.35, aligned+.35, aligned-1.2,
                    aligned+1.2, opposite, opposite-.35, opposite+.35)
        candidates = []
        for yaw in headings:
            if not any(math.cos(yaw-other) > 1.-1.e-10 for other, _ in candidates):
                candidates.append((yaw, None))
        offsets = (-.85, .85) if not self.point_attempts else (-1.25, -.65, .65, 1.25)
        if self.point_via_planner.server_is_ready():
            for offset in offsets:
                direction = bearing + offset
                yaw = direction if math.cos(direction-current) >= 0.0 else direction+math.pi
                candidates.append((yaw, direction))

        requests = {
            name: client.call_async(GetCostmap.Request())
            for name, client in self.point_grid_clients.items() if client.service_is_ready()
        }
        if self.point_footprint_client.service_is_ready():
            requests["footprint"] = self.point_footprint_client.call_async(
                GetParameters.Request(names=["footprint", "footprint_padding"])
            )
        waiting = set(requests)
        if not waiting:
            self.plan_point_candidate(point, ((yaw, direction, None) for yaw, direction in candidates), [], np.empty((0, 2)), None)
            return

        def snapshot_ready(name):
            waiting.discard(name)
            if waiting or self.point_target is not point:
                return
            layers = []
            footprint = []
            padding = 0.
            for key, future in requests.items():
                try:
                    response = future.result()
                    if key == "footprint":
                        footprint = json.loads(response.values[0].string_value or "[]")
                        if len(response.values) > 1:
                            padding = response.values[1].double_value
                        continue
                    grid = response.map
                    meta = grid.metadata
                    cells = np.frombuffer(grid.data, dtype=np.uint8).reshape(
                        meta.size_y, meta.size_x
                    )
                    free = np.empty(cells.shape, dtype=np.uint8)
                    np.not_equal(cells, 254, out=free)
                    if key != "local" and free.all():
                        continue
                    translation, yaw = (0., 0.), 0.
                    if grid.header.frame_id != self.frame_id:
                        transform = self.tf_buffer.lookup_transform(
                            grid.header.frame_id, self.frame_id, Time()
                        ).transform
                        translation = (transform.translation.x, transform.translation.y)
                        yaw = planar_yaw(transform.rotation)
                    distance = cv2.distanceTransform(free, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
                    distance *= meta.resolution
                    layers.append(ClearanceGrid(
                        distance, meta.origin.position.x, meta.origin.position.y,
                        meta.resolution, translation, yaw, key,
                    ))
                except (TransformException, TypeError, ValueError) as error:
                    self.get_logger().warning(f"无法读取航点净空数据 {key}：{error}")
            sides = np.empty((0, 2))
            if footprint:
                front = max(p[0] for p in footprint) + padding
                rear = min(p[0] for p in footprint) - padding
                left = max(p[1] for p in footprint) + padding
                right = min(p[1] for p in footprint) - padding
                sides = np.array(
                    [(x, y) for x in np.linspace(rear, front, 13) for y in (left, right)] +
                    [(x, y) for y in np.linspace(right, left, 9)[1:-1] for x in (rear, front)]
                )
            local = [grid for grid in layers if grid.scope == "local"]
            start_candidates = [(yaw, direction, None) for yaw, direction in candidates]
            if local and len(sides):
                # Resolve an occupied coarse start cell only by following a short,
                # collision-checked straight motion on the finer live costmap.
                for delta in (.08, -.08, .15, -.15):
                    prefix = []
                    for distance in np.linspace(0., delta, 6):
                        pose = PoseStamped()
                        pose.header.frame_id = self.frame_id
                        pose.pose.position.x = base.translation.x + distance*math.cos(current)
                        pose.pose.position.y = base.translation.y + distance*math.sin(current)
                        pose.pose.orientation = base.rotation
                        prefix.append(pose)
                    _, distances = route_clearance(prefix, sides, local)
                    if np.all(np.isfinite(distances) & (distances > 0.0)):
                        start_candidates.extend((yaw, None, prefix)
                                                for yaw in (aligned, aligned+.35, opposite))
            def plan_candidates():
                self.plan_point_candidate(point, iter(start_candidates), layers, sides, None)

            if self.point_rewind_pending:
                self.point_rewind_pending = False
                if self.try_point_rewind(point, base, local, sides, plan_candidates):
                    return
            plan_candidates()

        for name, future in requests.items():
            future.add_done_callback(lambda _future, name=name: snapshot_ready(name))

    def plan_point_candidate(self, point, candidates, grids, sides, best) -> None:
        candidate = next(candidates, None)
        if candidate is None or (candidate[2] is not None and best is not None):
            if best is None:
                text = ("局部避障停车，未找到可通行的其他接近方向"
                        if self.point_attempts else "无方向航点未找到可通行路径")
                self.finish_navigation(text)
                return
            _score, path, approach, room = best
            self.point_attempts.append(approach)
            self.point_planning = False
            self.point_collision_seen = False
            self.point_progress_stalled = False
            self.point_sent_at = self.get_clock().now().nanoseconds
            path.header.stamp = self.get_clock().now().to_msg()
            for pose in path.poses:
                pose.header.stamp = path.header.stamp
            self.point_plan_pub.publish(path)
            self.publish_status(f"已选择无方向航点路线，路线侧向净空评分 {room:.2f} m")
            navigation = self.point_navigation.send_goal_async(FollowPath.Goal(
                path=path, controller_id="FollowPath", goal_checker_id="general_goal_checker",
            ))
            navigation.add_done_callback(self.on_goal_response)
            return

        yaw, direction, prefix = candidate

        def make_pose(x, y):
            p = PoseStamped()
            p.header.frame_id = self.frame_id
            p.header.stamp = self.get_clock().now().to_msg()
            p.pose.position.x, p.pose.position.y = x, y
            p.pose.orientation.z, p.pose.orientation.w = math.sin(yaw/2), math.cos(yaw/2)
            return p

        final = make_pose(point.x, point.y)
        if direction is None:
            request = ComputePathToPose.Goal(goal=final, planner_id="GridBased")
            if prefix:
                request.use_start = True
                request.start = prefix[-1]
                request.start.header.stamp = final.header.stamp
            future = self.point_planner.send_goal_async(request)
        else:
            entry = make_pose(point.x-.60*math.cos(direction), point.y-.60*math.sin(direction))
            future = self.point_via_planner.send_goal_async(
                ComputePathThroughPoses.Goal(goals=[entry, final], planner_id="GridBased")
            )

        def on_plan_response(response):
            if self.point_target is not point:
                return
            try:
                handle = response.result()
            except Exception as error:
                self.finish_navigation(f"无法提交无方向航点规划：{error}")
                return
            if handle.accepted:
                handle.get_result_async().add_done_callback(on_plan_result)
            else:
                self.plan_point_candidate(point, candidates, grids, sides, best)

        def on_plan_result(response):
            if self.point_target is not point:
                return
            try:
                result = response.result()
            except Exception as error:
                self.finish_navigation(f"无法读取无方向航点路线：{error}")
                return
            path = result.result.path
            if result.status == GoalStatus.STATUS_SUCCEEDED and len(path.poses) > 1:
                end = path.poses[-1].pose.position
                error = math.hypot(end.x-point.x, end.y-point.y)
                approach = terminal_approach(path.poses)
                if (error <= POINT_GOAL_TOLERANCE
                        and ((self.point_stable_recovery and not self.point_progress_replan) or all(
                            math.cos(approach-old) < math.cos(.35) for old in self.point_attempts))):
                    validity = self.point_path_check.call_async(IsPathValid.Request(path=path))
                    validity.add_done_callback(
                        lambda reply: on_path_checked(reply, path, approach, error)
                    )
                    return
            self.plan_point_candidate(point, candidates, grids, sides, best)

        def on_path_checked(response, path, approach, error):
            if self.point_target is not point:
                return
            selected = best
            try:
                is_valid = response.result().is_valid
            except Exception as error:
                self.finish_navigation(f"无法检查无方向航点路线：{error}")
                return
            if is_valid and prefix:
                path.poses = prefix[:-1] + list(path.poses)
            local = [grid for grid in grids if grid.scope == "local"]
            if is_valid and local and len(sides):
                _, distances = route_clearance(path.poses, sides, local)
                is_valid = not np.any(distances == 0.)
            if is_valid:
                travel, endpoint_error = position_path_score(path.poses, error)
                room, penalty = route_side_space(path.poses, sides, grids)
                # Wide approaches outrank short paths that hug occupied cells.
                if self.point_stable_recovery:
                    xy = np.array([(p.pose.position.x, p.pose.position.y) for p in path.poses])
                    yaw = np.array([planar_yaw(p.pose.orientation) for p in path.poses[:-1]])
                    steps = np.diff(xy, axis=0)
                    lengths = np.linalg.norm(steps, axis=1)
                    projection = (steps*np.column_stack((np.cos(yaw), np.sin(yaw)))).sum(axis=1)
                    direction = projection[np.abs(projection) > np.maximum(.005, .45*lengths)] > 0
                    changes = int(np.count_nonzero(direction[1:] != direction[:-1]))
                    score = (round(max(0., .065-room), 2), changes,
                             travel+2.0*penalty, endpoint_error)
                else:
                    score = (round(max(0., POINT_APPROACH_CLEARANCE-room), 2),
                             travel+2.0*penalty, endpoint_error)
                if selected is None or score < selected[0]:
                    selected = (score, path, approach, room)
                if (grids and len(sides) and room >= POINT_APPROACH_CLEARANCE
                        and penalty < 1.e-5
                        and travel+error <= self.point_position_error()+.06):
                    self.plan_point_candidate(point, iter(()), grids, sides, selected)
                    return
            self.plan_point_candidate(point, candidates, grids, sides, selected)

        future.add_done_callback(on_plan_response)

    def point_pose(self, base) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = self.frame_id
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = base.translation.x
        pose.pose.position.y = base.translation.y
        pose.pose.orientation = base.rotation
        return pose

    def try_point_rewind(self, point, base, local, sides, fallback) -> bool:
        if not local or not len(sides) or not self.point_path_check.service_is_ready():
            return False
        rewind = NavPath()
        rewind.poses = [self.point_pose(base)]
        rewind.header = rewind.poses[0].header
        length = 0.0
        for old in reversed(self.point_history):
            p, q = rewind.poses[-1].pose.position, old.pose.position
            step = math.hypot(p.x-q.x, p.y-q.y)
            if step < .026:
                continue
            if step > .15:
                return False
            length += step
            pose = deepcopy(old)
            pose.header = rewind.header
            rewind.poses.append(pose)
            if length >= .62:
                break
        if length < .30:
            return False
        _, gaps = route_clearance(rewind.poses, sides, local)
        if not np.all(np.isfinite(gaps) & (gaps > 0.)):
            return False

        def checked(future):
            if self.point_target is not point:
                return
            try:
                result = future.result()
            except Exception:
                fallback()
                return
            if result is None or not result.is_valid:
                fallback()
                return
            self.point_planning = False
            self.point_rewind_goal = rewind.poses[-1].pose.position
            self.publish_status(f"局部障碍阻断，沿已驶轨迹回退约 {length:.2f} 米后重规划")
            goal = self.point_navigation.send_goal_async(
                FollowPath.Goal(path=rewind, controller_id="FollowPath",
                                goal_checker_id="general_goal_checker")
            )
            goal.add_done_callback(self.on_goal_response)

        self.point_path_check.call_async(IsPathValid.Request(path=rewind)).add_done_callback(checked)
        return True

    def point_position_error(self) -> float:
        try:
            base = self.tf_buffer.lookup_transform(
                self.frame_id, "base_link", Time()
            ).transform.translation
        except TransformException:
            return math.inf
        return math.hypot(base.x - self.point_target.x, base.y - self.point_target.y)

    def check_point_arrival(self) -> None:
        if (self.point_target is None or self.active_goal_handle is None
                or self.point_arrival_cancel or self.pending_cancel_responses):
            return
        try:
            base = self.tf_buffer.lookup_transform(self.frame_id, "base_link", Time()).transform
        except TransformException:
            return
        if self.point_rewind_goal is None:
            self.point_history.append(self.point_pose(base))
            goal = self.point_target
            tolerance = POINT_GOAL_TOLERANCE
        else:
            goal = self.point_rewind_goal
            tolerance = .075
        if math.hypot(base.translation.x-goal.x, base.translation.y-goal.y) <= tolerance:
            self.point_arrival_cancel = True
            self.active_goal_handle.cancel_goal_async()

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
        if self.point_planning:
            self.finish_navigation("已停止无方向航点规划")
        elif self.point_target is not None:
            self.cancel_after_accept = True
            if self.active_goal_handle is not None:
                self.active_goal_handle.cancel_goal_async().add_done_callback(
                    self.on_cancel_response
                )
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
        self.sync_map_session()
        ready = self.action_client.server_is_ready()
        changed = ready != self.nav2_ready
        self.nav2_ready = ready
        self.publish_catalog()
        if not changed:
            return
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
        if self.cancel_after_accept:
            cancel = goal_handle.cancel_goal_async()
            cancel.add_done_callback(self.on_cancel_response)
            result.add_done_callback(self.on_action_result)
            return
        if self.point_rewind_goal is not None:
            self.publish_status("Nav2 已接受沿原轨迹回退")
        elif self.point_target is not None:
            self.publish_status("Nav2 已接受无方向航点")
        elif len(self.active_route_names) == 1:
            self.publish_status(f"Nav2 已接受语义目标：{self.active_route_names[0]}")
        else:
            self.publish_status(f"Nav2 已接受 {len(self.active_route_names)} 点路线")
        result.add_done_callback(self.on_action_result)

    def on_action_feedback(self, feedback_message) -> None:
        feedback = feedback_message.feedback
        remaining = getattr(feedback, "number_of_poses_remaining", None)
        if remaining is None or remaining == self.last_remaining:
            return
        self.last_remaining = remaining
        self.publish_status(f"路线执行中，剩余 {remaining} 个目标点")

    def on_action_result(self, future, *, settled=False) -> None:
        try:
            wrapped = future.result()
            status = int(wrapped.status)
            detail = str(wrapped.result)
        except Exception as error:
            self.finish_navigation(f"读取导航结果失败：{error}")
            return
        if self.point_rewind_goal is not None:
            if self.cancel_after_accept or (
                status == GoalStatus.STATUS_CANCELED and not self.point_arrival_cancel
            ):
                self.finish_navigation("已停止无方向航点回退")
                return
            self.active_goal_handle = None
            self.point_rewind_goal = None
            self.point_arrival_cancel = False
            self.point_history.clear()
            self.publish_status("回退结束，重新规划同一航点")
            self.start_point_planning(self.point_target)
            return
        if self.point_target is not None:
            error = self.point_position_error()
            if (status == GoalStatus.STATUS_SUCCEEDED and not settled
                    and not self.cancel_after_accept
                    and POINT_GOAL_TOLERANCE < error <= POINT_GOAL_TOLERANCE + .07):
                point = self.point_target

                def verify_after_stop():
                    self.destroy_timer(timer)
                    if self.point_target is point:
                        self.on_action_result(future, settled=True)

                timer = self.create_timer(.40, verify_after_stop)
                return
            if (status == GoalStatus.STATUS_SUCCEEDED or self.point_arrival_cancel
                    ) and error <= POINT_GOAL_TOLERANCE:
                text = f"已到达无方向航点，位置误差 {error:.2f} m"
            elif self.cancel_after_accept or status == GoalStatus.STATUS_CANCELED:
                text = "无方向航点导航已停止"
            elif (len(self.point_attempts) <= POINT_MAX_REPLANS
                  and (self.point_collision_seen or status == GoalStatus.STATUS_SUCCEEDED
                       or (self.point_stable_recovery and status == GoalStatus.STATUS_ABORTED))):
                self.active_goal_handle = None
                self.point_sent_at = None
                if self.point_collision_seen and len(self.point_attempts) == 1:
                    self.point_rewind_pending = True
                    self.point_stable_recovery = True
                self.point_progress_replan = self.point_progress_stalled or (
                    self.point_stable_recovery and status == GoalStatus.STATUS_ABORTED
                    and not self.point_collision_seen)
                if self.point_progress_replan:
                    reason = "回退绕行后控制器提前结束"
                else:
                    reason = "局部避障停车" if self.point_collision_seen else "控制器已停，尚差目标位置"
                self.publish_status(f"{reason}，从当前位置调整接近方向重规划")
                self.start_point_planning(self.point_target)
                return
            else:
                text = f"无方向航点未到达，距目标 {error:.2f} m，状态码 {status}"
            self.finish_navigation(text)
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
        self.point_attempts.clear()
        self.point_history.clear()
        self.point_rewind_pending = False
        self.point_rewind_goal = None
        self.point_stable_recovery = False
        self.point_progress_stalled = False
        self.point_progress_replan = False
        self.point_collision_seen = False
        self.point_sent_at = None
        self.point_target = None
        self.point_planning = False
        self.point_arrival_cancel = False
        self.navigation_active = False
        self.active_route_names = []
        self.active_goal_handle = None
        self.cancel_after_accept = False
        self.last_remaining = None
        self.publish_catalog()
        self.publish_status(text)


def main(args=None) -> None:
    # Limit the one-shot distance transform to one CPU thread.
    cv2.setNumThreads(1)
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
