"""Read-only deployment check; no chassis control or parameter updates."""
from pathlib import Path
import collections,json,os,time
import rclpy
from std_msgs.msg import String
rclpy.init();node=rclpy.create_node('verify_palm_chain_runtime');rows=[]
node.create_subscription(String,'/vision/body_tracking/status',lambda m:rows.append(json.loads(m.data)),10)
end=time.monotonic()+50
while time.monotonic()<end:
    rclpy.spin_once(node,timeout_sec=.2)
    good=[r for r in rows if r.get('hand_search_debug',{}).get('palm_backend')=='TensorRT FP32 Full palm']
    if len(good)>=12:break
summary=dict(frames=len(rows),palm_verified_frames=len(good),errors=dict(collections.Counter(r.get('hand_error') for r in good)))
if good:
    last=good[-1]
    summary.update(palm=last['hand_search_debug']['palm_backend'],tracker=last['hand_search_debug']['nanotrack'],
        hand=last.get('hand_model_backend'),resolution=last.get('rgb_resolution'),
        body_tracking=last.get('body_tracking'),velocity=last.get('velocity_request'),
        hand_ms=last.get('hand_ms'),processing_fps=last.get('processing_fps'))
(Path(__file__).parent/'runtime.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary),flush=True)
assert len(good)>=12,'New palm backend not observed'
assert not any(r.get('hand_error') for r in good),'Hand inference error'
assert not any(r.get('body_tracking',{}).get('motion_enabled') for r in good),'Motion enabled during verification'
os._exit(0)
