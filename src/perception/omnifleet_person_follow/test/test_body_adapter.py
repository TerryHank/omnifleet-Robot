import json
from types import SimpleNamespace as NS
import pytest
from std_msgs.msg import Header,String
from geometry_msgs.msg import Twist
from omnifleet_person_follow.body_adapter import body_targets,BodyTrackingAdapter


def test_body_roi_does_not_depend_on_depth_or_fabricate_head_or_keypoints():
    header=Header(frame_id='camera_color_optical_frame');header.stamp.sec=17
    track=dict(id=7,bbox=[10,20,300,600],confidence=.9)
    without=body_targets([track],header)
    with_depth=body_targets([{**track,'xyz':[.1,.2,.3]}],header)
    assert without==with_depth
    target=without.targets[0]
    assert target.track_id==7 and target.rois[0].type=='body'
    assert target.rois[0].rect.width==290 and target.rois[0].rect.height==580
    assert not target.attributes and not target.points and len(target.rois)==1
    assert header.frame_id=='camera_color_optical_frame' and without.header.stamp.sec==17
    assert not body_targets([],header).targets


def test_native_id_is_authoritative_and_velocity_is_only_observed():
    publishers=[];callbacks={}
    node=NS(global_frame='map',manager=NS(),following=NS(),navigation=NS(),
            goal_marker_pub=NS(publish=lambda message:None),
            create_publisher=lambda kind,topic,qos:publishers.append(topic) or NS(publish=lambda message:None),
            create_subscription=lambda kind,topic,callback,qos:callbacks.update({topic:callback}))
    bridge=BodyTrackingAdapter(node)
    callbacks['/vision/body_tracking/native_status'](String(data=json.dumps(dict(state='TRACKING',track_id=22,serial_lost_num=0))))
    command=Twist();command.linear.x=.2;command.angular.z=-.4
    callbacks['/vision/body_tracking/cmd_vel'](command)
    bridge.tick();assert node.manager.track_id==22
    data=dict(target_depth_m=.65,nav_goal={'x':1},follow_distance_m=1,nav2_controller='FollowPathMPPI')
    bridge.annotate(data)
    assert data['controller_backend']=='body_tracking_cpp'
    assert data['depth_display_m']==.65 and not data['depth_display_only']
    assert data['depth_backoff_enabled']
    assert data['follow_distance_m']==1.0 and data['nav_goal'] is None
    assert data['metric_distance_control'] and data['nav2_controller'] is None
    assert data['velocity_request']==pytest.approx(dict(linear_x=.2,angular_z=-.4))
    assert publishers==['/vision/body_tracking/targets']  # No Python motion publisher.
