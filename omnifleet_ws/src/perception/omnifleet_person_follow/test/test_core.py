import numpy as np
from omnifleet_person_follow.core import FollowManager, classify_hand, depth_position, hand_owner, trailing_goal, mask_coordinates


def test_auto_follow_locks_center_person_without_depth_and_keeps_that_id():
    manager=FollowManager()
    left=dict(id=3,bbox=[0,0,100,200],confidence=.99)
    center=dict(id=7,bbox=[400,0,600,200],confidence=.8)
    assert manager.auto_lock([left,center],10.,1000) is center
    assert (manager.state,manager.track_id,manager.last_seen)==('TRACKING',7,10.)
    assert manager.target(center,10.) is None
    assert manager.auto_lock([left],10.1,1000) is None and manager.track_id==7
    manager.observe([],11.1)
    assert manager.state=='LOST' and manager.track_id==7
    assert manager.auto_lock([left],11.2,1000) is None


def test_auto_follow_does_not_override_an_explicit_pause():
    manager=FollowManager(state='PAUSED')
    assert manager.auto_lock([dict(id=7,bbox=[0,0,100,200])],1.,100) is None
    assert manager.state=='PAUSED' and manager.track_id is None


def hand(extended, thumb=False):
    points = np.zeros((21, 3), np.float32)
    points[1, :2], points[2, :2] = (1, -3), (2, -5)
    points[3, :2], points[4, :2] = (2, -7 if thumb else -4), (2, -11 if thumb else -3)
    for opened, (pip, dip, tip) in zip(extended, ((6,7,8), (10,11,12), (14,15,16), (18,19,20))):
        x = (pip - 12) / 3
        points[pip, :2] = (x, -5)
        points[dip, :2] = (x, -7 if opened else -4)
        points[tip, :2] = (x, -12 if opened else -3)
    return points


def test_three_requested_gestures():
    assert classify_hand(hand([False]*4, True)) == 'thumbs_up'
    assert classify_hand(hand([True]*4, True)) == 'open_palm'
    assert classify_hand(hand([True,True,False,False])) == 'victory'
    assert classify_hand(hand([False]*4)) == 'unknown'


def test_finger_bends_use_existing_3d_output_under_foreshortening():
    world = hand([True]*4, True)
    screen = np.zeros_like(world)
    assert classify_hand(screen, world) == 'open_palm'


def test_bystander_cannot_pause_end_or_resume_the_locked_person():
    state = FollowManager()
    assert state.gesture('thumbs_up', 7) == 'locked'
    for gesture in ['victory', 'open_palm', 'thumbs_up']:
        assert state.gesture(gesture, 8) is None
        assert (state.state, state.track_id) == ('TRACKING', 7)
    assert state.gesture('open_palm', 7) == 'paused'
    state.observe([], 100.)
    assert (state.state, state.track_id) == ('PAUSED', 7)
    assert state.gesture('thumbs_up', 8) is None
    assert state.gesture('thumbs_up', 7) == 'resumed'
    assert state.gesture('victory', 7) == 'ended'
    assert (state.state, state.track_id) == ('IDLE', None)


def test_lost_same_id_recovery_prediction_and_no_automatic_id_switch():
    state = FollowManager()
    state.gesture('thumbs_up', 7)
    state.observe([{'id':7, 'world':[0.,0.,0.]}], 10.)
    state.observe([{'id':7, 'world':[1.,0.,0.]}], 11.)
    state.observe([{'id':8, 'world':[1.1,0.,0.]}], 12.1)
    assert state.state == 'LOST' and state.track_id == 7
    assert 1 < state.predicted_position(12.1)[0] <= 4
    assert state.predicted_position(20.) is None
    state.observe([{'id':7, 'world':[1.2,0.,0.]}], 12.2)
    assert state.state == 'TRACKING'


def test_mask_wrist_association_rejects_overlap():
    track = {'id':7, 'bbox':[0,0,12,12], 'mask':np.ones((12,12),bool)}
    assert hand_owner([6,6], [track], (12,12,3)) == 7
    assert hand_owner([6,6], [track,dict(track,id=8)], (12,12,3)) is None
    assert hand_owner([13,6], [track], (12,12,3)) is None


def test_native_camera_mask_padding_matches_yolo_letterbox_rounding():
    x,y = mask_coordinates(0,0,(1280,1536,3),(512,512))
    assert int(x) == 0 and int(y) == 42


def test_depth_uses_mask_holes_original_millimetres_and_camera_intrinsics():
    depth = np.full((12,12), 3000, np.uint16)
    mask = np.zeros((12,12), bool)
    mask[3:10,3:10] = True
    depth[mask] = 1000
    depth[6,6] = 0
    track = dict(bbox=[0,0,12,12], mask=mask)
    xyz = depth_position(track, depth, [100,100,6,6], (12,12,3))
    np.testing.assert_allclose(xyz, [0.,0.,1.])
    assert depth[6,6] == 0 and depth[0,0] == 3000
    assert depth_position(track, np.zeros_like(depth), [100,100,6,6], (12,12,3)) is None


def test_trailing_goal_holds_without_reverse_or_cancel_inside_follow_distance():
    np.testing.assert_allclose(trailing_goal([0,0], [2,0,0], 1.), [1,0,0])
    np.testing.assert_allclose(trailing_goal([0,0], [.5,0,0], 1.), [0,0,0])


def test_brief_missing_depth_or_detection_preserves_dynamic_goal():
    state = FollowManager()
    state.gesture('thumbs_up', 7)
    state.observe([{'id':7, 'world':[2.,0.,0.]}], 10.)
    np.testing.assert_allclose(state.target({'id':7}, 10.1), [2.,0.,0.])
    np.testing.assert_allclose(state.target(None, 10.9), [2.,0.,0.])
    assert state.target(None, 12.) is None
