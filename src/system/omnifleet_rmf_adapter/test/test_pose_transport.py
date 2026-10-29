import math
from types import SimpleNamespace as NS
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer
from omnifleet_rmf_adapter.client import RobotObserver


def test_fresh_tf_replaces_missing_odometry_without_refreshing_replayed_samples():
    samples={};records=[]
    def record(key,value):samples[key]=(0.,value);records.append(value)
    observer=NS(transforms={'tf':{},'tf_static':{}},cache_pending={},pose_buffer=Buffer(),
                pose_frame='map',pose_base='base_link',samples=samples,record=record)
    t=TransformStamped();t.header.frame_id='map';t.child_frame_id='base_link';t.header.stamp.sec=2
    t.transform.translation.x=1.;t.transform.rotation.z=math.sin(.4/2);t.transform.rotation.w=math.cos(.4/2)
    RobotObserver.cache_tf(observer,'tf',TFMessage(transforms=[t]))
    assert records[-1]['x']==1. and records[-1]['source']=='tf'
    count=len(records);RobotObserver.cache_tf(observer,'tf',TFMessage(transforms=[t]))
    assert len(records)==count
    odom=Odometry();odom.header.frame_id='map';odom.header.stamp.sec=1;odom.pose.pose.orientation.w=1.
    RobotObserver.pose(observer,odom);assert len(records)==count
    odom.header.stamp.sec=3;odom.pose.pose.position.x=2.
    RobotObserver.pose(observer,odom)
    assert records[-1]['source']=='odometry' and records[-1]['x']==2.
