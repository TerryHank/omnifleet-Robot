import json,os
from pathlib import Path
import rclpy
from rcl_interfaces.srv import GetParameters
rclpy.init();node=rclpy.create_node('verify_122_original_tuning')
client=node.create_client(GetParameters,'/body_tracking_104/horizon_tracking_RobotCmdVel/get_parameters')
assert client.wait_for_service(timeout_sec=8)
names=['steering_max_speed','reverse_max_speed','enable_motion']
future=client.call_async(GetParameters.Request(names=names))
rclpy.spin_until_future_complete(node,future,timeout_sec=5)
assert future.result()
values=future.result().values
result=dict(steering_max_speed=values[0].double_value,reverse_max_speed=values[1].double_value,enable_motion=values[2].bool_value)
print(result,flush=True)
assert abs(result['steering_max_speed']-.3)<1e-8
assert abs(result['reverse_max_speed']-.2)<1e-8
assert result['enable_motion'] is False
Path(__file__).with_name('actual-control-parameters.json').write_text(json.dumps(result,indent=2))
os._exit(0)
