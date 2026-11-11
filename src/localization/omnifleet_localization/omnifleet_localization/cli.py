import argparse
import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from omnifleet_interfaces.msg import SlamStatus
from omnifleet_interfaces.srv import SaveMap, SwitchMode


def _wait_future(node, future, timeout_sec):
    deadline = time.monotonic() + timeout_sec
    while rclpy.ok() and time.monotonic() < deadline and not future.done():
        rclpy.spin_once(node, timeout_sec=0.1)
    if not future.done():
        raise TimeoutError("等待服务响应超时")
    return future.result()


def _status(node, timeout_sec=3.0):
    received = []
    qos = QoSProfile(depth=1)
    qos.reliability = ReliabilityPolicy.RELIABLE
    qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
    subscription = node.create_subscription(
        SlamStatus, "/rrc_slam/status", received.append, qos
    )
    deadline = time.monotonic() + timeout_sec
    try:
        while rclpy.ok() and time.monotonic() < deadline and not received:
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_subscription(subscription)
    if not received:
        raise TimeoutError("未收到 /rrc_slam/status 消息")
    return received[-1]


def _print_status(status):
    print(
        f"状态={status.state} 模式={status.mode or '-'} "
        f"操作={status.operation or '-'} 地图ID={status.map_id or '-'} "
        f"事务={status.transaction_id or '-'} 消息={status.message}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(prog="rrc-slamctl")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")

    switch = subparsers.add_parser("switch")
    switch.add_argument("mode")
    switch.add_argument(
        "--operation",
        choices=("mapping", "localization", "slam_navigation"),
        default="mapping",
    )
    switch.add_argument("--map-id", default="")

    subparsers.add_parser("stop")
    save = subparsers.add_parser("save-map")
    save.add_argument("--label", default="")
    args = parser.parse_args(argv)

    rclpy.init()
    node = Node("rrc_slamctl")
    try:
        if args.command == "status":
            _print_status(_status(node))
            return 0
        if args.command == "save-map":
            client = node.create_client(SaveMap, "/rrc_slam/save_map")
            if not client.wait_for_service(timeout_sec=3.0):
                raise RuntimeError("/rrc_slam/save_map 服务不可用")
            request = SaveMap.Request()
            request.label = args.label
            result = _wait_future(node, client.call_async(request), 90.0)
            print(f"成功={result.success} 地图ID={result.map_id} {result.message}")
            return 0 if result.success else 1

        client = node.create_client(SwitchMode, "/rrc_slam/switch_mode")
        if not client.wait_for_service(timeout_sec=3.0):
            raise RuntimeError("/rrc_slam/switch_mode 服务不可用")
        request = SwitchMode.Request()
        if args.command == "stop":
            request.mode = "__stop__"
        else:
            request.mode = args.mode
            request.operation = args.operation
            request.map_id = args.map_id
        result = _wait_future(node, client.call_async(request), 5.0)
        print(
            f"已接受={result.accepted} 事务={result.transaction_id} "
            f"消息={result.message}"
        )
        return 0 if result.accepted else 1
    except Exception as error:
        print(f"rrc-slamctl 错误：{error}", file=sys.stderr)
        return 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
