"""Lightweight point-goal fleet controller for three Ackermann robots."""

import json
from collections import deque
from dataclasses import dataclass
from itertools import combinations
from math import atan2, hypot
from time import monotonic
from typing import Deque, Dict, Optional, Tuple

import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry, Path
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from std_srvs.srv import Trigger

from .core import (
    Pose2D,
    ackermann_command,
    nearest_available_robot,
    nearest_robot_for_route,
    normalize_waypoints,
    safety_speed_scale,
)


ROBOT_NAMES = ("robot1", "robot2", "robot3")
AUTO_GOALS = {
    "robot1": (2.5, 0.0),
    "robot2": (1.5, 1.2),
    "robot3": (1.5, -1.2),
}


@dataclass
class GoalTask:
    task_id: int
    goal: Tuple[float, float]
    target_robot: Optional[str] = None
    route_id: Optional[int] = None
    waypoint_index: Optional[int] = None
    waypoint_count: Optional[int] = None


@dataclass
class Robot:
    name: str
    pose: Optional[Pose2D] = None
    last_odom: float = 0.0
    online: bool = False
    task: Optional[GoalTask] = None
    state: str = "offline"


class FleetController(Node):
    def __init__(self) -> None:
        super().__init__("fleet_controller")
        self.declare_parameter("auto_demo", True)
        self.declare_parameter("odom_timeout", 1.0)
        self.declare_parameter("startup_settle_time", 2.0)
        self.robots: Dict[str, Robot] = {name: Robot(name) for name in ROBOT_NAMES}
        self.queue: Deque[GoalTask] = deque()
        self.completed_count = 0
        self.next_task_id = 1
        self.next_route_id = 1
        self.auto_demo_sent = False
        self.auto_demo_ready_since = None

        transient_qos = QoSProfile(depth=20)
        transient_qos.reliability = ReliabilityPolicy.RELIABLE
        transient_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.status_pub = self.create_publisher(String, "/fleet/status", transient_qos)
        self.events_pub = self.create_publisher(String, "/fleet/events", transient_qos)
        self.cmd_pubs = {
            name: self.create_publisher(Twist, f"/{name}/cmd_vel", 10)
            for name in ROBOT_NAMES
        }
        self._subscription_refs = []
        for name in ROBOT_NAMES:
            self._subscription_refs.append(
                self.create_subscription(
                    Odometry,
                    f"/{name}/odom",
                    lambda msg, robot_name=name: self._on_odom(robot_name, msg),
                    20,
                )
            )
            self._subscription_refs.append(
                self.create_subscription(
                    Path,
                    f"/{name}/waypoints",
                    lambda msg, robot_name=name: self._on_direct_waypoints(robot_name, msg),
                    10,
                )
            )
            self._subscription_refs.append(
                self.create_subscription(
                    PoseStamped,
                    f"/{name}/goal_pose",
                    lambda msg, robot_name=name: self._on_direct_goal(robot_name, msg),
                    10,
                )
            )
        self._subscription_refs.append(
            self.create_subscription(PoseStamped, "/fleet/goal", self._on_fleet_goal, 10)
        )
        self._subscription_refs.append(
            self.create_subscription(PoseStamped, "/goal_pose", self._on_fleet_goal, 10)
        )
        self._subscription_refs.append(
            self.create_subscription(Path, "/fleet/waypoints", self._on_fleet_waypoints, 10)
        )
        self.create_service(Trigger, "/fleet/cancel_all", self._cancel_all)
        self.create_service(Trigger, "/fleet/clear_queue", self._clear_queue)
        self.create_timer(0.05, self._tick)

    @staticmethod
    def _goal_from_message(msg: PoseStamped) -> Tuple[float, float]:
        return float(msg.pose.position.x), float(msg.pose.position.y)

    def _new_task(
        self,
        goal: Tuple[float, float],
        target: Optional[str] = None,
        route_id: Optional[int] = None,
        waypoint_index: Optional[int] = None,
        waypoint_count: Optional[int] = None,
    ) -> GoalTask:
        task = GoalTask(
            self.next_task_id,
            goal,
            target,
            route_id,
            waypoint_index,
            waypoint_count,
        )
        self.next_task_id += 1
        return task

    @staticmethod
    def _route_fields(task: GoalTask):
        return {
            "route_id": task.route_id,
            "waypoint_index": task.waypoint_index,
            "waypoint_count": task.waypoint_count,
        }

    def _tasks_from_path(self, msg: Path, target: Optional[str]):
        try:
            waypoints = normalize_waypoints(
                (pose.pose.position.x, pose.pose.position.y) for pose in msg.poses
            )
        except ValueError as exc:
            self._event("route_rejected", robot=target, reason=str(exc))
            return []
        route_id = self.next_route_id
        self.next_route_id += 1
        return [
            self._new_task(point, target, route_id, index, len(waypoints))
            for index, point in enumerate(waypoints)
        ]

    def _on_fleet_goal(self, msg: PoseStamped) -> None:
        task = self._new_task(self._goal_from_message(msg))
        robot_name = nearest_available_robot(
            task.goal,
            {name: robot.pose for name, robot in self.robots.items() if robot.pose},
            [name for name, robot in self.robots.items() if robot.online and robot.task is None],
        )
        if robot_name is None:
            self.queue.append(task)
            self._event("queued", task=task.task_id, goal=task.goal)
        else:
            self._assign(robot_name, task)

    def _on_direct_goal(self, robot_name: str, msg: PoseStamped) -> None:
        task = self._new_task(self._goal_from_message(msg), robot_name)
        robot = self.robots[robot_name]
        if robot.online and robot.task is None:
            self._assign(robot_name, task)
        else:
            self.queue.append(task)
            self._event("queued", task=task.task_id, robot=robot_name, goal=task.goal)

    def _on_fleet_waypoints(self, msg: Path) -> None:
        tasks = self._tasks_from_path(msg, None)
        if not tasks:
            return
        selected = nearest_robot_for_route(
            [task.goal for task in tasks],
            {name: robot.pose for name, robot in self.robots.items() if robot.pose},
            [name for name, robot in self.robots.items() if robot.online and robot.task is None],
        )
        if selected:
            for task in tasks:
                task.target_robot = selected
            self._assign(selected, tasks[0])
            for task in reversed(tasks[1:]):
                self.queue.appendleft(task)
        else:
            self.queue.extend(tasks)
            self._event(
                "route_queued",
                route_id=tasks[0].route_id,
                waypoint_count=len(tasks),
            )

    def _on_direct_waypoints(self, robot_name: str, msg: Path) -> None:
        tasks = self._tasks_from_path(msg, robot_name)
        if not tasks:
            return
        robot = self.robots[robot_name]
        if robot.online and robot.task is None:
            self._assign(robot_name, tasks[0])
            for task in reversed(tasks[1:]):
                self.queue.appendleft(task)
        else:
            self.queue.extend(tasks)
            self._event(
                "route_queued",
                robot=robot_name,
                route_id=tasks[0].route_id,
                waypoint_count=len(tasks),
            )

    def _on_odom(self, name: str, msg: Odometry) -> None:
        q = msg.pose.pose.orientation
        yaw = atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        robot = self.robots[name]
        robot.pose = Pose2D(msg.pose.pose.position.x, msg.pose.pose.position.y, yaw)
        robot.last_odom = monotonic()
        if not robot.online:
            robot.online = True
            robot.state = "idle" if robot.task is None else "active"
            self._event("online", robot=name)

    def _assign(self, robot_name: str, task: GoalTask) -> None:
        robot = self.robots[robot_name]
        robot.task = task
        robot.state = "active"
        self._event(
            "assigned",
            task=task.task_id,
            robot=robot_name,
            goal=task.goal,
            **self._route_fields(task),
        )

    def _dispatch_queue(self) -> None:
        for task in list(self.queue):
            if task.target_robot:
                robot = self.robots[task.target_robot]
                selected = task.target_robot if robot.online and robot.task is None else None
            else:
                selected = nearest_available_robot(
                    task.goal,
                    {name: robot.pose for name, robot in self.robots.items() if robot.pose},
                    [name for name, robot in self.robots.items() if robot.online and robot.task is None],
                )
            if selected:
                if task.route_id is not None and task.target_robot is None:
                    for queued_task in self.queue:
                        if queued_task.route_id == task.route_id:
                            queued_task.target_robot = selected
                self.queue.remove(task)
                self._assign(selected, task)

    def _cancel_all(self, _request, response):
        self.queue.clear()
        for robot in self.robots.values():
            robot.task = None
            robot.state = "idle" if robot.online else "offline"
            self.cmd_pubs[robot.name].publish(Twist())
        response.success = True
        response.message = "all active and queued tasks cancelled"
        self._event("cancel_all")
        return response

    def _clear_queue(self, _request, response):
        count = len(self.queue)
        self.queue.clear()
        response.success = True
        response.message = f"cleared {count} queued tasks"
        self._event("clear_queue", count=count)
        return response

    def _event(self, event: str, **fields) -> None:
        msg = String()
        msg.data = json.dumps({"event": event, **fields}, separators=(",", ":"))
        self.events_pub.publish(msg)

    def _pair_distances(self):
        distances = {}
        online = [robot for robot in self.robots.values() if robot.online and robot.pose]
        for left, right in combinations(online, 2):
            distances[(left.name, right.name)] = hypot(
                left.pose.x - right.pose.x, left.pose.y - right.pose.y
            )
        return distances

    def _tick(self) -> None:
        now = monotonic()
        timeout = float(self.get_parameter("odom_timeout").value)
        for robot in self.robots.values():
            if robot.online and now - robot.last_odom > timeout:
                robot.online = False
                robot.state = "offline"
                if robot.task:
                    if robot.task.route_id is None:
                        robot.task.target_robot = None
                    self.queue.appendleft(robot.task)
                    self._event(
                        "requeued_offline",
                        task=robot.task.task_id,
                        robot=robot.name,
                        **self._route_fields(robot.task),
                    )
                    robot.task = None
                self.cmd_pubs[robot.name].publish(Twist())
                self._event("offline", robot=robot.name)

        all_online = all(robot.online for robot in self.robots.values())
        if not all_online:
            self.auto_demo_ready_since = None
        elif bool(self.get_parameter("auto_demo").value) and not self.auto_demo_sent:
            if self.auto_demo_ready_since is None:
                self.auto_demo_ready_since = now
                self._event("startup_settle_started")
            elif now - self.auto_demo_ready_since >= float(
                self.get_parameter("startup_settle_time").value
            ):
                self.auto_demo_sent = True
                for name, goal in AUTO_GOALS.items():
                    self._assign(name, self._new_task(goal, name))
                self._event("auto_demo_started")

        self._dispatch_queue()
        pair_distances = self._pair_distances()
        for robot in self.robots.values():
            command = Twist()
            if robot.online and robot.pose and robot.task:
                distance = hypot(robot.pose.x - robot.task.goal[0], robot.pose.y - robot.task.goal[1])
                if distance <= 0.15:
                    completed_task = robot.task
                    self._event(
                        "completed",
                        task=completed_task.task_id,
                        robot=robot.name,
                        **self._route_fields(completed_task),
                    )
                    robot.task = None
                    robot.state = "idle"
                    self.completed_count += 1
                else:
                    linear, angular = ackermann_command(robot.pose, robot.task.goal)
                    nearest = min(
                        (value for pair, value in pair_distances.items() if robot.name in pair),
                        default=float("inf"),
                    )
                    scale = safety_speed_scale(nearest)
                    command.linear.x = linear * scale
                    command.angular.z = angular * scale
            self.cmd_pubs[robot.name].publish(command)
        self._publish_status(pair_distances)

    def _publish_status(self, pair_distances) -> None:
        status = {
            "robots": {
                name: {
                    "online": robot.online,
                    "state": robot.state,
                    "pose": None if robot.pose is None else [robot.pose.x, robot.pose.y, robot.pose.yaw],
                    "task": None if robot.task is None else robot.task.task_id,
                    "goal": None if robot.task is None else list(robot.task.goal),
                    "route_id": None if robot.task is None else robot.task.route_id,
                    "waypoint_index": None if robot.task is None else robot.task.waypoint_index,
                    "waypoint_count": None if robot.task is None else robot.task.waypoint_count,
                }
                for name, robot in self.robots.items()
            },
            "queue": [
                {
                    "task": task.task_id,
                    "goal": list(task.goal),
                    "robot": task.target_robot,
                    **self._route_fields(task),
                }
                for task in self.queue
            ],
            "completed_count": self.completed_count,
            "min_pair_distance": min(pair_distances.values(), default=None),
        }
        msg = String()
        msg.data = json.dumps(status, separators=(",", ":"))
        self.status_pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = FleetController()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
