"""ROS API execution; vehicle heartbeats stop when the central process is lost."""
import json,math,os,re,socket,time
from pathlib import Path
from rclpy.action import ActionClient
from std_msgs.msg import String
from std_srvs.srv import Trigger,SetBool
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import ComputePathThroughPoses
from nav2_msgs.msg import SpeedLimit
from rclpy.qos import QoSProfile,DurabilityPolicy
from omnifleet_navigation_interfaces.action import ExecuteNavigation, ExecuteFormation
from omnifleet_navigation_interfaces.msg import NavigationPoint
from .client import RobotObserver
from .permanent_parameters import ParameterClient
from .web_client import WebClient
from .formation_profile import FormationProfile

class NavigationClient(RobotObserver):
    def __init__(self):
        super().__init__()
        self.permanent_parameters=ParameterClient(self)
        self.web=WebClient(self)
        self.read_only=False
        self.motion_enabled = self.profile.get('motion_enabled', False)
        self.permission_path=Path(os.environ['OMNIFLEET_CONFIG']);self.permission_mtime=None;self.permission_error=None
        self.emit_timer.cancel();self.emit_timer=self.create_timer(.1,self.emit,clock=self.steady_clock)
        self.command_path=Path(os.environ['OMNIFLEET_DATA'])/'run'/f'{self.robot_id}-command.sock'
        self.command_path.unlink(missing_ok=True)
        self.commands=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        self.commands.bind(str(self.command_path));self.command_path.chmod(0o600);self.commands.setblocking(False)
        self.enable=self.create_client(SetBool,'/navigation/allow_fleet')
        self.acquire=self.create_client(Trigger,'/navigation/fleet/acquire')
        self.operator_stop=self.create_client(Trigger,'/navigation/stop')
        self.action=ActionClient(self,ExecuteNavigation,'/navigation/execute')
        self.formation_action=ActionClient(self,ExecuteFormation,'/navigation/formation')
        self.path_action=ActionClient(self,ComputePathThroughPoses,'/compute_path_through_poses');self.plan_handles={};self.selected_algorithms={}
        self.formation_profile=FormationProfile(self)
        self.create_timer(.2,self.formation_profile.tick,clock=self.steady_clock)
        latched=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        for kind in ('planner','controller'):
            self.create_subscription(String,'/'+kind+'_selector',lambda m,k=kind:self.selected_algorithms.update({k:m.data}),latched)
        self.heartbeat=self.create_publisher(String,'/navigation/fleet/heartbeat',1)
        self.manual_publisher=self.create_publisher(Twist,self.profile.get('manual_topic','/cmd_vel'),1);self.manual_until=0.
        self.follow_publisher=self.create_publisher(String,'/navigation/fleet/follow_trail',1);self.follow_sequence=0
        self.traffic_publisher=self.create_publisher(String,'/navigation/fleet/traffic_pause',1);self.traffic_sequence=0
        self.formation_speed_output=self.create_publisher(SpeedLimit,'/speed_limit',1)
        self.formation_speed=100.;self.formation_speed_seen=0.;self.formation_speed_applied=100.
        self.epoch=None;self.sequence=0;self.revision=0;self.task_id='';self.central_seen=0.;self.generation=0
        self.goal_handle=None;self.inflight=None;self.pending=None;self.arm_pending=False;self.armed_since=0.;self.events={};self.control={'phase':'disabled','event':None}
        self.arm_service_future=None;self.release_future=None;self.release_requested=False;self.queued_arm=None
        self.create_timer(.05,self.poll,clock=self.steady_clock);self.create_timer(.2,self.renew,clock=self.steady_clock)

    def event(self,request,phase,**fields):
        event={'request_id':request,'phase':phase,**fields};self.events[request]=event
        while len(self.events)>64:self.events.pop(next(iter(self.events)))
        self.control={'phase':phase,'event':event,'history':dict(self.events),
                      'busy':bool(self.goal_handle or self.inflight or self.pending or self.arm_pending),'armed':bool(self.epoch),
                      'motion_enabled':self.motion_enabled,'permission_error':self.permission_error,
                      'selected_algorithms':getattr(self,'selected_algorithms',{}),
                      'lease_diagnostics':getattr(self,'lease_diagnostics',{})}
        self.record('fleet_client',self.control)

    def poll(self):
        self.refresh_execution_permission()
        NavigationClient.progress_release(self)
        while True:
            try:packet=json.loads(self.commands.recv(16384))
            except BlockingIOError:break
            except ValueError:continue
            if packet.get('schema')!=1 or not 0<=time.monotonic()-packet.get('sent_monotonic',0)<=1:continue
            op=packet.get('op');request=packet.get('id','')
            if op=='ping':self.central_seen=time.monotonic();continue
            if op in ('nav_parameters_read','nav_parameters_save'):
                self.permanent_parameters.request(packet);continue
            if op in ('web_watch','web_diagnostic','web_service','web_estimate'):
                self.web.request(packet);continue
            if op in ('arm','navigate','manual') and not self.motion_enabled:
                self.event(request,'rejected',message='motion_disabled: central commissioning mode');continue
            if op=='prepare':
                poses=packet.get('poses',[packet.get('pose')])
                if not isinstance(poses,list) or not 1<=len(poses)<=100 or any(not isinstance(p,list) or len(p)!=3 or not all(type(v) in (int,float) and math.isfinite(v) for v in p) for p in poses):
                    self.event(request,'rejected',message='invalid pose');continue
                nav=self.samples.get('navigation',(0,{}))[1]
                if packet.get('localization_epoch')!=nav.get('localization_epoch'):
                    self.event(request,'rejected',message='localization epoch changed');continue
                if not nav.get('local_ready') or nav.get('navigation_active'):
                    self.event(request,'rejected',message='onboard navigation not ready or busy');continue
                self.event(request,'prepared',pose=poses[-1],point_count=len(poses),domain_id=self.profile['domain_id'],motion_sent=False);continue
            if time.monotonic()-self.central_seen>.5 and op not in ('cancel','disarm','operator_stop','cancel_plan'):
                self.event(request,'failed',message='central heartbeat stale');continue
            if op=='arm':self.arm(request)
            elif op=='plan':self.plan(packet)
            elif op=='cancel_plan':
                plan=self.plan_handles.pop(request,None)
                if plan and plan.get('handle'):plan['handle'].cancel_goal_async()
            elif op=='traffic_pause':
                if self.epoch and self.goal_handle and request==self.task_id and type(packet.get('paused')) is bool:
                    self.traffic_sequence+=1
                    self.traffic_publisher.publish(String(data=json.dumps({'task_id':self.task_id,'epoch':self.epoch,
                        'revision':self.revision,'sequence':self.traffic_sequence,'paused':packet['paused'],'reason':packet.get('reason','')})))
            elif op=='follow_update':self.update_follow(packet)
            elif op=='formation_speed':
                value=packet.get('percentage')
                if type(value) in (int,float) and math.isfinite(value) and 0<value<=100:
                    self.formation_speed=float(value);self.formation_speed_seen=time.monotonic()
            elif op=='manual':self.manual(packet)
            elif op=='operator_stop':
                self.cancel(request,disarm=True)
                if self.operator_stop.service_is_ready():
                    future=self.operator_stop.call_async(Trigger.Request())
                    def stopped(f,identifier=request):
                        response=f.result()
                        self.event(identifier,'stopped' if response.success else 'failed',confirmed=response.success,message=response.message)
                    future.add_done_callback(stopped)
                else:self.event(request,'failed',message='车端停止接口暂不可用')
            elif op=='navigate':
                poses=packet.get('poses',[packet.get('pose')])
                nav=self.samples.get('navigation',(0,{}))[1]
                if packet.get('localization_epoch')!=nav.get('localization_epoch'):
                    self.event(request,'failed',message='localization epoch changed');continue
                if not self.epoch or self.goal_handle or self.inflight or self.pending or not (self.formation_action if packet.get('follow_formation',False) else self.action).server_is_ready():
                    self.event(request,'failed',message='not armed, busy, or requested navigation interface unavailable');continue
                if not isinstance(poses,list) or not 1<=len(poses)<=100 or any(not isinstance(pose,list) or len(pose)!=3 or not all(type(v) in (int,float) and math.isfinite(v) for v in pose) for pose in poses):
                    self.event(request,'failed',message='invalid pose');continue
                self.revision+=1;self.task_id=request;self.pending=(packet,time.monotonic()+2.);self.renew()
            elif op in ('cancel','disarm'):
                self.cancel(request,disarm=op=='disarm')
        if self.pending:
            packet,deadline=self.pending;status=self.samples.get('navigation',(0,{}))[1]
            if status.get('fleet_lease_task_id')==self.task_id and status.get('fleet_lease_revision')==self.revision:
                self.pending=None;self.send_goal(packet)
            elif time.monotonic()>deadline:
                self.pending=None;self.event(packet['id'],'failed',message='onboard lease ACK timeout')
        if getattr(self,'manual_until',0.) and (time.monotonic()>self.manual_until or time.monotonic()-self.central_seen>.5):self.stop_manual()

    def manual(self,packet):
        velocity=packet.get('velocity')
        if not isinstance(velocity,list) or len(velocity)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in velocity):return
        if abs(velocity[0])>.3 or abs(velocity[1])>1.5:return
        if any(velocity) and not self.motion_enabled:return
        message=Twist();message.linear.x=float(velocity[0]);message.angular.z=float(velocity[1])
        self.manual_publisher.publish(message);self.manual_until=time.monotonic()+.3 if any(velocity) else 0.

    def plan(self,packet):
        identifier=packet['id'];poses=packet.get('poses');planner=self.selected_algorithms.get('planner')
        if not re.fullmatch(r'plan-[0-9a-f]{32}',identifier):return
        nav=self.samples.get('navigation',(0,{}))[1]
        if packet.get('localization_epoch')!=nav.get('localization_epoch') or not planner or not self.path_action.server_is_ready():
            self.event(identifier,'plan_failed',message='车端规划器选择或规划接口未就绪');return
        if not isinstance(poses,list) or not 1<=len(poses)<=100 or any(not isinstance(p,list) or len(p)!=3 or not all(type(v) in (int,float) and math.isfinite(v) for v in p) for p in poses):
            self.event(identifier,'plan_failed',message='规划目标无效');return
        goal=ComputePathThroughPoses.Goal(planner_id=planner,use_start=False)
        for x,y,yaw in poses:
            point=PoseStamped();point.header.frame_id='map';point.header.stamp=self.get_clock().now().to_msg()
            point.pose.position.x=float(x);point.pose.position.y=float(y)
            point.pose.orientation.z=math.sin(yaw/2);point.pose.orientation.w=math.cos(yaw/2);goal.goals.append(point)
        entry={};self.plan_handles[identifier]=entry
        def accepted(future):
            handle=future.result()
            if self.plan_handles.get(identifier) is not entry:
                if handle.accepted:handle.cancel_goal_async()
                return
            if not handle.accepted:
                self.plan_handles.pop(identifier,None);self.event(identifier,'plan_failed',message='车端规划请求被拒绝');return
            entry['handle']=handle
            def completed(result):
                if self.plan_handles.pop(identifier,None) is not entry:return
                outcome=result.result()
                if outcome.status!=4 or not outcome.result.path.poses:
                    self.event(identifier,'plan_failed',message='车端 Nav2 无可行路径，状态='+str(outcome.status));return
                path=[]
                for point in outcome.result.path.poses:
                    p,q=point.pose.position,point.pose.orientation
                    path.append([p.x,p.y,math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))])
                folder=Path(os.environ['OMNIFLEET_DATA'])/'run'/'plans'/self.robot_id;folder.mkdir(parents=True,exist_ok=True)
                target=folder/(identifier+'.json');temporary=target.with_suffix('.tmp')
                temporary.write_text(json.dumps({'path':path,'epoch':packet['localization_epoch'],'planner_id':planner},allow_nan=False));temporary.replace(target)
                self.event(identifier,'planned',planner_id=planner,point_count=len(path))
            handle.get_result_async().add_done_callback(completed)
        self.path_action.send_goal_async(goal).add_done_callback(accepted)

    def stop_manual(self):
        if getattr(self,'manual_until',0.):self.manual_publisher.publish(Twist());self.manual_until=0.

    def refresh_execution_permission(self):
        try:
            modified=self.permission_path.stat().st_mtime_ns
            if modified==self.permission_mtime:return
            value=json.loads(self.permission_path.read_text(encoding='utf-8'))['robots'][self.robot_id].get('motion_enabled',False)
            if type(value) is not bool:raise ValueError('Invalid execution permission')
            self.permission_mtime=modified;self.permission_error=None
        except (OSError,ValueError,KeyError,TypeError):
            value=False;self.permission_mtime=None;self.permission_error='无法读取有效执行许可配置，已关闭调度执行'
        previous=self.motion_enabled;self.motion_enabled=value
        if previous and not value:self.cancel('execution-permission-revoked',disarm=True)
        self.control.update(motion_enabled=value,permission_error=self.permission_error)
        self.record('fleet_client',self.control)

    def cancel(self,request,disarm=False):
        NavigationClient.stop_manual(self)
        was_arming=self.arm_pending
        self.generation+=1;self.pending=None;self.arm_pending=False;self.queued_arm=None
        if self.goal_handle:
            self.goal_handle.cancel_goal_async();self.event(request,'cancel_requested')
        else:self.event(request,'stopped',confirmed=self.stopped())
        if disarm or was_arming:
            self.epoch=None;self.release_requested=True

    def stopped(self):
        stamp,v=self.samples.get('control',(0,{}))
        return time.monotonic()-stamp<1. and v.get('stopped_seconds',0)>=.3 and not v.get('nav_active') and not self.inflight

    def progress_release(self):
        pending=getattr(self,'arm_service_future',None)
        if pending is not None and not pending.done():
            if not getattr(self,'release_requested',False) or self.arm_pending or time.monotonic()-getattr(self,'arm_service_started',0.)<1.:return
            self.arm_service_future=None;pending.cancel()
        pending=getattr(self,'release_future',None)
        if pending is not None:
            if time.monotonic()-self.release_started<1.:return
            self.release_future=None;pending.cancel()
        if getattr(self,'release_requested',False):
            if not self.enable.service_is_ready():return
            self.release_started=time.monotonic()
            self.release_future=self.enable.call_async(SetBool.Request(data=False))
            def released(f):
                if self.release_future is not f:return
                self.release_future=None
                if f.exception() is None and f.result().success:self.release_requested=False
            self.release_future.add_done_callback(released)
            return
        request=getattr(self,'queued_arm',None)
        if request:
            self.queued_arm=None;self.arm(request)

    def arm(self,request):
        if not self.motion_enabled:
            self.event(request,'rejected',message='motion_disabled: central commissioning mode');return
        if getattr(self,'release_requested',False) or getattr(self,'release_future',None) is not None:
            self.queued_arm=request;self.event(request,'arming',message='正在完成上次租约释放');return
        if self.arm_pending or self.epoch or self.goal_handle or not self.enable.service_is_ready() or not self.acquire.service_is_ready():
            self.event(request,'failed',message='control busy or unavailable');return
        self.arm_pending=True
        generation=self.generation
        def enabled(f):
            if self.arm_service_future is f:self.arm_service_future=None
            if generation!=self.generation:return
            if not f.result().success:
                self.arm_pending=False;self.event(request,'failed',message=f.result().message);return
            def acquired(result):
                if self.arm_service_future is result:self.arm_service_future=None
                if generation!=self.generation:return
                self.arm_pending=False;r=result.result()
                if not r.success:self.event(request,'failed',message=r.message);return
                self.epoch=json.loads(r.message)['epoch'];self.sequence=0;self.revision=0;self.task_id='';self.armed_since=time.monotonic()
                self.renew();self.event(request,'armed')
            self.arm_service_started=time.monotonic()
            self.arm_service_future=self.acquire.call_async(Trigger.Request())
            self.arm_service_future.add_done_callback(acquired)
        self.arm_service_started=time.monotonic()
        self.arm_service_future=self.enable.call_async(SetBool.Request(data=True))
        self.arm_service_future.add_done_callback(enabled)

    def renew(self):
        now = time.monotonic()
        diagnostics = getattr(self, 'lease_diagnostics', {})
        self.lease_diagnostics = diagnostics
        self.control['lease_diagnostics'] = diagnostics
        diagnostics.update(central_age=now-self.central_seen,
            max_central_age=max(diagnostics.get('max_central_age', 0.) if self.epoch else 0., now-self.central_seen),
            max_renew_gap=max(diagnostics.get('max_renew_gap', 0.) if self.epoch else 0., now-getattr(self, 'last_renew', now)))
        self.last_renew = now
        percentage=self.formation_speed if time.monotonic()-self.formation_speed_seen<=.5 and time.monotonic()-self.central_seen<=.5 else 100.
        if percentage<100. or self.formation_speed_applied<100.:
            message=SpeedLimit(percentage=True,speed_limit=percentage);message.header.stamp=self.get_clock().now().to_msg()
            self.formation_speed_output.publish(message)
        self.formation_speed_applied=percentage
        stamp,nav=self.samples.get('navigation',(0,{}))
        if self.epoch and time.monotonic()-self.armed_since>.8 and time.monotonic()-stamp<1. and (not nav.get('fleet_enabled') or not nav.get('fleet_lease_fresh')):
            diagnostics['lost'] = {'monotonic':now, 'sequence':self.sequence,
                'central_age':now-self.central_seen, 'navigation_age':now-stamp,
                'max_renew_gap':diagnostics['max_renew_gap'], 'max_central_age':diagnostics['max_central_age'],
                'fleet_enabled':nav.get('fleet_enabled'), 'fleet_lease_fresh':nav.get('fleet_lease_fresh'),
                'onboard_sequence':nav.get('fleet_lease_sequence'), 'message':nav.get('message')}
            self.epoch=None;self.generation+=1;self.pending=None
            if self.goal_handle:self.goal_handle.cancel_goal_async()
        if self.epoch and time.monotonic()-self.central_seen<=.5:
            self.sequence+=1
            self.heartbeat.publish(String(data=json.dumps({'epoch':self.epoch,'sequence':self.sequence,'task_id':self.task_id,'revision':self.revision})))
            diagnostics.update(sent_sequence=self.sequence,sent_monotonic=now)
        if (self.epoch is None and self.goal_handle and not self.inflight and now-stamp<.5
                and not nav.get('navigation_active') and not nav.get('fleet_enabled')
                and not nav.get('fleet_lease_fresh') and self.stopped()):
            # A lost terminal Action result must not leave a dead, lease-less
            # handle marked busy after the vehicle has confirmed stopping.
            self.goal_handle=None
        self.control.update(busy=bool(self.goal_handle or self.inflight or self.pending or self.arm_pending),armed=bool(self.epoch),
                            motion_enabled=self.motion_enabled,permission_error=self.permission_error)
        self.control['selected_algorithms']=getattr(self,'selected_algorithms',{})
        self.control['formation_speed_percent']=percentage
        self.record('fleet_client',self.control)

    def send_goal(self,packet):
        if not self.motion_enabled:
            self.event(packet['id'],'rejected',message='motion_disabled: central commissioning mode');return
        if self.goal_handle or self.inflight:
            self.event(packet['id'],'failed',message='previous goal not drained');return
        generation=self.generation
        self.inflight=packet['id']
        poses=packet.get('poses',[packet.get('pose')])
        if packet.get('follow_formation',False):
            goal=ExecuteFormation.Goal(task_id=self.task_id,command_epoch=self.epoch,revision=self.revision)
            action=self.formation_action
        else:
            goal=ExecuteNavigation.Goal(task_id=self.task_id,command_epoch=self.epoch,revision=self.revision,source=1,single_point=packet.get('single_point',len(poses)==1))
            goal.follow_trail=bool(packet.get('follow_trail',False))
            action=self.action
        radius=getattr(self,'samples',{}).get('waypoints',(0,{}))[1].get('pass_radius')
        if type(radius) in (int,float) and math.isfinite(radius) and .05<=radius<=.5:goal.pass_radius=float(radius)
        for i,pose in enumerate(poses):
            point=NavigationPoint(name=self.task_id+'-'+str(i+1),kind=NavigationPoint.STOP if i==len(poses)-1 else NavigationPoint.PASS)
            point.pose.header.frame_id='map';point.pose.header.stamp=self.get_clock().now().to_msg()
            point.pose.pose.position.x,point.pose.pose.position.y=pose[:2]
            point.pose.pose.orientation.z=math.sin(pose[2]/2);point.pose.pose.orientation.w=math.cos(pose[2]/2);goal.waypoints.append(point)
        def accepted(f):
            handle=f.result()
            if not handle.accepted:
                if self.inflight==packet['id']:self.inflight=None
                self.event(packet['id'],'failed',message='goal rejected');return
            if generation==self.generation:
                self.inflight=None;self.goal_handle=handle;self.event(packet['id'],'executing')
            else:handle.cancel_goal_async()
            def finished(result):
                r=result.result()
                if self.goal_handle is handle:self.goal_handle=None
                if self.inflight==packet['id']:self.inflight=None
                success=bool(r.result.success and r.status==4 and generation==self.generation)
                self.event(packet['id'],'completed' if success else 'failed',success=success,code=r.result.code,message=r.result.message,action_status=r.status)
            handle.get_result_async().add_done_callback(finished)
        def feedback(m):
            if generation==self.generation:self.event(packet['id'],'executing',navigation_phase=m.feedback.phase,navigation_message=m.feedback.message,passed_points=m.feedback.passed_points,tf_age_ms=m.feedback.tf_age_ms)
        action.send_goal_async(goal,feedback_callback=feedback).add_done_callback(accepted)

    def update_follow(self,packet):
        nav=self.samples.get('navigation',(0,{}))[1]
        if (not self.motion_enabled or not self.epoch or not self.goal_handle or packet['id']!=self.task_id or
            packet.get('localization_epoch')!=nav.get('localization_epoch')):return
        self.follow_sequence+=1
        self.lease_diagnostics.update(follow_sent_sequence=self.follow_sequence,follow_sent_monotonic=time.monotonic())
        self.follow_publisher.publish(String(data=json.dumps({'task_id':self.task_id,'epoch':self.epoch,
            'revision':self.revision,'sequence':self.follow_sequence,
            'localization_epoch':packet['localization_epoch'],'poses':packet.get('poses'),
            'mode':packet.get('mode','trail'),
            'predecessor_velocity':packet.get('predecessor_velocity',[0.,0.]),
            'follow_distance':packet.get('follow_distance',0.),'range_rate':packet.get('range_rate',0.)})))
