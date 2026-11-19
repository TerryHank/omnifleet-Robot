import math
import pytest
from test_missions import fleet

def start(fleet):
    fleet.states['a']['samples']['pose']['value'].update(x=2.,y=0.,yaw=0.,stamp_seconds=10.)
    fleet.states['b']['samples']['pose']['value'].update(x=0.,y=0.,yaw=0.)
    fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':1.},fleet.states);fleet.tick(5)

def last(fleet):
    return [p[3]['predecessor_velocity'] for p in fleet.sent if p[0]=='follow_update'][-1]

def test_spinning_wheels_at_stationary_pose_do_not_make_follower_chase(fleet):
    start(fleet);fleet.states['a']['samples']['control']['value']['velocity']=[.5,0.]
    for i in range(5):
        fleet.states['a']['samples']['pose']['value']['stamp_seconds']+=.1;fleet.tick()
    assert last(fleet)==pytest.approx([0.,0.])

def test_ground_speed_comes_from_position_even_when_encoders_report_zero(fleet):
    start(fleet)
    for i in range(1,6):
        fleet.states['a']['samples']['pose']['value'].update(x=2.+.03*i,stamp_seconds=10.+.1*i);fleet.tick()
    assert last(fleet)==pytest.approx([.3,0.])

def test_heading_wrap_does_not_create_angular_velocity_spike(fleet):
    start(fleet)
    history=fleet.owner.follow_pose_history;history.clear()
    state=fleet.states['a'];state['samples']['pose']['value']['stamp_seconds']=20.
    fleet.owner.observed_velocity('a',state,[0.,0.,math.pi-.01])
    state['samples']['pose']['value']['stamp_seconds']=20.1
    v=fleet.owner.observed_velocity('a',state,[0.,0.,-math.pi+.01])
    assert v[2]==pytest.approx(.2)
