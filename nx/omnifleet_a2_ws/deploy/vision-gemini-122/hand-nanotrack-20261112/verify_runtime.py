from pathlib import Path
import json
import time
import os
import collections
import rclpy
from std_msgs.msg import String

rclpy.init();node=rclpy.create_node('verify_hand_nanotrack_runtime')
rows=[];publisher=node.create_publisher(String,'/vision/demo/control',10)
node.create_subscription(String,'/vision/body_tracking/status',lambda m:rows.append(json.loads(m.data)),10)
end=time.monotonic()+90;next_request=0
while time.monotonic()<end:
    if time.monotonic()>next_request and publisher.get_subscription_count():
        publisher.publish(String(data=json.dumps(dict(op='start',case_id='04_09_body_tracking',id='hand-nanotrack-verify',warm=True))))
        next_request=time.monotonic()+25
    rclpy.spin_once(node,timeout_sec=.2)
    verified=[r for r in rows if r.get('hand_search_debug',{}).get('nanotrack',{}).get('backend')=='NanoTrack CUDA FP32']
    if len(verified)>=25:break
summary=dict(frames=len(rows),verified_frames=len(verified),
    backend=dict(collections.Counter(r.get('hand_search_debug',{}).get('nanotrack',{}).get('backend') for r in rows)),
    errors=dict(collections.Counter(r.get('hand_error') for r in rows)))
if rows:
    summary.update(last_state=rows[-1].get('body_tracking'),last_velocity=rows[-1].get('velocity_request'),
                   tracker=rows[-1].get('hand_search_debug',{}).get('nanotrack'),hand_ms=rows[-1].get('hand_ms'))
Path(__file__).with_name('runtime-verification.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
assert len(verified)>=25,'NanoTrack backend not observed'
assert not any(r.get('hand_error') for r in verified),'Inference error'
assert not any(r.get('body_tracking',{}).get('motion_enabled') for r in verified),'Motion unexpectedly enabled'
os._exit(0)
