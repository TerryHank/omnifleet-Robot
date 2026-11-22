import time
from types import SimpleNamespace as NS

import pytest
from std_msgs.msg import Header
from omnifleet_person_follow.tros_adapter import TrosAdapter, make_target, parse_status


@pytest.mark.parametrize('text,state,identity,distance',[
    ('FollowStatus DISABLED','PAUSED',None,None),
    ('FollowStatus IDLE_SEARCHING','IDLE',None,None),
    ('FollowStatus TRACKING:id=7:dist=1.23','TRACKING',7,1.23),
    ('FollowStatus TRACKING_TOO_CLOSE:id=7:dist=0.42','TRACKING',7,.42),
    ('FollowStatus WILL_BE_LOST:id=7:dist=1.15','TRACKING',7,1.15),
    ('FollowStatus LOST_BELIEF_NAV:round=2:dist=1.8','LOST',None,1.8),
])
def test_official_status_is_not_python_manager_state(text,state,identity,distance):
    assert parse_status(text)[1:]==(state,identity,distance)


def test_metric_dimensions_and_rep103_position_are_not_depth_pixels():
    track=dict(id=7,bbox=[10,20,210,420],confidence=.9,xyz=[.1,-.2,1.])
    target=make_target(track,[1.,-.1,.2],[1000.,0,0,0,1000.,0,0,0,1])
    attributes={a.type:a.value for a in target.attributes}
    assert attributes==pytest.approx(dict(x_cm=100,y_cm=-10,width_cm=20,height_cm=40,y_offset=20))
    assert (target.track_id,target.rois[0].rect.width,target.rois[0].confidence)==pytest.approx((7,200,.9))


def adapter():
    a=TrosAdapter.__new__(TrosAdapter)
    published=[]
    a.node=NS(tf=NS(lookup_transform=lambda *args:object()),coordinate_error='')
    a.input_pub=NS(publish=published.append);a.input_frames=0
    return a,published


def test_bridge_preserves_measurement_header_and_rejects_stale_depth():
    a,out=adapter();header=Header(frame_id='camera_color_optical_frame');header.stamp.sec=10
    fresh=dict(id=7,bbox=[0,0,20,40],confidence=.9,xyz=[.1,0,1.],position_time=time.monotonic())
    stale={**fresh,'id':8,'position_time':time.monotonic()-1}
    a.publish([fresh,stale],header,NS(k=[1000.,0,0,0,1000.,0,0,0,1]),lambda *args:[1.,-.1,0.])
    assert header.frame_id=='camera_color_optical_frame'
    assert out[0].header.frame_id=='rgbd_view_z_up' and out[0].header.stamp.sec==10
    assert [t.track_id for t in out[0].targets]==[7]
    a.publish([],header,None,lambda *args:None)
    assert not out[-1].targets  # Empty frames still drive official LOST/IDLE timers.


def test_pause_during_enable_request_still_sends_disable():
    a,out=adapter()
    requests=[]
    a.name,a.state,a.track_id,a.distance='DISABLED','PAUSED',None,None
    a.raw_status='FollowStatus DISABLED';a.goal=None
    a.node.manager=NS();a.node.following=NS();a.node.navigation=NS()
    a.node.goal_marker_pub=NS(publish=lambda message:None)
    a.future_desired=True;a.desired=False;a.applied=False
    a.future=NS(done=lambda:True,result=lambda:NS(success=True,message='enabled'))
    a.enable=NS(service_is_ready=lambda:True,call_async=lambda request:requests.append(request) or NS())
    a.tick()
    assert len(requests)==1 and not requests[0].data
