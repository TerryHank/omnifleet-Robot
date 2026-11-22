from pathlib import Path
import collections
import json
import os
import time
import rclpy
from std_msgs.msg import String

rclpy.init();node=rclpy.create_node('hand_nanotrack_live_test');rows=[]
path=Path(__file__).with_name('live-tracking-extended.jsonl');file=path.open('w')
ready=False
def callback(message):
    global ready
    data=json.loads(message.data);rows.append(data);file.write(json.dumps(data)+'\n');file.flush()
    tracker=data.get('hand_search_debug',{}).get('nanotrack',{})
    if not ready and tracker.get('backend'):
        print('CAPTURE_READY',tracker['backend'],data.get('body_tracking',{}).get('motion_enabled'),flush=True);ready=True
    if tracker.get('active'):
        print('TRACKING',tracker.get('score'),tracker.get('bbox'),[h.get('gesture') for h in data.get('hands',[])],flush=True)
node.create_subscription(String,'/vision/body_tracking/status',callback,10)
end=time.monotonic()+600
while time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.2)
file.close();os._exit(0)
