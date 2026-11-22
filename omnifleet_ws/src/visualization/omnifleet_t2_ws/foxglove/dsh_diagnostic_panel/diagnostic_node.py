#!/usr/bin/env python3
"""Read-only ROS snapshots, answered by a restricted DSH headless profile."""
import importlib.util
import hashlib,os
from causal_evidence import collect_evidence,prepare_scope,RELEVANT
import json
import math
import re
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path as FilePath

from fleet_scope import frame
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from rclpy.time import Time
from std_msgs.msg import String
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid, Odometry, Path
from geometry_msgs.msg import Twist
from action_msgs.msg import GoalStatusArray
from rcl_interfaces.msg import Log
from rcl_interfaces.srv import GetParameters
from tf2_ros import Buffer, TransformListener, TransformException
from dsh_runner import ask_dsh, DiagnosticTimeout, MODEL_TIMEOUT_SECONDS
from snapshot_fallback import build_fallback
from parameter_guidance import build_parameter_details
from model_catalog import DEFAULT_MODEL, fetch_catalog, load_catalog, save_catalog

ROOT = FilePath('/home/iecme/omnifleet_a2_ws/src/visualization/omnifleet_t2_ws/foxglove/nav2_permanent_panel')
import sys

def timeout_completion(snapshot,error,timings):
    """Build the terminal message used when the model deadline is exceeded."""
    code=getattr(error,'code','model_timeout')
    fallback,fields=build_fallback(snapshot,timings.get('model_elapsed_seconds',120),code)
    updated=dict(timings);updated['fallback']='snapshot_only'
    return {'status':'complete','answer':fallback,**fields,
            'captured_at':snapshot.get('captured_at_unix',time.time()),
            'parameter_labels':{},'timings':updated}
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('parameter_store', ROOT/'nav2_parameter_store.py')
parameter_store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parameter_store)
QUESTION = '/omnifleet_t2/diagnostics/question'
ANSWER = '/omnifleet_t2/diagnostics/answer'
MODELS = '/omnifleet_t2/diagnostics/models'


def stamp(header):
    return header.stamp.sec + header.stamp.nanosec / 1e9


def grid_summary(msg):
    cells = msg.data
    result = {'frame':msg.header.frame_id, 'stamp':stamp(msg.header),
              'width':msg.info.width, 'height':msg.info.height, 'resolution':msg.info.resolution,
              'origin':{'x':msg.info.origin.position.x,'y':msg.info.origin.position.y},
              'cells':len(cells), 'unknown':sum(v<0 for v in cells),
              'free':sum(v==0 for v in cells), 'occupied_100':sum(v==100 for v in cells),
              'intermediate_cost':sum(0<v<100 for v in cells)}
    if msg.info.width and msg.info.height:
        step = max(1, math.ceil(max(msg.info.width/32, msg.info.height/20)))
        lines = []
        for y in range(msg.info.height-1,-1,-step):
            line = ''
            for x in range(0,msg.info.width,step):
                block=[cells[yy*msg.info.width+xx] for yy in range(max(0,y-step+1),y+1) for xx in range(x,min(x+step,msg.info.width))]
                line += '#' if any(v==100 for v in block) else '+' if any(v>0 for v in block) else '.' if any(v==0 for v in block) else '?'
            lines.append(line)
        result['coarse_map']={'legend':'# occupied=100, + intermediate cost, . free, ? unknown; coarse blocks, not exact geometry', 'rows':lines}
    return result


class Diagnostics(Node):
    def __init__(self):
        super().__init__('omnifleet_t2_dsh_diagnostics')
        self.group = ReentrantCallbackGroup()
        self.lock = threading.Lock()
        self.samples, self.logs, self.seen = {}, deque(maxlen=20), deque(maxlen=50)
        self.reply_cache = {}
        self.robot_id=os.environ['OMNIFLEET_ROBOT_ID']
        self.causal_events=deque(maxlen=240);self.latest_local_status={};self.last_local_signature=None
        self.fleet_sample=None
        self.motion_history={t:deque(maxlen=500) for t in ('/odom','/lidar_odometry/pose','/cmd_vel','/navigation/nav_cmd_vel','/navigation/cmd_vel_safe','/motor_command_sent')}
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.active = None
        self.model_catalog = load_catalog()
        self.model_catalog_error = ''
        self.tf = None
        self.parameter_clients = {}
        latched = QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        sensor = QoSProfile(depth=1,reliability=ReliabilityPolicy.BEST_EFFORT)
        self.output = self.create_publisher(String,ANSWER,latched)
        self.model_output = None
        self.create_subscription(String,QUESTION,self.on_question,10)
        topics=[('/rslidar_points',PointCloud2,sensor),('/map',OccupancyGrid,latched),
                ('/local_costmap/costmap',OccupancyGrid,latched),('/global_costmap/costmap',OccupancyGrid,latched),
                ('/odom',Odometry,sensor),('/lidar_odometry/pose',Odometry,sensor),
                ('/fleet/map',OccupancyGrid,latched),
                ('/cmd_vel',Twist,sensor),('/navigation/nav_cmd_vel',Twist,sensor),('/navigation/cmd_vel_safe',Twist,sensor),('/motor_command_sent',Twist,sensor),('/plan',Path,sensor),('/local_plan',Path,sensor),
                ('/planner_selector',String,latched),('/controller_selector',String,latched),
                ('/navigate_to_pose/_action/status',GoalStatusArray,latched),
                ('/navigate_through_poses/_action/status',GoalStatusArray,latched)]
        self.topic_specs = topics
        self.expected_topics=[x[0] for x in topics]
        self.params={}
        for key,s in parameter_store.SPECS.items():
            self.params.setdefault(s[2],{}).update({s[3]+leaf:key for leaf in s[1]})
        self.params['/controller_server']['controller_frequency']='controller_frequency'
        self.params['/controller_server'].update({k:k for k in ('progress_checker.required_movement_radius','progress_checker.movement_time_allowance')})
        self.params['/controller_server']['FollowPathRPP.use_velocity_scaled_lookahead_dist']='rpp_velocity_scaled_enabled'
        # Read critic activation conditions as well as the exposed weight.
        self.params['/controller_server'].update({k:k for k in (
            'FollowPathMPPI.PathAngleCritic.enabled',
            'FollowPathMPPI.PathAngleCritic.max_angle_to_furthest',
            'FollowPathMPPI.PathAngleCritic.threshold_to_consider',
            'FollowPathMPPI.PathAngleCritic.offset_from_furthest',
            'FollowPathMPPI.PathAngleCritic.forward_preference',
            'FollowPath.PathAlign.forward_point_distance',
        )})
        self.params['/planner_server']['GridBased.downsampling_factor']='planner_downsampling_factor'
        for name in ('/local_costmap/local_costmap','/global_costmap/global_costmap'):
            self.params[name].update({k:k for k in ('global_frame','footprint','resolution','update_frequency','publish_frequency','inflation_layer.enabled')})
        self.model_catalog_timer = self.create_timer(300.0, self.refresh_model_catalog)
        self.refresh_model_catalog()

    def on_local_status(self,message):
        try:data=json.loads(message.data)
        except ValueError:return
        signature=tuple(data.get(k) for k in ('run_id','phase','message'))
        with self.lock:
            self.latest_local_status=data
            if self.last_local_signature is not None and signature!=self.last_local_signature:
                self.causal_events.append({'time':time.time(),'source':'local navigation status',
                    'task_id':data.get('task_id'),'run_id':data.get('run_id'),'phase':data.get('phase'),
                    'tf_age_ms':data.get('tf_age_ms'),'message':str(data.get('message',''))[:850]})
            self.last_local_signature=signature

    def on_sample(self,topic,msg):
        with self.lock:
            now=time.monotonic();self.samples[topic]=(now,msg)
            if topic in self.motion_history:
                if isinstance(msg,Odometry):
                    p=msg.pose.pose.position
                    self.motion_history[topic].append((now,p.x,p.y,msg.twist.twist.linear.x,msg.twist.twist.angular.z))
                else:self.motion_history[topic].append((now,0.,0.,msg.linear.x,msg.angular.z))

    def on_log(self,msg):
        if any(v in msg.name for v in ('local_navigation','navigation_policy')) and RELEVANT.search(msg.msg):
            with self.lock:self.causal_events.append({'time':msg.stamp.sec+msg.stamp.nanosec*1e-9,
                'source':msg.name,'message':msg.msg[:850]})
        if msg.level>=30 and any(s in msg.name for s in ('costmap','controller','planner','navigator','mola')):
            entry={'time':time.time(),'node':msg.name,'level':msg.level,'message':msg.msg[:600]}
            with self.lock:
                for old in list(self.logs):
                    if old['node']==entry['node'] and old['message']==entry['message']:self.logs.remove(old)
                self.logs.append(entry)

    def reply(self,request_id,status,**extra):
        payload = json.dumps({'request_id':request_id,'status':status,**extra},ensure_ascii=False,allow_nan=False)
        with self.lock:
            self.reply_cache[request_id] = payload
            while len(self.reply_cache) > 50:
                self.reply_cache.pop(next(iter(self.reply_cache)))
        self.output.publish(String(data=payload))

    def on_fleet(self,msg):
        try:
            data=json.loads(msg.data)
            with self.lock:self.fleet_sample=(time.monotonic(),data)
        except ValueError:pass

    def refresh_model_catalog(self):
        try:
            catalog = fetch_catalog(timeout=20)
            save_catalog(catalog)
            with self.lock:
                self.model_catalog = catalog
                self.model_catalog_error = ''
        except Exception as error:
            with self.lock:
                self.model_catalog_error = str(error)[:240]
        self.publish_model_catalog()

    def publish_model_catalog(self):
        if self.model_output is None:
            latched = QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
            self.model_output = self.create_publisher(String,MODELS,latched)
        with self.lock:
            packet={**self.model_catalog,'error':self.model_catalog_error}
        self.model_output.publish(String(data=json.dumps(packet,ensure_ascii=False)))

    def on_question(self,msg):
        try:
            request=json.loads(msg.data)
            request_id=request['request_id']; question=request['question'].strip()
            if not isinstance(request_id,str) or not 1<=len(request_id)<=80 or not 1<=len(question)<=4000:raise ValueError('问题长度无效')
        except (ValueError,KeyError,TypeError,AttributeError):return
        engine=request.get('engine','dsh')
        if engine not in ('dsh','phyagentos'):
            self.reply(request_id,'error',answer='不支持的诊断引擎',error_code='invalid_engine');return
        with self.lock:
            available=list(self.model_catalog.get('models',[]));default_model=self.model_catalog.get('default_model',DEFAULT_MODEL)
        model=request.get('model',default_model)
        if not isinstance(model,str) or model not in available:
            self.reply(request_id,'error',answer='所选模型不在当前API文本模型列表中',error_code='invalid_model',available_models=available);return
        if request_id in self.seen:
            with self.lock: cached = self.reply_cache.get(request_id)
            if cached is not None: self.output.publish(String(data=cached))
            return
        self.seen.append(request_id)
        if self.active is not None and not self.active.done():
            self.reply(request_id,'error',answer='已有诊断正在进行，请稍后再试。');return
        # The model list is advertised only as part of an explicit user query.
        self.publish_model_catalog()
        self.get_logger().info(f'诊断请求已接收 {request_id} question_chars={len(question)} model={model}')
        self.reply(request_id,'collecting',engine=engine,model=model,answer='正在读取当前话题、地图、参数和错误日志……')
        self.active=self.pool.submit(self.diagnose,request_id,question,request.get('foxglove',{}),request.get('reported_error'),engine,model)

    def collect(self,foxglove):
        # No sensor, TF, rosout, fleet or parameter reads happen while idle.
        # They exist only for this explicit request and are torn down before the
        # model call starts.
        with self.lock:
            self.samples.clear(); self.logs.clear(); self.causal_events.clear()
            self.latest_local_status={}; self.last_local_signature=None; self.fleet_sample=None
            for values in self.motion_history.values(): values.clear()
        live_subscriptions=[]
        live_tf=None
        live_tf_listener=None
        try:
            for topic,kind,qos in self.topic_specs:
                live_subscriptions.append(self.create_subscription(kind,topic,lambda m,t=topic:self.on_sample(t,m),qos))
            live_subscriptions.append(self.create_subscription(String,'/'+self.robot_id+'/navigation/status',self.on_local_status,10))
            live_subscriptions.append(self.create_subscription(String,'/fleet/status',self.on_fleet,10))
            live_subscriptions.append(self.create_subscription(Log,'/rosout',self.on_log,30))
            live_tf=Buffer()
            live_tf_listener=TransformListener(live_tf,self)
            self.tf=live_tf
            time.sleep(3)
            with self.lock:samples=dict(self.samples);logs=list(self.logs);history={k:list(v) for k,v in self.motion_history.items()}
            with self.lock:fleet=self.fleet_sample
            transforms={}
            for target,source in [('map','base_link'),('base_link','rslidar')]:
                try:
                    t=live_tf.lookup_transform(frame(target),frame(source),Time());v=t.transform.translation
                    transforms[target+'<-'+source]={'stamp':stamp(t.header),'translation':{'x':v.x,'y':v.y,'z':v.z}}
                except TransformException as e:transforms[target+'<-'+source]={'error':str(e)[:300]}
        finally:
            for subscription in live_subscriptions:
                self.destroy_subscription(subscription)
            live_tf_listener=None
            self.tf=None
            for client in self.parameter_clients.values():
                self.destroy_client(client)
            self.parameter_clients={}
        now=time.monotonic()
        data={'captured_at_unix':time.time(),'host':'113','read_only':True,'observations':{},
              'missing_samples':[t for t in self.expected_topics if t not in samples],
              'recent_errors':[e for e in logs if time.time()-e['time']<120],
              'visible_topics':[t for t,_ in self.get_topic_names_and_types()][:200],
              'foxglove':{'topic_names':foxglove.get('topic_names',[])[:200]} if isinstance(foxglove,dict) else {}}
        if any(t=='/navigation/cmd_vel_safe' for t,_ in self.get_topic_names_and_types()):
            data['velocity_topic_roles']={'/cmd_vel':'manual input', '/navigation/nav_cmd_vel':'Nav2 requested velocity before safety gate', '/navigation/cmd_vel_safe':'command after safety gate', '/motor_command_sent':'driver transmitted command, not measured wheel velocity', '/odom':'measured chassis velocity'}
        data['motion_window']={}
        data['parameter_owner']=self.robot_id
        data['interface_capabilities']={'parameter_panel_robot':self.robot_id,'fleet_control_panel_installed':True,
            'robot_104_parameter_panel_installed':self.robot_id=='robot_104'}
        data['observation_semantics']={
            'selected_algorithms_empty':'No selector message observed; this does not mean no algorithm is configured. BT defaults may apply.',
            'shared_map_source_age':'Time since last observed map message, not a configured update period; do not invent a normal fixed period.',
            'poses':'Latest asynchronous poses; distance alone does not prove side-by-side placement or physical scene details.'}
        if fleet:
            received,state=fleet
            data['fleet']={k:state.get(k) for k in ('mission_state','motion_enabled','failure_reason','frame_id','shared_map','current_robot_distance')}
            data['fleet']['age']=now-received
            data['fleet']['robots']={robot:{k:s.get(k) for k in ('online','health','local_pose','fleet_pose','pose_age','velocity','velocity_age',
                'nav_ready','control_mode','goal_error','shared_map','shared_map_ready','selected_algorithms','runtime_parameters')}
                for robot,s in state.get('robots',{}).items()}
        for topic,values in history.items():
            values=[v for v in values if now-v[0]<=10]
            if len(values)<2:continue
            first,last=values[0],values[-1]
            item={'samples':len(values),'duration_seconds':round(last[0]-first[0],3),
                  'mean_abs_vx':sum(abs(v[3]) for v in values)/len(values),
                  'mean_abs_wz':sum(abs(v[4]) for v in values)/len(values),
                  'window_ended_at_unix':data['captured_at_unix']-(now-last[0])}
            if topic in ('/odom','/lidar_odometry/pose'):
                item['net_displacement_m']=math.hypot(last[1]-first[1],last[2]-first[2])
                item['max_distance_from_first_sample_m']=max(math.hypot(v[1]-first[1],v[2]-first[2]) for v in values)
            data['motion_window'][topic]=item
        for topic,(received,msg) in samples.items():
            item={'received_seconds_ago':round(now-received,3)}
            if isinstance(msg,OccupancyGrid):item.update(grid_summary(msg))
            elif isinstance(msg,PointCloud2):item.update(frame=msg.header.frame_id,stamp=stamp(msg.header),points=msg.width*msg.height)
            elif isinstance(msg,Odometry):
                pos=msg.pose.pose.position;ori=msg.pose.pose.orientation
                item.update(frame=msg.header.frame_id,stamp=stamp(msg.header),position={'x':pos.x,'y':pos.y,'z':pos.z},orientation={'x':ori.x,'y':ori.y,'z':ori.z,'w':ori.w},vx=msg.twist.twist.linear.x,wz=msg.twist.twist.angular.z)
            elif isinstance(msg,Twist):item.update(vx=msg.linear.x,wz=msg.angular.z)
            elif isinstance(msg,Path):
                item.update(frame=msg.header.frame_id,stamp=stamp(msg.header),poses=len(msg.poses))
                if msg.poses:item['goal']={'x':msg.poses[-1].pose.position.x,'y':msg.poses[-1].pose.position.y}
            elif isinstance(msg,String):item['value']=msg.data[:200]
            elif isinstance(msg,GoalStatusArray):item['goal_statuses']=[s.status for s in msg.status_list][-12:]
            data['observations'][topic]=item
        data['transforms']=transforms
        data['saved_parameters']=parameter_store.saved_values()
        data['saved_algorithms']=parameter_store.selected_algorithms()
        panel_source=(ROOT/'Nav2PermanentPanel.js').read_text()
        data['parameter_catalog']={m[0]:m[1] for m in re.findall(r"^\s*\[[\"']([^\"']+)[\"'],\s*[\"']([^\"']+)[\"']",panel_source,re.M)}
        data['parameter_catalog'].update(local_controller_algorithm='局部路径规划算法', global_planner_algorithm='全局路径规划算法')
        escape=lambda s:s.replace('~','~0').replace('/','~1')
        data['parameter_evidence_paths']={key:[f'/live_parameters/{escape(s[2])}/{escape(s[3]+leaf)}' for leaf in s[1]] for key,s in parameter_store.SPECS.items()}
        data['parameter_evidence_paths']['costmap_radius'] = (
            data['parameter_evidence_paths']['local_radius'] +
            data['parameter_evidence_paths']['global_radius'])
        data['parameter_evidence_paths']['costmap_scaling'] = (
            data['parameter_evidence_paths']['local_scaling'] +
            data['parameter_evidence_paths']['global_scaling'])
        data['parameter_evidence_paths']['costmap_padding'] = (
            data['parameter_evidence_paths']['local_padding'] +
            data['parameter_evidence_paths']['global_padding'])
        for key,leaf in parameter_store.HEIGHT_KEYS.items():
            data['parameter_evidence_paths'][key]=[f'/saved_parameters/{key}/{leaf}']
        for key, kind, topic in [('local_controller_algorithm','local','/controller_selector'), ('global_planner_algorithm','global','/planner_selector')]:
            data['parameter_evidence_paths'][key] = [f'/saved_algorithms/{kind}']
            if topic in data['observations'] and 'value' in data['observations'][topic]:
                data['parameter_evidence_paths'][key].append(f'/observations/{escape(topic)}/value')
        futures={}
        parameter_clients={name:self.create_client(GetParameters,name+'/get_parameters',callback_group=self.group) for name in self.params}
        self.parameter_clients=parameter_clients
        deadline=time.monotonic()+4
        while time.monotonic()<deadline:
            for name,client in parameter_clients.items():
                if name not in futures and client.service_is_ready():
                    futures[name]=client.call_async(GetParameters.Request(names=list(self.params[name])))
            if len(futures)==len(parameter_clients) and all(f.done() for f in futures.values()):break
            time.sleep(.05)
        data['live_parameters']={}
        for name,keys in self.params.items():
            f=futures.get(name)
            if f is None or not f.done():
                data['live_parameters'][name]={'error':'运行时参数服务未响应'}
                if f is not None:parameter_clients[name].remove_pending_request(f)
                continue
            vals=f.result().values
            data['live_parameters'][name]={k:v.bool_value if v.type==1 else v.integer_value if v.type==2 else v.double_value if v.type==3 else v.string_value if v.type==4 else None for k,v in zip(keys,vals)}
        data['parameter_details']=build_parameter_details(panel_source,data,parameter_store.SPECS,parameter_store.ALGORITHMS)
        data['parameter_semantics']={
            'FollowPathMPPI.PathAngleCritic': {
                'source':'Nav2 Humble path_angle_critic.cpp score()',
                'activation':'enabled为true；离路径终点超过threshold_to_consider；与路径参考点的角差达到max_angle_to_furthest才参与评分。',
                'reference_point':'offset_from_furthest是路径参考点的索引偏移，不是距离阈值。',
                'limit':'评分权重只影响轨迹偏好，不保证未对齐时线速度为零。',
            },
        }
        for client in parameter_clients.values():
            self.destroy_client(client)
        self.parameter_clients={}
        return data

    def diagnose(self,request_id,question,foxglove,reported_error=None,engine='dsh',model=DEFAULT_MODEL):
        label='DSH' if engine=='dsh' else 'PhyAgentOS'
        def send(status,**fields):self.reply(request_id,status,engine=engine,model=model,**fields)
        started=time.monotonic(); timings={}
        try:
            snapshot=self.collect(foxglove)
            with self.lock:
                events=list(self.causal_events);local_status=dict(self.latest_local_status)
            snapshot['local_navigation']=local_status
            snapshot['localization_architecture']=os.environ.get('OMNIFLEET_ARCHITECTURE','unknown')
            snapshot['causal_evidence']=collect_evidence(self.robot_id,events)
            snapshot=prepare_scope(question,snapshot)
            evidence_dir=FilePath.home()/'.local/share/omnifleet_t2/diagnostic-evidence'
            evidence_dir.mkdir(parents=True,exist_ok=True)
            evidence_id=hashlib.sha256(request_id.encode()).hexdigest()[:20]
            (evidence_dir/(evidence_id+'.json')).write_text(json.dumps({'request_id':request_id,'question':question,'snapshot':snapshot},ensure_ascii=False))
            timings['collection_seconds']=round(time.monotonic()-started,3)
            self.get_logger().info(f'诊断采集完成 {request_id} seconds={timings["collection_seconds"]}')
            if isinstance(reported_error,dict):
                timestamp=reported_error.get('stamp')
                snapshot['reported_error']={'node':str(reported_error.get('node',''))[:200],
                    'message':str(reported_error.get('message',''))[:1500],
                    'stamp':timestamp if isinstance(timestamp,(int,float)) and math.isfinite(timestamp) else None}
            def progress(stage,model_timings):
                timings.update(model_timings)
                text={'request_start':'正在连接模型，等待接口响应……','response_headers':'模型接口已响应，等待开始生成……','first_model_token':'模型正在生成诊断结果……','model_stream_end':'模型生成结束，正在整理诊断结果……','request_error':'模型连接未成功，正在等待处理结果……'}.get(stage,label+' 正在分析任务、规划、定位和取消的事件链……')
                if stage=='first_reasoning_token':text='模型已连接，正在推理，尚未输出答案……'
                if stage=='model_progress':
                    event=model_timings.get('model_events',[{}])[-1]
                    text='正在输出诊断答案……' if event.get('answer_chars',0)>0 else '模型仍在推理，尚未输出答案……'
                send('thinking',stage=stage,answer=text,timings=dict(timings))
                self.get_logger().info(f'诊断阶段 {request_id} stage={stage} timings='+json.dumps(timings,ensure_ascii=False))
            send('thinking',stage='model_startup',answer='采集完成，正在启动 '+label+'……',timings=dict(timings))
            answer=ask_dsh(question,snapshot,timeout=MODEL_TIMEOUT_SECONDS,on_progress=progress,engine=engine,model=model)
            timings.update(answer.pop('timings',{}));timings['total_seconds']=round(time.monotonic()-started,3)
            (evidence_dir/(evidence_id+'-answer.json')).write_text(json.dumps(answer,ensure_ascii=False))
            send('complete',**answer,captured_at=snapshot['captured_at_unix'],
                       parameter_labels={k:snapshot['parameter_catalog'][k] for k in answer['parameter_ids']},timings=dict(timings))
            self.get_logger().info('诊断完成 '+request_id+' timings='+json.dumps(timings,ensure_ascii=False))
        except Exception as error:
            timings.update(getattr(error,'timings',{}));timings['total_seconds']=round(time.monotonic()-started,3)
            code=getattr(error,'code','diagnostic_error')
            if isinstance(error,DiagnosticTimeout):
                terminal=timeout_completion(snapshot,error,timings)
                send(**terminal)
                timings.update(terminal['timings'])
                self.get_logger().warning(f'诊断模型超时，已返回快照兜底 {request_id} code={code} timings='+json.dumps(timings,ensure_ascii=False))
                return
            send('error',answer='诊断未完成：'+str(error)[:400],error_code=code,timings=dict(timings))
            self.get_logger().warning(f'诊断失败 {request_id} code={code} timings='+json.dumps(timings,ensure_ascii=False))


def main():
    rclpy.init();node=Diagnostics();executor=MultiThreadedExecutor(num_threads=3);executor.add_node(node)
    try:
        # Bound the middleware wait so a missed wake-up cannot stall requests indefinitely.
        while rclpy.ok():
            executor.spin_once(timeout_sec=0.1)
    except KeyboardInterrupt:pass
    finally:node.pool.shutdown(wait=False,cancel_futures=True);executor.shutdown();node.destroy_node();rclpy.try_shutdown()

if __name__=='__main__':main()
