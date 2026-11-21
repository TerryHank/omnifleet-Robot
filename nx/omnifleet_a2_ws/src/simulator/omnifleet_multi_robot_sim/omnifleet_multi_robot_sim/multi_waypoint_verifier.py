"""Dynamic verifier for an arbitrary-length route owned by robot1."""

import argparse
import json
from math import hypot
from pathlib import Path as FilePath
from time import monotonic

import rclpy
try:
    from gazebo_msgs.msg import ModelStates
except ImportError:
    ModelStates = None
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

from .core import normalize_waypoints


ROBOT_NAMES = ("robot1", "robot2", "robot3")
DEFAULT_WAYPOINTS = ((-0.5, 0.0), (0.5, 0.0), (1.5, 0.0))


def parse_waypoints_json(value):
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"invalid waypoint JSON: {exc}") from exc
    if not isinstance(decoded, list) or not all(
        isinstance(point, (list, tuple)) and len(point) == 2 for point in decoded
    ):
        raise argparse.ArgumentTypeError("waypoints must be a JSON array of [x, y] pairs")
    try:
        return normalize_waypoints(decoded)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


class MultiWaypointVerifier(Node):
    def __init__(self, waypoints=DEFAULT_WAYPOINTS, use_gazebo_models=True) -> None:
        super().__init__("multi_waypoint_verifier")
        self.waypoints = normalize_waypoints(waypoints)
        self.use_gazebo_models = bool(use_gazebo_models and ModelStates is not None)
        self.status = {}
        self.minimum_distance = float("inf")
        self.entity_first = {}
        self.entity_latest = {}
        self.entity_max_drift = {name: 0.0 for name in ROBOT_NAMES}
        self.odom_latest = {}
        self.completed_events = []
        self.online_since = None
        self.route_sent = False
        self.last_robot1_motion = monotonic()

        transient_qos = QoSProfile(depth=50)
        transient_qos.reliability = ReliabilityPolicy.RELIABLE
        transient_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.path_pub = self.create_publisher(Path, "/robot1/waypoints", 10)
        self._subscription_refs = [
            self.create_subscription(String, "/fleet/status", self._on_status, transient_qos),
            self.create_subscription(String, "/fleet/events", self._on_event, transient_qos),
        ]
        if self.use_gazebo_models:
            self._subscription_refs.append(
                self.create_subscription(ModelStates, "/gazebo/model_states", self._on_models, 10)
            )
        for name in ROBOT_NAMES:
            self._subscription_refs.append(
                self.create_subscription(
                    Odometry,
                    f"/{name}/odom",
                    lambda msg, robot_name=name: self._on_odom(robot_name, msg),
                    20,
                )
            )
        self.create_timer(0.1, self._maybe_publish_route)

    def _on_status(self, msg: String) -> None:
        try:
            self.status = json.loads(msg.data)
            distance = self.status.get("min_pair_distance")
            if distance is not None:
                self.minimum_distance = min(self.minimum_distance, float(distance))
        except (TypeError, ValueError, json.JSONDecodeError):
            self.get_logger().warning("ignored malformed /fleet/status JSON")

    def _on_event(self, msg: String) -> None:
        try:
            event = json.loads(msg.data)
        except (TypeError, ValueError, json.JSONDecodeError):
            return
        if event.get("event") == "completed" and event.get("route_id") is not None:
            signature = (
                event.get("route_id"),
                event.get("waypoint_index"),
                event.get("robot"),
            )
            if signature not in [
                (item.get("route_id"), item.get("waypoint_index"), item.get("robot"))
                for item in self.completed_events
            ]:
                self.completed_events.append(event)

    def _on_models(self, msg: ModelStates) -> None:
        for name, pose in zip(msg.name, msg.pose):
            if name not in ROBOT_NAMES:
                continue
            point = (float(pose.position.x), float(pose.position.y))
            origin = self.entity_first.setdefault(name, point)
            previous = self.entity_latest.get(name)
            self.entity_latest[name] = point
            self.entity_max_drift[name] = max(
                self.entity_max_drift[name],
                hypot(point[0] - origin[0], point[1] - origin[1]),
            )
            if name == "robot1" and previous and hypot(
                point[0] - previous[0], point[1] - previous[1]
            ) > 0.005:
                self.last_robot1_motion = monotonic()

    def _on_odom(self, name: str, msg: Odometry) -> None:
        point = (
            float(msg.pose.pose.position.x),
            float(msg.pose.pose.position.y),
        )
        self.odom_latest[name] = point
        if not self.use_gazebo_models:
            origin = self.entity_first.setdefault(name, point)
            previous = self.entity_latest.get(name)
            self.entity_latest[name] = point
            self.entity_max_drift[name] = max(
                self.entity_max_drift[name],
                hypot(point[0] - origin[0], point[1] - origin[1]),
            )
            if name == "robot1" and previous and hypot(
                point[0] - previous[0], point[1] - previous[1]
            ) > 0.005:
                self.last_robot1_motion = monotonic()

    def _maybe_publish_route(self) -> None:
        if self.route_sent:
            return
        robots = self.status.get("robots", {})
        ready = len(robots) == 3 and all(
            robot.get("online") and robot.get("state") == "idle"
            for robot in robots.values()
        )
        if not ready or len(self.entity_first) != 3:
            self.online_since = None
            return
        if self.online_since is None:
            self.online_since = monotonic()
            return
        if monotonic() - self.online_since < 2.0:
            return
        route = Path()
        route.header.frame_id = "world"
        route.header.stamp = self.get_clock().now().to_msg()
        for x, y in self.waypoints:
            waypoint = PoseStamped()
            waypoint.header = route.header
            waypoint.pose.position.x = x
            waypoint.pose.position.y = y
            waypoint.pose.orientation.w = 1.0
            route.poses.append(waypoint)
        self.path_pub.publish(route)
        self.route_sent = True

    def report(self):
        robots = self.status.get("robots", {})
        route_ids = {event.get("route_id") for event in self.completed_events}
        waypoint_indices = [event.get("waypoint_index") for event in self.completed_events]
        route_robots = [event.get("robot") for event in self.completed_events]
        robot1_start = self.entity_first.get("robot1")
        robot1_final = self.entity_latest.get("robot1")
        robot1_displacement = (
            hypot(robot1_final[0] - robot1_start[0], robot1_final[1] - robot1_start[1])
            if robot1_start and robot1_final
            else 0.0
        )
        final_goal_error = (
            hypot(
                robot1_final[0] - self.waypoints[-1][0],
                robot1_final[1] - self.waypoints[-1][1],
            )
            if robot1_final
            else float("inf")
        )
        waypoint_count = len(self.waypoints)
        expected_indices = list(range(waypoint_count))
        expected_route_robots = ["robot1"] * waypoint_count
        expected_displacement = (
            hypot(
                self.waypoints[-1][0] - robot1_start[0],
                self.waypoints[-1][1] - robot1_start[1],
            )
            if robot1_start
            else float("inf")
        )
        idle_drift = {
            name: self.entity_max_drift.get(name, 0.0)
            for name in ("robot2", "robot3")
        }
        checks = {
            "route_published": self.route_sent,
            "same_robot_completed_route": len(route_ids) == 1
            and route_robots == expected_route_robots,
            "waypoints_completed_in_order": waypoint_indices == expected_indices,
            "completed_count_matches_route": int(self.status.get("completed_count", 0))
            == waypoint_count,
            "robot1_entity_displacement": robot1_displacement
            >= max(0.0, expected_displacement - 0.25),
            "robot1_final_goal": final_goal_error <= 0.20,
            "other_robots_zero_command_stable": all(value <= 0.08 for value in idle_drift.values()),
            "minimum_distance_safe": self.minimum_distance >= 0.55,
            "stopped_stably": bool(robots)
            and all(robot.get("state") == "idle" for robot in robots.values())
            and monotonic() - self.last_robot1_motion >= 1.5,
        }
        return {
            "passed": all(checks.values()),
            "backend": "gazebo" if self.use_gazebo_models else "kinematic",
            "requested_waypoints": self.waypoints,
            "waypoint_count": waypoint_count,
            "checks": checks,
            "route_id": next(iter(route_ids)) if len(route_ids) == 1 else None,
            "completed_waypoint_indices": waypoint_indices,
            "completed_route_robots": route_robots,
            "completed_count": int(self.status.get("completed_count", 0)),
            "robot1_entity_displacement": robot1_displacement,
            "robot1_final_position": robot1_final,
            "robot1_final_goal_error": None if final_goal_error == float("inf") else final_goal_error,
            "idle_robot_max_drift": idle_drift,
            "minimum_pair_distance": None if self.minimum_distance == float("inf") else self.minimum_distance,
        }


def _write_report(report, output):
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if output:
        path = FilePath(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")


def main(args=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--output")
    parser.add_argument("--kinematic", action="store_true")
    parser.add_argument(
        "--waypoints-json",
        type=parse_waypoints_json,
        help='JSON array of [x, y] pairs; for example "[[0.5,0],[1.0,0.2]]"',
    )
    parsed, ros_args = parser.parse_known_args(args)
    if parsed.timeout <= 0:
        parser.error("--timeout must be positive")
    waypoints = DEFAULT_WAYPOINTS if parsed.waypoints_json is None else parsed.waypoints_json
    rclpy.init(args=ros_args)
    node = MultiWaypointVerifier(waypoints, use_gazebo_models=not parsed.kinematic)
    deadline = monotonic() + parsed.timeout
    exit_code = 2
    try:
        while rclpy.ok() and monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
            report = node.report()
            if report["passed"]:
                exit_code = 0
                break
        else:
            report = node.report()
        _write_report(report, parsed.output)
    except ExternalShutdownException:
        report = node.report()
        _write_report(report, parsed.output)
    except Exception as exc:
        _write_report({"passed": False, "error": str(exc)}, parsed.output)
        exit_code = 3
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    raise SystemExit(exit_code)
