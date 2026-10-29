"""Simulation-only five-axis command/feedback and controller service check."""
import json
import os
import time

import rclpy
from controller_manager_msgs.srv import ListControllers
from sensor_msgs.msg import JointState
from rclpy.qos import qos_profile_sensor_data

assert os.environ['ROS_DOMAIN_ID'] == '105'
assert os.environ['RMW_IMPLEMENTATION'] == 'rmw_zenoh_cpp'
rclpy.init()
node = rclpy.create_node('lion_native_zenoh_verification')
feedback = {}
count = 0


def receive(message):
    global count
    feedback.update(zip(message.name, message.position))
    count += 1


node.create_subscription(JointState, '/joint_states', receive, qos_profile_sensor_data)
publisher = node.create_publisher(JointState, '/lion_1061/joint_position_command', 10)
client = node.create_client(ListControllers, '/controller_manager/list_controllers')
names = ['x_slide', 'y_slide', 'a_yaw', 'b_pitch', 'c_roll']
target = [0.01, 0.01, 0.05, 0.05, 0.05]
try:
    assert client.wait_for_service(timeout_sec=5)
    future = client.call_async(ListControllers.Request())
    rclpy.spin_until_future_complete(node, future, timeout_sec=5)
    controllers = {c.name: c.state for c in future.result().controller}
    assert controllers.get('joint_state_broadcaster') == 'active'
    assert controllers.get('lion_position_controller') == 'active'
    for positions in (target, [0.0] * 5):
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            publisher.publish(JointState(name=names, position=positions))
            rclpy.spin_once(node, timeout_sec=0.05)
        assert all(abs(feedback.get(k, 999) - v) < 0.001 for k, v in zip(names, positions))
    print(json.dumps({'passed': True, 'domain': 105, 'joint_state_messages': count,
                      'controllers': controllers, 'final_position': feedback}))
finally:
    publisher.publish(JointState(name=names, position=[0.0] * 5))
    node.destroy_node()
    rclpy.try_shutdown()
