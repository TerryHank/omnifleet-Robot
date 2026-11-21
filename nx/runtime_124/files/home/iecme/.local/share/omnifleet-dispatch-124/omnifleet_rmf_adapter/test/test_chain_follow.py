import math
import pytest
from test_missions import fleet
from omnifleet_rmf_adapter.missions import Trail


def start(fleet):
    for robot,x in zip(('a','b','c'),(4.,2.,0.)):
        fleet.states[robot]['samples']['pose']['value'].update(x=x,y=0.)
    fleet.owner.command({'op':'follow_start','order':['a','b','c'],'distance':1.4},fleet.states)
    fleet.tick(5)


def test_start_with_existing_spacing_does_not_wait_for_leader_to_arrive(fleet):
    start(fleet)
    assert fleet.owner.jobs['b']['phase']=='EXECUTING'
    assert fleet.owner.jobs['c']['phase']=='EXECUTING'
    assert fleet.owner.jobs['b']['predecessor']=='a'
    assert fleet.owner.jobs['c']['predecessor']=='b'
    assert all(p[3]['follow_trail'] for p in fleet.sent if p[0]=='navigate')


def test_updates_arrive_during_execution_without_goal_completion_or_cancel(fleet):
    start(fleet)
    before=len([p for p in fleet.sent if p[0]=='navigate' and p[2]=='b'])
    for _ in range(8):
        fleet.states['a']['samples']['pose']['value']['x']+=.2
        fleet.tick()
    updates=[p for p in fleet.sent if p[0]=='follow_update' and p[2]=='b']
    assert len(updates)>=8
    assert updates[-1][3]['poses'][-1][0]>updates[0][3]['poses'][-1][0]+1.
    assert len([p for p in fleet.sent if p[0]=='navigate' and p[2]=='b'])==before
    assert not any(p[0]=='disarm' for p in fleet.sent)
    assert fleet.owner.jobs['b']['phase']=='EXECUTING'


def test_third_vehicle_uses_second_vehicles_current_pose(fleet):
    start(fleet)
    for i in range(10):
        fleet.states['a']['samples']['pose']['value']['x']+=.2
        fleet.states['b']['samples']['pose']['value']['y']+=.2
        fleet.tick()
    second=[p for p in fleet.sent if p[0]=='follow_update' and p[2]=='b'][-1][3]['poses']
    third=[p for p in fleet.sent if p[0]=='follow_update' and p[2]=='c'][-1][3]['poses']
    assert len(second)==1
    assert len(third)==1
    bearing=math.atan2(2.,2.)
    assert third[-1]==pytest.approx([2.-1.4*math.cos(bearing),2.-1.4*math.sin(bearing),bearing])
    assert any(p[1]>.1 for p in third)


def test_lost_middle_vehicle_stops_chain_without_skipping_it(fleet):
    start(fleet);fleet.states['b']['online']=False;fleet.tick()
    assert not fleet.owner.follow['active']
    assert fleet.owner.follow['order']==['a','b','c']
    assert any(p[0]=='disarm' and p[2]=='c' for p in fleet.sent)


def test_pose_freshness_flag_does_not_stop_connected_stream(fleet):
    start(fleet);fleet.states['a']['transport_connected']=True;fleet.states['a']['online']=False;fleet.states['a']['fresh']['pose']=False;fleet.tick()
    assert fleet.owner.follow['active']


def test_corner_target_keeps_arc_length_and_does_not_cut_to_current_leader():
    trail=Trail()
    for pose in ([0.,0.,0.],[1.,0.,0.],[2.,0.,0.],[2.,1.,math.pi/2],[2.,2.,math.pi/2]):trail.add(pose)
    progress,path=trail.segment([1.,0.,0.],1.,1.4)
    assert progress==pytest.approx(1.)
    assert path[-1]==pytest.approx([2.,.6,math.pi/2])
    assert [2.,0.,0.] in path
