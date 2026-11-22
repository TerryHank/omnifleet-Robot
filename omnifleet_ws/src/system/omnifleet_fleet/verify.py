import json,os,time,sys,re
from collections import Counter
from pathlib import Path
import rclpy
from rclpy.qos import QoSProfile,ReliabilityPolicy,DurabilityPolicy
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry,OccupancyGrid
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage
rclpy.init();n=rclpy.create_node('fleet_static_verification_'+os.environ['OMNIFLEET_ROBOT_ID'])
counts=Counter();details={};tf={};received={}
def cb(topic,msg):
    counts[topic]+=1;received[topic]=time.monotonic()
    if isinstance(msg,PointCloud2):details[topic]={'points':msg.width*msg.height,'frame':msg.header.frame_id}
    if isinstance(msg,Odometry):details[topic]={'v':msg.twist.twist.linear.x,'w':msg.twist.twist.angular.z,'frame':msg.header.frame_id,'child':msg.child_frame_id}
    if isinstance(msg,OccupancyGrid):details[topic]={'width':msg.info.width,'height':msg.info.height,'frame':msg.header.frame_id}
    if isinstance(msg,String):
        try:
            data=json.loads(msg.data);details[topic]={k:data.get(k) for k in ('robot_id','control_mode','nav_ready','control_gate_ready','network_error','safety_stop_reason','local_pose','velocity','estop','shared_map','coordinator_age')}
        except ValueError:details[topic]=msg.data[:100]
    if isinstance(msg,Twist):details[topic]={'v':msg.linear.x,'w':msg.angular.z}
    if isinstance(msg,TFMessage):
        for t in msg.transforms:tf[topic+' '+t.header.frame_id+' -> '+t.child_frame_id]={'stamp':t.header.stamp.sec+t.header.stamp.nanosec*1e-9,'x':t.transform.translation.x,'y':t.transform.translation.y}
for topic,kind,latched in [('rslidar_points',PointCloud2,False),('odom',Odometry,False),('lidar_odometry/pose',Odometry,False),('map',OccupancyGrid,True),('global_costmap/costmap',OccupancyGrid,True),('local_costmap/costmap',OccupancyGrid,True),('navigation/local_status',String,False),('navigation/cmd_vel_safe',Twist,False),('tf',TFMessage,False),('tf_static',TFMessage,True)]:
    name='/'+topic
    qos=QoSProfile(depth=5,reliability=ReliabilityPolicy.RELIABLE if latched else ReliabilityPolicy.BEST_EFFORT,durability=DurabilityPolicy.TRANSIENT_LOCAL if latched else DurabilityPolicy.VOLATILE)
    n.create_subscription(kind,name,lambda m,t=name:cb(t,m),qos)
end=time.monotonic()+float(sys.argv[1] if len(sys.argv)>1 else 8)
while time.monotonic()<end:rclpy.spin_once(n,timeout_sec=.05)
topics=n.get_topic_names_and_types();nodes=n.get_node_names_and_namespaces();services=n.get_service_names_and_types()
result={'host':os.environ['OMNIFLEET_ROBOT_ID'],'rmw':os.environ['RMW_IMPLEMENTATION'],'domain':os.environ['ROS_DOMAIN_ID'],
        'counts':dict(counts),'details':details,'tf':tf,'nodes':nodes,'topics':topics,'services':services,
        'unexpected_prefixed_topics':[t for t,_ in topics if re.match(r'^/robot_[0-9]+/', t)]}
path=Path('/home/iecme/robot_backups/fleet_zenoh_20260910')/(sys.argv[2] if len(sys.argv)>2 else 'verify-latest.json');path.write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ('topics','services','nodes','tf')},indent=2))
n.destroy_node();rclpy.shutdown()
