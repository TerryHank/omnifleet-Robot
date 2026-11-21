from concurrent.futures import Future
from types import SimpleNamespace as NS
import json
import pytest
from builtin_interfaces.msg import Time
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from omnifleet_rmf_adapter.onboard_plans import OnboardPlans
from omnifleet_rmf_adapter.control_client import NavigationClient
from omnifleet_rmf_adapter.missions import Missions
from test_missions import fleet


def test_coordinator_never_falls_back_to_its_own_grid_planner(fleet):
 f=fleet;f.owner.onboard_planner=None
 with pytest.raises(ValueError,match='车端 Nav2'):f.owner.plan('a',[{'pose':[1.,0.,0.]}],f.states)


def test_provider_uses_vehicle_path_and_transform_and_rejects_changed_epoch(tmp_path):
 sent=[];maps=NS(alignment={'a':[2.,3.,0.]});state={'a':{'online':True,'samples':{'navigation':{'value':{'localization_epoch':'epoch'}},'fleet_client':{'value':{'history':{}}}}}}
 provider=OnboardPlans(tmp_path,maps,lambda *a,**k:sent.append((a,k)))
 future=provider.request('a',[{'pose':[1.,0.,0.]}],state);identifier=sent[-1][0][1]
 assert sent[-1][0][0]=='plan' and 'planner_id' not in sent[-1][1]
 folder=tmp_path/'run/plans/a';folder.mkdir(parents=True);path=folder/(identifier+'.json')
 path.write_text(json.dumps({'path':[[0.,0.,0.],[1.,0.,0.]],'epoch':'epoch','planner_id':'chosen_by_vehicle'}))
 state['a']['samples']['fleet_client']['value']['history'][identifier]={'phase':'planned'}
 provider.tick(state);assert future.result()['path']==[[2.,3.,0.],[3.,3.,0.]] and not path.exists()
 future=provider.request('a',[{'pose':[1.,0.,0.]}],state);state['a']['samples']['navigation']['value']['localization_epoch']='new'
 provider.tick(state)
 with pytest.raises(ValueError,match='会话变化'):future.result()
 assert sent[-1][0][0]=='cancel_plan'


def test_vehicle_planner_selection_and_compute_request_never_arms_or_moves(tmp_path,monkeypatch):
 monkeypatch.setenv('OMNIFLEET_DATA',str(tmp_path));sent=[];events=[]
 accepted=Future();completed=Future()
 node=NS(selected_algorithms={'planner':'GridSmac','controller':'FollowPathMPPI'},plan_handles={},robot_id='a',
  samples={'navigation':(0,{'localization_epoch':'current'})},get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())),
  path_action=NS(server_is_ready=lambda:True,send_goal_async=lambda goal:sent.append(goal) or accepted),event=lambda *a,**k:events.append((a,k)))
 identifier='plan-'+'1'*32
 NavigationClient.plan(node,{'id':identifier,'poses':[[1.,2.,.3],[2.,3.,.4]],'localization_epoch':'current'})
 assert len(sent)==1 and sent[0].planner_id=='GridSmac' and not sent[0].use_start and len(sent[0].goals)==2
 accepted.set_result(NS(accepted=True,get_result_async=lambda:completed))
 path=Path();p=PoseStamped();p.pose.orientation.w=1.;path.poses=[p]
 completed.set_result(NS(status=4,result=NS(path=path)))
 result=json.loads((tmp_path/'run/plans/a'/(identifier+'.json')).read_text())
 assert result['planner_id']=='GridSmac' and result['epoch']=='current' and events[-1][0][1]=='planned'


def test_whole_queue_reaches_shared_navigation_api_without_parameter_overrides():
 accepted=Future();goals=[]
 node=NS(motion_enabled=True,generation=0,inflight=None,goal_handle=None,epoch='lease',task_id='queue',revision=1,samples={'waypoints':(0,{'pass_radius':.17})},
    action=NS(send_goal_async=lambda goal,**kwargs:goals.append(goal) or accepted),get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())),event=lambda *a,**k:None)
 NavigationClient.send_goal(node,{'id':'queue','poses':[[1.,0.,0.],[2.,0.,.5]],'single_point':False})
 assert len(goals[0].waypoints)==2 and not goals[0].single_point and goals[0].source==1
 assert [p.kind for p in goals[0].waypoints]==[0,1]
 assert goals[0].pass_radius==pytest.approx(.17)
 assert not hasattr(goals[0],'controller_id') and not hasattr(goals[0],'planner_id')


def test_vehicle_feedback_controls_progress_of_whole_queue(fleet):
 f=fleet;f.owner.command({'op':'route_save','robot_id':'a','points':[[1.,0.,0.],[2.,0.,0.]],'id':'save'},f.states)
 f.owner.command({'op':'route_start','robot_id':'a','id':'start'},f.states);f.tick(5)
 job=f.owner.jobs['a'];request=job['request']
 f.states['a']['samples']['fleet_client']['value']['history'][request]={'phase':'executing','passed_points':1}
 f.tick();assert job['index']==1 and len([s for s in f.sent if s[0]=='navigate'])==1
 f.finish('a');f.tick(3);assert job['index']==2 and job['phase']=='COMPLETED'
