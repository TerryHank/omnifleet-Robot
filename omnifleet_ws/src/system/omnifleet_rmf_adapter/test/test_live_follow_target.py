import math
import pytest
from test_missions import fleet
from omnifleet_rmf_adapter.map_hub import compose,inverse


def latest(fleet,robot):
    return [p[3]['poses'] for p in fleet.sent if p[0]=='follow_update' and p[2]==robot][-1]


def test_turn_uses_current_relative_position_without_mandatory_old_corner(fleet):
    fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':1.},fleet.states)
    fleet.tick(5)
    fleet.states['a']['samples']['pose']['value'].update(x=3.,y=2.,yaw=math.pi/2)
    fleet.states['b']['samples']['pose']['value'].update(x=3.,y=0.,yaw=0.)
    fleet.tick()
    assert len(latest(fleet,'b'))==1
    assert latest(fleet,'b')[0]==pytest.approx([3.,1.,math.pi/2])


def test_each_vehicle_follows_its_immediate_predecessor(fleet):
    fleet.owner.command({'op':'follow_start','order':['a','b','c'],'distance':1.},fleet.states)
    fleet.tick(5)
    fleet.states['a']['samples']['pose']['value'].update(x=10.,y=0.,yaw=0.)
    fleet.states['b']['samples']['pose']['value'].update(x=4.,y=3.,yaw=math.pi/2)
    fleet.states['c']['samples']['pose']['value'].update(x=4.,y=1.,yaw=0.)
    fleet.tick()
    bearing=math.atan2(-3.,6.)
    assert latest(fleet,'b')[0]==pytest.approx([10.-math.cos(bearing),-math.sin(bearing),bearing])
    assert latest(fleet,'c')[0]==pytest.approx([4.,2.,math.pi/2])


def test_current_target_is_transformed_into_followers_own_map(fleet):
    fleet.maps.alignment['a']=[2.,3.,math.pi/2]
    fleet.maps.alignment['b']=[-2.,1.,-.3]
    fleet.states['a']['samples']['pose']['value'].update(x=1.,y=0.,yaw=.2)
    fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':1.},fleet.states)
    fleet.tick(5)
    head=compose(fleet.maps.alignment['a'],[1.,0.,.2])
    tail=compose(fleet.maps.alignment['b'],[0.,4.,0.])
    bearing=math.atan2(head[1]-tail[1],head[0]-tail[0])
    target=[head[0]-math.cos(bearing),head[1]-math.sin(bearing),bearing]
    assert latest(fleet,'b')[0]==pytest.approx(compose(inverse(fleet.maps.alignment['b']),target))


def test_stationary_leader_still_starts_follow_without_recorded_travel(fleet):
    fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':1.},fleet.states)
    fleet.tick(5)
    assert latest(fleet,'b')[0]==pytest.approx([0.,1.,-math.pi/2])
    assert fleet.owner.jobs['b']['phase']=='EXECUTING'


def test_turning_in_place_does_not_swing_position_target_around_leader(fleet):
    fleet.states['a']['samples']['pose']['value'].update(x=2.,y=0.,yaw=0.)
    fleet.states['b']['samples']['pose']['value'].update(x=0.,y=0.,yaw=0.)
    fleet.states['a']['samples']['control']['value']['velocity']=[.2,.3]
    fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':1.},fleet.states)
    fleet.tick(5)
    previous=latest(fleet,'b')
    fleet.states['a']['samples']['pose']['value']['yaw']=math.pi/2
    fleet.tick()
    assert latest(fleet,'b')==previous
    assert abs([p[3]['predecessor_velocity'][0] for p in fleet.sent if p[0]=='follow_update'][-1])<1e-6
