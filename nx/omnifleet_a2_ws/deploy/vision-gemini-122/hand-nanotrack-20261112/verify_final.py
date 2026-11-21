"""Read-only runtime verification after deployment."""
from pathlib import Path
import collections
import json
import os
import time
import rclpy
from std_msgs.msg import String

rclpy.init()
node=rclpy.create_node('verify_hand_tracking_final')
rows=[]
node.create_subscription(String,'/vision/body_tracking/status',lambda m:rows.append(json.loads(m.data)),10)
deadline=time.monotonic()+40
while time.monotonic()<deadline:
    rclpy.spin_once(node,timeout_sec=.2)
    good=[r for r in rows if r.get('hand_search_debug',{}).get('nanotrack',{}).get('backend')=='NanoTrack CUDA FP32']
    if len(good)>=12:break
summary=dict(frames=len(rows),verified=len(good),errors=dict(collections.Counter(r.get('hand_error') for r in good)))
if rows:
    summary.update(last_resolution=rows[-1].get('rgb_resolution'),body_tracking=rows[-1].get('body_tracking'),
        velocity=rows[-1].get('velocity_request'),backend=rows[-1].get('hand_model_backend'),
        tracker=rows[-1].get('hand_search_debug',{}).get('nanotrack'),
        processing_fps=rows[-1].get('processing_fps'),hand_ms=rows[-1].get('hand_ms'))
Path(__file__).with_name('final-runtime.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary),flush=True)
assert len(good)>=12,'No active NanoTrack backend observed'
assert not any(r.get('hand_error') for r in good),'Hand inference error'
assert not any(r.get('body_tracking',{}).get('motion_enabled') for r in good),'Motion enabled'
os._exit(0)
