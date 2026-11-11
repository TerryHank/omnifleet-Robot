import json,time,uuid
import rclpy
from std_msgs.msg import String
from rclpy.qos import QoSProfile,ReliabilityPolicy,DurabilityPolicy
rclpy.init();node=rclpy.create_node('codex_dsh_panel_acceptance');request_id='test-'+uuid.uuid4().hex;answers=[]
def receive(msg):
 data=json.loads(msg.data)
 if data.get('request_id')==request_id:
  answers.append(data);print(json.dumps(data,ensure_ascii=False),flush=True)
node.create_subscription(String,'/omnifleet_t2/diagnostics/answer',receive,QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL))
pub=node.create_publisher(String,'/omnifleet_t2/diagnostics/question',10)
end=time.monotonic()+5
while pub.get_subscription_count()==0 and time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.1)
assert pub.get_subscription_count()>0
pub.publish(String(data=json.dumps({'request_id':request_id,'question':'请根据当前真实数据，简短判断导航是否有明显问题；列出你实际读到的局部膨胀半径、地图分辨率和TF状态。不要修改任何参数。'})))
end=time.monotonic()+140
while time.monotonic()<end and not any(a['status'] in ('complete','error') for a in answers):rclpy.spin_once(node,timeout_sec=.2)
assert answers and answers[-1]['status']=='complete',answers
node.destroy_node();rclpy.shutdown()
