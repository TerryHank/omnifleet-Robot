"""Discover the public navigation API without sending goals or service requests."""
import json
import os
from pathlib import Path
import time

import rclpy
from rclpy.action import ActionClient
from omnifleet_navigation_interfaces.action import ExecuteNavigation
from std_srvs.srv import Trigger

config = json.loads((Path.home() / 'workspaces/omnifleet_ws/src/system/omnifleet_rmf_adapter/config/framework.json').read_text())
profile = config['robots']['robot_104']
assert int(os.environ['ROS_DOMAIN_ID']) == profile['domain_id']
rclpy.init()
node = rclpy.create_node('omnifleet_read_only_api_verification')
prefix = profile['observed_namespace']
action = ActionClient(node, ExecuteNavigation, prefix + '/navigation/execute')
stop = node.create_client(Trigger, prefix + '/navigation/stop')
deadline = time.monotonic() + 5.0
while time.monotonic() < deadline and not (action.server_is_ready() and stop.service_is_ready()):
    rclpy.spin_once(node, timeout_sec=0.1)
result = {'domain': profile['domain_id'], 'execute_available': action.server_is_ready(),
          'stop_available': stop.service_is_ready(), 'goals_sent': 0, 'stop_calls_sent': 0}
print(json.dumps(result))
action.destroy()
node.destroy_node()
rclpy.try_shutdown()
assert result['execute_available'] and result['stop_available']
