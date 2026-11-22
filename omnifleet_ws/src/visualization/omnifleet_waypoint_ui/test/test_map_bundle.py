import asyncio
import copy
import json
import time
from types import SimpleNamespace

import pytest
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PointStamped
from geometry_msgs.msg import PoseWithCovarianceStamped
from mola_msgs.srv import MapLoad, MapSave
from omnifleet_waypoint_ui import map_bundle as bundle
from omnifleet_waypoint_ui.waypoint_ui_bridge import SemanticWaypoint, load_route, save_route


def state(tmp_path):
    pose=Pose();pose.position.x=1.25;pose.orientation.w=1.
    n=SimpleNamespace(frame_id='map',waypoints=[SemanticWaypoint('装货点',pose,'stop',3.)],pass_radius=.3,
        route_file=tmp_path/'live.json',navigation_active=False,edit_navigation_state={'navigation_active':False},
        edit_navigation_time=time.monotonic(),pending_name='',status=[],visuals=0)
    n.publish_status=n.status.append
    n.publish_visuals=lambda:setattr(n,'visuals',n.visuals+1)
    n.create_timer=lambda *_:object();n.destroy_timer=lambda _:None
    save_route(n.route_file,n.frame_id,n.waypoints,n.pass_radius)
    return n


class Client:
    def __init__(self,success=True):self.success=success;self.calls=[]
    def service_is_ready(self):return True
    def call_async(self,request):
        self.calls.append(request.map_path)
        f=asyncio.get_running_loop().create_future()
        f.set_result(SimpleNamespace(success=self.success,error_message='' if self.success else 'backend failure'))
        return f


def save(n,client,path):return asyncio.run(bundle.save_map(n,client,MapSave.Request(map_path=str(path)),MapSave.Response()))
def load(n,client,path):return asyncio.run(bundle.load_map(n,client,MapLoad.Request(map_path=str(path)),MapLoad.Response()))


def test_saved_snapshot_is_restored_including_route_options(tmp_path):
    n=state(tmp_path);c=Client();prefix=tmp_path/'site';original=copy.deepcopy(n.waypoints)
    assert save(n,c,str(prefix)+'.mm').success
    snapshot=tmp_path/'site.waypoints.json';saved=snapshot.read_bytes()
    n.waypoints[0].pose.position.x=99.;n.waypoints[0].kind='pass';n.waypoints[0].dwell_seconds=0.;n.pass_radius=.2
    save_route(n.route_file,n.frame_id,n.waypoints,n.pass_radius)
    assert snapshot.read_bytes()==saved
    assert load(n,c,str(prefix)+'.simplemap').success
    assert n.waypoints[0].pose.position.x==original[0].pose.position.x
    assert n.waypoints[0].name=='装货点' and n.waypoints[0].kind=='stop' and n.waypoints[0].dwell_seconds==3.
    assert n.pass_radius==.3 and n.visuals==1 and load_route(n.route_file)[0].pose.position.x==1.25
    assert c.calls==[str(prefix),str(prefix)]


def test_failed_map_save_preserves_last_snapshot(tmp_path):
    n=state(tmp_path);p=tmp_path/'site';assert save(n,Client(),p).success
    old=(tmp_path/'site.waypoints.json').read_bytes();n.waypoints=[]
    response=save(n,Client(False),p)
    assert not response.success and 'backend failure' in response.error_message
    assert (tmp_path/'site.waypoints.json').read_bytes()==old
    assert not list(tmp_path.glob('*.pending'))


@pytest.mark.parametrize('invalid',['corrupt','frame','active','stale'])
def test_bad_or_running_load_never_changes_map(tmp_path,invalid):
    n=state(tmp_path);p=tmp_path/'site';assert save(n,Client(),p).success
    sidecar=tmp_path/'site.waypoints.json'
    if invalid=='corrupt':sidecar.write_text('{broken')
    elif invalid=='frame':
        d=json.loads(sidecar.read_text());d['frame_id']='odom';sidecar.write_text(json.dumps(d))
    elif invalid=='active':n.edit_navigation_state['navigation_active']=True
    else:n.edit_navigation_time-=3
    c=Client();old=n.route_file.read_bytes();assert not load(n,c,p).success
    assert c.calls==[] and n.route_file.read_bytes()==old and n.visuals==0


def test_map_without_waypoints_clears_previous_map_points(tmp_path):
    n=state(tmp_path);assert load(n,Client(),tmp_path/'other').success
    assert n.waypoints==[] and load_route(n.route_file)==[] and n.visuals==1


def test_failed_backend_load_preserves_current_route(tmp_path):
    n=state(tmp_path);old=n.route_file.read_bytes()
    assert not load(n,Client(False),tmp_path/'missing').success
    assert n.route_file.read_bytes()==old and len(n.waypoints)==1 and n.visuals==0


def test_toolbar_point_uses_existing_add_pose_validation():
    received=[];n=SimpleNamespace(on_add_pose=received.append)
    point=PointStamped();point.header.frame_id='map';point.point.x=2.;point.point.y=3.
    bundle.add_point(n,point)
    assert len(received)==1 and received[0].header.frame_id=='map'
    assert received[0].pose.position.x==2. and received[0].pose.position.y==3.
    assert received[0].pose.orientation.w==1.


@pytest.mark.parametrize('active',[False,True])
def test_initial_pose_is_forwarded_only_while_navigation_is_idle(tmp_path,active):
    n=state(tmp_path);n.edit_navigation_state['navigation_active']=active
    pose=PoseWithCovarianceStamped();pose.header.frame_id='map';pose.pose.pose.orientation.w=1.
    class Relocator(Client):
        def call_async(self,request):
            self.calls.append(request.pose)
            f=asyncio.get_running_loop().create_future();f.set_result(SimpleNamespace(accepted=True));return f
    c=Relocator();asyncio.run(bundle.set_initial_pose(n,c,pose))
    assert len(c.calls)==(0 if active else 1)
