#!/usr/bin/env python3

import argparse
import json
import math
import sys
import time

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped, Twist
from nav2_msgs.action import NavigateThroughPoses
from nav_msgs.msg import Odometry
from rclpy.action import ActionClient
from rclpy.node import Node


DEFAULT_ROUTE = [
    (1.485, -0.615, -0.785),
    (2.100, -2.100, -1.571),
    (1.485, -3.585, -2.356),
    (0.000, -4.200, 3.142),
    (-1.485, -3.585, 2.356),
    (-2.100, -2.100, 1.571),
    (-2.100, -0.600, 1.571),
    (-2.100, 1.200, 1.571),
    (-2.100, 2.800, 1.571),
]


class ClosedLoopProbe(Node):
    def __init__(self):
        super().__init__('omnifleet_a2_traffic_closed_loop_test')
        self.action_client = ActionClient(
            self, NavigateThroughPoses, '/navigate_through_poses'
        )
        self.create_subscription(Twist, '/cmd_vel', self._on_cmd_vel, 20)
        self.create_subscription(Odometry, '/odom', self._on_odom, 20)
        self.latest_xy = None
        self.previous_xy = None
        self.travelled = 0.0
        self.nonzero_commands = 0
        self.max_linear = 0.0
        self.max_angular = 0.0

    def _on_cmd_vel(self, message):
        self.max_linear = max(self.max_linear, abs(message.linear.x))
        self.max_angular = max(self.max_angular, abs(message.angular.z))
        if abs(message.linear.x) > 1e-3 or abs(message.angular.z) > 1e-3:
            self.nonzero_commands += 1

    def _on_odom(self, message):
        current = (message.pose.pose.position.x, message.pose.pose.position.y)
        if self.previous_xy is not None:
            self.travelled += math.dist(current, self.previous_xy)
        self.previous_xy = current
        self.latest_xy = current

    def pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose


def spin_until(node, future, deadline):
    while rclpy.ok() and not future.done() and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
    return future.done()


def run(timeout):
    rclpy.init()
    node = ClosedLoopProbe()
    started = time.monotonic()
    deadline = started + timeout
    try:
        while node.latest_xy is None and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
        if node.latest_xy is None:
            raise RuntimeError('No /odom feedback received')
        if not node.action_client.wait_for_server(timeout_sec=min(45.0, timeout)):
            raise RuntimeError('NavigateThroughPoses action server is unavailable')

        goal = NavigateThroughPoses.Goal()
        goal.poses = [node.pose(*waypoint) for waypoint in DEFAULT_ROUTE]
        send_future = node.action_client.send_goal_async(goal)
        if not spin_until(node, send_future, deadline):
            raise RuntimeError('Timed out while sending navigation goal')
        goal_handle = send_future.result()
        if not goal_handle.accepted:
            raise RuntimeError('NavigateThroughPoses goal was rejected')

        result_future = goal_handle.get_result_async()
        if not spin_until(node, result_future, deadline):
            goal_handle.cancel_goal_async()
            raise RuntimeError('Navigation did not finish before timeout')

        wrapped_result = result_future.result()
        final_goal = DEFAULT_ROUTE[-1]
        final_error = math.dist(node.latest_xy, final_goal[:2])
        metrics = {
            'status': int(wrapped_result.status),
            'succeeded': wrapped_result.status == GoalStatus.STATUS_SUCCEEDED,
            'elapsed_s': round(time.monotonic() - started, 2),
            'travelled_m': round(node.travelled, 3),
            'final_error_m': round(final_error, 3),
            'nonzero_cmd_count': node.nonzero_commands,
            'max_linear_mps': round(node.max_linear, 3),
            'max_angular_rps': round(node.max_angular, 3),
        }
        passed = (
            metrics['succeeded']
            and node.travelled > 12.0
            and final_error < 0.35
            and node.nonzero_commands >= 20
            and node.max_linear > 0.05
        )
        metrics['passed'] = passed
        print('CLOSED_LOOP_RESULT ' + json.dumps(metrics, sort_keys=True))
        return 0 if passed else 1
    except RuntimeError as error:
        print('CLOSED_LOOP_RESULT ' + json.dumps({'passed': False, 'error': str(error)}))
        return 2
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=float, default=240.0)
    args = parser.parse_args()
    sys.exit(run(args.timeout))


if __name__ == '__main__':
    main()
