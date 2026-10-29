"""A virtual formation goal, with joint planning and elastic local tracking."""
import copy
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from ament_index_python.packages import get_package_prefix

from .map_hub import compose, inverse
from .elastic_trajectory import estimate_frame,plan_joint,path_samples,wrap,transform
from .formation_scene import scene


TERMINAL = ('STOPPED','COMPLETED','FAILED','INVALIDATED')


class Formation:
    def __init__(self, missions):
        self.owner=missions
        self.path=missions.file.parent/'formation.json'
        self.saved=json.loads(self.path.read_text()) if self.path.exists() else None
        self.active=False;self.phase='SAVED' if self.saved else 'UNSAVED'
        self.message='';self.bindings={};self.targets={};self.errors={};self.angle_errors={}
        self.route_path=missions.file.parent/'formation-route.json'
        self.route=json.loads(self.route_path.read_text()) if self.route_path.exists() else {'points':[],'revision':0}
        self.queue=[];self.completed=0;self.goal=None;self.frame=None
        self.trajectory=None;self.elapsed=0.;self.last_tick=time.monotonic();self.rate=0.
        self.worker=ThreadPoolExecutor(max_workers=1,thread_name_prefix='formation-plan')
        self.future=None;self.plan_number=0;self.negotiated=False;self.arrived=False
        self.path_wait_since=None
        # Convert existing leader-relative offsets in memory; the original file
        # remains untouched until the operator explicitly captures a new shape.
        if self.saved and self.saved.get('schema',1)==1:
            center=[sum(self.saved['offsets'][r][k] for r in self.saved['order'])/len(self.saved['order']) for k in (0,1)]
            self.saved={**self.saved,'schema':2,'reference':'centroid','offsets':
                {r:[p[0]-center[0],p[1]-center[1],p[2]] for r,p in self.saved['offsets'].items()}}

    def close(self):self.worker.shutdown(wait=False,cancel_futures=True)

    @staticmethod
    def manual_active(control):
        return control.get('manual_active') and control.get('manual_command_age',0)<=.5

    def pose(self, robot, states):
        state=states.get(robot,{})
        sample=state.get('samples',{}).get('pose',{})
        if not state.get('fresh',{}).get('pose') or (not self.active and sample.get('age_seconds',0)+state.get('ipc_age_seconds',0)>.5):
            raise ValueError('车辆定位不新鲜：'+robot)
        p=sample.get('value',{})
        values=[p.get(k) for k in ('x','y','yaw')]
        if not all(type(v) in (int,float) and math.isfinite(v) for v in values):
            raise ValueError('车辆定位无效：'+robot)
        return compose(self.owner.maps.alignment[robot],values)

    def binding(self, robot, states):
        return [self.owner.nav(states[robot]).get('localization_epoch'),list(self.owner.maps.alignment[robot])]

    def validate(self, order, states):
        if not isinstance(order,list) or len(order)<2 or len(set(order))!=len(order) or any(r not in self.owner.maps.names for r in order):
            raise ValueError('编队需要至少两辆不同的已接入车辆')
        for robot in order:
            if not self.owner.ready(robot,states):raise ValueError('编队车辆地图或导航未就绪：'+robot)
            self.pose(robot,states)

    def capture(self, order, states, clear_route=True):
        if self.active or self.owner.follow['active']:raise ValueError('请先停止当前编队或跟随，再保存队形')
        self.validate(order,states)
        for robot in order:
            if (not self.owner.stopped(states[robot]) or self.manual_active(self.owner.control(states[robot]))
                    or self.owner.nav(states[robot]).get('navigation_active')
                    or self.owner.jobs.get(robot,{}).get('phase','STOPPED') not in TERMINAL):
                raise ValueError('请先结束各车操作并停稳，再保持队形')
        poses=[self.pose(r,states) for r in order]
        center=[sum(p[k] for p in poses)/len(poses) for k in (0,1)]+[poses[0][2]]
        offsets={robot:compose(inverse(center),self.pose(robot,states)) for robot in order}
        for offset in offsets.values():offset[2]=math.atan2(math.sin(offset[2]),math.cos(offset[2]))
        saved={'schema':2,'reference':'centroid','leader':order[0],'order':list(order),'offsets':offsets,'captured_at':time.time()}
        temporary=self.path.with_suffix('.tmp');temporary.write_text(json.dumps(saved,ensure_ascii=False,indent=2));temporary.replace(self.path)
        self.saved=saved;self.phase='SAVED';self.message='已保存各车相对队形中心的位置与朝向；尚未开始运动'
        self.frame=center
        if clear_route:self.save_route([])
        self.targets={};self.errors={};self.angle_errors={}
        return {'phase':'saved','message':self.message}

    def save_route(self, values):
        self.route={'points':copy.deepcopy(values),'revision':self.route['revision']+1}
        temporary=self.route_path.with_suffix('.tmp');temporary.write_text(json.dumps(self.route,ensure_ascii=False,indent=2));temporary.replace(self.route_path)

    def command(self, request, states):
        from .missions import points
        op=request['op']
        if not self.saved:raise ValueError('请先保存当前位置队形')
        if op in ('route_save','route_add','route_update'):
            if op=='route_add':values=points(self.route['points']+[request['point']])
            elif op=='route_save':values=points(request['points']) if request.get('points') else []
            else:
                if request.get('route_revision')!=self.route['revision']:raise ValueError('队形航点队列已变化，请重新拖动')
                index=request.get('index');position=request.get('position')
                if type(index) is not int or not 1<=index<=len(self.route['points']):raise ValueError('航点编号无效')
                if not isinstance(position,list) or len(position)!=2:raise ValueError('航点坐标无效')
                values=copy.deepcopy(self.route['points']);values[index-1]['pose'][:2]=position;values=points(values)
            self.save_route(values)
            return {'phase':'saved','message':'队形中心航点已保存，尚未发车','revision':self.route['revision']}
        if op in ('route_stop','route_clear'):
            result=self.stop('停止队形导航')
            if op=='route_clear':self.save_route([])
            return result
        if op not in ('single_goal','route_start'):raise ValueError('队形不支持此航点操作')
        if not self.active:raise ValueError('请先开始编队，再执行队形航点')
        values=points([request['point']]) if op=='single_goal' else points(self.route['points'])
        self.owner.motion_allowed(self.saved['order'])
        self.queue=copy.deepcopy(values);self.completed=0
        self.begin_plan(self.queue[0]['pose'],states)
        return {'phase':'accepted','message':'已向队形中心提交目标，全体成员共同规划'}

    def profiles(self, states):
        result=[]
        for robot in self.saved['order']:
            sample=states[robot].get('samples',{}).get('formation_profile',{})
            value=sample.get('value')
            if not value:raise ValueError('尚未读到本车控制器速度与碰撞轮廓参数：'+robot)
            result.append(copy.deepcopy(value))
        return result

    def begin_plan(self, goal, states):
        order=self.saved['order'];starts=[self.pose(r,states) for r in order]
        offsets=[self.saved['offsets'][r] for r in order]
        profiles=self.profiles(states)
        frame=estimate_frame(starts,offsets,(self.frame or starts[0])[2])
        world=scene(self.owner.maps,states,order,profiles,starts)
        binary=Path(get_package_prefix('omnifleet_formation_planner'))/'lib/omnifleet_formation_planner/joint_plan'
        if self.future:self.future.cancel()
        self.plan_number+=1;self.goal=list(goal);self.frame=frame
        self.trajectory=None;self.elapsed=0.;self.rate=0.;self.negotiated=False;self.arrived=False
        self.path_wait_since=None
        self.targets=dict(zip(order,starts));self.phase='PLANNING';self.message='正在联合规划各成员路径'
        # Planning is outside the ROS timer, so OMPL cannot starve lease renewals.
        self.future=self.worker.submit(plan_joint,binary,world,starts,offsets,frame,goal,profiles,order)

    def start(self, order, states, capture_current=False):
        if capture_current:
            self.validate(order,states);self.owner.motion_allowed(order)
            self.capture(order,states,clear_route=False)
        if not self.saved:raise ValueError('请先点击保持队形，保存当前相对关系')
        if order!=self.saved['order']:raise ValueError('成员顺序已改变，请重新保持队形')
        if self.active or self.owner.follow['active']:raise ValueError('请先停止当前编队或跟随')
        self.validate(order,states);self.owner.motion_allowed(order)
        if any(not self.owner.stopped(states[r]) or self.manual_active(self.owner.control(states[r]))
               or self.owner.nav(states[r]).get('navigation_active')
               or self.owner.jobs.get(r,{}).get('phase','STOPPED') not in TERMINAL for r in order):
            raise ValueError('参与车辆必须先结束独立任务和人工操作并停稳')
        starts=[self.pose(r,states) for r in order]
        frame=estimate_frame(starts,[self.saved['offsets'][r] for r in order],starts[0][2])
        self.begin_plan(frame,states)
        self.bindings={r:self.binding(r,states) for r in order};self.active=True
        self.queue=[];self.completed=0;self.last_tick=time.monotonic()
        for robot in order:
            previous=self.owner.jobs.get(robot,{})
            if previous.get('source')=='formation' and previous.get('phase') in TERMINAL:self.owner.jobs.pop(robot)
        return {'phase':'accepted','message':'编队已启动；航点发送给队形中心，允许临时绕障后归位'}

    def stop(self, reason='操作者停止编队', failed=False):
        if self.saved and self.owner.rmf_dispatch:
            for robot in self.saved['order']:self.owner.rmf_dispatch.cancel_pending(robot=robot)
        if self.active:
            for robot in self.saved['order']:self.owner.stop(robot,reason,'FAILED' if failed else 'STOPPED')
        if self.future:self.future.cancel();self.future=None
        self.active=False;self.phase='FAILED' if failed else 'STOPPED';self.message=reason;self.targets={}
        self.trajectory=None;self.queue=[];self.rate=0.
        return {'phase':'accepted','message':reason}

    def admit(self, robot):
        if self.active and robot in self.saved['order']:
            raise ValueError('当前为队形导航，请将航点发送给队形中心')

    def tick(self, states):
        if not self.active:return
        owner=self.owner;order=self.saved['order'];now=time.monotonic()
        dt=min(.2,max(0.,now-self.last_tick));self.last_tick=now
        try:
            if any(self.binding(r,states)!=self.bindings[r] for r in order):
                raise ValueError('编队地图或定位会话变化；停止后重新确认，不自动续跑')
            # Admission readiness is not a running-task health check. Nav2
            # briefly reports not-ready while resuming its retained action.
            for robot in order:
                if not owner.follow_ready(robot,states):raise ValueError('编队控制连接或定位失效：'+robot)
            poses=[self.pose(r,states) for r in order]
            for robot in order:
                job=owner.jobs.get(robot);control=owner.control(states[robot])
                if self.manual_active(control) or (job and job['phase']!='ARMING' and control.get('local_override')):
                    raise ValueError('编队成员人工或本地接管：'+robot)
                if job and job['source']=='formation' and job['phase'] in ('FAILED','INVALIDATED','CANCEL_UNCONFIRMED'):
                    raise ValueError(robot+'：'+job.get('message','编队跟踪失败'))
            if self.future and self.future.done():
                future=self.future;self.future=None;self.trajectory=future.result()
                (owner.file.parent/'formation-last-plan.json').write_text(json.dumps(self.trajectory.payload()))
                samples=path_samples(self.trajectory.phases,.08) or [poses]
                for i,robot in enumerate(order):
                    local=compose(inverse(owner.maps.alignment[robot]),self.targets[robot])
                    job=owner.jobs.get(robot)
                    if not job or job['phase'] in TERMINAL:
                        owner.enqueue(robot,[{'name':'队形中心联动目标','pose':local}],'formation',owner.nav(states[robot])['localization_epoch'])
                        job=owner.jobs[robot]
                    path=[p[i] for p in samples]
                    job.update(follow_points=[local],formation_plan=self.plan_number,path=path,reservation=path,path_index=0)
                    owner.preview_paths[robot]=path
                self.phase='FORMING';self.message='共同起步准备中'
            targets=[self.targets[r] for r in order];velocities=[[0.,0.] for _ in order]
            if self.trajectory:
                targets,_=self.trajectory.sample(self.elapsed)
                errors=[math.dist(a[:2],b[:2]) for a,b in zip(poses,targets)]
                heading_errors=[abs(wrap(a[2]-b[2])) for a,b in zip(poses,targets)]
                all_started=all(owner.jobs[r]['phase']=='EXECUTING' and
                    owner.client(states[r]).get('history',{}).get(owner.jobs[r]['request'],{}).get('phase') in ('executing','accepted') for r in order)
                traffic=owner.rmf_traffic
                if not self.negotiated:
                    self.negotiated=traffic.admit_formation(self.trajectory,order,self.plan_number,states) if traffic else True
                waiting=not self.negotiated or bool(traffic and traffic.group_wait)
                blocked=any(owner.nav(states[r]).get('formation_stream',{}).get('blocked') for r in order)
                no_path=all_started and not waiting and not self.arrived and any(
                    owner.nav(states[r]).get('formation_stream',{}).get('waiting_for_path') or
                    ((errors[i]>(.08 if self.elapsed>=self.trajectory.duration else .25) or heading_errors[i]>.25) and max(map(abs,owner.control(states[r]).get('velocity',[0.,0.])))<.02)
                    for i,r in enumerate(order))
                if not no_path:self.path_wait_since=None
                elif self.path_wait_since is None:self.path_wait_since=now
                elif now-self.path_wait_since>=3.:
                    self.begin_plan(self.goal,states)
                    targets=poses
                    self.message='车端持续无可行路径，按当前障碍重新联合规划'
                    for robot,pose in zip(order,poses):
                        job=owner.jobs[robot];local=compose(inverse(owner.maps.alignment[robot]),pose)
                        job['follow_points']=[local]
                        owner.send('follow_update',job['request'],robot_id=robot,poses=[local],mode='formation',
                            predecessor_velocity=[0.,0.],localization_epoch=job['epoch'])
                    return
                # Only the virtual clock slows. Each car retains its permanent
                # limits and local planner to take a temporary obstacle detour.
                lag=max(max(errors)/.25,max(heading_errors)/.25)
                desired=0. if waiting or blocked or not all_started else 1./(1.+lag*lag)
                self.rate=desired
                self.elapsed=min(self.trajectory.duration,self.elapsed+dt*self.rate)
                targets,velocities=self.trajectory.sample(self.elapsed)
                velocities=[[v*self.rate,w*self.rate] for v,w in velocities]
                self.phase='WAITING' if waiting else 'AVOIDING' if blocked or max(errors)>.25 else 'MOVING'
                self.message='等待 Open-RMF 全队交通放行' if waiting else '成员临时绕障，虚拟队形放慢等待归位' if self.phase=='AVOIDING' else '全队跟踪共同轨迹'
                if self.elapsed>=self.trajectory.duration and not waiting:
                    requested=[transform(self.goal,self.saved['offsets'][r]) for r in order]
                    arrived=self.arrived or all(math.dist(p[:2],q[:2])<=.08 and abs(wrap(p[2]-q[2]))<=.25 for p,q in zip(poses,requested))
                    if arrived and all_started:
                        self.arrived=True;self.rate=0.
                        self.frame=list(self.goal);self.phase='HOLDING';self.message='已到达队形目标，各成员保持自己的位置'
                        if self.queue:
                            self.queue.pop(0);self.completed+=1
                            if self.queue:self.begin_plan(self.queue[0]['pose'],states);return
            self.targets=dict(zip(order,targets))
            self.frame=estimate_frame(targets,[self.saved['offsets'][r] for r in order],self.frame[2])
            self.errors={r:math.dist(p[:2],q[:2]) for r,p,q in zip(order,poses,targets)}
            self.angle_errors={r:abs(wrap(p[2]-q[2])) for r,p,q in zip(order,poses,targets)}
            for robot,target,velocity in zip(order,targets,velocities):
                job=owner.jobs.get(robot)
                if not job or job.get('source')!='formation':continue
                local=compose(inverse(owner.maps.alignment[robot]),target);job['follow_points']=[local]
                if job['phase']=='EXECUTING':
                    owner.send('follow_update',job['request'],robot_id=robot,poses=[local],mode='formation',
                        predecessor_velocity=velocity,localization_epoch=job['epoch'])
        except (ValueError,KeyError,RuntimeError,OSError) as error:self.stop(str(error),failed=True)

    def snapshot(self):
        return {'saved':copy.deepcopy(self.saved),'active':self.active,'phase':self.phase,'reference':'centroid',
                'message':self.message,'targets':copy.deepcopy(self.targets),'position_errors':dict(self.errors),
                'heading_errors':dict(self.angle_errors),'route':copy.deepcopy(self.route),'goal':self.goal,
                'center':self.frame,'completed':self.completed,'remaining':len(self.queue),
                'planner':self.trajectory.planner if self.trajectory else None,'elapsed':self.elapsed,
                'duration':self.trajectory.duration if self.trajectory else 0.,'progress_rate':self.rate}
