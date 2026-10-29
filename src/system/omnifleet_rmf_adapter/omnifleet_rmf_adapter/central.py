from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
import fcntl
import json
import math
import os
from pathlib import Path
import socket
import time
import signal
import subprocess
import sys
import uuid

import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped,TransformStamped
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Path as RosPath
from rcl_interfaces.srv import GetParameters
import rmf_adapter
from .control_http import ControlHTTP

from .state import summarize
from .map_hub import MapHub
from .missions import Missions
from .registration import AutoRegistration, registration_members
from .robot_names import RobotNames
from .identity import FleetIdentities
from .discovery import TTL, new_vehicle
from .operator_controls import OperatorControls
from .onboard_plans import OnboardPlans
from .permanent_parameters import ParameterCommands,FIELDS
from .rmf_dispatch import RmfDispatch
from .rmf_traffic import RmfTraffic


class CentralObserver(Node):
    def create_timer(self,period,callback,*args,**kwargs):
        def measured():
            started=time.monotonic()
            try:return callback()
            finally:
                elapsed=time.monotonic()-started
                if elapsed>.2:print(json.dumps({'event':'slow_callback','callback':callback.__qualname__,'elapsed':elapsed,'at':started}),flush=True)
        return super().create_timer(period,measured,*args,**kwargs)

    def __init__(self,adapter):
        super().__init__('omnifleet_rmf_state_bridge')
        self.steady_clock = Clock(clock_type=ClockType.STEADY_TIME)
        self.config = json.loads(Path(os.environ['OMNIFLEET_CONFIG']).read_text())
        self.data = Path(os.environ['OMNIFLEET_DATA'])
        run = self.data / 'run'
        run.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = (run / 'central.lock').open('w')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.socket_path = run / 'state.sock'
        self.socket_path.unlink(missing_ok=True)
        self.ipc = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.ipc.bind(str(self.socket_path))
        self.socket_path.chmod(0o600)
        self.ipc.setblocking(False)
        self.states = {}
        self.command_ipc=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        self.command_ipc.setblocking(False)
        self.ui=ControlHTTP();self.ui_results={}
        self.robot_ids=[r for r,p in self.config['robots'].items() if p['enabled']]
        self.initialized_clients=set();self.session_id=uuid.uuid4().hex
        self.display_names=RobotNames(self.config,self.data)
        self.identities=FleetIdentities(self.config,os.environ['OMNIFLEET_CONFIG'])
        self.maps=MapHub(self,self.config,self.data)
        self.map_executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix="fleet_maps")
        self.map_future=None
        self.missions=Missions(self.config,self.maps,self.data,self.send_command)
        self.plans=OnboardPlans(self.data,self.maps,self.send_command)
        self.permanent_parameters=ParameterCommands(self.send_command)
        self.missions.onboard_planner=self.plans.request
        self.rmf_traffic = RmfTraffic(self, adapter)
        self.rmf_dispatch = RmfDispatch(self)
        self.missions.rmf_dispatch, self.missions.rmf_traffic = self.rmf_dispatch, self.rmf_traffic
        self.operator=OperatorControls(self)
        self.path_publishers={r:self.create_publisher(RosPath,ns+'/missions/preview_path',10) for r,ns in self.maps.names.items()}
        self.registration=None
        self.auto_registration=AutoRegistration()
        self.discovery_status={'fresh':False,'robots':[],'conflicts':[]}
        self.schedule_response = 0.0
        self.schedule_service = ''
        self.schedule_client = None
        self.schedule_request = None
        self.publisher = self.create_publisher(String, '/omnifleet/rmf/connection_status', QoSProfile(depth=1,reliability=ReliabilityPolicy.BEST_EFFORT))
        self.robot_publishers = {
            key: self.create_publisher(String, assignment['namespace'] + '/rmf/connection_status', QoSProfile(depth=1,reliability=ReliabilityPolicy.BEST_EFFORT))
            for key, assignment in self.config['central']['assignments'].items()
            if self.config['robots'][key]['enabled']
        }
        self.create_timer(0.1, self.receive,clock=self.steady_clock)
        self.create_timer(1.0, self.publish,clock=self.steady_clock)
        self.create_timer(5.0, self.probe_schedule,clock=self.steady_clock)
        self.create_timer(.2,self.control_cycle,clock=self.steady_clock)
        self.create_timer(.1,self.map_cycle,clock=self.steady_clock)
        self.create_timer(.5,self.preview_cycle,clock=self.steady_clock)
        self.create_timer(1.0,self.sync_discovery,clock=self.steady_clock)

    def sync_discovery(self):
        path=self.data/'discovery.json'
        if not path.exists():
            self.discovery_status={'fresh':False,'robots':[],'conflicts':[]};return
        discovered=json.loads(path.read_text())
        if not 0<=time.monotonic()-discovered.get('updated_monotonic',0)<TTL:
            self.discovery_status={'fresh':False,'robots':[],'conflicts':[]};return
        self.discovery_status={'fresh':True,'robots':list(discovered.get('robots',{})),'conflicts':discovered.get('conflicts',[])}
        changed=False
        for robot,profile in discovered.get('robots',{}).items():
            if robot not in self.config['robots']:
                settings,assignment=new_vehicle(profile,self.config['central']['assignments'])
                namespace=assignment['namespace']
                self.maps.publishers[robot]=self.maps.create_vehicle_publishers(namespace)
                self.robot_publishers[robot]=self.create_publisher(String,namespace+'/rmf/connection_status',10)
                self.path_publishers[robot]=self.create_publisher(RosPath,namespace+'/missions/preview_path',10)
                assignment['display_name']=self.display_names.default(robot)
                self.config['robots'][robot]=settings
                self.config['central']['assignments'][robot]=assignment
                self.maps.names[robot]=namespace;self.robot_ids.append(robot)
                if self.config['central'].get('reference_robot') not in self.config['robots']:
                    self.config['central']['reference_robot']=robot;self.maps.reference=robot
                self.missions.follow['order'].append(robot)
                self.identities.revision+=1
                self.config['central']['identity_revision']=self.identities.revision
                self.operator.bind()
                self.get_logger().info('广播发现并接入车辆：'+robot+'；未授予运动许可')
                changed=True
            settings=self.config['robots'][robot]
            for key in ('domain_id','rmw','pose_topic','local_namespace','observed_namespace'):
                if settings.get(key)!=profile[key]:settings[key]=profile[key];changed=True
        if changed:
            temporary=self.identities.path.with_suffix('.discovery.tmp')
            temporary.write_text(json.dumps(self.config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            temporary.replace(self.identities.path)

    def send_command(self,op,request_id,robot_id,**fields):
        packet={'schema':1,'sent_monotonic':time.monotonic(),'op':op,'id':request_id,**fields}
        if robot_id not in self.robot_ids:raise ValueError('Robot is not assigned by the central configuration')
        try:
            self.command_ipc.sendto(json.dumps(packet).encode(),str(self.data/'run'/(robot_id+'-command.sock')))
            return True
        except (FileNotFoundError,ConnectionRefusedError,BlockingIOError):
            self.get_logger().warning('Robot client unavailable: '+robot_id)
            return False

    def snapshots(self):
        return {r:summarize(p,time.monotonic(),self.config['stale_after_seconds']) for r,p in self.states.items()}

    def execution_permissions(self, snapshots):
        requested={r:p.get('motion_enabled',False) is True for r,p in self.config['robots'].items() if p.get('enabled',True)}
        observed={r:bool(snapshots.get(r,{}).get('online') and snapshots.get(r,{}).get('fresh',{}).get('fleet_client')
                         and self.missions.client(snapshots[r]).get('motion_enabled') is True) for r in requested}
        return requested,observed,{r:requested[r] and observed[r] for r in requested}

    def set_execution_permission(self, command, snapshots):
        robot,enabled=command.get('robot_id'),command.get('enabled')
        if robot not in self.maps.names or type(enabled) is not bool:raise ValueError('请选择有效车辆并设置布尔执行许可')
        path=self.identities.path
        stored=json.loads(path.read_text(encoding='utf-8'))
        if stored['central'].get('identity_revision',0)!=self.identities.revision or any(
                (a['robot_name'],a['namespace'])!=(stored['central']['assignments'][r]['robot_name'],stored['central']['assignments'][r]['namespace'])
                for r,a in self.config['central']['assignments'].items()):
            raise ValueError('车辆身份配置已变化，请重新加载调度端')
        stored['robots'][robot]['motion_enabled']=enabled
        temporary=path.with_suffix('.permission.tmp')
        try:
            temporary.write_text(json.dumps(stored,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temporary.replace(path)
        except OSError as error:raise RuntimeError('执行许可保存失败：'+str(error)) from error
        self.config['robots'][robot]['motion_enabled']=enabled
        if not enabled:
            if self.missions.formation.active and robot in self.missions.formation.saved['order']:
                self.missions.formation.stop('撤销成员执行许可，停止编队')
            if self.missions.follow['active'] and robot in self.missions.follow['order']:
                self.missions.command({'op':'follow_stop'},snapshots)
            self.missions.stop(robot,'已撤销本车调度执行许可')
            self.send_command('disarm',command['id'],robot_id=robot)
        return {'phase':'execution_configured','robot_id':self.config['central']['assignments'][robot]['robot_name'],
                'enabled':enabled,'message':'许可已保存；等待接入端回读，开启许可不会发送导航目标' if enabled else '调度执行许可已关闭；相关任务已请求停止'}

    def reassign_identity(self, command, snapshots):
        robot=command.get('connection_id');prefix=self.identities.target(robot,command.get('prefix'))
        if self.missions.follow['active'] or self.missions.formation.active or any(j['phase'] not in ('STOPPED','COMPLETED','FAILED','INVALIDATED') for j in self.missions.jobs.values()):
            raise ValueError('请先停止调度任务并确认车辆停稳，再修改前缀')
        state=snapshots.get(robot,{})
        control=state.get('samples',{}).get('control',{}).get('value',{})
        nav=state.get('samples',{}).get('navigation',{}).get('value',{})
        if state.get('online') and (control.get('manual_active') or control.get('nav_active') or nav.get('navigation_active') or control.get('stopped_seconds',0)<.5):
            raise ValueError('该车仍在运动或导航，请先停稳')
        namespace='/'+prefix
        if namespace!=self.maps.names[robot]:
            created=[]
            try:
                map_publishers=self.maps.create_vehicle_publishers(namespace,created)
                status=self.create_publisher(String,namespace+'/rmf/connection_status',10);created.append(status)
                path=self.create_publisher(RosPath,namespace+'/missions/preview_path',10);created.append(path)
                self.identities.commit(robot,prefix)
            except Exception as error:
                for publisher in created:self.destroy_publisher(publisher)
                raise RuntimeError('前缀切换失败：'+str(error)) from error
            old=[*self.maps.publishers[robot].values(),self.robot_publishers[robot],self.path_publishers[robot]]
            self.maps.names[robot]=namespace;self.maps.publishers[robot]=map_publishers
            self.robot_publishers[robot]=status;self.path_publishers[robot]=path
            for publisher in old:self.destroy_publisher(publisher)
            self.operator.bind()
            self.maps.seen={k:v for k,v in self.maps.seen.items() if k[1]!='tf_static' and not (k[0]==robot and k[1] in ('map','description','global_costmap','local_costmap'))}
            self.maps.last_map_publish=0.
        return {'phase':'reassigned','connection_id':robot,'robot_id':prefix,'namespace':namespace,'identity_revision':self.identities.revision}

    def map_cycle(self):
        if self.map_future is not None:
            if not self.map_future.done():return
            self.map_future.result()
        states=self.snapshots()
        transforms=self.maps.transforms(states)
        def update_maps():
            began=time.monotonic()
            try:self.maps.tick(states,transforms)
            finally:
                elapsed=time.monotonic()-began
                if elapsed>.2:print(json.dumps({'event':'slow_map_worker','elapsed':elapsed}),flush=True)
        self.map_future=self.map_executor.submit(update_maps)

    def preview_cycle(self):
        self.publish_formation_frames()
        for robot,publisher in self.path_publishers.items():
            path=RosPath();path.header.frame_id='fleet_map';path.header.stamp=self.get_clock().now().to_msg()
            for x,y,yaw in self.missions.preview_paths.get(robot,[]):
                p=PoseStamped();p.header=path.header;p.pose.position.x=float(x);p.pose.position.y=float(y)
                p.pose.orientation.z=math.sin(yaw/2);p.pose.orientation.w=math.cos(yaw/2);path.poses.append(p)
            publisher.publish(path)

    def publish_formation_frames(self):
        formation=self.missions.formation
        if not formation.active:return
        transforms=[]
        for robot,(x,y,yaw) in formation.targets.items():
            t=TransformStamped();t.header.frame_id='fleet_map';t.header.stamp=self.get_clock().now().to_msg()
            t.child_frame_id='fleet_formation/'+self.config['central']['assignments'][robot]['robot_name']
            t.transform.translation.x=float(x);t.transform.translation.y=float(y)
            t.transform.rotation.z=math.sin(yaw/2);t.transform.rotation.w=math.cos(yaw/2)
            transforms.append(t)
        self.maps.tf.publish(TFMessage(transforms=transforms))

    def start_registration(self, trigger, robots=None):
        if self.registration is not None and self.registration.poll() is None:
            raise ValueError('Map registration is already running')
        if robots is None:
            robots=registration_members(self.snapshots(),self.maps.names,self.maps.reference)
        if len(robots)<2:raise ValueError('等待参考车和待配准车辆上线、地图就绪并停稳')
        self.registration=subprocess.Popen([sys.executable,'-m','omnifleet_rmf_adapter.registration'],
            stdout=(self.data/'alignment-job.log').open('w'),stderr=subprocess.STDOUT,
            env={**os.environ,'OMNIFLEET_REGISTRATION_TRIGGER':trigger,'OMNIFLEET_REGISTRATION_ROBOTS':json.dumps(robots)})

    def decorated_states(self):
        snapshots=self.snapshots()
        requested,observed,enabled=self.execution_permissions(snapshots)
        for robot,state in snapshots.items():
            blockers=[]
            if not state['online']:blockers.append('vehicle_offline')
            if not self.missions.nav(state).get('local_ready'):blockers.append('navigation_not_ready')
            if robot not in self.maps.valid_robots:blockers.append('map_session_not_validated')
            if not self.config['robots'][robot].get('motion_enabled',False):blockers.append('motion_disabled')
            elif not enabled.get(robot):blockers.append('execution_permission_unconfirmed')
            assignment=self.config['central']['assignments'][robot]
            state.update(blockers=blockers,rmf_registered=self.rmf_traffic.registered(robot),dispatch_enabled=not blockers,
                         robot_id=assignment['robot_name'],connection_id=robot,
                         assigned_robot_name=assignment['robot_name'],assigned_namespace=assignment['namespace'])
        return snapshots

    def control_cycle(self):
        snapshots=self.snapshots()
        for robot,value in snapshots.items():
            if value['transport_connected']:
                if robot not in self.initialized_clients:
                    if not self.send_command('disarm','central-start-'+self.session_id,robot_id=robot):continue
                    self.initialized_clients.add(robot)
                self.send_command('ping','central-heartbeat',robot_id=robot)
        while not self.ui.inbox.empty():
            command=self.ui.inbox.get();identifier=command['id']
            if identifier in self.ui_results:continue
            try:
                command=self.identities.command(command)
                if command['op']=='align_maps':
                    self.start_registration('manual');result={'phase':'registering'}
                elif command['op']=='robot_reassign':
                    result=self.reassign_identity(command,snapshots)
                elif command['op']=='robot_rename':
                    result=self.display_names.rename(command.get('robot_id'),command.get('name'))
                elif command['op'].startswith('web_'):
                    result=self.operator.web_command(command,snapshots)
                elif command['op']=='execution_permission':
                    result=self.set_execution_permission(command,snapshots)
                elif command['op'] in ('nav_parameters_read','nav_parameters_save'):
                    result=self.permanent_parameters.request(command,snapshots)
                elif command['op']=='route_update':
                    result=self.operator.update_waypoint(command,snapshots)
                elif command['op']=='routes_start':
                    result=self.operator.start_routes(command,snapshots)
                elif command['op'] == 'rmf_submit_task':
                    from .missions import points
                    submitted = {'op':'route_start','id':identifier,'shared_points':points(command['points']),'kind':command.get('kind','single')}
                    result = self.rmf_dispatch.submit(submitted, snapshots)
                elif command['op'] in ('route_clear','routes_clear'):
                    result=self.missions.command(command,snapshots);self.operator.receipt=None
                elif command['op']=='routes_stop':
                    self.missions.goal_dispatch.stop('操作者停止全部导航')
                    self.rmf_dispatch.cancel_pending(routes_only=True)
                    for robot,job in self.missions.jobs.items():
                        if job['source'] in ('route','single'):self.missions.stop(robot,'操作者停止全部航点导航')
                    result={'phase':'accepted','message':'已请求停止全部车辆的航点导航'}
                else:
                    if command['op'] == 'shared_costmap_configure':
                        self.ui_results[identifier] = self.maps.shared_costmap.configure(command)
                        continue
                    if command['op'] in ('dispatch_goal','follow_start','formation_start','route_start'):
                        if self.operator.stopped:raise ValueError('调度操控处于停止状态，请先释放操控面板的停止按钮')
                        targets=command.get('order',[]) if command['op'] in ('follow_start','formation_start') else ([command['robot_id']] if 'robot_id' in command else [])
                        if command.get('target')=='formation':targets=self.missions.formation.saved['order']
                        requested,observed,enabled=self.execution_permissions(snapshots)
                        if any(requested.get(r) and not enabled.get(r) for r in targets):
                            raise ValueError('执行许可尚未收到接入端确认，请稍后再开始任务')
                    result=self.missions.command(command,snapshots)
                self.ui_results[identifier]=result
            except (ValueError,RuntimeError,TypeError) as error:
                self.ui_results[identifier]={'phase':'rejected','message':str(error)}
        self.maps.transforms(snapshots)
        members=registration_members(snapshots,self.maps.names,self.maps.reference,self.maps.valid_robots)
        if self.auto_registration.due(snapshots,members,not members,
                self.registration is not None and self.registration.poll() is None,time.monotonic()):
            self.get_logger().info('Both vehicles stationary and ready; validating current map sessions')
            self.start_registration('automatic_session_recovery',members)
        self.plans.tick(snapshots)
        self.permanent_parameters.tick(snapshots,self.ui_results)
        for state in snapshots.values():
            self.ui_results.update(state.get('samples',{}).get('web_replies',{}).get('value',{}))
        self.rmf_traffic.tick(snapshots)
        self.missions.tick(snapshots)
        self.rmf_dispatch.tick(snapshots)
        while len(self.ui_results)>128:self.ui_results.pop(next(iter(self.ui_results)))
        registration=self.data/'registration-job.json'
        mission_state=self.missions.snapshot()
        requested,observed,enabled=self.execution_permissions(snapshots)
        self.ui.state={'ready':True,'discovery':getattr(self,'discovery_status',{}),'robots':self.decorated_states(),'maps':self.maps.state,
                       'missions':mission_state,'commands':{**self.ui_results,**mission_state['prechecks']},
                       'rmf':{'dispatch':self.rmf_dispatch.snapshot(),'traffic':self.rmf_traffic.snapshot()},
                       'navigation_parameter_fields':FIELDS,
                       'assignments':self.config['central']['assignments'],'execution_enabled':enabled,
                       'execution_requested':requested,'execution_observed':observed,
                       'robot_names':self.display_names.snapshot(),
                       'identity_revision':self.identities.revision,
                       'operator':self.operator.receipt,
                       'operator_stopped':self.operator.stopped,
                       'motion_enabled':any(enabled.values()),
                       'rmf_schedule_connected':bool(self.schedule_response) and time.monotonic()-self.schedule_response<=15.,
                       'registration':json.loads(registration.read_text()) if registration.exists() else None}

    def probe_schedule(self):
        # Humble's heartbeat publisher uses DDS liveliness, not message samples.
        names = [name for name, ns in self.get_node_names_and_namespaces()
                 if ns == '/' and name.startswith('rmf_traffic_schedule_node_')]
        if len(names) != 1:
            return
        service = '/' + names[0] + '/get_parameters'
        if service != self.schedule_service:
            if self.schedule_request is not None:
                self.schedule_request.cancel()
            if self.schedule_client is not None:
                self.destroy_client(self.schedule_client)
            self.schedule_client = self.create_client(GetParameters, service)
            self.schedule_service = service
        if self.schedule_request is not None and not self.schedule_request.done():
            self.schedule_request.cancel()
        if self.schedule_client.service_is_ready():
            self.schedule_request = self.schedule_client.call_async(GetParameters.Request(names=['use_sim_time']))
            self.schedule_request.add_done_callback(self.schedule_reply)

    def schedule_reply(self, future):
        if not future.cancelled() and future.result() is not None:
            self.schedule_response = time.monotonic()

    def receive(self):
        while True:
            try:
                payload = json.loads(self.ipc.recv(65536))
            except BlockingIOError:
                break
            profile = self.config['robots'].get(payload['robot_id'])
            if profile and profile['enabled'] and profile['domain_id'] == payload['domain_id'] and payload['schema'] == 1:
                self.states[payload['robot_id']] = payload

    def publish(self):
        now = time.monotonic()
        connections=self.decorated_states()
        report = {
            'schema': 1, 'wall_time_seconds': time.time(), 'mode': 'follow_and_waypoints',
            'central_domain_id': self.config['central']['domain_id'],
            'rmf_adapter_initialized': True,
            'rmf_adapter_connected': bool(self.schedule_response) and now - self.schedule_response <= 15.0,
            'schedule_rpc_age_seconds': now - self.schedule_response if self.schedule_response else None,
            'robots': {state['robot_id']:state for state in connections.values()},
        }
        for key,state in connections.items():
            self.robot_publishers[key].publish(String(data=json.dumps(state,allow_nan=False,ensure_ascii=False)))
        text = json.dumps(report, allow_nan=False, ensure_ascii=False)
        self.publisher.publish(String(data=text))
        temporary = self.data / 'connection_status.json.tmp'
        temporary.write_text(text + '\n')
        temporary.replace(self.data / 'connection_status.json')


def main():
    rmf_adapter.init_rclcpp()
    adapter = rmf_adapter.Adapter.make('omnifleet_rmf_adapter', wait_time=timedelta(seconds=10))
    if adapter is None:
        raise RuntimeError('RMF schedule not reachable in the central domain')
    adapter.start()
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = CentralObserver(adapter)
    def interrupted(signum,frame):raise KeyboardInterrupt
    signal.signal(signal.SIGINT,interrupted);signal.signal(signal.SIGTERM,interrupted)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.plans.close()
        node.missions.close()
        for robot in node.robot_ids:node.send_command('disarm','central-shutdown',robot_id=robot)
        node.map_executor.shutdown(wait=True,cancel_futures=True)
        node.ipc.close()
        node.command_ipc.close();node.ui.close()
        node.socket_path.unlink(missing_ok=True)
        node.lock.close()
        node.destroy_node()
        rclpy.try_shutdown()
        adapter.stop()


if __name__ == '__main__':
    main()
