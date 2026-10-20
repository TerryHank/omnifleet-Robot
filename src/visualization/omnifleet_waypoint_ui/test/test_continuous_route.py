import copy,json,math,time
from types import SimpleNamespace as S
from unittest.mock import patch
import pytest
from rclpy.clock import Clock
from geometry_msgs.msg import Pose
from nav_msgs.msg import Odometry,OccupancyGrid,Path
from omnifleet_waypoint_ui.waypoint_ui_bridge import SemanticWaypoint,load_route,save_route,load_pass_radius,validate_waypoint_options
from omnifleet_waypoint_ui import continuous_route as c

class Future:
 def __init__(self,value=None,ready=False):self.value=value;self.ready=ready;self.callbacks=[]
 def result(self):return self.value
 def add_done_callback(self,fn):
  if self.ready:fn(self)
  else:self.callbacks.append(fn)
 def complete(self,value):
  self.value=value;self.ready=True
  for fn in self.callbacks:fn(self)
class Handle:
 def __init__(self):self.accepted=True;self.future=Future();self.cancels=0
 def get_result_async(self):return self.future
 def cancel_goal_async(self):self.cancels+=1;return Future(S(return_code=0),True)
class Client:
 def __init__(self,*_):self.sent=[]
 def server_is_ready(self):return True
 def send_goal_async(self,goal,feedback_callback=None):
  f=Future();self.sent.append((goal,f));return f
 def accept(self,index=-1):
  h=Handle();self.sent[index][1].complete(h);return h
class Publisher:
 def __init__(self):self.messages=[]
 def publish(self,m):self.messages.append(m)
class Node:
 def __init__(self):
  self.frame_id='map';self.navigation_active=False;self.pass_radius=.25;self.preview_planner_id='GridBased';self.preview_revision=0;self.preview_goal_handle=None;self.path_pub=Publisher();self.status=[]
 def create_publisher(self,*_):return Publisher()
 def create_subscription(self,*_):pass
 def create_timer(self,*_):pass
 def create_client(self,*_):return S(call_async=lambda _:Future(S(values=[S(type=1,bool_value=False)]),True))
 def get_clock(self):return Clock()
 def publish_status(self,text):self.status.append(text)
 def publish_catalog(self):pass

def point(x,kind='pass',wait=0):
 p=Pose();p.position.x=float(x);p.orientation.w=1.;return SemanticWaypoint(str(x),p,kind,wait)
def grid():
 g=OccupancyGrid();g.info.resolution=.1;g.info.width=g.info.height=200;g.info.origin.position.x=g.info.origin.position.y=-10.;g.info.origin.orientation.w=1.;g.data=[0]*40000;return g
@pytest.fixture
def engine(tmp_path):
 clock=[100.]
 with patch.object(c,'ActionClient',Client),patch.object(c.time,'monotonic',lambda:clock[0]),patch.object(c.time,'time',lambda:clock[0]),patch.object(c.Path,'home',return_value=tmp_path):
  n=Node();e=c.ContinuousRoute(n);e.pose=(clock[0],Odometry());e.pose[1].pose.pose.orientation.w=1.;e.odom=(clock[0],Odometry());e.grid=(clock[0],grid())
  e.health.observe(clock[0]-.1,clock[0]);e.health.stable_since=clock[0]-3
  def tick(dt=0):
   clock[0]+=dt;e.health.observe(clock[0]-.1,clock[0]);e.pose=(clock[0],e.pose[1]);e.odom=(clock[0],e.odom[1]);e.grid=(clock[0],e.grid[1]);e.tick()
  yield e,n,tick
def complete_plan(e):
 goal=e.planner.sent[-1][0];h=e.planner.accept();p=Path();p.poses=goal.goals;h.future.complete(S(status=4,result=S(path=p)))

def test_legacy_and_new_schema(tmp_path):
 p=tmp_path/'r.json';save_route(p,'map',[point(1),point(2,'stop',2)],.3)
 assert load_route(p)[0].kind=='pass';assert load_pass_radius(p)==.3
 data=json.loads(p.read_text())
 for item in data['waypoints']:item.pop('kind');item.pop('dwell_seconds')
 p.write_text(json.dumps(data));assert all(w.kind=='stop' for w in load_route(p))
 save_route(p,'map',load_route(p));assert list(tmp_path.glob('*.backup-*'))
def test_invalid_options():
 for kind,dwell in [('bad',0),('stop',float('nan')),('stop',601),('stop',True)]:
  with pytest.raises(ValueError):validate_waypoint_options(kind,dwell)
def test_reverse_heading_and_stop_preserved():
 points=[point(-1),point(-2),point(-3,'stop')];points[-1].pose.orientation.z=1.;points[-1].pose.orientation.w=0.
 result=c.oriented_route(points,0.)
 assert abs(c.yaw(result[0].pose))<1e-6
 assert abs(c.yaw(result[-1].pose)-math.pi)<1e-6
 assert c.split_blocks([point(1),point(2,'stop'),point(3)])==[(0,2),(2,3)]
def test_three_pass_points_one_navigation_action(engine):
 e,n,tick=engine;e.start([point(1),point(2),point(3)]);assert len(e.planner.sent)==1;assert not e.navigator.sent
 complete_plan(e);assert len(e.navigator.sent)==1;assert len(e.navigator.sent[0][0].poses)==3
 e.on_execution_state(S(data=json.dumps({'run_id':e.run_id+'-0','state':'tracking','remaining':2})))
 assert e.states[0]=='已通过';assert len(e.navigator.sent)==1;assert len(e.planner.sent)==1
def test_all_blocks_preflight_before_motion(engine):
 e,n,tick=engine;e.start([point(1),point(2,'stop',2),point(3)])
 complete_plan(e);assert len(e.planner.sent)==2;assert not e.navigator.sent
 assert e.planner.sent[1][0].start.pose.position.x==2
 complete_plan(e);assert len(e.navigator.sent)==1
 h=e.navigator.accept();h.future.complete(S(status=4,result=S()))
 tick();tick(.31);assert e.phase=='waiting';tick(1.9);assert len(e.navigator.sent)==1
 tick(.11);assert len(e.navigator.sent)==2
def test_stop_before_accept_cancels_late_goal(engine):
 e,n,tick=engine;e.start([point(1),point(2)]);e.stop('stop');tick();assert n.navigation_active
 h=e.planner.accept();assert h.cancels==1
 h.future.complete(S(status=5,result=S()));tick();assert not n.navigation_active;assert not e.navigator.sent
def test_timeout_and_late_success_never_starts_motion(engine):
 e,n,tick=engine;e.start([point(1)]);tick(11);assert e.phase=='canceling';tick(6);assert e.phase=='cancel_unconfirmed'
 h=e.planner.accept();p=Path();p.poses=e.planner.sent[0][0].goals;h.future.complete(S(status=4,result=S(path=p)));tick()
 assert not e.navigator.sent;assert not n.navigation_active
def test_preflight_failure_does_not_send_navigation(engine):
 e,n,tick=engine;e.start([point(1),point(2,'stop'),point(3)]);complete_plan(e)
 h=e.planner.accept();h.future.complete(S(status=6,result=S()));tick();assert not e.navigator.sent;assert e.phase=='failed'
def test_cleanup_preserves_original_failure(engine):
 e,n,tick=engine;e.start([point(1)]);h=e.planner.accept();h.future.complete(S(status=6,result=S()))
 original=e.cancel_reason;e.stop('cleanup stop');tick()
 assert e.phase=='failed';assert e.cancel_reason==original
def test_duplicate_start_and_dwell_cancel(engine):
 e,n,tick=engine;e.start([point(1,'stop',10),point(2)]);e.start([point(5)]);assert len(e.planner.sent)==1
 complete_plan(e);complete_plan(e);h=e.navigator.accept();h.future.complete(S(status=4,result=S()));tick();tick(.31)
 e.stop('stop');tick(20);assert len(e.navigator.sent)==1;assert not n.navigation_active
def test_preview_only_has_no_navigation(engine):
 e,n,tick=engine;e.start([point(1),point(2)],preflight_only=True);complete_plan(e)
 assert e.phase=='preview_ready';assert not e.navigator.sent;assert not n.navigation_active
def test_path_interpolation_detects_obstacle(engine):
 e,n,tick=engine;p=Path();p.poses=[e.stamped(point(0).pose),e.stamped(point(1).pose)]
 g=grid();assert c.path_valid(g,p)
 g.data[100*200+105]=100;assert not c.path_valid(g,p)
 g.data[100*200+105]=-1;assert not c.path_valid(g,p);assert c.path_valid(g,p,True)
