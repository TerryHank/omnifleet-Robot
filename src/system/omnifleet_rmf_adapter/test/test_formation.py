import copy
import math

import pytest

from test_missions import fleet, save, start
from omnifleet_rmf_adapter.missions import Missions


def capture(fleet):
    return fleet.owner.command({'op':'formation_capture','order':['a','b','c']},fleet.states)


def test_capture_is_stationary_persistent_and_sends_no_commands(fleet):
    capture(fleet)
    assert fleet.sent==[]
    saved=fleet.owner.formation.saved
    assert saved['offsets']['b']==[0.,4.,0.] and saved['offsets']['c']==[0.,8.,0.]
    other=Missions(fleet.config,fleet.maps,fleet.root,lambda *a,**k:None)
    assert other.formation.saved==saved and not other.formation.active and not other.jobs


@pytest.mark.parametrize('fault',['moving','manual','stale_pose','unregistered'])
def test_capture_rejects_incomplete_or_moving_fleet(fleet,fault):
    if fault=='moving':fleet.states['b']['samples']['control']['value']['stopped_seconds']=0
    elif fault=='manual':fleet.states['b']['samples']['control']['value']['manual_active']=True
    elif fault=='stale_pose':fleet.states['b']['samples']['pose']['age_seconds']=.7
    else:fleet.maps.valid_robots.remove('b')
    with pytest.raises(ValueError):capture(fleet)
    assert not fleet.owner.formation.path.exists() and not fleet.sent


def test_each_slot_tracks_the_leader_not_the_predecessor(fleet):
    capture(fleet)
    f=fleet.owner.formation;f.start(['a','b','c'],fleet.states)
    # Rotate/translate the leader before the followers finish arming.
    fleet.states['a']['samples']['pose']['value'].update(x=10.,y=2.,yaw=math.pi/2)
    f.tick(fleet.states)
    assert f.targets['b']==pytest.approx([6.,2.,math.pi/2])
    assert f.targets['c']==pytest.approx([2.,2.,math.pi/2])
    assert fleet.owner.jobs['b']['follow_points'][0]==pytest.approx([6.,2.,math.pi/2])
    assert not any(p[0]=='navigate' and p[2]=='a' for p in fleet.sent)


def test_alignment_is_used_to_convert_targets_back_to_each_local_map(fleet):
    fleet.maps.alignment['b']=[5.,2.,math.pi/2]
    capture(fleet);f=fleet.owner.formation;f.start(['a','b','c'],fleet.states)
    fleet.states['a']['samples']['pose']['value']['x']=.1;f.tick(fleet.states)
    assert fleet.owner.jobs['b']['follow_points'][0]==pytest.approx([0.,3.9,0.])


def test_formation_retains_independent_routes_and_only_admits_leader_goals(fleet):
    save(fleet,'a',[[1.,0.,0.],[2.,0.,0.]])
    save(fleet,'b',[[1.,4.,0.]])
    original=copy.deepcopy(fleet.owner.saved)
    capture(fleet);fleet.owner.command({'op':'formation_start','order':['a','b','c']},fleet.states)
    fleet.tick(7)
    assert fleet.owner.formation.phase=='HOLDING'
    packets=[p for p in fleet.sent if p[0]=='navigate']
    assert len(packets)==2 and all(p[3]['follow_formation'] and not p[3]['follow_trail'] for p in packets)
    with pytest.raises(ValueError,match='仅向领车'):start(fleet,'b')
    start(fleet,'a');fleet.tick(5)
    assert any(p[0]=='navigate' and p[2]=='a' and p[3]['poses']==[[1.,0.,0.],[2.,0.,0.]] for p in fleet.sent)
    assert fleet.owner.saved==original


@pytest.mark.parametrize('fault',['offline','epoch','map_transform','blocked'])
def test_member_failure_stops_all_owned_tasks_and_never_auto_resumes(fleet,fault):
    capture(fleet);f=fleet.owner.formation;f.start(['a','b','c'],fleet.states);fleet.tick(7)
    assert f.phase=='HOLDING'
    if fault=='offline':fleet.states['b']['online']=False
    elif fault=='epoch':fleet.states['b']['samples']['navigation']['value']['localization_epoch']='changed'
    elif fault=='map_transform':fleet.maps.alignment['b'][0]+=.1
    elif fault=='blocked':fleet.states['b']['samples']['navigation']['value']['formation_stream']={'blocked':True}
    fleet.tick(3)
    assert not f.active and f.phase=='FAILED'
    before=len([p for p in fleet.sent if p[0]=='navigate'])
    fleet.states['b']['online']=True;fleet.tick(8)
    assert len([p for p in fleet.sent if p[0]=='navigate'])==before


def test_avoiding_an_obstacle_keeps_the_saved_slot_and_reduces_leader_pace(fleet):
    capture(fleet);f=fleet.owner.formation;f.start(['a','b','c'],fleet.states);fleet.tick(7)
    saved=copy.deepcopy(f.saved)
    fleet.states['b']['samples']['pose']['value']['x']+=.7
    fleet.tick(2)
    assert f.active and f.saved==saved and f.errors['b']>.5
    pace=[p for p in fleet.sent if p[0]=='formation_speed'][-1]
    assert 0<pace[3]['percentage']<100./8.


def test_single_and_multi_point_navigation_remain_independent_when_not_in_formation(fleet):
    capture(fleet)
    fleet.owner.command({'op':'single_goal','robot_id':'a','point':[1.,0.,0.]},fleet.states)
    fleet.owner.command({'op':'route_add','robot_id':'b','point':[1.,4.,0.]},fleet.states)
    fleet.owner.command({'op':'route_add','robot_id':'c','point':[1.,8.,0.]},fleet.states)
    fleet.owner.command({'op':'route_start','robot_id':'b','id':'execute-b'},fleet.states)
    fleet.owner.command({'op':'route_start','robot_id':'c','id':'execute-c'},fleet.states)
    fleet.tick(5)
    assert {p[2] for p in fleet.sent if p[0]=='navigate'}=={'a','b','c'}
    assert not fleet.owner.formation.active


def test_changing_member_order_requires_explicit_recapture(fleet):
    capture(fleet)
    with pytest.raises(ValueError,match='顺序'):fleet.owner.formation.start(['b','a','c'],fleet.states)
    assert not fleet.sent


def test_released_stopped_manual_mode_can_capture_and_acquire_formation_lease(fleet):
    for state in fleet.states.values():
        state['samples']['control']['value'].update(manual_active=True,manual_command_age=2.)
    capture(fleet);fleet.owner.formation.start(['a','b','c'],fleet.states);fleet.tick(7)
    assert fleet.owner.formation.phase=='HOLDING'


def test_running_formation_uses_shared_pose_validity_instead_of_reapplying_capture_age(fleet):
    capture(fleet);f=fleet.owner.formation;f.start(['a','b','c'],fleet.states);fleet.tick(7)
    assert f.phase=='HOLDING'
    fleet.states['a']['samples']['pose']['age_seconds']=.572
    fleet.states['a']['ipc_age_seconds']=.087
    fleet.states['a']['fresh']['pose']=True
    f.tick(fleet.states)
    assert f.active and f.phase=='HOLDING'
    fleet.states['a']['fresh']['pose']=False
    f.tick(fleet.states)
    assert not f.active and f.phase=='FAILED' and '定位不新鲜' in f.message


def test_slot_velocity_includes_the_leader_translation_and_rotation(fleet):
    capture(fleet);f=fleet.owner.formation;f.start(['a','b','c'],fleet.states);fleet.tick(7)
    fleet.states['a']['samples']['control']['value'].update(velocity=[.3,.2],velocity_age=0.)
    fleet.states['a']['samples']['control']['age_seconds']=0.
    f.tick(fleet.states)
    updates=[p for p in fleet.sent if p[0]=='follow_update' and p[2]=='b']
    assert updates[-1][3]['predecessor_velocity']==pytest.approx([-.5,.2])
