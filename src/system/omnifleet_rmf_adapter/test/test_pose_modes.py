import copy
import pytest
from geometry_msgs.msg import PoseStamped
from test_missions import fleet,save
from test_operator_controls import controls


def single(f,pose=None):
 return f.owner.command({'op':'single_goal','robot_id':'a','point':{'pose':pose or [1.,0.,0.]},'id':'single'},f.states)


def test_single_goal_is_immediate_and_does_not_enter_saved_multigoal_route(fleet):
 f=fleet;save(f,'a',[[2.,0.,0.],[3.,0.,0.]])
 before=copy.deepcopy(f.owner.saved);single(f);f.tick(5)
 assert f.owner.jobs['a']['source']=='single' and f.owner.jobs['a']['phase']=='EXECUTING'
 assert f.owner.saved==before and len(f.owner.jobs['a']['points'])==1
 assert [s[3]['pose'] for s in f.sent if s[0]=='navigate']==[[1.,0.,0.]]


def test_new_single_goal_cancels_old_goal_then_executes_only_latest(fleet):
 f=fleet;single(f);f.tick(5);single(f,[2.,0.,0.]);single(f,[3.,0.,0.])
 assert f.owner.jobs['a']['phase']=='STOPPING';f.tick(6)
 assert f.owner.jobs['a']['source']=='single' and f.owner.jobs['a']['phase']=='EXECUTING'
 assert [s[3]['pose'] for s in f.sent if s[0]=='navigate']==[[1.,0.,0.],[3.,0.,0.]]


def test_single_replaces_multigoal_execution_but_preserves_saved_queue(fleet):
 f=fleet;save(f,'a',[[1.,0.,0.],[2.,0.,0.]])
 f.owner.command({'op':'route_start','robot_id':'a','id':'multi'},f.states);f.tick(5)
 before=copy.deepcopy(f.owner.saved);single(f,[3.,0.,0.]);f.tick(6)
 assert f.owner.saved==before and f.owner.jobs['a']['source']=='single'
 assert [s[3]['pose'] for s in f.sent if s[0]=='navigate']==[[1.,0.,0.],[3.,0.,0.]]


def test_multi_add_stages_without_interrupting_single(fleet):
 f=fleet;single(f);f.tick(5)
 f.owner.command({'op':'route_add','robot_id':'a','point':{'pose':[2.,0.,0.]},'id':'multi'},f.states);f.tick(6)
 assert f.owner.jobs['a']['source']=='single' and f.owner.saved['routes']['a']['points']==[{'name':'航点1','pose':[2.,0.,0.]}]
 assert [s[3]['pose'] for s in f.sent if s[0]=='navigate']==[[1.,0.,0.]]


@pytest.mark.parametrize('op',['route_stop','route_clear','routes_clear'])
def test_stop_or_clear_prevents_pending_single_goal_from_restarting(fleet,op):
 f=fleet;single(f);f.tick(5);single(f,[2.,0.,0.]);f.owner.command({'op':op,'robot_id':'a'},f.states);f.tick(8)
 assert f.owner.jobs['a']['phase']=='STOPPED' and len([s for s in f.sent if s[0]=='navigate'])==1


def test_epoch_change_during_replacement_does_not_send_new_goal(fleet):
 f=fleet;single(f);f.tick(5);single(f,[2.,0.,0.]);f.states['a']['samples']['navigation']['value']['localization_epoch']='new';f.tick(8)
 assert f.owner.jobs['a']['phase'] in ('INVALIDATED','STOPPED') and len([s for s in f.sent if s[0]=='navigate'])==1


def test_goal_and_multi_subscriptions_use_different_endpoints(controls):
 f=controls
 callbacks=dict(f.subscriptions)
 m=PoseStamped();m.header.frame_id='fleet_map';m.pose.orientation.w=1.
 callbacks['/car_new/ui/r9/goal'](m)
 assert f.owner.missions.jobs['connection']['source']=='single' and not f.owner.missions.saved['routes']
 f.operator.publish_waypoints()
 assert f.published[-1].markers[-1].text=='car_new / 单点目标'
 f.owner.missions.command({'op':'route_clear','robot_id':'connection'},f.states)
 f.operator.publish_waypoints();assert len(f.published[-1].markers)==1
 f.owner.missions.jobs.clear();callbacks['/car_new/ui/r9/waypoint'](m)
 assert not f.owner.missions.jobs and len(f.owner.missions.saved['routes']['connection']['points'])==1
