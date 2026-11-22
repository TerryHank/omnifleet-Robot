"""The real client must keep polling/renewing while ROS time freezes or rewinds."""
import json
import subprocess
import sys
import os


def test_client_control_timers_survive_backward_ros_time_jump(tmp_path):
    (tmp_path/'run').mkdir()
    config = tmp_path/'config.json'
    config.write_text(json.dumps({'robots': {'clock_test': {
        'observed_namespace': '', 'domain_id': 201, 'motion_enabled': False, 'pose_topic': '/odometry'}}}))
    script = r'''
import time
import rclpy
from rclpy.clock import ClockType
from rclpy.parameter import Parameter
from rclpy.time import Time
from omnifleet_rmf_adapter.control_client import NavigationClient

counts = {'poll': 0, 'renew': 0}
for name in counts:
    original = getattr(NavigationClient, name)
    def observed(self, name=name, original=original):
        counts[name] += 1
        original(self)
    setattr(NavigationClient, name, observed)
rclpy.init()
node = NavigationClient()
try:
    node.set_parameters([Parameter('use_sim_time', value=True)])
    clock = node.get_clock()
    assert clock.ros_time_is_active
    clock.set_ros_time_override(Time(seconds=100))
    started = time.monotonic()
    while time.monotonic()-started < .5:
        rclpy.spin_once(node, timeout_sec=.02)
    before = dict(counts)
    clock.set_ros_time_override(Time(seconds=98))
    started = time.monotonic()
    while time.monotonic()-started < .7:
        rclpy.spin_once(node, timeout_sec=.02)
    assert counts['poll']-before['poll'] >= 8, counts
    assert counts['renew']-before['renew'] >= 2, counts
    assert node.steady_clock.clock_type == ClockType.STEADY_TIME
finally:
    node.commands.close()
    node.ipc.close()
    node.destroy_node()
    rclpy.shutdown()
'''
    env = {**os.environ, 'ROS_DOMAIN_ID': '201', 'ROS_LOCALHOST_ONLY': '1',
           'OMNIFLEET_ROBOT_ID': 'clock_test', 'OMNIFLEET_CONFIG': str(config),
           'OMNIFLEET_DATA': str(tmp_path), 'RMW_IMPLEMENTATION': 'rmw_fastrtps_cpp'}
    env.pop('OMNIFLEET_DISCOVERY_PROFILE', None)
    result = subprocess.run([sys.executable, '-c', script], env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout+result.stderr
