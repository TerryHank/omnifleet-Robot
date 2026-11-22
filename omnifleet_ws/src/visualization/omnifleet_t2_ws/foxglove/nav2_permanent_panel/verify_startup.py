import rclpy
from rclpy.node import Node
from nav2_parameter_store import YAML_FILE
rclpy.init(args=['--ros-args', '--params-file', str(YAML_FILE)])
node = Node('controller_server', automatically_declare_parameters_from_overrides=True)
try:
    values = [node.get_parameter('FollowPath.' + key).value for key in ('max_vel_x', 'max_speed_xy')]
    print('Fresh ROS parameter-loader values:', values, flush=True)
    assert values == [.35, .35]
    assert all(type(v) is float for v in values)
finally:
    node.destroy_node()
    rclpy.shutdown()
