from types import SimpleNamespace as NS
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from omnifleet_rmf_adapter.client import RobotObserver


def observer():
    transform=TransformStamped();transform.header.frame_id='map';transform.child_frame_id='base_link'
    transform.header.stamp.sec=10;transform.transform.translation.x=1.22
    transform.transform.rotation.w=1.
    node=NS(samples={'pose':(0.,{'stamp_seconds':10.,'source':'odometry','x':1.})},
        transforms={'tf':{},'tf_static':{}},cache_pending={},pose_frame='map',pose_base='base_link',
        pose_buffer=NS(set_transform=lambda *a:None,set_transform_static=lambda *a:None,lookup_transform=lambda *a:transform))
    node.record=lambda key,value:node.samples.update({key:(0.,value)})
    return node,transform


def test_base_tf_replaces_sensor_odometry_with_the_same_timestamp():
    node,t=observer()
    RobotObserver.cache_tf(node,'tf',TFMessage(transforms=[t]))
    assert node.samples['pose'][1]['source']=='tf'
    assert node.samples['pose'][1]['x']==1.22


def test_new_lidar_odometry_does_not_move_the_body_pose_back_to_sensor_origin():
    node,t=observer();RobotObserver.cache_tf(node,'tf',TFMessage(transforms=[t]))
    message=Odometry();message.header.stamp.sec=11;message.header.frame_id='map'
    message.pose.pose.orientation.w=1.;message.pose.pose.position.x=2.
    RobotObserver.pose(node,message)
    assert node.samples['pose'][1]['source']=='tf'
    assert node.samples['pose'][1]['x']==1.22
