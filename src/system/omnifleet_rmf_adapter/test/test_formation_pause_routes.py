from types import SimpleNamespace as NS
from unittest.mock import Mock
from test_missions import fleet,save
from test_rmf_traffic_bridge import attach
from omnifleet_rmf_adapter.operator_controls import OperatorControls


def test_rmf_canceling_status_is_a_pause_not_a_new_admission_failure(fleet):
    f=fleet.owner.formation;f.capture(['a','b'],fleet.states);f.start(['a','b'],fleet.states);fleet.tick(7)
    traffic=attach(fleet);traffic.pause('b')
    fleet.states['b']['samples']['navigation']['value']['local_ready']=False
    f.tick(fleet.states)
    assert f.active and traffic.group_wait
    assert 'Open-RMF' in f.message
    fleet.states['b']['samples']['navigation']['value']['localization_epoch']='changed'
    f.tick(fleet.states)
    assert not f.active


def test_shared_execute_button_submits_only_the_formation_leader(fleet):
    save(fleet,'a',[[1.,0.,0.]]);save(fleet,'b',[[1.,4.,0.]])
    f=fleet.owner.formation;f.capture(['a','b'],fleet.states);f.start(['a','b'],fleet.states);fleet.tick(7)
    command=Mock(wraps=fleet.owner.command);fleet.owner.command=command
    operator=NS(stopped=False,owner=NS(missions=fleet.owner,execution_permissions=lambda s:({},{},{'a':True,'b':True})))
    result=OperatorControls.start_routes(operator,{'id':'ui-execute'},fleet.states)
    assert result['phase']=='accepted'
    assert command.call_args.args[0]['robot_id']=='a'
    assert fleet.owner.jobs['b']['source']=='formation'
    assert fleet.owner.saved['routes']['b']['points'][0]['pose']==[1.,4.,0.]
