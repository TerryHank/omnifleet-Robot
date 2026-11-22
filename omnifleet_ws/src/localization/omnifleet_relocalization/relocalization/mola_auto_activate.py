#!/usr/bin/env python3
"""Apply a MOLA relocalization result and unlock LIO only after it is accepted.

This is intentionally a one-shot gate for the unified launch.  It never sends
an action goal and exits non-zero on any missing service, rejected pose, or
stale odometry, so the launch cannot start Nav2 from a fabricated zero pose.
"""
import json
import math
import os
import sys
import time

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from mola_msgs.srv import MolaRuntimeParamSet, RelocalizeNearPose
from nav_msgs.msg import Odometry


def quat_from_yaw(yaw):
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


class Gate:
    def __init__(self, robot, result):
        self.robot = robot
        self.result = result
        self.node = rclpy.create_node("mola_auto_relocalization_gate")
        self.last_odom = None
        self.node.create_subscription(
            Odometry, "/lidar_odometry/pose", self._odom, 10
        )
        self.reloc = self.node.create_client(
            RelocalizeNearPose, "/relocalize_near_pose"
        )
        self.activate = self.node.create_client(
            MolaRuntimeParamSet, "/mola_runtime_param_set"
        )

    def _odom(self, msg):
        self.last_odom = msg

    def spin_until(self, predicate, timeout):
        deadline = time.monotonic() + timeout
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.2)
            if predicate():
                return True
        return False

    def run(self):
        if not self.result.get("success"):
            raise RuntimeError("relocalization likelihood returned no candidate")
        for name, client in (("relocalize_near_pose", self.reloc), ("mola_runtime_param_set", self.activate)):
            if not client.wait_for_service(timeout_sec=20.0):
                raise RuntimeError(f"service unavailable: /{name}")

        pose = PoseWithCovarianceStamped()
        pose.header.frame_id = "map"
        pose.header.stamp = self.node.get_clock().now().to_msg()
        pose.pose.pose.position.x = float(self.result["x"])
        pose.pose.pose.position.y = float(self.result["y"])
        qx, qy, qz, qw = quat_from_yaw(float(self.result["yaw"]))
        pose.pose.pose.orientation.x = qx
        pose.pose.pose.orientation.y = qy
        pose.pose.pose.orientation.z = qz
        pose.pose.pose.orientation.w = qw
        cov = [0.0] * 36
        cov[0] = cov[7] = 0.25**2
        cov[35] = math.radians(15.0) ** 2
        pose.pose.covariance = cov
        req = RelocalizeNearPose.Request()
        req.pose = pose
        response = self.reloc.call_async(req)
        if not self.spin_until(lambda: response.done(), 20.0):
            raise RuntimeError("relocalize_near_pose timed out")
        if not response.result().accepted:
            raise RuntimeError("relocalize_near_pose rejected candidate")

        activate = MolaRuntimeParamSet.Request()
        activate.parameters = "mola::LidarOdometry:lidar_odom:\n  active: true\n"
        response = self.activate.call_async(activate)
        if not self.spin_until(lambda: response.done(), 20.0):
            raise RuntimeError("mola_runtime_param_set timed out")
        if not response.result().success:
            raise RuntimeError(response.result().error_message or "MOLA activation rejected")

        if not self.spin_until(lambda: self.last_odom is not None, 15.0):
            raise RuntimeError("no fresh lidar_odometry/pose after activation")
        print(json.dumps({"robot": self.robot, "accepted": True, "odom": True, "x": self.result["x"], "y": self.result["y"], "yaw": self.result["yaw"]}, ensure_ascii=False), flush=True)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("mola_auto_activate.py RESULT.json")
    with open(sys.argv[1], encoding="utf-8") as f:
        result = json.load(f)
    robot = os.environ.get("OMNIFLEET_ROBOT_ID", "").strip()
    if not robot:
        raise SystemExit("OMNIFLEET_ROBOT_ID is required")
    rclpy.init()
    gate = Gate(robot, result)
    try:
        gate.run()
    except Exception as exc:
        print(f"[mola-auto-relocalize] {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1)
    finally:
        gate.node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
