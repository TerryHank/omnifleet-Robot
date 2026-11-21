from pathlib import Path
import collections
import json
import os
import time
import rclpy
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import String
from sensor_msgs.msg import Image, CameraInfo

rclpy.init();node=rclpy.create_node('verify_synced_122_vision')
status=[];manager=[];camera={};ready=False
publisher=node.create_publisher(String,'/vision/demo/control',10)
node.create_subscription(String,'/vision/body_tracking/status',lambda m:status.append(json.loads(m.data)),10)
node.create_subscription(String,'/vision/demo/status',lambda m:manager.append(json.loads(m.data)),10)
node.create_subscription(Image,'/camera/color/image_raw',lambda m:camera.update(rgb=[m.width,m.height]),qos_profile_sensor_data)
node.create_subscription(CameraInfo,'/camera/depth/camera_info',lambda m:camera.update(depth=[m.width,m.height]),qos_profile_sensor_data)
end=time.monotonic()+85;next_request=0
while time.monotonic()<end:
    if time.monotonic()>next_request and publisher.get_subscription_count():
        publisher.publish(String(data=json.dumps(dict(op='start',case_id='04_09_body_tracking',id='sync122-unified-check',warm=True))))
        next_request=time.monotonic()+20
    rclpy.spin_once(node,timeout_sec=.2)
    good=[d for d in status if d.get('body_tracking',{}).get('operator_mode')=='unified']
    if len(good)>=35:
        ready=True;break
summary=dict(ready=ready,frames=len(status),camera=camera,
    modes=dict(collections.Counter(d.get('body_tracking',{}).get('operator_mode') for d in status)),
    backends=dict(collections.Counter(d.get('hand_model_backend') for d in status)),
    errors=dict(collections.Counter(d.get('hand_error') for d in status)),
    coordinate_errors=dict(collections.Counter(d.get('coordinate_error') for d in status)),
    manager=manager[-1] if manager else None)
if status:
    last=status[-1];summary.update(last_state=last.get('body_tracking'),rgb_resolution=last.get('rgb_resolution'),
        velocity=last.get('velocity_request'),processing_fps=last.get('processing_fps'))
root=Path(__file__).parent
(root/'runtime-verification.json').write_text(json.dumps(summary,indent=2))
(root/'runtime-status.json').write_text(json.dumps(status))
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
assert ready,'Unified pipeline did not become ready'
assert not any(d.get('hand_error') for d in good),'Hand inference errors'
assert not any(d.get('body_tracking',{}).get('motion_enabled') for d in good),'Motion unexpectedly enabled'
assert all(d.get('hand_model_backend')=='TensorRT FP32 Full' for d in good),'Incorrect model backend'
os._exit(0)
