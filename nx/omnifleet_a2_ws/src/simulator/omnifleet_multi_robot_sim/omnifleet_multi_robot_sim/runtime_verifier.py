"""Runtime acceptance verifier for the three-robot Classic simulation."""

import argparse
import json
from math import hypot
from pathlib import Path
from time import monotonic

import rclpy
try:
    from gazebo_msgs.msg import ModelStates
except ImportError:
    ModelStates = None
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String


ROBOT_NAMES = ("robot1", "robot2", "robot3")


class RuntimeVerifier(Node):
    def __init__(self, use_gazebo_models=True) -> None:
        super().__init__("multi_robot_runtime_verifier")
        self.use_gazebo_models = bool(use_gazebo_models and ModelStates is not None)
        self.odom_first = {}
        self.odom_latest = {}
        self.entity_first = {}
        self.entity_latest = {}
        self.last_motion = monotonic()
        self.status = {}
        self.minimum_distance = float("inf")
        self.startup_odom_origin = {}
        self.startup_max_drift = {}
        self.tasks_seen = False
        self._subscription_refs = [
            self.create_subscription(
                Odometry,
                f"/{name}/odom",
                lambda msg, robot_name=name: self._odom(robot_name, msg),
                20,
            )
            for name in ROBOT_NAMES
        ]
        if self.use_gazebo_models:
            self._subscription_refs.append(
                self.create_subscription(ModelStates, "/gazebo/model_states", self._models, 10)
            )
        self._subscription_refs.append(self.create_subscription(String, "/fleet/status", self._status, 10))

    def _odom(self, name, msg):
        point = (float(msg.pose.pose.position.x), float(msg.pose.pose.position.y))
        self.odom_first.setdefault(name, point)
        if not self.tasks_seen:
            origin = self.startup_odom_origin.setdefault(name, point)
            self.startup_max_drift[name] = max(
                self.startup_max_drift.get(name, 0.0),
                hypot(point[0] - origin[0], point[1] - origin[1]),
            )
        previous = self.odom_latest.get(name)
        self.odom_latest[name] = point
        if not self.use_gazebo_models:
            self.entity_first.setdefault(name, point)
            self.entity_latest[name] = point
        if previous and hypot(point[0] - previous[0], point[1] - previous[1]) > 0.005:
            self.last_motion = monotonic()

    def _models(self, msg):
        for name, pose in zip(msg.name, msg.pose):
            if name in ROBOT_NAMES:
                point = (float(pose.position.x), float(pose.position.y))
                self.entity_first.setdefault(name, point)
                self.entity_latest[name] = point

    def _status(self, msg):
        try:
            self.status = json.loads(msg.data)
            robots = self.status.get("robots", {})
            if int(self.status.get("completed_count", 0)) > 0 or any(
                robot.get("state") == "active" for robot in robots.values()
            ):
                self.tasks_seen = True
            distance = self.status.get("min_pair_distance")
            if distance is not None:
                self.minimum_distance = min(self.minimum_distance, float(distance))
        except (TypeError, ValueError, json.JSONDecodeError):
            self.get_logger().warning("ignored malformed /fleet/status JSON")

    @staticmethod
    def _displacements(first, latest):
        return {
            name: hypot(latest[name][0] - first[name][0], latest[name][1] - first[name][1])
            for name in ROBOT_NAMES
            if name in first and name in latest
        }

    def report(self):
        odom_motion = self._displacements(self.odom_first, self.odom_latest)
        entity_motion = self._displacements(self.entity_first, self.entity_latest)
        robots = self.status.get("robots", {})
        checks = {
            "three_odom_topics": len(self.odom_latest) == 3,
            "three_entities_moved": len(entity_motion) == 3 and all(value >= 0.20 for value in entity_motion.values()),
            "three_robots_moved": len(odom_motion) == 3 and all(value >= 0.20 for value in odom_motion.values()),
            "startup_zero_command_stable": len(self.startup_max_drift) == 3 and all(
                value <= 0.08 for value in self.startup_max_drift.values()
            ),
            "three_tasks_completed": int(self.status.get("completed_count", 0)) >= 3,
            "minimum_distance_safe": self.minimum_distance >= 0.55,
            "stopped_stably": bool(robots) and all(data.get("state") == "idle" for data in robots.values()) and monotonic() - self.last_motion >= 1.5,
        }
        return {
            "passed": all(checks.values()),
            "backend": "gazebo" if self.use_gazebo_models else "kinematic",
            "checks": checks,
            "odom_displacement": odom_motion,
            "entity_displacement": entity_motion,
            "startup_zero_command_drift": self.startup_max_drift,
            "minimum_pair_distance": None if self.minimum_distance == float("inf") else self.minimum_distance,
            "completed_count": int(self.status.get("completed_count", 0)),
        }


def _write_report(report, output):
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")


def main(args=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output")
    parser.add_argument("--kinematic", action="store_true")
    parsed, ros_args = parser.parse_known_args(args)
    if parsed.timeout <= 0:
        parser.error("--timeout must be positive")
    rclpy.init(args=ros_args)
    node = RuntimeVerifier(use_gazebo_models=not parsed.kinematic)
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
    except Exception as exc:  # runtime verifier must produce machine-readable failure evidence
        _write_report({"passed": False, "error": str(exc)}, parsed.output)
        exit_code = 3
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    raise SystemExit(exit_code)
