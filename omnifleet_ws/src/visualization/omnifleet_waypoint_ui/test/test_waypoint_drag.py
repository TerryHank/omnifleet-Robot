import copy,json,time
from pathlib import Path
from types import SimpleNamespace
import pytest
from geometry_msgs.msg import Pose
from std_msgs.msg import String
from omnifleet_waypoint_ui import waypoint_ui_bridge as module

def fake(tmp_path):
 p=Pose();p.position.x=1.;p.position.y=2.;p.position.z=.1;p.orientation.z=.5;p.orientation.w=3**.5/2
 w=module.SemanticWaypoint(name='航点1',pose=p,kind='pass',dwell_seconds=0.)
 node=SimpleNamespace(navigation_active=False,edit_navigation_state={'navigation_active':False},edit_navigation_time=time.monotonic(),frame_id='map',route_file=tmp_path/'route.json',waypoints=[w],pass_radius=.25,status=[],visuals=0)
 node.publish_status=node.status.append
 def visuals():node.visuals+=1
 node.publish_visuals=visuals;module.save_route(node.route_file,'map',node.waypoints,.25);return node
def request(**kw):
 d={'index':1,'name':'航点1','frame_id':'map','position':{'x':3.,'y':4.},'previous_position':{'x':1.,'y':2.}};d.update(kw);return String(data=json.dumps(d))
def test_position_persists_and_preserves_other_properties(tmp_path):
 n=fake(tmp_path);before=copy.deepcopy(n.waypoints[0]);module.WaypointUiBridge.on_update_options(n,request())
 assert n.visuals==1 and n.status[-1]=='航点位置已保存'
 loaded=module.load_route(n.route_file)[0]
 assert (loaded.pose.position.x,loaded.pose.position.y)==(3.,4.)
 assert loaded.name==before.name and loaded.kind==before.kind and loaded.dwell_seconds==before.dwell_seconds
 assert loaded.pose.position.z==before.pose.position.z and n.waypoints[0].pose.orientation==before.pose.orientation
 assert loaded.pose.orientation.z==pytest.approx(before.pose.orientation.z) and loaded.pose.orientation.w==pytest.approx(before.pose.orientation.w)
@pytest.mark.parametrize('change',[{'position':{'x':True,'y':2}},{'position':{'x':float('nan'),'y':2}},{'position':{'x':1,'y':float('inf')}},{'index':0},{'frame_id':'odom'},{'previous_position':{'x':0,'y':2}},{'name':'other'}])
def test_invalid_drag_does_not_change_route(tmp_path,change):
 n=fake(tmp_path);old=n.route_file.read_bytes();module.WaypointUiBridge.on_update_options(n,request(**change));assert n.route_file.read_bytes()==old and n.visuals==0 and n.waypoints[0].pose.position.x==1.
@pytest.mark.parametrize('mode',['route','single','stale'])
def test_running_or_stale_state_rejects_drag(tmp_path,mode):
 n=fake(tmp_path)
 if mode=='route':n.navigation_active=True
 elif mode=='single':n.edit_navigation_state['navigation_active']=True
 else:n.edit_navigation_time-=3
 old=n.route_file.read_bytes();module.WaypointUiBridge.on_update_options(n,request());assert n.route_file.read_bytes()==old and n.visuals==0
def test_failed_save_preserves_memory_and_file(tmp_path,monkeypatch):
 n=fake(tmp_path);old=n.route_file.read_bytes()
 def fail(*a,**k):raise OSError('readonly')
 monkeypatch.setattr(module,'save_route',fail);module.WaypointUiBridge.on_update_options(n,request());assert n.route_file.read_bytes()==old and n.waypoints[0].pose.position.x==1. and n.visuals==0
