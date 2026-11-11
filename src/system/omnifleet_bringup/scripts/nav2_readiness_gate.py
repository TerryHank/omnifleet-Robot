#!/usr/bin/env python3
"""Wait for received sensor/map data and a fresh complete TF chain before Nav2."""
import os
import sys
import time
import argparse
import signal
import subprocess

from fleet_scope import frame
import rclpy
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
from tf2_ros import Buffer, TransformListener, TransformException
from omnifleet_waypoint_ui.localization_health import LocalizationHealth


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--wait-timeout',type=float,default=120.);parser.add_argument('--temporal-samples',type=int,default=5);parser.add_argument('--monitor-only',action='store_true')
    args,ros=parser.parse_known_args()
    rclpy.init(args=ros)
    node = rclpy.create_node('nav2_readiness_gate')
    buffer = Buffer()
    listener = TransformListener(buffer, node)
    received = {'cloud': 0.0, 'cloud_stamp': None, 'cloud_seq': 0, 'map': False}

    def cloud(msg):
        if msg.width * msg.height > 0:
            received['cloud'] = time.monotonic()
            received['cloud_stamp'] = Time.from_msg(msg.header.stamp)
            received['cloud_seq'] += 1

    def grid(msg):
        received['map'] = msg.info.width * msg.info.height > 0 and len(msg.data) == msg.info.width * msg.info.height

    node.create_subscription(PointCloud2, '/' + frame('navigation/deskewed_points'), cloud,
                             QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT))
    node.create_subscription(OccupancyGrid, '/' + frame('map'), grid,
                             QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                                        durability=DurabilityPolicy.TRANSIENT_LOCAL))
    deadline = time.monotonic() + args.wait_timeout if args.wait_timeout>0 else float('inf')
    next_log = 0.0
    ready = False
    temporal_hits = 0
    last_checked_seq = -1
    health = LocalizationHealth()
    while rclpy.ok() and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
        tf_ok = False
        temporal_ok = False
        try:
            transform = buffer.lookup_transform(frame('map'), frame('base_link'), Time())
            stamp = Time.from_msg(transform.header.stamp).nanoseconds / 1e9
            if stamp != health.stamp:
                health.observe(stamp, time.monotonic())
            tf_ok = health.ready(node.get_clock().now().nanoseconds / 1e9, time.monotonic())
            buffer.lookup_transform(frame('base_link'), frame('rslidar'), Time())
            if received['cloud_stamp'] is not None and received['cloud_seq'] != last_checked_seq:
                # Verify the exact incoming cloud timestamp is covered by the
                # TF cache. This rejects startup/backlog clouds before Nav2
                # subscribes, instead of merely checking that a current TF exists.
                buffer.lookup_transform(frame('map'), frame('rslidar'), received['cloud_stamp'])
                temporal_ok = True
                last_checked_seq = received['cloud_seq']
                temporal_hits += 1
        except TransformException as error:
            temporal_hits = 0
            last_checked_seq = received['cloud_seq']
            tf_ok = False
            health.stable_since = None
            health.reason = str(error)
        cloud_ok = time.monotonic() - received['cloud'] < .5
        if not cloud_ok or not received['map']:
            health.stable_since = None
        ready = cloud_ok and received['map'] and tf_ok and temporal_hits >= args.temporal_samples
        if ready or time.monotonic() >= next_log:
            node.get_logger().info(f'readiness: pointcloud={cloud_ok}, map={received["map"]}, TF={tf_ok}, temporal_tf={temporal_hits}/{args.temporal_samples}, tf_age_ms={health.age_ms}, reason={health.reason}')
            next_log = time.monotonic() + 5
        if ready:
            break
    if not ready:
        node.destroy_node()
        rclpy.try_shutdown()
        print('Nav2 startup blocked: required data/TF did not become ready before the configured timeout', flush=True)
        return 21
    if args.monitor_only:
        node.get_logger().info('readiness passed; monitor-only mode will not launch a second Nav2 stack')
        node.destroy_node()
        rclpy.try_shutdown()
        return 0
    command = ['ros2', 'launch', 'omnifleet_bringup', 'navigation.launch.py',
                      'transform_tolerance:=0.8', 'odom_topic:='+('/lidar_odometry/nav_odom' if os.environ.get('OMNIFLEET_ARCHITECTURE')=='pure_mola' else '/odom'), 'obstacle_topic:=/' + frame('navigation/deskewed_points'),
                      'obstacle_clearing:=true', 'use_sim_time:=false', 'autostart:=true',
                      'params_file:=/home/iecme/omnifleet_a2_ws/install_111/omnifleet_planner/share/omnifleet_planner/config/nav2_t2.yaml']
    # Keep the readiness context alive for the application lifetime. Closing a
    # transient Zenoh context must not prevent an already-ready Nav2 from starting.
    child = subprocess.Popen(command, start_new_session=True)
    def forward(signum, _frame):
        if child.poll() is None:
            try:
                os.killpg(child.pid, signum)
            except ProcessLookupError:
                pass
    signal.signal(signal.SIGINT, forward)
    signal.signal(signal.SIGTERM, forward)
    try:
        return child.wait()
    finally:
        if child.poll() is None:
            forward(signal.SIGINT, None)
            try:
                child.wait(timeout=8)
            except subprocess.TimeoutExpired:
                forward(signal.SIGKILL, None)
                child.wait()
        node.destroy_node()
        try:
            rclpy.try_shutdown()
        except RuntimeError as error:
            print(f'Nav2 has stopped; readiness context cleanup: {error}', flush=True)



if __name__ == '__main__':
    sys.exit(main())
