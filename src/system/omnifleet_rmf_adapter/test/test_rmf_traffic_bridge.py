from types import SimpleNamespace as NS
from unittest.mock import Mock

import rmf_adapter as rmf
from test_missions import fleet
from omnifleet_rmf_adapter.rmf_traffic import RmfTraffic


def attach(fleet):
    owner=NS(missions=fleet.owner,maps=fleet.maps,snapshots=lambda:fleet.states)
    traffic=RmfTraffic(owner,Mock());traffic.available=True
    fleet.owner.rmf_traffic=traffic
    return traffic


def test_formation_traffic_wait_retains_offsets_and_resumes(fleet):
    fleet.owner.command({'op':'formation_capture','order':['a','b']},fleet.states)
    fleet.owner.command({'op':'formation_start','order':['a','b']},fleet.states)
    fleet.tick(6)
    traffic=attach(fleet);saved=fleet.owner.formation.saved.copy()
    traffic.pause('b')
    assert fleet.owner.formation.active and fleet.owner.jobs['b']['phase']=='EXECUTING'
    assert fleet.owner.jobs['b']['traffic_paused']
    fleet.owner.formation.tick(fleet.states)
    assert fleet.owner.formation.saved==saved
    handle=Mock();handle.waiting_after.return_value=rmf.easy_traffic_light.WaitingInstruction.Wait
    traffic.members['b']={'handle':handle};traffic.routes['b']={'index':0}
    fleet.states['b']['samples']['navigation']['value']['traffic_paused']=True
    fleet.states['b']['samples']['navigation']['value']['task_id']=fleet.owner.jobs['b']['request']
    assert not traffic.resumed('b',fleet.states)
    handle.waiting_after.return_value=rmf.easy_traffic_light.WaitingInstruction.Resume
    assert traffic.resumed('b',fleet.states) and traffic.group_wait is None
    fleet.tick(8)
    assert fleet.owner.jobs['b']['phase']=='EXECUTING' and fleet.owner.formation.active


def test_stopping_formation_cancels_all_queued_member_goals(fleet):
    fleet.owner.command({'op':'formation_capture','order':['a','b']},fleet.states)
    dispatch=Mock();fleet.owner.rmf_dispatch=dispatch
    fleet.owner.formation.stop()
    assert {call.kwargs['robot'] for call in dispatch.cancel_pending.call_args_list}=={'a','b'}


def test_humble_async_optional_is_retried_but_other_failures_propagate():
    import pytest
    assert RmfTraffic.instruction(Mock(side_effect=RuntimeError('bad optional access'))) is None
    with pytest.raises(RuntimeError,match='actual failure'):
        RmfTraffic.instruction(Mock(side_effect=RuntimeError('actual failure')))
