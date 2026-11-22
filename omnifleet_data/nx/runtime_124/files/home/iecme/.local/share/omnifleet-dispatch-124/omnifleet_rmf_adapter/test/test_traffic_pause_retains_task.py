import time
from types import SimpleNamespace as NS
from unittest.mock import Mock
import rmf_adapter as rmf
from test_missions import fleet
from test_rmf_traffic_bridge import attach


def executing(fleet):
    fleet.owner.command({'op':'single_goal','id':'one-click','robot_id':'a','point':{'pose':[2.,0.,0.]}},fleet.states)
    fleet.tick(6)
    fleet.states['a']['samples']['navigation']['value']['task_id']=fleet.owner.jobs['a']['request']
    traffic=attach(fleet);traffic.enroll=Mock();traffic.last_idle=time.monotonic()
    traffic.owner.get_node_names_and_namespaces=lambda:[('rmf_traffic_blockade_node','/')]
    handle=Mock();handle.waiting_after.return_value=rmf.easy_traffic_light.WaitingInstruction.Wait
    handle.moving_from.return_value=rmf.easy_traffic_light.MovingInstruction.PauseImmediately
    traffic.members={'a':{'handle':handle,'state':'MOVING','blockers':[]}}
    traffic.routes={'a':{'job':fleet.owner.jobs['a']['id'],'path':[[0.,0.,0.],[1.,0.,0.],[2.,0.,0.]],'index':0,'transform':[0.,0.,0.]}}
    return traffic,handle


def test_repeated_pause_resume_retains_one_navigation_action(fleet):
    traffic,handle=executing(fleet);job=fleet.owner.jobs['a'];identifier=job['id'];request=job['request']
    for _ in range(3):
        traffic.tick(fleet.states)
        assert job['traffic_paused'] and job['phase']=='EXECUTING'
        fleet.states['a']['samples']['navigation']['value']['traffic_paused']=True
        traffic.tick(fleet.states);assert job['traffic_paused']
        handle.waiting_after.return_value=rmf.easy_traffic_light.WaitingInstruction.Resume
        traffic.tick(fleet.states)
        assert not job['traffic_paused']
        fleet.states['a']['samples']['navigation']['value']['traffic_paused']=False
        handle.waiting_after.return_value=rmf.easy_traffic_light.WaitingInstruction.Wait
    fleet.tick(20)
    assert fleet.owner.jobs['a']['id']==identifier and job['request']==request
    assert len([p for p in fleet.sent if p[0]=='navigate'])==1
    assert not any(p[0]=='disarm' for p in fleet.sent)
    assert [p[3]['paused'] for p in fleet.sent if p[0]=='traffic_pause']==[True,False]*3


def test_existing_wait_obligation_is_not_skipped_by_lookahead(fleet):
    traffic,handle=executing(fleet)
    handle.moving_from.return_value=rmf.easy_traffic_light.MovingInstruction.WaitAtNextCheckpoint
    fleet.states['a']['samples']['pose']['value']['x']=.5
    traffic.tick(fleet.states)
    assert not fleet.owner.jobs['a'].get('traffic_paused')
    fleet.states['a']['samples']['pose']['value']['x']=.98
    traffic.tick(fleet.states)
    assert handle.moving_from.call_args.args[0]==0
    assert fleet.owner.jobs['a']['traffic_paused']


def test_resume_waits_for_onboard_ack_and_actual_stop(fleet):
    traffic,handle=executing(fleet);traffic.pause('a')
    handle.waiting_after.return_value=rmf.easy_traffic_light.WaitingInstruction.Resume
    assert not traffic.resumed('a',fleet.states)
    fleet.states['a']['samples']['navigation']['value']['traffic_paused']=True
    fleet.states['a']['samples']['control']['value']['velocity']=[.1,0.]
    assert not traffic.resumed('a',fleet.states)
    fleet.states['a']['samples']['control']['value']['velocity']=[0.,0.]
    assert traffic.resumed('a',fleet.states)

def test_lost_pause_packet_is_retried_until_current_task_ack(fleet):
    traffic,_=executing(fleet);traffic.pause('a')
    traffic.tick(fleet.states)
    assert len([p for p in fleet.sent if p[0]=='traffic_pause'])==2
    fleet.states['a']['samples']['navigation']['value']['traffic_paused']=True
    traffic.tick(fleet.states)
    assert len([p for p in fleet.sent if p[0]=='traffic_pause'])==2


def test_reference_map_change_does_not_cancel_accepted_local_map_goal(fleet):
    traffic,_=executing(fleet);job=fleet.owner.jobs['a'];request=job['request']
    fleet.maps.alignment.pop('a');fleet.maps.valid_robots.discard('a')
    assert traffic.pose('a',fleet.states)==[0.,0.,0.]
    fleet.tick(5)
    assert job['phase']=='EXECUTING' and job['request']==request
    assert not any(p[0]=='disarm' for p in fleet.sent)
    fleet.states['a']['samples']['navigation']['value']['localization_epoch']='own-map-restarted'
    fleet.tick(2)
    assert job['phase']=='INVALIDATED' and any(p[0]=='disarm' for p in fleet.sent)
