"""Bounded graph/message check. Select the domain using environment variables."""
import json
import argparse
import time

import rclpy
from std_msgs.msg import String
from rmf_task_msgs.srv import GetDispatchStates

parser = argparse.ArgumentParser()
parser.add_argument('--expect', choices=['central', 'isolated'], required=True)
args = parser.parse_args()
rclpy.init()
node = rclpy.create_node('omnifleet_connection_verification')
messages = []
node.create_subscription(String, '/robot_104/rmf/connection_status',
                         lambda m: messages.append(json.loads(m.data)), 10)
deadline = time.monotonic() + 4.0
while time.monotonic() < deadline:
    rclpy.spin_once(node, timeout_sec=0.1)
topics = dict(node.get_topic_names_and_types())
robot_topics = [name for name in topics if name.startswith('/robot_104/') and node.count_publishers(name)]
result = {
    'nodes': node.get_node_names(),
    'robot_topics': robot_topics,
    'central_state_messages': len(messages),
    'last_state_online': messages[-1]['online'] if messages else None,
    'transport_connected': messages[-1]['transport_connected'] if messages else None,
    'robot_navigation_visible': '/robot_104/navigation/status' in topics,
}
if args.expect == 'central':
    client = node.create_client(GetDispatchStates, '/get_dispatches')
    assert client.wait_for_service(timeout_sec=3)
    future = client.call_async(GetDispatchStates.Request())
    rclpy.spin_until_future_complete(node, future, timeout_sec=3)
    response = future.result()
    result['dispatcher_query_success'] = response is not None and response.success
    result['active_dispatches'] = len(response.states.active) if response is not None else None
    result['finished_dispatches'] = len(response.states.finished) if response is not None else None
    result['passed'] = bool(messages) and messages[-1]['transport_connected'] and 'omnifleet_rmf_adapter' in result['nodes'] and not result['robot_navigation_visible']
    result['passed'] = result['passed'] and result['dispatcher_query_success']
else:
    result['passed'] = not messages and not robot_topics and len(result['nodes']) == 1
print(json.dumps(result, indent=2))
node.destroy_node()
rclpy.try_shutdown()
assert result['passed'], 'Unexpected graph or state reception'
