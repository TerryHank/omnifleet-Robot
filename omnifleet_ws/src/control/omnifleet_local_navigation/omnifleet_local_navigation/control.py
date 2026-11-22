from .scope import frame, topic
import argparse,copy,json,math,time,os
from collections import deque
from pathlib import Path
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.time import Time
from rclpy.qos import QoSProfile,DurabilityPolicy
from geometry_msgs.msg import Twist,PoseStamped
from nav_msgs.msg import Odometry,OccupancyGrid,Path as NavPath
from nav2_msgs.action import NavigateToPose,NavigateThroughPoses
from lifecycle_msgs.srv import GetState
from rcl_interfaces.srv import GetParameters,ListParameters
from action_msgs.srv import CancelGoal
from action_msgs.msg import GoalStatusArray
from std_msgs.msg import Empty,Bool,String
from tf2_ros import Buffer,TransformListener
from .geometry import pose,compose,inverse
from .storage import read,save
from .tracking_guard import TrackingGuard
from source_time_executor import velocity_command_time,with_source_time

def yaw(q):return math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))

class LocalControl(Node):
    def __init__(self,config):
        super().__init__('local_navigation_'+config['robot_id'],namespace='/');self.config=config
        if not math.isfinite(config.get('safety_clearance',.2)) or config.get('safety_clearance',.2)<.2:raise ValueError('invalid safety clearance')
        self.applied_seq=0;self.command_epoch=''
        self.mode='STARTUP';self.startup_canceled=False;self.startup_done=False;self.startup_stopped=None;self.startup_cancel_calls={}
        self.fleet_hold=True;self.estop=False;self.manual_time=0.;self.nav_time=0.
        self.manual=[0.,0.];self.nav=[0.,0.];self.velocity=[0.,0.];self.velocity_time=0.
        self.expired_velocity_commands={'nav':0,'manual':0}
        self.state_path=Path(config.get('state_file',str(Path.home()/'.local/share/omnifleet_t2'/('local-navigation-'+config['robot_id']+'.json'))))
        self.zero_since=None;self.estop_input=False;self.safety_latched=read(self.state_path,{}).get('safety_latched',False)
        self.estop=self.safety_latched
        self.local_pose=None;self.local_pose_3d=None;self.pose_age=99.;self.pose_stamp_ns=0;self.states={};self.pending_states=set();self.nav_status={}
        self.active_goal_ids={};self.manual_blocked_goals=set()
        self.goal_handle=None;self.goal=None;self.pending_goal=False;self.goal_error='';self.completed_seq=0
        self.goal_is_route=False;self.deferred_navigation=None;self.outstanding_results=set()
        self.pending_goal_requests={}
        self.cancel_pending=0;self.control_gate_ready=False;self.grid=None;self.grid_time=0.
        self.safety_reason='';self.epoch='';self.process_epoch='';self.map_generation=0;self.pose_time=0.
        self.trace=[];self.planned_path=[];self.own_snapshot={}
        self.tracking_guard=TrackingGuard(config['length'],config['width'],config['padding'])
        self.tracking_stop_reason='';self.obstacle_resolution=.05
        self.pose_window=deque(maxlen=20)
        self.runtime_parameters={};self.parameter_time=0.;self.parameter_pending=set();self.selection={}
        self.pending_state_calls={};self.pending_parameter_calls={}
        self.obstacles=[];self.obstacle_stamp=0.;self.obstacle_complete=False;self.obstacle_grid=None
        self.contact=None;self.contact_time=0.
        self.machine_boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        self.tf=Buffer();self.listener=TransformListener(self.tf,self)
        self.output=self.create_publisher(Twist,'/navigation/cmd_vel_safe',10)
        self.heartbeat_pub=self.create_publisher(String,'/navigation/local_status',10)
        self.create_subscription(Twist,'/cmd_vel',self.on_manual,1)
        self.create_subscription(Twist,'/navigation/nav_cmd_vel',self.on_nav,1)
        self.create_subscription(Odometry,'/odom',self.on_odom,20)
        self.create_subscription(Bool,'/navigation/estop',self.on_estop,10)
        self.create_subscription(Bool,'/navigation/contact',self.on_contact,10)
        for name in ('planner','controller'):
            self.create_subscription(String,'/'+name+'_selector',lambda m,n=name:self.selection.update({n:m.data}),
                QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.parameter_names={
            'controller_server':['controller_plugins','general_goal_checker.xy_goal_tolerance','general_goal_checker.yaw_goal_tolerance',
                'fleet_goal_checker.xy_goal_tolerance',
                'progress_checker.required_movement_radius','progress_checker.movement_time_allowance',
                'FollowPath.max_vel_x','FollowPath.max_vel_theta','FollowPath.BaseObstacle.scale',
                'FollowPathRPP.desired_linear_vel','FollowPathRPP.rotate_to_heading_angular_vel','FollowPathMPPI.vx_max','FollowPathMPPI.wz_max',
                'FollowPathMPPI.model_dt','FollowPathMPPI.time_steps',
                'FleetMPPI.model_dt','FleetMPPI.time_steps',
                'FleetMPPI.vx_max','FleetMPPI.vx_min','FleetMPPI.wz_max'],
            'planner_server':['planner_plugins'],
            'omnifleet_navigation_policy':['automatic_recovery'],
            'global_costmap/global_costmap':['global_frame','resolution','footprint','footprint_padding','static_layer.map_topic',
                'inflation_layer.inflation_radius','inflation_layer.cost_scaling_factor'],
            'local_costmap/local_costmap':['global_frame','resolution','footprint','robot_radius','footprint_padding','inflation_layer.inflation_radius',
                'inflation_layer.cost_scaling_factor']}
        self.parameter_clients={name:self.create_client(GetParameters,'/'+name+'/get_parameters') for name in self.parameter_names}
        self.parameter_list_clients={name:self.create_client(ListParameters,'/'+name+'/list_parameters') for name in self.parameter_names}
        self.create_timer(5.,self.read_parameters)
        self.create_subscription(OccupancyGrid,'/global_costmap/costmap',self.on_grid,
            QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.create_subscription(OccupancyGrid,'/local_costmap/costmap',self.on_obstacle_grid,
            QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.create_subscription(NavPath,'/plan',self.on_plan,10)
        actions=('follow_waypoints','navigate_to_pose','navigate_through_poses','follow_path','spin','backup','drive_on_heading','wait')
        for action in actions:
            self.create_subscription(GoalStatusArray,self.backend_name(action)+'/_action/status',
                lambda m,a=action:self.on_nav_status(a,m),
                QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.state_clients={name:self.create_client(GetState,'/'+name+'/get_state') for name in ('controller_server','planner_server','bt_navigator')}
        self.cancel_clients=[self.create_client(CancelGoal,self.backend_name(a)+'/_action/cancel_goal') for a in actions]
        self.create_timer(.02,self.control_tick);self.create_timer(.2,self.snapshot);self.create_timer(1.,self.discovery)

    @with_source_time
    def on_nav(self,msg,info):
        issued=velocity_command_time(msg,info)
        if issued is None:
            self.nav=[0.,0.];self.nav_time=0.;self.expired_velocity_commands['nav']+=1;return
        self.nav=[msg.linear.x,msg.angular.z];self.nav_time=issued
    def on_contact(self,msg):
        self.contact=bool(msg.data);self.contact_time=time.monotonic()
        if self.contact:
            self.fleet_enabled=False;self.fleet_lease.revoke()
            self.safety_latched=True;save(self.state_path,{'safety_latched':True});self.estop=True;self.fleet_hold=True;self.cancel_all()


    def read_parameters(self):
        fields={1:'bool_value',2:'integer_value',3:'double_value',4:'string_value',5:'byte_array_value',6:'bool_array_value',7:'integer_array_value',8:'double_array_value',9:'string_array_value'}
        for name,client in self.parameter_clients.items():
            if name in self.parameter_pending or not client.service_is_ready():continue
            list_client=self.parameter_list_clients[name]
            if not list_client.service_is_ready():continue
            self.parameter_pending.add(name);future=list_client.call_async(ListParameters.Request())
            self.pending_parameter_calls[name]=(list_client,future,time.monotonic())
            def listed(f,name=name,client=client):
                try:
                    available=f.result().result.names;names=[k for k in self.parameter_names[name] if k in available]
                    request_=GetParameters.Request();request_.names=names;pending=client.call_async(request_)
                    self.pending_parameter_calls[name]=(client,pending,time.monotonic())
                    def done(result):
                        self.parameter_pending.discard(name);self.pending_parameter_calls.pop(name,None)
                        try:
                            values={k:getattr(v,fields[v.type]) if v.type in fields else None for k,v in zip(names,result.result().values)}
                            self.runtime_parameters[name]={'values':values,'received_at':time.monotonic()}
                        except Exception:self.runtime_parameters.pop(name,None)
                    pending.add_done_callback(done)
                except Exception:
                    self.parameter_pending.discard(name);self.pending_parameter_calls.pop(name,None);self.runtime_parameters.pop(name,None)
            future.add_done_callback(listed)
    def on_odom(self,msg):
        self.velocity=[msg.twist.twist.linear.x,msg.twist.twist.angular.z];self.velocity_time=time.monotonic()
        if abs(self.velocity[0])<.02 and abs(self.velocity[1])<.05:
            if self.zero_since is None:self.zero_since=self.velocity_time
        else:self.zero_since=None
    def on_grid(self,msg):
        self.grid=msg;self.grid_time=time.monotonic()
    def on_obstacle_grid(self,msg):
        self.obstacle_grid=msg
        self.obstacles=[];self.obstacle_complete=False
        if self.local_pose is None:return
        try:
            origin=[msg.info.origin.position.x,msg.info.origin.position.y,yaw(msg.info.origin.orientation)]
            transform=[0.,0.,0.]
            if msg.header.frame_id!=frame('map'):
                t=self.tf.lookup_transform(frame('map'),msg.header.frame_id,Time());v=t.transform
                transform=[v.translation.x,v.translation.y,yaw(v.rotation)]
            combined=compose(transform,origin);res=msg.info.resolution;self.obstacle_resolution=res
            if not math.isfinite(res) or res<=0:raise ValueError('invalid obstacle resolution')
            for index,value in enumerate(msg.data):
                if value<100:continue
                p=compose(combined,[(index%msg.info.width+.5)*res,(index//msg.info.width+.5)*res,0.])
                if math.dist(p[:2],self.local_pose[:2])<4:self.obstacles.append(p[:2])
            if len(self.obstacles)>10000:self.obstacles=[];self.obstacle_stamp=0.;return
            self.obstacle_complete=True
            self.obstacle_stamp=time.monotonic()
        except Exception:self.obstacles=[];self.obstacle_stamp=0.
    def on_plan(self,msg):
        stride=max(1,len(msg.poses)//100)
        points=[[p.pose.position.x,p.pose.position.y] for p in msg.poses[::stride]][:101]
        try:
            if msg.header.frame_id!=frame('map'):
                t=self.tf.lookup_transform(frame('map'),msg.header.frame_id,Time());v=t.transform
                points=[compose([v.translation.x,v.translation.y,yaw(v.rotation)],[*p,0.])[:2] for p in points]
            self.planned_path=points
        except Exception:self.planned_path=[]

    @with_source_time
    def on_manual(self,msg,info):
        issued=velocity_command_time(msg,info)
        if issued is None:
            self.manual=[0.,0.];self.manual_time=0.;self.expired_velocity_commands['manual']+=1;return
        self.policy.local_override=True;self.fleet_enabled=False
        self.fleet_lease.revoke()
        if not self.control_gate_ready:return
        self.manual=[msg.linear.x,msg.angular.z];self.manual_time=issued
        if self.mode!='MANUAL':
            self.manual_blocked_goals=set().union(*self.active_goal_ids.values()) if self.active_goal_ids else set()
            self.mode='MANUAL';self.fleet_hold=True;self.cancel_all()

    def on_nav_status(self,action,msg):
        previous=self.active_goal_ids.get(action,set())
        aborted=any(s.status==6 and bytes(s.goal_info.goal_id.uuid).hex() in previous for s in msg.status_list)
        active={bytes(s.goal_info.goal_id.uuid).hex() for s in msg.status_list if s.status in (1,2,3)}
        self.active_goal_ids[action]=active;self.nav_status[action]=bool(active)
        if self.mode=='MANUAL' and time.monotonic()-self.manual_time>.35 and self.cancel_pending==0:
            if active-self.manual_blocked_goals and time.monotonic()-self.velocity_time<.5 and abs(self.velocity[0])<.02 and abs(self.velocity[1])<.05:
                self.mode='LOCAL';self.nav_time=0.;self.startup_done=True
        if action=='follow_path' and aborted and hasattr(self,'recover_from_nav2_failure'):
            self.recover_from_nav2_failure()

    def on_estop(self,msg):
        self.estop_input=bool(msg.data)
        if self.estop_input:self.safety_latched=True;save(self.state_path,{'safety_latched':True})
        self.estop=self.estop_input or self.safety_latched
        if self.estop:
            self.fleet_enabled=False;self.fleet_lease.revoke()
            self.manual_blocked_goals=set().union(*self.active_goal_ids.values()) if self.active_goal_ids else set()
            self.mode='MANUAL';self.manual=[0.,0.];self.manual_time=time.monotonic()
            self.fleet_hold=True;self.cancel_all()



    def discovery(self):
        now=time.monotonic()
        if self.mode=='STARTUP':
            for client,(future,sent) in list(self.startup_cancel_calls.items()):
                if now-sent>3. and client.service_is_ready():
                    client.remove_pending_request(future)
                    self._request_startup_cancel(client)
        for calls,pending,values in ((self.pending_state_calls,self.pending_states,self.states),
                                      (self.pending_parameter_calls,self.parameter_pending,self.runtime_parameters)):
            for name,(client,future,sent) in list(calls.items()):
                if now-sent>2.:
                    client.remove_pending_request(future);calls.pop(name,None);pending.discard(name);values.pop(name,None)
        legacy=self.get_publishers_info_by_topic(self.resolve_topic_name('/cmd_vel'))
        consumers=self.get_subscriptions_info_by_topic(self.resolve_topic_name('/navigation/cmd_vel_safe'))
        legacy_consumers=self.get_subscriptions_info_by_topic(self.resolve_topic_name('/cmd_vel'))
        self.control_gate_ready=(self.config.get('enable_control',False) and
            any(i.node_name=='omnifleet_t2_driver' for i in consumers) and
            not any(i.node_name=='omnifleet_t2_driver' for i in legacy_consumers) and
            not any(i.node_name in ('controller_server','behavior_server') for i in legacy) and
            self.count_publishers(self.resolve_topic_name('/navigation/cmd_vel_safe'))==1)
        gate_state=(self.config.get('enable_control',False),tuple(i.node_name for i in consumers),
                    tuple(i.node_name for i in legacy_consumers),tuple(i.node_name for i in legacy),
                    self.count_publishers(self.resolve_topic_name('/navigation/cmd_vel_safe')))
        if gate_state!=getattr(self,'last_gate_state',None):
            self.last_gate_state=gate_state
            self.get_logger().info('control gate inputs: '+repr(gate_state))
        for name,c in self.state_clients.items():
            if name not in self.pending_states and c.service_is_ready():
                self.pending_states.add(name);f=c.call_async(GetState.Request())
                self.pending_state_calls[name]=(c,f,time.monotonic())
                def done(f,name=name):
                    self.pending_states.discard(name);self.pending_state_calls.pop(name,None)
                    try:self.states[name]=(f.result().current_state.id,time.monotonic())
                    except Exception:self.states.pop(name,None)
                f.add_done_callback(done)
        ids=[]
        for p in Path('/proc').glob('[0-9]*'):
            try:
                argv=(p/'cmdline').read_bytes().split(b'\0')
                if argv and Path(os.fsdecode(argv[0])).name=='mola-cli':ids.append(p.name+':'+(p/'stat').read_text().split()[21])
            except (OSError,IndexError):pass
        epoch=self.machine_boot+'|'+'|'.join(sorted(ids)) if ids else ''
        if self.process_epoch and epoch!=self.process_epoch:
            self.fleet_hold=True;self.goal_error='localization restarted';self.cancel_all()
        if epoch!=self.process_epoch:self.map_generation=0
        self.process_epoch=epoch;self.epoch=epoch+':'+str(self.map_generation) if epoch else ''

    def goal_safe(self,target):
        m=self.grid
        if m is None or time.monotonic()-self.grid_time>3:return False
        try:
            if m.header.frame_id!=frame('map'):
                t=self.tf.lookup_transform(m.header.frame_id,frame('map'),Time());v=t.transform
                target=compose([v.translation.x,v.translation.y,yaw(v.rotation)],target)
        except Exception:return False
        origin=[m.info.origin.position.x,m.info.origin.position.y,yaw(m.info.origin.orientation)]
        x,y,theta=compose(inverse(origin),target);res=m.info.resolution
        hl=self.config['length']/2+self.config['padding']+res*.71
        hw=self.config['width']/2+self.config['padding']+res*.71
        radius=math.hypot(hl,hw)
        x0,x1=math.floor((x-radius)/res),math.ceil((x+radius)/res)
        y0,y1=math.floor((y-radius)/res),math.ceil((y+radius)/res)
        if x0<0 or y0<0 or x1>=m.info.width or y1>=m.info.height:return False
        c,s=math.cos(theta),math.sin(theta)
        for iy in range(y0,y1+1):
            for ix in range(x0,x1+1):
                dx,dy=(ix+.5)*res-x,(iy+.5)*res-y
                if abs(c*dx+s*dy)<=hl and abs(-s*dx+c*dy)<=hw:
                    value=m.data[iy*m.info.width+ix]
                    if value<0 or value>=100:return False
        return True


    def control_tick(self):
        now=time.monotonic()
        command=[0.,0.];self.safety_reason='';self.near_turn_active=False
        escape=getattr(self,'clearance_escape',None)
        if self.control_gate_ready:
            if self.mode=='STARTUP':
                if not self.startup_canceled:self.cancel_all();self.startup_canceled=True
                stopped=not any(self.nav_status.values()) and not self.cancel_pending and not self.pending_goal_requests and now-self.velocity_time<.5 and max(abs(v) for v in self.velocity)<.02
                if stopped:
                    if self.startup_stopped is None:self.startup_stopped=now
                    if now-self.startup_stopped>=.5:self.mode='LOCAL';self.nav_time=0.;self.startup_done=True
                else:self.startup_stopped=None
            elif self.mode=='MANUAL':
                if now-self.manual_time<.35:command=self.manual
            elif self.mode=='LOCAL':
                if escape:command=self.recovery_command(now)
                elif self.output_permitted() and now-self.nav_time<.35:command=self.nav
            elif self.mode=='FLEET':
                job=self.current_job
                if not self.fleet_enabled or not self.fleet_lease.fresh(now) or self.fleet_localization_epoch!=self.epoch:self.expire_fleet()
                elif job and not self.fleet_lease.matches(job.ticket,now):self.expire_fleet()
                elif job and self.output_permitted() and now-self.nav_time<.35:
                    command=self.nav
        if not all(math.isfinite(v) for v in command):command=[0.,0.];self.safety_reason='nonfinite command'
        turn=None
        if not escape and self.mode=='LOCAL' and hasattr(self,'bounded_turn_command'):
            turn=self.bounded_turn_command(now,command)
        if turn is not None:
            command=turn;self.near_turn_active=True;self.tracking_guard.reset()
        elif escape and self.mode=='LOCAL':
            self.tracking_guard.reset()
        elif self.mode in ('MANUAL','LOCAL','FLEET') and any(abs(v)>1e-6 for v in command):
            reason,latch=self.tracking_guard.evaluate(now,self.local_pose,self.pose_stamp_ns/1e9,command,
                self.planned_path,self.obstacles,self.obstacle_resolution,self.pose_age,
                now-self.obstacle_stamp if self.obstacle_stamp else 99.,self.obstacle_complete,
                require_path=self.mode!='MANUAL',check_body_clearance=self.mode=='FLEET')
            if reason=='predicted_body_clearance' and self.mode=='LOCAL' and hasattr(self,'bounded_turn_command'):
                turn=self.bounded_turn_command(now,command,start=True)
                if turn is not None:
                    command=turn;reason='';latch=False;self.near_turn_active=True;self.tracking_guard.reset()
            if reason:
                command=[0.,0.];self.safety_reason=reason
                if latch:
                    self.tracking_stop_reason=reason;self.goal_error=reason
                    if reason=='predicted_body_clearance' and hasattr(self,'prepare_clearance_recovery'):
                        self.prepare_clearance_recovery()
                    self.fleet_enabled=False;self.fleet_lease.revoke();self.manual=[0.,0.]
                    # Tracking alerts cancel motion; physical inputs own the estop latch.
                    self.fleet_hold=True;self.cancel_all()
        else:self.tracking_guard.reset()
        if self.estop:command=[0.,0.];self.safety_reason='estop'
        m=Twist();m.linear.x=command[0];m.angular.z=command[1];self.output.publish(m)

    def snapshot(self):
        now=time.monotonic()
        try:
            t=self.tf.lookup_transform(frame('map'),frame('base_link'),Time())
            age=(self.get_clock().now().nanoseconds-(t.header.stamp.sec*10**9+t.header.stamp.nanosec))/1e9
            self.pose_stamp_ns=t.header.stamp.sec*10**9+t.header.stamp.nanosec
            v=t.transform;self.local_pose_3d=[v.translation.x,v.translation.y,v.translation.z,v.rotation.x,v.rotation.y,v.rotation.z,v.rotation.w]
            if age<-.5:raise ValueError('localization timestamp is in the future')
            current=pose([t.transform.translation.x,t.transform.translation.y,yaw(t.transform.rotation)])
            if self.local_pose is not None:
                dt=max(.01,now-self.pose_time)
                jump=math.dist(current[:2],self.local_pose[:2])>.4*dt+.2 or abs(math.atan2(math.sin(current[2]-self.local_pose[2]),math.cos(current[2]-self.local_pose[2])))>1.2*dt+.3
                if jump:
                    self.map_generation+=1;self.epoch=self.process_epoch+':'+str(self.map_generation)
                    if self.mode=='FLEET':self.fleet_hold=True;self.goal_error='localization jump; alignment must be checked';self.cancel_all()
            self.pose_age=max(0.,age);self.local_pose=current;self.pose_time=now
            self.pose_window.append((now,current))
        except Exception:self.pose_age=99.;self.local_pose=None
        while self.pose_window and now-self.pose_window[0][0]>1.5:self.pose_window.popleft()
        pose_stationary=bool(self.local_pose is not None and self.pose_age<.8 and self.pose_window and now-self.pose_window[0][0]>=1. and
            all(math.dist(p[:2],self.local_pose[:2])<.015 and abs(math.atan2(math.sin(p[2]-self.local_pose[2]),math.cos(p[2]-self.local_pose[2])))<.05 for _,p in self.pose_window))
        ready=all(self.states.get(name,(0,0))[0]==3 and now-self.states[name][1]<3 for name in self.state_clients) and self.execution.single.server_is_ready() and self.execution.inputs_ready()
        state={'supports_route':True,'bounded_turn_active':getattr(self,'near_turn_active',False),'local_pose_3d':self.local_pose_3d,'local_pose':self.local_pose,'pose_age':self.pose_age,'velocity':self.velocity,'velocity_age':now-self.velocity_time,
            'pose_stamp_ns':self.pose_stamp_ns,
            'pose_stationary':pose_stationary,
            'contact':self.contact if now-self.contact_time<1. else None,
            'selected_algorithms':copy.deepcopy(self.selection),
            'obstacles':self.obstacles,'obstacle_age':now-self.obstacle_stamp if self.obstacle_stamp else 99.,
            'obstacle_observations_complete':self.obstacle_complete,
            'runtime_parameters':{k:{'values':v['values'],'age':now-v['received_at']} for k,v in self.runtime_parameters.items()},
            'stopped_seconds':now-self.zero_since if self.zero_since is not None and now-self.velocity_time<.5 else 0.,
            'localization_epoch':self.epoch,'nav_ready':ready,'control_gate_ready':self.control_gate_ready and self.startup_done,
            'control_mode':self.mode,'local_navigation_independent':True,'local_override':self.policy.local_override,'fleet_enabled':self.fleet_enabled,'fleet_permission_epoch':self.fleet_permission_epoch,
            'fleet_overlay_active':self.mode=='FLEET','manual_active':self.mode=='MANUAL',
            'manual_command_age':now-self.manual_time,'expired_velocity_commands':dict(self.expired_velocity_commands),
            'body_clearance_stop_enabled':self.mode=='FLEET',
            'estop':self.estop,'estop_input':self.estop_input,
            'control_epoch':self.command_epoch,'applied_command_seq':self.applied_seq,
            'nav_active':self.navigation_active or any(self.nav_status.values()),'pending_goal':self.pending_goal or bool(self.pending_goal_requests) or self.cancel_pending>0 or self.deferred_navigation is not None,
            'goal':self.goal,'goal_error':self.goal_error,'completed_seq':self.completed_seq,
            'planned_path':self.planned_path,'safety_stop_reason':self.safety_reason,
            'tracking_stop_reason':self.tracking_stop_reason,
            'health':'READY' if ready and self.pose_age<.8 else 'WAITING_LOCALIZATION_OR_NAV2'}
        self.own_snapshot=state
        msg=String();msg.data=json.dumps({'robot_id':self.config['robot_id'],**state});self.heartbeat_pub.publish(msg)



    @staticmethod
    def backend_name(action):
        return '/navigation_backend/'+action if action in ('navigate_to_pose','navigate_through_poses','follow_waypoints') else '/'+action

    def create_publisher(self,msg_type,name,*args,**kwargs):
        return super().create_publisher(msg_type,topic(name),*args,**kwargs)

    def create_subscription(self,msg_type,name,*args,**kwargs):
        return super().create_subscription(msg_type,topic(name),*args,**kwargs)

    def create_client(self,srv_type,name,*args,**kwargs):
        return super().create_client(srv_type,topic(name),*args,**kwargs)

    def resolve_topic_name(self,name,*args,**kwargs):
        return super().resolve_topic_name(topic(name),*args,**kwargs)

    def cancel_all(self):
        self.fleet_hold=True;self.nav=[0.,0.];self.nav_time=0.
        if hasattr(self,'execution') and self.execution.active:
            self.execution.stop(self.goal_error or '本地控制停止')
        elif self.mode=='STARTUP':
            for client in self.cancel_clients:
                if client.service_is_ready():
                    self._request_startup_cancel(client)

    def _request_startup_cancel(self,client):
        if client not in self.startup_cancel_calls:self.cancel_pending+=1
        future=client.call_async(CancelGoal.Request())
        self.startup_cancel_calls[client]=(future,time.monotonic())
        def done(f):
            if self.startup_cancel_calls.get(client,(None,))[0] is not f:return
            try:
                if f.result().return_code!=0:return
            except Exception:return
            self.startup_cancel_calls.pop(client,None)
            self.cancel_pending=max(0,self.cancel_pending-1)
        future.add_done_callback(done)

    def stationary(self):
        return self.zero_since is not None and time.monotonic()-self.zero_since>=.3 and time.monotonic()-self.velocity_time<.4

    def output_permitted(self):
        return (self.current_job is not None and self.execution.active and
                self.execution.phase in ('tracking','replanning','preplanning') and
                not self.policy.canceling)
