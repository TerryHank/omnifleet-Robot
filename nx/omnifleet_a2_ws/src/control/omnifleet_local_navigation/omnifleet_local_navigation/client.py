"""Foxglove/route-storage adapter; execution stays in the onboard module."""
import copy,json,time,uuid
from types import SimpleNamespace
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile,ReliabilityPolicy,DurabilityPolicy,qos_profile_sensor_data
from std_msgs.msg import String
from std_srvs.srv import Trigger
from nav_msgs.msg import Odometry,OccupancyGrid
from omnifleet_navigation_interfaces.action import ExecuteNavigation
from omnifleet_navigation_interfaces.msg import NavigationPoint

class NavigationClient:
    def __init__(self,node):
        self.n=node;namespace=node.frame_id.strip('/').rpartition('/')[0]
        self.prefix=('/'+namespace) if namespace else ''
        self.navigator=ActionClient(node,ExecuteNavigation,self.prefix+'/navigation/execute')
        self.stop_client=node.create_client(Trigger,self.prefix+'/navigation/stop')
        self.active=False;self.phase='idle';self.states=[];self.run_id='';self.handle=None
        self.pose=self.grid=None;self.controller='FollowPath';self.module={};self.module_at=0.
        self.health=SimpleNamespace(reason='等待本地导航模块',age_ms=None)
        self.cancel_after_accept=False
        q=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        node.create_subscription(String,self.prefix+'/navigation/status',self.on_status,q)
        node.create_subscription(Odometry,self.prefix+'/lidar_odometry/pose',lambda m:setattr(self,'pose',(time.monotonic(),m)),qos_profile_sensor_data)
        node.create_subscription(OccupancyGrid,self.prefix+'/global_costmap/costmap',lambda m:setattr(self,'grid',(time.monotonic(),m)),q)
        node.create_subscription(String,self.prefix+'/controller_selector',lambda m:setattr(self,'controller',m.data),q)

    def on_status(self,message):
        try:data=json.loads(message.data)
        except ValueError:return
        self.module=data;self.module_at=time.monotonic()
        self.health.reason=data.get('readiness_reason') or data.get('localization_status','等待本地定位')
        self.health.age_ms=data.get('tf_age_ms')
        if self.active and data.get('task_id')==self.run_id:
            self.phase=data.get('phase',self.phase);self.states=data.get('waypoint_states',self.states)
        self.n.publish_catalog()

    def inputs_ready(self):
        return time.monotonic()-self.module_at<1 and self.module.get('local_ready',False)

    def catalog(self):
        result={k:self.module.get(k) for k in ('source','local_override','fleet_enabled','tf_age_ms','localization_status','message','execution_strategy')}
        result.update(run_id=self.run_id,phase=self.phase,waypoint_states=self.states,
                      remaining_wait=self.module.get('remaining_wait',0),block=self.module.get('block',0),blocks=self.module.get('blocks',0))
        if not self.active and self.module.get('source')=='FLEET':result['phase']='fleet_running'
        return result

    def start(self,points,preflight_only=False,single_point=False):
        if preflight_only:raise ValueError('Preview uses the read-only planning interface')
        if self.active:
            self.n.publish_status('本地任务已提交，请先停止或等待结果');return
        if not points or not self.inputs_ready() or not self.navigator.server_is_ready():
            self.n.publish_status('不能开始：'+self.health.reason);return
        self.run_id='local-ui-'+uuid.uuid4().hex;self.cancel_after_accept=False;self.handle=None
        self.n.preview_revision+=1;self.n.preview_dirty=False
        if self.n.preview_goal_handle:self.n.preview_goal_handle.cancel_goal_async()
        goal=ExecuteNavigation.Goal();goal.task_id=self.run_id;goal.source=ExecuteNavigation.Goal.LOCAL
        goal.single_point=single_point;goal.pass_radius=float(self.n.pass_radius)
        for i,w in enumerate(points):
            p=NavigationPoint();p.name=w.name;p.pose.header.frame_id=self.n.frame_id
            p.pose.header.stamp=self.n.get_clock().now().to_msg();p.pose.pose=copy.deepcopy(w.pose)
            p.kind=NavigationPoint.STOP if w.kind=='stop' or i==len(points)-1 else NavigationPoint.PASS
            p.dwell_seconds=float(w.dwell_seconds);goal.waypoints.append(p)
        self.active=self.n.navigation_active=True;self.phase='preplanning';self.states=['待通过']*len(points)
        self.n.publish_status('已提交给本车独立导航模块；若协同正在执行，将先停稳再接管')
        run=self.run_id
        self.navigator.send_goal_async(goal,feedback_callback=self.feedback).add_done_callback(lambda f:self.accepted(f,run))

    def accepted(self,future,run):
        try:
            if run!=self.run_id:
                old=future.result()
                if old.accepted:old.cancel_goal_async()
                return
            self.handle=future.result()
            if not self.handle.accepted:raise RuntimeError('本地模块拒绝目标')
            self.handle.get_result_async().add_done_callback(lambda f:self.finished(f,run))
            if self.cancel_after_accept:self.handle.cancel_goal_async()
        except Exception as error:
            self.active=self.n.navigation_active=False;self.phase='failed';self.n.publish_status(str(error));self.n.publish_catalog()

    def feedback(self,message):
        f=message.feedback
        if f.task_id==self.run_id:
            self.phase=f.phase;self.n.publish_status(f.message);self.n.publish_catalog()

    def finished(self,future,run):
        if run!=self.run_id:return
        self.active=self.n.navigation_active=False;self.handle=None
        try:
            r=future.result();self.phase='completed' if r.result.success else 'canceled' if r.status==5 else 'failed'
            self.n.publish_status(r.result.message)
        except Exception as error:self.phase='failed';self.n.publish_status(str(error))
        self.n.publish_catalog()

    def stop(self,reason='用户停止导航',failed=False):
        self.cancel_after_accept=True
        if self.handle:self.handle.cancel_goal_async()
        if not self.stop_client.service_is_ready():
            self.n.publish_status('停止尚未确认：本地导航模块不可用');return
        self.phase='canceling';self.n.publish_status(reason+'；等待本地模块确认')
        def replied(f):
            try:self.n.publish_status(f.result().message)
            except Exception as error:self.n.publish_status('停止请求失败：'+str(error))
        self.stop_client.call_async(Trigger.Request()).add_done_callback(replied)
