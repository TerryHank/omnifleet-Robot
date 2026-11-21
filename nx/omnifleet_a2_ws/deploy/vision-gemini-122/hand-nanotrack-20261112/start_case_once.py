"""Start the existing unified vision case once; does not enable chassis motion."""
import json
import os
import time
import rclpy
from std_msgs.msg import String
rclpy.init()
node=rclpy.create_node('start_unified_hand_validation')
publisher=node.create_publisher(String,'/vision/demo/control',10)
end=time.monotonic()+25
while time.monotonic()<end and not publisher.get_subscription_count():
    rclpy.spin_once(node,timeout_sec=.2)
assert publisher.get_subscription_count(),'No vision manager subscription'
publisher.publish(String(data=json.dumps(dict(op='start',case_id='04_09_body_tracking',id='final-hand-verify',warm=True))))
end=time.monotonic()+2
while time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.1)
print('START_SENT_ONCE',flush=True)
os._exit(0)
