import copy
from types import SimpleNamespace as NS
import pytest
from test_missions import fleet
from test_operator_controls import controls
from geometry_msgs.msg import PoseStamped

def add(f,robot='a',pose=None):
    return f.owner.command({'op':'route_add','robot_id':robot,'id':'map','point':{'name':'new','pose':pose or [1.,0.,0.]}},f.states)
def start(f):return f.owner.command({'op':'route_start','robot_id':'a','id':'execute'},f.states)

def test_points_only_deploy_until_explicit_execute(fleet):
    f=fleet;assert add(f)['phase']=='saved';add(f,pose=[2.,0.,0.]);f.tick(10)
    assert not f.owner.jobs and not f.sent and len(f.owner.saved['routes']['a']['points'])==2
    start(f);f.tick(5)
    assert f.owner.jobs['a']['phase']=='EXECUTING' and [p[0] for p in f.sent]==['arm','navigate']
    f.finish('a');f.tick(5)
    assert [p[3]['poses'] for p in f.sent if p[0]=='navigate']==[[[1.,0.,0.],[2.,0.,0.]]]

def test_add_while_executing_edits_only_the_saved_draft(fleet):
    f=fleet;add(f);start(f);f.tick(5);job=f.owner.jobs['a'];old=copy.deepcopy(job);before=list(f.sent)
    add(f,pose=[2.,0.,.4])
    assert job==old and f.sent==before and len(f.owner.saved['routes']['a']['points'])==2
    f.finish('a');f.tick(6)
    assert job['phase']=='COMPLETED' and len([p for p in f.sent if p[0]=='navigate'])==1

def test_add_after_completion_waits_for_another_execute(fleet):
    f=fleet;add(f);start(f);f.tick(5);f.finish('a');f.tick(6);before=list(f.sent)
    add(f,pose=[3.,0.,0.]);f.tick(10)
    assert f.sent==before and f.owner.jobs['a']['phase']=='COMPLETED'
    start(f);assert f.owner.jobs['a']['index']==0 and len(f.owner.jobs['a']['points'])==2

def test_add_during_completion_does_not_restart_the_task(fleet):
    f=fleet;add(f);start(f);f.tick(5);f.finish('a');f.tick();add(f,pose=[2.,0.,0.]);f.tick(6)
    assert f.owner.jobs['a']['phase']=='COMPLETED'
    assert len([p for p in f.sent if p[0]=='navigate'])==1

def test_following_members_can_stage_without_executing(fleet):
    f=fleet;f.owner.follow.update(active=True,leader='a',order=['a','b']);add(f);add(f,'b')
    assert set(f.owner.saved['routes'])=={'a','b'} and not f.owner.jobs and not f.sent

def test_failed_queue_is_not_retried_by_editing(fleet):
    f=fleet;add(f);start(f);f.tick(5);f.finish('a',success=False);f.tick(6);before=list(f.sent)
    add(f,pose=[2.,0.,0.]);f.tick(10)
    assert f.sent==before and f.owner.jobs['a']['phase']=='FAILED'

def test_invalid_or_offline_points_do_not_change_the_draft(fleet):
    f=fleet;f.states['a']['online']=False
    with pytest.raises(ValueError):add(f)
    assert not f.owner.saved['routes'] and not f.sent
    f.states['a']['online']=True
    with pytest.raises(ValueError):add(f,pose=[float('nan'),0.,0.])
    assert not f.owner.saved['routes']

def test_map_deployment_does_not_require_motion_permission(controls):
    f=controls;m=PoseStamped();m.header.frame_id='fleet_map';m.pose.orientation.w=1.
    f.operator.stopped=True;f.owner.execution_permissions=lambda _:({},{},{'connection':False})
    f.operator.waypoint('connection',m)
    assert f.operator.receipt['phase']=='saved' and not f.sent and not f.owner.missions.jobs
    f.operator.waypoint('connection',m,single=True)
    assert f.operator.receipt['phase']=='rejected' and not f.owner.missions.jobs

def test_staging_never_starts_rmf_bidding_or_cooperative_takeover(fleet):
    f=fleet;f.owner.rmf_dispatch=NS(api=NS(get_subscription_count=lambda:1),submit=lambda *a:pytest.fail('staging bid'))
    f.states['a']['samples']['control']['value']['stopped_seconds']=0.
    add(f);assert not f.owner.pending_cooperative and not f.sent and not f.owner.jobs


def test_legacy_completion_flag_cannot_automatically_restart_a_queue(fleet):
    f=fleet;add(f);start(f);f.tick(5)
    f.owner.jobs['a']['restart_after_completion']=True
    f.finish('a');f.tick(8)
    assert f.owner.jobs['a']['phase']=='COMPLETED'
    assert len([p for p in f.sent if p[0]=='navigate'])==1
