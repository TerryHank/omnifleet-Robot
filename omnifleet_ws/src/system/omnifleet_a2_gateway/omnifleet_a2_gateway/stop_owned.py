"""Cancel only the native Nav2 goal owned by the A2 fleet gateway."""
import json
import os
from pathlib import Path
import time
import rclpy
from action_msgs.srv import CancelGoal
from rclpy.node import Node
from unique_identifier_msgs.msg import UUID


def main():
    path = Path(os.environ['RRC_ROBOT_WS']).parent/'omnifleet_a2_data/run/fleet-owned-goal.json'
    if not path.exists():return
    saved = json.loads(path.read_text())
    assert saved['kind'] in ('navigate_to_pose','navigate_through_poses')
    rclpy.init()
    node = Node('omnifleet_a2_stop_owned')
    try:
        client = node.create_client(CancelGoal, '/navigation_backend/'+saved['kind']+'/_action/cancel_goal')
        if not client.wait_for_service(timeout_sec=5):
            raise RuntimeError('Owned Nav2 cancel service unavailable; task record retained')
        request = CancelGoal.Request()
        request.goal_info.goal_id = UUID(uuid=saved['uuid'])
        future = client.call_async(request)
        rclpy.spin_until_future_complete(node, future, timeout_sec=5)
        if not future.done() or future.result().return_code not in (0,2,3):
            raise RuntimeError('Owned task cancellation unconfirmed; record retained')
        path.unlink(missing_ok=True)
        print('Owned Ackermann Nav2 task cancellation acknowledged')
    finally:
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()


if __name__ == '__main__':main()
