from types import SimpleNamespace as NS
import math
import numpy as np
from omnifleet_person_follow.core import FollowManager
from omnifleet_person_follow.recovery import SearchRecovery, nearest_free


def detection(identity, x, stamp, confidence=.9):
    return dict(id=identity, world=[x, 0., 0.], position_time=stamp, confidence=confidence)


def lost_manager():
    manager = FollowManager()
    manager.gesture('thumbs_up', 7)
    manager.observe([detection(7, 1., 10.)], 10.)
    manager.observe([detection(7, 1.1, 11.)], 11.)
    manager.observe([], 12.1)
    assert manager.state == 'LOST'
    return manager


def test_relock_new_id_requires_measured_movement_and_world_proximity():
    manager = lost_manager()
    manager.observe([detection(8, 1.2, 12.2)], 12.2)
    assert manager.track_id == 7
    manager.observe([detection(8, 1.2, 12.5)], 12.5)
    assert manager.track_id == 7
    manager.observe([detection(8, 1.5, 12.9)], 12.9)
    assert (manager.state, manager.track_id) == ('TRACKING', 8)
    assert manager.relock_reason == 'new_id_spatial_motion_continuity'
    assert manager.gesture('open_palm', 7) is None
    assert manager.gesture('open_palm', 8) == 'paused'


def test_far_moving_and_low_confidence_candidates_do_not_replace_person():
    manager = lost_manager()
    for stamp, x in [(12.2, 10.), (12.9, 10.5)]:
        manager.observe([detection(8, x, stamp), detection(9, 1.+stamp-12., stamp, .4)], stamp)
    assert manager.state == 'LOST' and manager.track_id == 7


def test_reused_same_id_far_from_last_location_is_not_accepted():
    manager = lost_manager()
    manager.observe([detection(7, 20., 12.3)], 12.3)
    assert manager.state == 'LOST'
    manager.observe([detection(7, 1.2, 12.4)], 12.4)
    assert manager.state == 'TRACKING'


def test_stale_depth_does_not_keep_visible_detection_tracking_forever():
    manager = lost_manager()
    manager.observe([detection(7, 1.1, 11.)], 12.5)
    assert manager.state == 'LOST'
    assert manager.gesture('thumbs_up', 9) == 'relocked'
    assert manager.track_id == 9


def test_search_prediction_arrival_scan_then_history_without_freezing():
    recovery = SearchRecovery()
    recovery.start([(10., [1.,0.,0.]), (11., [2.,0.,0.])], [3.,0.,0.], [0.,0.,0.], None, 12.)
    assert recovery.phase == 'NAV_PREDICTED' and recovery.goal[:2] == [3.,0.]
    first = recovery.token
    recovery.update([3.,0.,0.], 13., completed=True)
    assert recovery.phase == 'SCAN' and recovery.token != first
    for i in range(4):
        previous = recovery.goal.copy()
        recovery.update(previous, 13.1+i*.1, completed=True)
    assert recovery.phase == 'NAV_LAST_KNOWN'
    assert recovery.goal[:2] == [2.,0.]


def test_no_depth_history_still_searches_directionally_and_timeout_finishes():
    recovery = SearchRecovery(timeout=30.)
    recovery.start([], None, [0.,0.,0.], None, 1., direction=-1.)
    assert recovery.phase == 'SCAN' and recovery.goal[2] == -math.pi/2
    assert recovery.update([0.,0.,0.], 32.) is None
    assert recovery.phase == 'EXHAUSTED'
    recovery.reset()
    assert recovery.phase == 'OFF' and recovery.goal is None


def test_history_observation_faces_last_location_from_observation_point():
    recovery = SearchRecovery()
    recovery.start([(1.,[1.,0.,0.]),(2.,[2.,0.,0.])],None,[3.,0.,0.],None,3.)
    recovery.update([2.,0.,math.pi],4.,completed=True)
    for index in range(4):
        recovery.update(recovery.goal.copy(),4.1+index*.1,completed=True)
    assert recovery.phase == 'NAV_HISTORY' and recovery.goal[:2] == [1.,0.]
    assert recovery.goal[2] == 0.


def test_nearest_free_skips_unknown_obstacles_and_rewinds_outside_map():
    data = np.full((10,10), 100, np.int8)
    data[3,3], data[4,4] = -1, 0
    origin = NS(position=NS(x=0.,y=0.), orientation=NS(x=0.,y=0.,z=0.,w=1.))
    grid = NS(info=NS(width=10,height=10,resolution=.1,origin=origin),data=data.ravel())
    np.testing.assert_allclose(nearest_free([.3,.3],grid),[.45,.45])
    recovery = SearchRecovery()
    recovery.start([(1.,[.45,.45,0.]),(2.,[20.,20.,0.])], [23.,20.,0.], [0.,0.,0.], grid, 3.)
    assert recovery.phase == 'NAV_HISTORY'
    np.testing.assert_allclose(recovery.goal[:2], [.45,.45])


def test_nav_failure_advances_search_and_paused_manager_never_relocks():
    recovery = SearchRecovery()
    recovery.start([(1.,[2.,0.,0.])], None, [0.,0.,0.], None, 3.)
    recovery.update([0.,0.,0.], 4., failed=True)
    assert recovery.phase == 'SCAN'
    recovery.update([0.,0.,0.], 5., failed=True)
    assert recovery.phase == 'EXHAUSTED'
    manager = lost_manager()
    manager.gesture('open_palm',7)
    manager.observe([detection(8,1.2,13.)],13.)
    manager.observe([detection(8,1.7,14.)],14.)
    assert (manager.state,manager.track_id) == ('PAUSED',7)
