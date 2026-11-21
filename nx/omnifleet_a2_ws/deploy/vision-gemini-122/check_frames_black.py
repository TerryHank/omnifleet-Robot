from pathlib import Path
import json,time,os
import rclpy
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
import numpy as np

rclpy.init();node=rclpy.create_node('verify_gemini_frames');rows={};counts={};subscriptions=[]
def frame(message,topic):
    counts[topic]=counts.get(topic,0)+1
    data=np.frombuffer(message.data,dtype=np.uint8)
    rows[topic]=dict(width=message.width,height=message.height,encoding=message.encoding,
        stamp=[message.header.stamp.sec,message.header.stamp.nanosec],sample_max=int(data[::64].max()) if data.size else 0,
        sample_std=float(data[::64].std()) if data.size else 0.)
for topic in ['/camera/color/image_raw','/camera/depth/image_raw']:
    subscriptions.append(node.create_subscription(Image,topic,lambda m,t=topic:frame(m,t),qos_profile_sensor_data))
start=time.monotonic();end=start+12
while time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.1)
summary=dict(seconds=time.monotonic()-start,counts=counts,last=rows)
Path(__file__).with_name('frames.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary),flush=True)
assert all(counts.get(t,0)>5 for t in ['/camera/color/image_raw','/camera/depth/image_raw']),'Missing advancing color/depth'
assert rows['/camera/color/image_raw']['sample_std']>1.,'Flat or black color frame'
os._exit(0)
