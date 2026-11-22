import numpy as np
from omnifleet_person_follow.identity import FollowIdentity


def track(identity=1, confidence=.9, bbox=(100,50,220,350)):
    return dict(id=identity, bbox=list(bbox), confidence=confidence)


def scene(color=(0,0,220)):
    return np.full((480,640,3), color, np.uint8)


def test_short_gap_new_tracker_id_keeps_follow_id_and_motion_prediction():
    identity=FollowIdentity(); warp=np.eye(2,3)
    initial=[track()]; identity.apply(initial,scene(),1,10.,warp,{})
    identity.apply([],scene(),1,10.1,warp,{})
    restored=[track(8,bbox=(135,50,255,350))]
    identity.apply(restored,scene(),1,10.2,np.array([[1,0,35],[0,1,0]]),{})
    assert restored[0]['id']==1 and restored[0]['tracker_id']==8
    assert identity.rebindings==1
    continued=[track(8,confidence=.25)]
    identity.apply(continued,scene(),1,10.23,warp,{})
    assert continued[0]['id']==1


def test_wrong_appearance_expired_gap_or_low_score_does_not_rebind():
    for image,stamp,confidence in [(scene((220,0,0)),10.2,.9),(scene(),13.,.9),(scene(),10.2,.3)]:
        identity=FollowIdentity(); identity.apply([track()],scene(),1,10.,np.eye(2,3),{})
        candidate=[track(8,confidence)]
        identity.apply(candidate,image,1,stamp,np.eye(2,3),{})
        assert candidate[0]['id']==8 and identity.rebindings==0


def test_two_similar_people_are_not_silently_swapped():
    identity=FollowIdentity(); identity.apply([track()],scene(),1,10.,np.eye(2,3),{})
    candidates=[track(8),track(9,bbox=(110,50,230,350))]
    identity.apply(candidates,scene(),1,10.2,np.eye(2,3),{})
    assert [item['id'] for item in candidates]==[8,9]


def test_inconsistent_available_depth_rejects_rebinding():
    identity=FollowIdentity(); identity.apply([track()],scene(),1,10.,np.eye(2,3),{})
    identity.observe_depth({1:dict(xyz=[0,0,1.],position_time=10.)})
    candidates=[track(8)]
    identity.apply(candidates,scene(),1,10.2,np.eye(2,3),
                   {8:dict(xyz=[0,0,3.],position_time=10.2)})
    assert candidates[0]['id']==8


def test_no_locked_target_does_not_change_other_tracker_ids():
    identity=FollowIdentity(); candidates=[track(8)]
    identity.apply(candidates,scene(),None,10.,np.eye(2,3),{})
    assert candidates[0]['id']==8 and identity.identity is None
