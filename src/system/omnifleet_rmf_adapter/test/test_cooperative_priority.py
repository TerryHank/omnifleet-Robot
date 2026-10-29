import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
from test_missions import fleet

def follower(fleet):
    state=fleet.states['b'];state['samples']['control']['value'].update(manual_active=True,manual_command_age=0.,local_override=True)
    state['samples']['navigation']['value']['navigation_active']=True
    state['samples']['control']['value'].update(nav_active=True,stopped_seconds=0.)
    state['samples']['fleet_client']['value']['busy']=True
    original=fleet.owner.send
    def send(op,request,robot_id,**fields):
        original(op,request,robot_id,**fields)
        if op=='arm':fleet.states[robot_id]['samples']['control']['value']['local_override']=False
    fleet.owner.send=send
    return state

def acknowledge(fleet,state):
    pending=fleet.owner.pending_cooperative;identifier=pending['requests']['b']
    state['samples']['navigation']['value']['navigation_active']=False
    state['samples']['control']['value'].update(manual_active=False,manual_command_age=99.,nav_active=False,stopped_seconds=1.)
    state['samples']['fleet_client']['value'].update(busy=False,armed=False)
    state['samples']['fleet_client']['value']['history'][identifier]={'phase':'stopped','confirmed':True}

def test_follow_preempts_local_and_manual_then_starts_automatically(fleet):
    state=follower(fleet)
    result=fleet.owner.command({'op':'follow_start','id':'start','order':['a','b'],'distance':1.},fleet.states)
    assert result['phase']=='accepted' and fleet.owner.pending_cooperative
    assert not fleet.owner.follow['active']
    assert any(p[0]=='operator_stop' and p[2]=='b' for p in fleet.sent)
    fleet.tick(2);assert not fleet.owner.follow['active']
    acknowledge(fleet,state);fleet.tick(10)
    assert fleet.owner.follow['active'] and fleet.owner.jobs['b']['phase']=='EXECUTING'

def test_historical_manual_mode_is_not_active_manual_control(fleet):
    fleet.states['b']['samples']['control']['value'].update(manual_active=True,manual_command_age=168.)
    result=fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':1.},fleet.states)
    assert result['phase']=='accepted' and fleet.owner.follow['active']

def test_user_stop_cancels_pending_cooperative_start(fleet):
    state=follower(fleet)
    fleet.owner.command({'op':'follow_start','order':['a','b']},fleet.states)
    fleet.owner.command({'op':'follow_stop'},fleet.states)
    assert fleet.owner.pending_cooperative is None
    fleet.tick(5);assert not fleet.owner.follow['active']

def test_single_goal_also_preempts_local_task(fleet):
    state=follower(fleet)
    result=fleet.owner.command({'op':'single_goal','id':'goal','robot_id':'b','point':{'pose':[1.,4.,0.]}},fleet.states)
    assert result['phase']=='accepted' and fleet.owner.pending_cooperative
    acknowledge(fleet,state);fleet.tick(6)
    assert fleet.owner.jobs['b']['phase']=='EXECUTING'

def test_formation_preempts_before_starting_saved_shape(fleet):
    fleet.owner.command({'op':'formation_capture','order':['a','b']},fleet.states)
    state=follower(fleet)
    result=fleet.owner.command({'op':'formation_start','id':'formation','order':['a','b']},fleet.states)
    assert result['phase']=='accepted' and fleet.owner.pending_cooperative
    pending=fleet.owner.pending_cooperative
    for r,identifier in pending['requests'].items():
        fleet.states[r]['samples']['fleet_client']['value']['history'][identifier]={'phase':'stopped','confirmed':True}
    acknowledge(fleet,state);fleet.tick(10)
    assert fleet.owner.formation.active

def test_direction_pad_does_not_cancel_active_cooperative_navigation(fleet):
    from geometry_msgs.msg import Twist
    from omnifleet_rmf_adapter.operator_controls import OperatorControls
    fleet.owner.command({'op':'single_goal','robot_id':'a','point':{'pose':[2.,0.,0.]}},fleet.states)
    fleet.tick(6);sender=Mock()
    operator=NS(stopped=False,owner=NS(missions=fleet.owner,snapshots=lambda:fleet.states,
        execution_permissions=lambda _:({},{},{'a':True}),send_command=sender))
    message=Twist();message.linear.x=.15
    OperatorControls.manual(operator,'a',message)
    assert fleet.owner.jobs['a']['phase']=='EXECUTING' and not sender.called
