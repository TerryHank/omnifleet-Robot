"""Two operator modes: fixed-leader trail following and independent waypoint queues."""

import copy

import json

import math

from pathlib import Path

import time

import uuid

from collections import deque



from scipy.spatial import cKDTree



from .coordination import grid_path

from .map_hub import compose, inverse, peer_grid

from .formation import Formation
from .goal_dispatch import GoalDispatch

from .traffic import Traffic, waiting_pose





def points(value):

    if not isinstance(value, list) or not 1 <= len(value) <= 100:

        raise ValueError('每车需要 1～100 个航点')

    result = []

    for index, point in enumerate(value):

        pose = point.get('pose') if isinstance(point, dict) else point

        if not isinstance(pose, list) or len(pose) != 3 or not all(type(v) in (int, float) and math.isfinite(v) for v in pose):

            raise ValueError('航点必须包含有限的 x、y、yaw（弧度）')

        result.append({'name': str(point.get('name', f'航点{index+1}'))[:80] if isinstance(point, dict) else f'航点{index+1}', 'pose': list(pose)})

    return result





def plan_route(grid, start, targets, peers, transform):

    grid = copy.deepcopy(grid)

    overlay = peer_grid(grid, [(compose(inverse(transform), pose), radius) for pose, radius in peers])

    for i, cost in enumerate(overlay.data):

        if cost == 100: grid.data[i] = 100

    path = [list(start)]

    for target in targets:

        leg = grid_path(grid, path[-1], target['pose'], radius=.01)

        path.extend(leg[1:] or [target['pose']])

    return {'path': [compose(transform, pose) for pose in path], 'targets': targets}





def path_conflict(first, second, clearance=1.):

    def samples(path):

        result = [path[0][:2]]

        for a, b in zip(path, path[1:]):

            steps = max(1, math.ceil(math.dist(a[:2], b[:2])/.1))

            result.extend([[a[j]+(b[j]-a[j])*i/steps for j in (0,1)] for i in range(1,steps+1)])

        return result

    return bool(first and second and min(cKDTree(samples(first)).query(samples(second))[0]) < clearance+.1)





class Trail:

    def __init__(self): self.samples = []



    def add(self, pose):

        if not self.samples:

            self.samples.append((0., list(pose))); return

        distance = math.dist(pose[:2], self.samples[-1][1][:2])

        if distance >= .08:

            self.samples.append((self.samples[-1][0]+distance, list(pose)))

            if len(self.samples) > 4000: self.samples.pop(0)



    def target(self, progress, lag):

        if not self.samples or self.samples[-1][0] < lag: return None

        end = min(max(progress, self.samples[0][0])+1., self.samples[-1][0]-lag)

        for (a, p), (b, q) in zip(self.samples, self.samples[1:]):

            if end <= b:

                ratio = max(0., (end-a)/(b-a))

                return end, [p[0]+ratio*(q[0]-p[0]), p[1]+ratio*(q[1]-p[1]), math.atan2(q[1]-p[1], q[0]-p[0])]

        return self.samples[-1]



    def segment(self, pose, progress, lag):

        end=self.samples[-1][0]-lag

        if end<=self.samples[0][0]:return None

        nearest=None

        for (a,p),(b,q) in zip(self.samples,self.samples[1:]):

            if b<progress-.1 or a>min(end,progress+2.):continue

            dx,dy=q[0]-p[0],q[1]-p[1]

            ratio=max(0.,min(1.,((pose[0]-p[0])*dx+(pose[1]-p[1])*dy)/(dx*dx+dy*dy)))

            s=a+ratio*(b-a)

            if s>end:s=end;ratio=(s-a)/(b-a)

            projected=[p[0]+ratio*dx,p[1]+ratio*dy,math.atan2(dy,dx)]

            distance=math.dist(pose[:2],projected[:2])

            if nearest is None or distance<nearest[0]:nearest=(distance,s,projected)

        if nearest is None:return None

        _,progress,projected=nearest

        targets=[projected]

        for (a,p),(b,q) in zip(self.samples,self.samples[1:]):

            if b<=progress:continue

            if a>=end:break

            ratio=min(1.,(end-a)/(b-a))

            target=[p[0]+ratio*(q[0]-p[0]),p[1]+ratio*(q[1]-p[1]),math.atan2(q[1]-p[1],q[0]-p[0])]

            if math.dist(targets[-1][:2],target[:2])>.001:targets.append(target)

        stride=max(1,math.ceil(len(targets)/99))

        return progress,targets[::stride]+([] if targets[::stride][-1]==targets[-1] else [targets[-1]])





class Missions:

    def __init__(self, config, maps, data, send):

        self.config, self.maps, self.send = config, maps, send

        self.file = Path(data)/'missions'/'routes.json'

        self.file.parent.mkdir(exist_ok=True)

        self.saved = json.loads(self.file.read_text()) if self.file.exists() else {'routes': {}}

        reference = config.get('central', {}).get('reference_robot')

        order = ([reference] if reference in maps.names else [])+[r for r in maps.names if r != reference]

        self.follow = {'active': False, 'leader': None, 'term': 0, 'phase': 'IDLE', 'order': order, 'distance': 1.}

        self.trail, self.leader_epoch = Trail(), None

        self.trails={};self.follow_epochs={};self.follow_pose_history={}

        self.handover = []

        self.jobs, self.prechecks, self.events = {}, {}, []
        self.pending_cooperative=None

        self.preview_paths = {}

        self.sequence = 0

        self.onboard_planner=None

        self.rmf_dispatch, self.rmf_traffic, self.current_rmf_task_id = None, None, None

        self.formation=Formation(self)

        self.traffic=Traffic(self)
        self.goal_dispatch=GoalDispatch(self)



    def save(self):

        temporary = self.file.with_suffix('.tmp')

        temporary.write_text(json.dumps(self.saved, ensure_ascii=False, indent=2))

        temporary.replace(self.file)



    def event(self, message):

        self.events.append({'time': time.time(), 'message': message})

        self.events = self.events[-24:]



    @staticmethod

    def nav(state): return state.get('samples', {}).get('navigation', {}).get('value', {})



    @staticmethod

    def control(state): return state.get('samples', {}).get('control', {}).get('value', {})



    @staticmethod

    def client(state): return state.get('samples', {}).get('fleet_client', {}).get('value', {})



    def ready(self, robot, states):

        state = states.get(robot, {})

        return bool(state.get('online') and state.get('fresh', {}).get('map') and self.nav(state).get('local_ready')

                    and robot in self.maps.valid_robots and self.control(state).get('control_gate_ready',False) and not self.control(state).get('estop'))



    def leader_available(self, robot, states):

        state = states.get(robot, {})

        return bool(state.get('transport_connected',state.get('online'))

                    and self.control(state).get('control_gate_ready',False) and not self.control(state).get('estop'))



    def follow_ready(self, robot, states):

        state=states.get(robot,{})

        return bool(self.leader_available(robot,states) and robot in self.maps.alignment

                    and self.nav(state).get('localization_epoch') and state.get('samples',{}).get('pose',{}).get('value'))



    def fence_followers(self, states, reason):

        self.handover = []

        for robot, job in self.jobs.items():

            if job['source'] != 'follow': continue

            self.stop(robot, reason)

            if states.get(robot, {}).get('online'): self.handover.append(robot)



    def stopped(self, state):

        control = self.control(state)

        return bool(state.get('online') and state.get('fresh', {}).get('fleet_client') and not self.client(state).get('busy', True)

                    and not control.get('nav_active') and control.get('stopped_seconds', 0) >= .3)



    def motion_allowed(self, robots):

        if any(not self.config['robots'][r].get('motion_enabled', False) for r in robots):

            raise ValueError('实际执行开关尚未启用；可以保存航点和进行不发车预检')



    def enqueue(self, robot, targets, source, epoch):

        self.sequence += 1

        settings=self.traffic.saved['settings'].get(robot,{}) if source in ('single','route') else {}

        self.jobs[robot] = {'id': uuid.uuid4().hex, 'source': source, 'phase': 'ARMING', 'points': copy.deepcopy(targets),

                            'index': 0, 'epoch': epoch, 'priority': self.sequence, 'request': None, 'arm': None,

                            'future': None, 'path': [], 'retry_after': 0., 'message': '', 'progress': 0.,

                            'created_at':time.time(), 'init_pose':None, 'rmf_task_id':self.current_rmf_task_id, **settings}



    def stop(self, robot, reason, final='STOPPED'):

        if self.pending_cooperative and robot in self.pending_cooperative['requests']:self.pending_cooperative=None
        job = self.jobs.get(robot)

        if job:job.pop('replacement',None)

        if not job or job['phase'] in ('STOPPED', 'FAILED', 'INVALIDATED') or (job['phase'] == 'COMPLETED' and job['source'] != 'follow'): return

        print(json.dumps({'event':'mission_stop','robot':robot,'job_id':job['id'],'request':job.get('request'),

            'from_phase':job['phase'],'final':final,'reason':reason},ensure_ascii=False),flush=True)

        self.send('disarm', 'stop-'+uuid.uuid4().hex, robot_id=robot)

        self.preview_paths[robot] = []

        if job.get('future'): job['future'].cancel(); job['future'] = None

        job.update(phase='STOPPING', message=reason, final=final, stop_deadline=time.monotonic()+8.)



    def cooperative_takeover(self, request, robots, states):
        requests={}
        for robot in robots:
            self.stop(robot,'协同优先接管，结束原任务')
            identifier='cooperative-takeover-'+uuid.uuid4().hex
            self.send('operator_stop',identifier,robot_id=robot)
            requests[robot]=identifier
        self.pending_cooperative={'request':{**request,'_rmf_awarded':True,'_cooperative_ready':True},
            'requests':requests,'epochs':{r:self.nav(states[r]).get('localization_epoch') for r in robots},
            'rmf_task_id':self.current_rmf_task_id}
        return {'phase':'accepted','message':'协同优先接管：正在结束原任务，停稳后自动启动'}

    def continue_cooperative(self, states):
        pending=self.pending_cooperative
        if not pending:return
        if any(not states.get(r,{}).get('online') or self.nav(states[r]).get('localization_epoch')!=epoch for r,epoch in pending['epochs'].items()):
            self.pending_cooperative=None;self.event('协同接管期间车辆连接或定位会话变化，已取消待启动请求');return
        for robot,identifier in pending['requests'].items():
            event=self.client(states[robot]).get('history',{}).get(identifier,{})
            if event.get('phase') in ('failed','rejected'):
                self.pending_cooperative=None;self.event('协同接管失败：'+event.get('message','车端停止请求失败'));return
            if event.get('phase')!='stopped' or not event.get('confirmed') or not self.stopped(states[robot]):return
            if self.jobs.get(robot,{}).get('phase','STOPPED') not in ('STOPPED','COMPLETED','FAILED','INVALIDATED'):return
        self.pending_cooperative=None
        previous=self.current_rmf_task_id;self.current_rmf_task_id=pending['rmf_task_id']
        try:
            self.command(pending['request'],states)
            self.event('原任务已结束，已自动进入协同控制')
        except (ValueError,RuntimeError) as error:self.event('协同接管未完成：'+str(error))
        finally:self.current_rmf_task_id=previous

    def command(self, request, states):

        op = request['op']; robot = request.get('robot_id')

        if op in ('dispatch_goal','dispatch_stop'):return self.goal_dispatch.command(request,states)
        if op in ('follow_start','formation_start','routes_stop','routes_clear'):
            self.goal_dispatch.stop('操作者切换或停止调度任务')

        if request.get('target')=='formation':return self.formation.command(request,states)

        if self.rmf_dispatch and not request.get('_rmf_awarded'):

            if (op in ('single_goal','route_start','formation_start','follow_start')
                    and (op!='single_goal' or robot is None) and self.rmf_dispatch.api.get_subscription_count()):

                return self.rmf_dispatch.submit(request, states)

            if op in ('route_stop','route_clear'):self.rmf_dispatch.cancel_pending(robot=robot)

            elif op in ('routes_stop','routes_clear'):self.rmf_dispatch.cancel_pending()

            elif op == 'formation_stop':self.rmf_dispatch.cancel_pending(group='formation_start')

            elif op == 'follow_stop':self.rmf_dispatch.cancel_pending(group=('follow_start','formation_start'))

        if robot is not None and robot not in self.maps.names: raise ValueError('车辆未由 WSL 分配')
        if op in ('follow_stop','formation_stop','routes_stop','routes_clear','route_stop','route_clear'):
            self.pending_cooperative=None
        if op in ('single_goal','route_start'):self.formation.admit(robot)
        if op in ('follow_start','formation_start','single_goal','route_start') and not request.get('_cooperative_ready'):
            if op in ('follow_start','formation_start') and (not isinstance(request.get('order'),list) or len(request['order'])<2 or len(set(request['order']))!=len(request['order'])):raise ValueError('协同顺序需要至少两台不同车辆')
            if op=='follow_start' and (type(request.get('distance',1.)) not in (int,float) or not math.isfinite(request.get('distance',1.)) or request.get('distance',1.)<0):raise ValueError('跟随间距必须为有效的非负数')
            if op=='route_start' and not self.saved['routes'].get(robot,{}).get('points'):raise ValueError('本车尚未保存航点')
            targets=(request.get('order') or [])[1:] if op=='follow_start' else list(request.get('order') or []) if op=='formation_start' else [robot]
            if targets and all(r in self.maps.names for r in targets):
                busy=[r for r in targets if not self.stopped(states.get(r,{})) or self.formation.manual_active(self.control(states.get(r,{})))]
                if busy:
                    self.motion_allowed(targets)
                    if any(not self.follow_ready(r,states) for r in targets):raise ValueError('参与车辆需要接入连接和地图坐标变换')
                    if op in ('single_goal','route_add'):points([request['point']])
                    if op=='formation_start' and request.get('capture_current') is not True and (not self.formation.saved or request.get('order')!=self.formation.saved['order']):raise ValueError('请先保存当前成员的队形')
                    return self.cooperative_takeover(request,targets,states)


        if op=='traffic_configure':return self.traffic.configure(request,states)

        if op=='traffic_recover':return self.traffic.recover(request,states)

        if op=='dispatch_order':return self.traffic.set_order(request)

        if op=='dispatch_settings':

            if robot is None:raise ValueError('请选择车辆')

            return self.traffic.settings(robot,request)

        if op=='traffic_call':

            self.traffic.tick(states)

            zone=next((z for z in self.traffic.saved['zones'] if z['id']==request.get('corridor')),None)

            side=request.get('side');action=request.get('action')

            if not zone or side not in ('a','b') or action not in ('wait','pass'):raise ValueError('请选择通道、入口方向和调用动作')

            if self.traffic.reason:raise ValueError(self.traffic.reason)

            if robot is None or not self.ready(robot,states):raise ValueError('请选择定位和导航就绪的车辆')

            self.motion_allowed([robot])

            if self.follow['active'] or self.formation.active:raise ValueError('请先停止跟随或编队，再逐车调度窄道')

            if not self.traffic.idle(robot,states):raise ValueError('请先结束本车任务并停稳')

            start=waiting_pose(zone,side)

            end=waiting_pose(zone,'b' if side=='a' else 'a');end[2]=start[2]

            world=[start] if action=='wait' else [start,[*zone[side],start[2]],[*zone['b' if side=='a' else 'a'],start[2]],end]

            local=[{'name':'通道 '+zone['id'],'pose':compose(inverse(self.maps.alignment[robot]),p)} for p in world]

            self.enqueue(robot,local,'route',self.nav(states[robot])['localization_epoch'])

            if action=='pass':self.jobs[robot]['corridor']=zone['id']

            return {'phase':'accepted','message':'已排队调用车辆到等待点' if action=='wait' else '已排队通行；取得路权后才发车'}

        if self.traffic.saved['zones'] and op in ('formation_start','follow_start'):

            raise ValueError('已配置窄道互斥区域，请逐车调度；编队或连续跟随通道尚未验收')

        if op=='formation_capture':return self.formation.capture(request.get('order'),states)

        if op=='formation_start':return self.formation.start(request.get('order'),states,capture_current=request.get('capture_current') is True)

        if op=='formation_stop':return self.formation.stop()


        if op in ('route_clear','routes_clear'):

            if op=='routes_clear':
                self.formation.stop('操作者清除全部航点')
                self.formation.save_route([])

            if op=='route_clear' and robot is None:raise ValueError('请选择车辆')

            targets=list(self.maps.names) if op=='routes_clear' else [robot]

            if self.follow['active'] and self.follow['leader'] in targets:

                self.command({'op':'follow_stop'},states)

            for target in targets:

                job=self.jobs.get(target)

                if job and job['source'] in ('route','single'):

                    self.stop(target,'操作者清除航点');job['hide_target']=True

                old=self.saved['routes'].get(target,{})

                self.saved['routes'][target]={'epoch':self.nav(states.get(target,{})).get('localization_epoch') or old.get('epoch'),

                    'points':[],'revision':old.get('revision',0)+1}

                self.preview_paths[target]=[]

                for check in self.prechecks.values():

                    if check['robot_id']==target:

                        if check.get('future'):check['future'].cancel()

                        check.update(phase='INVALIDATED',message='航点已清除')

            self.save()

            return {'phase':'cleared','robots':targets,'message':'航点已清除；执行中的相关任务已请求停止'}

        if op == 'follow_start':

            if self.formation.active:raise ValueError('请先停止保持队形模式')

            order, distance = request.get('order'), request.get('distance', 1.)

            if not isinstance(order, list) or len(order) < 2 or len(order) != len(set(order)) or any(r not in self.maps.names for r in order):

                raise ValueError('跟随顺序需要至少两台已分配车辆，且不能重复')

            if type(distance) not in (int, float) or not math.isfinite(distance) or distance < 0:

                raise ValueError('跟随间距必须为有效的非负数（米）')

            self.motion_allowed(order)

            if self.follow['active']: raise ValueError('请先停止当前跟随，再修改顺序')

            if any(not self.follow_ready(r, states) for r in order): raise ValueError('参与车辆需要接入连接和地图坐标变换')

            if any(not self.stopped(states[r]) or self.formation.manual_active(self.control(states[r])) for r in order[1:]):

                raise ValueError('跟随车必须先结束本地任务和人工操作并停稳')

            if any(r in self.jobs and self.jobs[r]['phase'] not in ('STOPPED', 'COMPLETED', 'FAILED', 'INVALIDATED') for r in order[1:]):

                raise ValueError('跟随车已有任务，请先停止并确认停稳')

            self.follow.update(active=True, order=order, distance=distance, leader=order[0], phase='WAIT_TRAIL', term=self.follow['term']+1, message='')

            self.fence_followers(states, '开始新的固定领车跟随，取消旧目标')

            self.trail=Trail();self.leader_epoch=(self.nav(states[order[0]]).get('localization_epoch'),tuple(self.maps.alignment[order[0]]))

            self.reset_trails(states)

            name=self.config.get('central',{}).get('assignments',{}).get(order[0],{}).get('robot_name',order[0])

            self.event('开始固定领车跟随：'+name)

            return {'phase': 'accepted'}

        if op == 'follow_stop':

            if self.formation.active:self.formation.stop('停止编队及跟随')

            self.follow.update(active=False, phase='STOPPED')

            for r, job in self.jobs.items():

                if job['source'] == 'follow': self.stop(r, '操作者停止跟随')

            return {'phase': 'accepted'}

        if robot is None: raise ValueError('请选择车辆')

        if op=='single_goal':

            self.motion_allowed([robot]);state=states.get(robot,{})

            if not self.ready(robot,states):raise ValueError('该车地图、定位或导航未就绪')

            if self.follow['active'] and robot in self.follow['order'] and robot!=self.follow['leader']:raise ValueError('该车正在跟随，请先停止跟随')

            if self.formation.manual_active(self.control(state)):raise ValueError('人工操作尚未结束')

            targets=points([request['point']]);epoch=self.nav(state).get('localization_epoch')

            job=self.jobs.get(robot);active=job and job['phase'] not in ('STOPPED','COMPLETED','FAILED','INVALIDATED')

            if active:

                if job['phase']=='CANCEL_UNCONFIRMED':raise ValueError('旧目标停止尚未确认')

                self.stop(robot,'新单点目标替换当前导航')

                job['replacement']={'points':targets,'epoch':epoch,'source':'single'}

            else:

                if self.nav(state).get('navigation_active') or not self.stopped(state):raise ValueError('本车任务尚未停止')

                self.enqueue(robot,targets,'single',epoch)

            return {'phase':'accepted','message':'单点目标已发送；替换当前导航，不加入多点队列'}

        if op == 'route_add':
            state=states.get(robot,{})
            epoch=self.nav(state).get('localization_epoch')
            if not epoch or not state.get('online'):raise ValueError('该车必须在线，以绑定当前地图会话')
            route=self.saved['routes'].get(robot)
            stale_route=route if route and route['points'] and route['epoch']!=epoch else None
            if stale_route:route={**route,'epoch':epoch,'points':[]}
            targets=points((route['points'] if route else [])+[request['point']])
            if stale_route:
                archive=self.file.parent/'route_archive';archive.mkdir(exist_ok=True)
                (archive/(robot+'-'+uuid.uuid4().hex+'.json')).write_text(json.dumps(
                    {'robot_id':robot,'archived_at':time.time(),'route':stale_route},ensure_ascii=False,indent=2))
                self.event('旧定位会话路线已备份，新航点建立当前会话队列：'+self.maps.names[robot].lstrip('/'))
            self.saved['routes'][robot]={'epoch':epoch,'points':targets,'revision':(route or {}).get('revision',0)+1}
            self.preview_paths[robot]=[]
            self.save()
            return {'phase':'saved','count':len(targets),'message':('旧定位会话路线已备份。' if stale_route else '')+'多点航点已保存；布置完成后点击“规划并执行”发车'}

        if op == 'route_save':

            if robot in self.jobs and self.jobs[robot]['phase'] not in ('STOPPED', 'COMPLETED', 'FAILED', 'INVALIDATED'):

                raise ValueError('请先停止该车任务再保存航点')

            epoch = self.nav(states.get(robot, {})).get('localization_epoch')

            if not epoch or not states.get(robot, {}).get('online'): raise ValueError('该车必须在线，以绑定当前地图会话')

            revision=self.saved['routes'].get(robot,{}).get('revision',0)+1

            targets=[] if request.get('points')==[] else points(request.get('points'))

            self.saved['routes'][robot] = {'epoch': epoch, 'points': targets, 'revision':revision}

            self.preview_paths[robot] = []

            self.save(); return {'phase': 'saved'}

        if op == 'route_stop':

            self.stop(robot, '操作者停止本车航点任务'); return {'phase': 'accepted'}

        if op not in ('route_prepare', 'route_start'): raise ValueError('未知任务操作')

        route = self.saved['routes'].get(robot)

        if not route or not route['points']: raise ValueError('请先保存该车航点')

        if route['epoch'] != self.nav(states.get(robot, {})).get('localization_epoch'):

            raise ValueError('该车定位会话已变化，请检查航点后重新保存；不会自动续跑旧任务')

        if not self.ready(robot, states): raise ValueError('该车地图、定位或导航未就绪')

        if op == 'route_prepare':

            if request['id'] in self.prechecks: return {'phase': 'PRECHECKING'}

            if len([p for p in self.prechecks.values() if p['phase'] == 'PRECHECKING']) >= 4: raise ValueError('已有预检正在运行')

            future = self.plan(robot, route['points'], states)

            self.prechecks[request['id']] = {'phase': 'PRECHECKING', 'robot_id': robot, 'future': future, 'epoch': route['epoch'], 'points': route['points'], 'created': time.monotonic()}

            return {'phase': 'PRECHECKING'}

        self.motion_allowed([robot])

        if self.follow['active'] and robot != self.follow['leader'] and robot in self.follow['order']:

            raise ValueError('该车正在跟随，请先停止跟随')

        if robot in self.jobs and self.jobs[robot]['phase'] not in ('STOPPED', 'COMPLETED', 'FAILED', 'INVALIDATED'):

            raise ValueError('该车已有任务，请先停止并确认停稳')

        if self.nav(states[robot]).get('navigation_active') or not self.stopped(states[robot]): raise ValueError('本车任务或人工操作尚未停止')

        self.enqueue(robot, route['points'], 'route', route['epoch'])

        return {'phase': 'accepted'}



    def plan(self, robot, targets, states):

        if self.onboard_planner is None:raise ValueError('车端 Nav2 路径计算接口未连接')

        return self.onboard_planner(robot,copy.deepcopy(targets),states)



    def reset_trails(self, states):

        self.trails={};self.follow_epochs={};self.follow_pose_history={}

        for robot in self.follow['order']:

            self.follow_epochs[robot]=(self.nav(states[robot]).get('localization_epoch'),tuple(self.maps.alignment[robot]))

        for predecessor,follower in zip(self.follow['order'],self.follow['order'][1:]):

            def pose(robot):

                p=states[robot]['samples']['pose']['value']

                return compose(self.maps.alignment[robot],[p['x'],p['y'],p['yaw']])

            head,tail=pose(predecessor),pose(follower);gap=math.dist(head[:2],tail[:2])

            trail=Trail()

            # Initial joining leg is planned on board; later samples are actual

            # predecessor observations, including any obstacle-avoidance detour.

            trail.samples=([(-gap,tail)] if gap>.001 else [])+[(0.,head)]

            self.trails[predecessor]=trail

        self.trail=self.trails[self.follow['leader']]



    def observed_velocity(self, robot, state, pose):

        history=self.follow_pose_history.setdefault(robot,deque(maxlen=10))

        stamp=state['samples']['pose']['value'].get('stamp_seconds',time.monotonic())

        if not history or stamp>history[-1][0]:history.append((stamp,pose))

        while len(history)>2 and history[-1][0]-history[0][0]>.3:history.popleft()

        sample=state['samples'].get('control',{});control=sample.get('value',{})
        velocity=control.get('velocity')
        if (sample.get('age_seconds',99.)+control.get('velocity_age',99.)<.3 and
            isinstance(velocity,list) and len(velocity)==2 and all(math.isfinite(v) for v in velocity)):
            return [velocity[0]*math.cos(pose[2]),velocity[0]*math.sin(pose[2]),velocity[1]]
        if len(history)<2:return [0.,0.,0.]

        average=sum(t for t,_ in history)/len(history)

        denominator=sum((t-average)**2 for t,_ in history)

        if denominator<=0:return [0.,0.,0.]

        velocity=[sum((t-average)*p[k] for t,p in history)/denominator for k in (0,1)]

        dt=history[-1][0]-history[0][0];delta=history[-1][1][2]-history[0][1][2]

        return velocity+[math.atan2(math.sin(delta),math.cos(delta))/dt]



    def follow_tick(self, states):

        if not self.follow['active']: return

        leader = self.follow['leader']

        unavailable=next((r for r in self.follow['order'] if not self.leader_available(r,states)),None)

        if unavailable is not None:

            name=self.maps.names[unavailable].lstrip('/')

            reason='接入连接中断' if not states.get(unavailable,{}).get('transport_connected',states.get(unavailable,{}).get('online')) else '底盘通道未就绪或急停已触发'

            self.follow.update(active=False,phase='FAILED',message=name+'：'+reason+'；跟随已停止')

            self.fence_followers(states,self.follow['message']);self.event(self.follow['message']);return

        if any(not self.follow_ready(r,states) for r in self.follow['order']):

            self.follow['phase'] = 'WAIT_MAP'

            if self.leader_epoch is not None:

                self.fence_followers(states, '等待当前地图配准，取消旧跟随目标')

                self.trail = Trail(); self.leader_epoch = None;self.follow_epochs={}

            return

        if self.rmf_traffic and self.rmf_traffic.group_wait:

            self.follow['phase']='RMF_PAUSED'

            return

        epoch = (self.nav(states[leader]).get('localization_epoch'), tuple(self.maps.alignment[leader]))

        epochs={r:(self.nav(states[r]).get('localization_epoch'),tuple(self.maps.alignment[r])) for r in self.follow['order']}

        if epochs != self.follow_epochs:

            self.leader_epoch = epoch;self.reset_trails(states); self.follow['term'] += 1

            self.fence_followers(states, '队列地图会话变化，等待新轨迹')

        if any(states.get(r, {}).get('online') and (not self.stopped(states[r]) or self.client(states[r]).get('armed')

               or self.nav(states[r]).get('fleet_enabled') or self.nav(states[r]).get('fleet_lease_fresh')) for r in self.handover):

            self.follow['phase'] = 'HANDOVER'; return

        self.handover = []

        for predecessor,trail in self.trails.items():

            p=states[predecessor]['samples']['pose']['value']

            trail.add(compose(self.maps.alignment[predecessor],[p['x'],p['y'],p['yaw']]))

        for predecessor,robot in zip(self.follow['order'],self.follow['order'][1:]):

            job = self.jobs.get(robot)

            if job and job['source'] == 'route' and job['phase'] not in ('STOPPED', 'COMPLETED', 'FAILED', 'INVALIDATED'): continue

            if job and job['phase'] in ('STOPPING', 'CANCEL_UNCONFIRMED'): continue

            if job and job['source'] == 'follow' and job.get('term') == self.follow['term'] and job['phase'] in ('FAILED', 'INVALIDATED'): continue

            if self.formation.manual_active(self.control(states[robot])): continue

            if self.nav(states[robot]).get('navigation_active') and not (job and job['source'] == 'follow' and job['phase'] == 'EXECUTING'): continue

            if job and job.get('manual_paused') == self.follow['term']: continue

            if job and job.get('term') == self.follow['term'] and job['phase'] != 'ARMING' and self.control(states[robot]).get('local_override'):

                self.stop(robot, '人工接管，等待重新开始跟随')

                job['manual_paused'] = self.follow['term']; continue

            p=states[predecessor]['samples']['pose']['value']

            head=compose(self.maps.alignment[predecessor],[p['x'],p['y'],p['yaw']])

            p=states[robot]['samples']['pose']['value']

            tail=compose(self.maps.alignment[robot],[p['x'],p['y'],p['yaw']])

            distance=self.follow['distance']

            bearing=math.atan2(head[1]-tail[1],head[0]-tail[0]) if math.dist(head[:2],tail[:2])>.001 else tail[2]

            target=[head[0]-distance*math.cos(bearing),head[1]-distance*math.sin(bearing),bearing]

            # A moving destination, not mandatory points from the predecessor's

            # history. The follower's own planner chooses its obstacle detour.

            local=[compose(inverse(self.maps.alignment[robot]),target)]

            if not job or job['phase'] in ('STOPPED','COMPLETED','FAILED','INVALIDATED'):

                self.enqueue(robot,[{'name':'实时跟随位置','pose':p} for p in local],'follow',self.nav(states[robot])['localization_epoch'])

                job=self.jobs[robot];job.update(term=self.follow['term'],predecessor=predecessor)

            job.update(follow_points=local)

            if job['phase']=='EXECUTING':

                observed=self.observed_velocity(predecessor,states[predecessor],head)

                tail_velocity=self.observed_velocity(robot,states[robot],tail)

                velocity=[observed[0]*math.cos(bearing)+observed[1]*math.sin(bearing),observed[2]]

                range_rate=(observed[0]-tail_velocity[0])*math.cos(bearing)+(observed[1]-tail_velocity[1])*math.sin(bearing)

                self.send('follow_update',job['request'],robot_id=robot,poses=local,

                    predecessor_velocity=velocity,

                    follow_distance=distance,range_rate=range_rate,localization_epoch=job['epoch'])

        active=[j for j in self.jobs.values() if j['source']=='follow' and j.get('term')==self.follow['term']]

        failed=next(((r,j) for r,j in self.jobs.items() if j['source']=='follow' and j.get('term')==self.follow['term'] and j['phase'] in ('FAILED','INVALIDATED')),None)

        if failed:

            robot,job=failed

            self.follow.update(active=False,phase='FAILED',message=self.maps.names[robot].lstrip('/')+'：'+job['message'])

            self.fence_followers(states,self.follow['message']);return

        blocked=any(self.nav(states[r]).get('follow_stream',{}).get('blocked') for r in self.follow['order'][1:])

        self.follow['phase']='BLOCKED' if blocked else 'FOLLOWING' if any(j['phase'] not in ('COMPLETED','STOPPED') for j in active) else 'WAIT_TRAIL'



    def tick(self, states, now=None):

        now = time.monotonic() if now is None else now
        self.continue_cooperative(states)

        self.traffic.tick(states)

        self.refresh_reservations(states)

        self.follow_tick(states)

        self.formation.tick(states)
        self.goal_dispatch.tick(states)

        for identifier, check in self.prechecks.items():

            if check['phase'] != 'PRECHECKING': continue

            robot = check['robot_id']

            if not self.ready(robot, states) or self.nav(states[robot]).get('localization_epoch') != check['epoch']:

                check.update(phase='INVALIDATED', message='预检期间地图会话或车辆状态变化'); continue

            if not check['future'].done(): continue

            try:

                self.preview_paths[robot] = check['future'].result()['path']

                self.send('prepare', identifier, robot_id=robot, poses=[p['pose'] for p in check['points']], localization_epoch=check['epoch'])

                check.update(phase='PREPARING', deadline=now+5.)

            except ValueError as error: check.update(phase='BLOCKED', message=str(error))

        for identifier, check in self.prechecks.items():

            if check['phase'] != 'PREPARING': continue

            event = self.client(states.get(check['robot_id'], {})).get('history', {}).get(identifier)

            if event: check.update(phase='PREPARED' if event['phase'] == 'prepared' else 'REJECTED', receipt=event)

            elif now > check['deadline']: check.update(phase='TIMED_OUT', message='车端准备回执超时')

        while len(self.prechecks) > 32:

            done = next((key for key, value in self.prechecks.items() if value['phase'] not in ('PRECHECKING', 'PREPARING')), None)

            if done is None: break

            self.prechecks.pop(done)

        for robot, job in sorted(self.jobs.items(), key=lambda item: (self.traffic.priority(item[0]),item[1]['priority'])):

            state = states.get(robot, {}); nav = self.nav(state); client = self.client(state)

            if job['phase'] == 'RMF_PAUSED':

                if self.rmf_traffic is None or self.rmf_traffic.resumed(robot, states):

                    self.enqueue(robot, job['points'], job['source'], job['epoch'])

                    self.jobs[robot].update({k:job[k] for k in ('index','rmf_task_id','created_at','init_pose') if k in job})

                continue

            if job['phase'] == 'CANCEL_UNCONFIRMED':
                if self.stopped(state) and not client.get('armed') and not nav.get('fleet_enabled') and not nav.get('fleet_lease_fresh'):
                    job.update(phase=job['final'], path=[], request=None, replacement=None,
                               message='旧任务停止已确认' if job['final']=='STOPPED' else job['message'])
                continue
            if job['phase'] in ('COMPLETED', 'STOPPED', 'FAILED', 'INVALIDATED'): continue

            if job['phase'] == 'STOPPING':

                if self.stopped(state) and not client.get('armed') and not nav.get('fleet_enabled') and not nav.get('fleet_lease_fresh'):

                    replacement=job.get('replacement')

                    if replacement:

                        if self.follow_ready(robot,states) and nav.get('localization_epoch')==replacement['epoch'] and not self.formation.manual_active(self.control(state)):

                            self.enqueue(robot,replacement['points'],replacement['source'],replacement['epoch'])

                            self.jobs[robot]['rmf_task_id'] = replacement.get('rmf_task_id')

                        else:job.update(phase='INVALIDATED',message='新目标等待期间定位或车辆状态变化；不会自动续跑',path=[],request=None,replacement=None)

                    else:job.update(phase=job['final'], path=[], request=None)

                elif now > job['stop_deadline']: job.update(phase='CANCEL_UNCONFIRMED', message='未确认停稳，禁止后续目标')

                continue

            # Readiness admits a new task. An accepted on-board task owns its

            # lifecycle; a delayed GetState reply must not cancel it in motion.

            independent=job['source'] in ('single','route','dispatch') and job['phase']=='EXECUTING'

            ready=(self.leader_available(robot,states) and bool(state.get('samples',{}).get('pose',{}).get('value'))

                   if independent else self.follow_ready(robot,states))

            if not ready or nav.get('localization_epoch') != job['epoch']:

                self.stop(robot, '定位、地图或连接失效；不会自动续跑', 'INVALIDATED'); continue

            control = self.control(state)

            manual=self.formation.manual_active(control) if job['source']=='formation' else self.formation.manual_active(control)

            if manual or (job['phase'] != 'ARMING' and control.get('local_override')):

                self.stop(robot, '人工或本地任务接管', 'STOPPED'); continue

            if job['source'] not in ('follow','formation') and job['phase']!='EXECUTING':

                if not self.ready(robot,states):

                    job.update(waiting_ready=True,message='已接收航点，等待本车导航就绪：'+(nav.get('readiness_reason') or '等待实时地图与导航状态'))

                    continue

                if job.pop('waiting_ready',False):job['message']=''

            if job.get('init_pose') is None:job['init_pose']=self.traffic.pose(robot,states)

            if job['phase'] in ('ARMING','PLANNING','YIELDING','BLOCKED','SCHEDULED') and time.time()<job.get('not_before',0):

                job['phase']='SCHEDULED';job['message']='等待计划开始时间';continue

            if job['phase']=='SCHEDULED':job.update(phase='ARMING',message='')

            if job['phase'] == 'ARMING':

                if client.get('armed') and nav.get('fleet_lease_fresh'):

                    job.update(phase='PLANNING', arm=None); continue

                if job['arm'] is None:

                    job.update(arm='arm-'+job['id'], deadline=now+5.)

                    self.send('arm', job['arm'], robot_id=robot)

                event = client.get('history', {}).get(job['arm'])

                if event and event['phase'] in ('failed', 'rejected') or now > job['deadline']:

                    self.stop(robot, event.get('message', '取得车队租约失败') if event else '取得租约超时', 'FAILED')

                continue

            if not client.get('armed') or not nav.get('fleet_lease_fresh'):

                event = client.get('history', {}).get(job.get('request'), {})
                reason = event.get('message') if event.get('phase') in ('failed', 'rejected') else None
                self.stop(robot, reason or '车端租约失效', 'FAILED'); continue

            if job['source'] in ('follow','formation') and job['phase']=='PLANNING':

                request='follow-'+job['id']

                self.send('navigate',request,robot_id=robot,poses=job['follow_points'],single_point=False,follow_trail=job['source']=='follow',follow_formation=job['source']=='formation',localization_epoch=job['epoch'])

                job.update(phase='EXECUTING',request=request)

                continue

            if job['phase'] == 'EXECUTING':

                event = client.get('history', {}).get(job['request'], {})

                if job['source']=='follow':job['message']=event.get('navigation_message',job['message'])

                if type(event.get('passed_points')) is int:

                    job['index']=min(job.get('batch_end',len(job['points'])),job.get('batch_start',job['index'])+event['passed_points'])

                if event.get('phase') in ('failed', 'rejected'):

                    self.stop(robot, event.get('message', '车端导航失败，不会反复重试'), 'FAILED')

                elif event.get('phase') == 'completed' and self.stopped(state):

                    job['index'] = job.get('batch_end',job['index']+1); job.update(path=[], reservation=[], request=None)

                    if job['index'] == len(job['points']):

                        job.update(progress=job.get('target_progress', job['progress']))

                        if job['source'] == 'follow': job.update(phase='COMPLETED', message='已到达当前跟随目标')

                        else: self.stop(robot, '全部航点到达', 'COMPLETED')

                    else: job['phase'] = 'PLANNING'

                continue

            if now < job['retry_after']: continue

            if job['future'] is None:

                job['future'] = self.plan(robot, job['points'][job['index']:], states)

                job['plan_started'] = now; continue

            if not job['future'].done(): continue

            try:

                planned = job['future'].result()

            except ValueError as error:

                job.update(future=None, phase='BLOCKED', retry_after=now+2., message=str(error)); continue

            earlier = [r for r, other in self.jobs.items() if self.traffic.priority(r) < self.traffic.priority(robot)

                       and other['source'] in ('single', 'route', 'dispatch') and other['phase'] in ('ARMING', 'PLANNING')

                       and time.time() >= other.get('not_before', 0) and self.ready(r, states)]

            if earlier:

                job.update(phase='YIELDING', retry_after=now+.2, message='等待序号更前车辆完成规划：'+', '.join(earlier)); continue

            granted,reason=self.traffic.acquire(robot,job,planned['path'],reserve=False)

            if not granted:

                job.update(phase='YIELDING',future=None,retry_after=now+1.,message=reason);continue

            conflicts = [r for r, other in self.jobs.items() if r != robot and other['path'] and path_conflict(planned['path'], other['path'])]

            if conflicts:

                job.update(phase='YIELDING', retry_after=now+1., message='等待 '+', '.join(conflicts)+' 通过'); continue

            if self.rmf_traffic:

                granted, reason = self.rmf_traffic.admit(robot, job, planned['path'], states)

                if not granted:

                    job.update(phase='YIELDING', retry_after=now+.2, message=reason); continue

            if not self.stopped(state): continue

            granted,reason=self.traffic.acquire(robot,job,planned['path'])

            if not granted:

                job.update(phase='YIELDING',future=None,retry_after=now+1.,message=reason);continue

            request = 'mission-'+job['id']+'-'+str(job['index'])

            targets=job['points'][job['index']:job['index']+len(planned['targets'])]

            self.send('navigate', request, robot_id=robot, pose=targets[0]['pose'],poses=[p['pose'] for p in targets],single_point=len(targets)==1,localization_epoch=job['epoch'])

            self.preview_paths[robot] = planned['path']

            job.update(phase='EXECUTING', request=request, path=planned['path'], reservation=planned['path'], path_index=0, future=None, message='',batch_start=job['index'],batch_end=job['index']+len(targets))



    def refresh_reservations(self, states):

        for robot, job in self.jobs.items():

            if job['phase'] != 'EXECUTING' or not job.get('reservation') or not self.ready(robot, states): continue

            p = states[robot]['samples']['pose']['value']

            pose = compose(self.maps.alignment[robot], [p['x'], p['y'], p['yaw']])

            path = job['reservation']; start = job.get('path_index', 0)

            nearest = min(range(start, len(path)), key=lambda i: math.dist(path[i][:2], pose[:2]))

            if math.dist(path[nearest][:2], pose[:2]) <= .5:

                job['path_index'] = nearest

                job['path'] = [pose]+path[nearest:]



    def snapshot(self):

        return {'goal_dispatch':self.goal_dispatch.snapshot(), 'traffic':self.traffic.snapshot(), 'dispatch_rows':self.traffic.rows(), 'follow': copy.deepcopy(self.follow), 'formation':self.formation.snapshot(), 'routes': self.saved['routes'], 'events': self.events,

                'jobs': {r: {k: v for k, v in job.items() if k not in ('future', 'path', 'reservation', 'path_index')} for r, job in self.jobs.items()},

                'prechecks': {r: {k: v for k, v in check.items() if k not in ('future', 'points')} for r, check in self.prechecks.items()}}



    def close(self):

        self.formation.close()

        for robot in self.jobs: self.send('disarm', 'central-shutdown', robot_id=robot)

