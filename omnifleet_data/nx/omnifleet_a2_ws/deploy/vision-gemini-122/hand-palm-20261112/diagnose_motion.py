"""Observe gesture, native controller and velocity topics without publishing."""
from pathlib import Path
import collections,json,os,time
import rclpy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
rclpy.init();node=rclpy.create_node('diagnose_gesture_motion');rows=collections.defaultdict(list);subscriptions=[]
end=time.monotonic()+4
while time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.2)
inventory=node.get_topic_names_and_types()
for topic,types in inventory:
    if types==['std_msgs/msg/String'] and any(s in topic for s in ['status','state','sbus','diagnostic']):
        def string(message,topic=topic):
            try:data=json.loads(message.data)
            except ValueError:data=message.data[:800]
            rows[topic].append(data)
        subscriptions.append(node.create_subscription(String,topic,string,10))
    elif types==['geometry_msgs/msg/Twist']:
        def twist(message,topic=topic):rows[topic].append(dict(x=message.linear.x,z=message.angular.z))
        subscriptions.append(node.create_subscription(Twist,topic,twist,10))
end=time.monotonic()+12
while time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.1)
output={}
for topic,values in rows.items():
    item=dict(count=len(values),last=values[-1])
    if topic=='/vision/body_tracking/status':
        last=values[-1]
        item['last']={k:last.get(k) for k in ['mode','state','gesture','person','gestures_enabled','hands','body_tracking','velocity_request','hand_ms','hand_age_ms','hand_error','hand_updated','processing_fps','rgb_input_fps','source_stamp']}
        item['last']['hand_debug']=last.get('hand_search_debug')
        item['gestures']=dict(collections.Counter(h.get('gesture') for row in values for h in row.get('hands',[])))
    if isinstance(values[-1],dict) and 'x' in values[-1] and 'z' in values[-1]:
        item['nonzero']=sum(abs(v['x'])+abs(v['z'])>1e-5 for v in values)
    output[topic]=item
path=Path(__file__).with_name('motion-diagnosis.json');path.write_text(json.dumps(dict(topics=inventory,observed=output),indent=2))
print(json.dumps(output),flush=True)
os._exit(0)
