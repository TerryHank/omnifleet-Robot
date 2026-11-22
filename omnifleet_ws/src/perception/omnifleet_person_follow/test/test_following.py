import math
from pathlib import Path
from types import SimpleNamespace as NS
import xml.etree.ElementTree as ET
import numpy as np
from omnifleet_person_follow.following import StandoffGoal, free_candidates,ImageCentering,VisualApproach


def test_stationary_person_goal_does_not_orbit_with_robot_motion():
    follow=StandoffGoal()
    goal=follow.update([0.,0.],[2.,0.],1.,7)
    np.testing.assert_allclose(goal,[1.,0.,0.])
    for index in range(1,10):
        np.testing.assert_allclose(follow.update([.02*index,.01*index],[2.,0.],1.+index*.1,7),goal)


def test_one_meter_noise_does_not_trigger_alternating_motion():
    follow=StandoffGoal()
    for index in range(100):
        x=1.+.08*math.sin(index)
        assert follow.update([0.,0.],[x,0.],index*.033,7) is None
        assert follow.mode=='HOLD'


def test_follow_holds_in_band_and_resumes_only_outside_hysteresis():
    follow=StandoffGoal()
    assert follow.update([0.,0.],[1.5,0.],1.,7) is not None
    assert follow.mode=='FOLLOW'
    assert follow.update([.5,0.],[1.5,0.],2.,7) is None
    assert follow.mode=='HOLD'
    assert follow.update([.4,0.],[1.5,0.],3.,7) is None
    assert follow.update([.3,0.],[1.5,0.],4.,7) is not None
    assert follow.mode=='FOLLOW'


def test_close_person_generates_nav2_goal_behind_robot_facing_person():
    follow=StandoffGoal()
    goal=follow.update([0.,0.],[.6,0.],1.,7)
    assert follow.mode=='BACKOFF'
    np.testing.assert_allclose(goal,[-.4,0.,0.])
    assert follow.update([-.4,0.],[.6,0.],2.,7) is None
    assert follow.mode=='HOLD'


def test_smoothing_and_step_do_not_replan_for_small_target_jitter():
    follow=StandoffGoal()
    first=follow.update([0.,0.],[2.,0.],1.,7)
    for index in range(1,100):
        point=[2.+.08*math.sin(index),.04*math.cos(index)]
        np.testing.assert_allclose(follow.update([0.,0.],point,1.+index*.033,7),first)
    moved=follow.update([0.,0.],[2.5,0.],10.,7)
    assert moved[0] > 1.4


def test_obstructed_standoff_selects_free_ring_and_never_commands_blocked_goal():
    costs=np.zeros((100,100),np.int8)
    costs[45:56,55:66]=100
    origin=NS(position=NS(x=-5.,y=-5.),orientation=NS(x=0.,y=0.,z=0.,w=1.))
    grid=NS(info=NS(width=100,height=100,resolution=.1,origin=origin),data=costs.ravel())
    follow=StandoffGoal()
    goal=follow.update([0.,0.],[2.,0.],1.,7,grid)
    assert goal is not None and abs(goal[1])>.4
    np.testing.assert_allclose(np.linalg.norm(np.array(goal[:2])-[2.,0.]),1.)
    costs[:]=100
    assert follow.update([0.,0.],[2.,0.],2.,7,grid) is None
    assert follow.blocked


def test_follow_tree_is_finite_with_actual_nav2_planning_obstacles_and_reverse_controller():
    root=ET.parse(Path(__file__).parents[1]/'config/follow_dynamic.xml')
    assert not root.findall('.//KeepRunningUntilFailure') and not root.findall('.//ForceSuccess')
    assert root.find('.//GoalUpdater') is not None
    assert root.find('.//ComputePathToPose') is not None
    assert root.find('.//FollowPath').get('controller_id')=='FollowPathMPPI'
    assert root.find('.//RecoveryNode') is not None


def test_inflation_cost_is_not_an_extra_follow_admission_gate():
    origin=NS(position=NS(x=0.,y=0.),orientation=NS(x=0.,y=0.,z=0.,w=1.))
    grid=NS(info=NS(width=4,height=1,resolution=1.,origin=origin),data=[94,99,100,-1])
    np.testing.assert_array_equal(free_candidates([[.5,.5],[1.5,.5],[2.5,.5],[3.5,.5]],grid),[True,False,False,True])


def test_image_centering_turns_toward_person_without_changing_world_position():
    center=ImageCentering()
    goal=center.update([1.,2.,.1],[0,0,20,100],100,100)
    np.testing.assert_allclose(goal[:2],[1.,2.])
    assert goal[2]>.1 and center.spin_angle>0
    original=goal.copy()
    np.testing.assert_allclose(center.update([1.01,2.,.2],[5,0,25,100],100,100),original)
    assert center.update([1.,2.,.3],[45,0,55,100],100,100) is None


def test_centered_image_jitter_does_not_keep_restarting_turns():
    center=ImageCentering()
    for index in range(100):
        offset=3*math.sin(index)
        assert center.update([0.,0.,0.],[40+offset,0,60+offset,100],100,100) is None


def test_visual_approach_is_one_fixed_nav2_step_until_completion():
    approach=VisualApproach()
    first=approach.update([0.,0.,0.],0.)
    assert first==[.2,0.,0.]
    token=approach.token
    assert approach.update([.1,0.,0.],0.)==first and approach.token==token
    assert approach.update([.2,0.,0.],0.,completed=True)==[.4,0.,0.]
    assert approach.token>token
    approach.reset();assert approach.goal is None


def test_person_approach_enters_backoff_below_90cm_and_holds_above_95cm():
    follow=StandoffGoal()
    assert follow.update([0.,0.],[1.,0.],0.,7) is None
    assert follow.update([0.,0.],[.92,0.],2.,7) is None
    goal=follow.update([0.,0.],[.88,0.],4.,7)
    assert follow.mode=='BACKOFF' and goal[0]<0 and abs(goal[2])<1e-9
    assert follow.update([-.1,0.],[.88,0.],6.,7) is None
    assert follow.mode=='HOLD'
    for index in range(90):
        distance=.98+.07*math.sin(index)
        assert follow.update([0.,0.],[distance,0.],7.+index/30.,7) is None


def test_blocked_rear_never_substitutes_a_forward_or_sideways_approach():
    costs=np.zeros((80,80),np.int8)
    costs[:,:40]=100
    origin=NS(position=NS(x=-2.,y=-2.),orientation=NS(x=0.,y=0.,z=0.,w=1.))
    grid=NS(info=NS(width=80,height=80,resolution=.05,origin=origin),data=costs.ravel())
    follow=StandoffGoal()
    assert follow.update([0.,0.],[.6,0.],1.,7,grid) is None
    assert follow.mode=='BACKOFF' and follow.blocked


def test_reverse_goal_is_fixed_in_world_and_moves_further_back_as_person_approaches():
    follow=StandoffGoal()
    first=follow.update([0.,0.],[.75,0.],1.,7)
    for index in range(1,5):
        assert follow.update([-.01*index,0.],[.75,0.],1.+index*.1,7)==first
    closer=follow.update([-.04,0.],[.5,0.],3.,7)
    assert closer[0] < first[0] and abs(closer[2])<1e-9


def test_rapid_person_approach_reverses_without_waiting_for_ema_to_catch_up():
    follow=StandoffGoal()
    assert follow.update([0.,0.],[1.4,0.],1.,7)[0]>0
    goal=follow.update([0.,0.],[.8,0.],1.033,7)
    assert follow.mode=='BACKOFF' and goal[0]<0


def test_half_meter_standoff_follows_holds_and_reverses_with_hysteresis():
    follow=StandoffGoal(distance=.5)
    np.testing.assert_allclose(follow.update([0.,0.],[1.,0.],1.,7),[.5,0.,0.])
    assert follow.update([.5,0.],[1.,0.],2.,7) is None and follow.mode=='HOLD'
    assert follow.update([.5,0.],[.96,0.],4.,7) is None
    goal=follow.update([.5,0.],[.84,0.],6.,7)
    assert follow.mode=='BACKOFF' and goal[0]<.5
    assert follow.update([.34,0.],[.84,0.],8.,7) is None and follow.mode=='HOLD'
