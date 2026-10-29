"""Open-RMF traffic-light negotiation for paths executed by onboard Nav2."""
from datetime import timedelta
import json
import math
import queue
import time

import rmf_adapter as rmf
from rmf_adapter import geometry, vehicletraits
from .map_hub import compose

REBASE_ROUTE = object()

def traffic_waypoints(path):
    # Nav2 owns continuous tracking. Grid samples describe route geometry;
    # only its actual start and destination are holding locations.
    return [rmf.Waypoint('fleet_map',p,timedelta(seconds=0),i in (0,len(path)-1))
            for i,p in enumerate(path)]

def simplify_formation_path(path):
    if len(path)<3:return path
    a,b=path[0],path[-1];dx,dy=b[0]-a[0],b[1]-a[1];length=dx*dx+dy*dy
    def distance(p):
        t=max(0.,min(1.,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length)) if length else 0.
        return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
    index=max(range(1,len(path)-1),key=lambda i:distance(path[i]))
    if distance(path[index])<=.01:return [a,b]
    return simplify_formation_path(path[:index+1])[:-1]+simplify_formation_path(path[index:])


class RmfTraffic:
    def __init__(self, owner, adapter):
        self.owner, self.adapter = owner, adapter
        self.members, self.routes, self.events = {}, {}, queue.SimpleQueue()
        self.last_idle = 0.
        self.available = False
        self.group_wait = None
        self.audit = []
        self.formation_reservation=None

    def admit_formation(self,trajectory,order,number,states):
        from .formation_traffic import FormationTraffic
        reservation=self.formation_reservation
        if reservation is None or reservation.number!=number:
            if reservation:reservation.clear()
            reservation=FormationTraffic(self,trajectory,order,number,states)
            self.formation_reservation=reservation
        return reservation.admit(states)

    def record(self, kind, robot, **fields):
        job=self.owner.missions.jobs.get(robot,{})
        value={'time':time.time(),'event':kind,'robot':robot,'job_id':job.get('id'),
               'request':job.get('request'),'blockers':self.members.get(robot,{}).get('blockers',[]),**fields}
        self.audit.append(value);self.audit=self.audit[-128:]
        print('rmf_traffic '+json.dumps(value,ensure_ascii=False),flush=True)

    def enroll(self):
        for robot in self.owner.maps.names:
            if robot in self.members:continue
            limits = self.owner.config.get('robots', {}).get(robot, {}).get('rmf_traits', {})
            profile = vehicletraits.Profile(
                geometry.make_final_convex_circle(limits.get('footprint_radius', .39)),
                geometry.make_final_convex_circle(limits.get('vicinity_radius', .49)))
            # Nav2 supplies the feasible Ackermann path; RMF uses its execution limits.
            traits = vehicletraits.VehicleTraits(
                vehicletraits.Limits(limits.get('linear_velocity', .5), limits.get('linear_acceleration', .5)),
                vehicletraits.Limits(limits.get('angular_velocity', .8), limits.get('angular_acceleration', .8)), profile)
            traits.differential.reversible = True
            self.members[robot] = {'handle': None, 'state': 'REGISTERING', 'blockers': []}
            self.adapter.add_easy_traffic_light(
                lambda handle, r=robot: self.events.put(('registered', r, handle)),
                'omnifleet_'+robot, self.owner.config['central']['assignments'][robot]['robot_name'], traits,
                lambda r=robot: self.events.put(('pause', r, None)),
                lambda r=robot: self.events.put(('resume', r, None)),
                lambda blockers, r=robot: self.events.put(('blockers', r, [str(b) for b in blockers])))

    def pose(self, robot, states):
        value = states.get(robot, {}).get('samples', {}).get('pose', {}).get('value')
        transform=self.owner.maps.alignment.get(robot)
        entry=self.routes.get(robot)
        job=self.owner.missions.jobs.get(robot,{})
        if entry and entry.get('job')==job.get('id') and job.get('phase')=='EXECUTING':
            transform=entry.get('transform',transform)
        if value and transform is not None:
            return compose(transform, [value['x'], value['y'], value['yaw']])
        return None

    @staticmethod
    def instruction(method, *args):
        try:return method(*args)
        except RuntimeError as error:
            # Humble can expose an empty optional while its asynchronous
            # worker replaces the current plan. Retry on the next update.
            if str(error) == 'bad optional access':return None
            if str(error).startswith('[EasyTrafficLight::Implementation::Shared::update_delay] Excessive delay was calculated:'):
                # An RMF interpolation failure is a recoverable plan error,
                # not a reason to terminate all vehicle heartbeats.
                print('rmf_instruction_replan '+str(error),flush=True)
                return REBASE_ROUTE
            raise

    def admit(self, robot, job, path, states):
        member = self.members.get(robot, {})
        handle = member.get('handle')
        # Existing path checks remain the fallback while registration reconnects.
        if not self.available or not handle or len(path) < 2 or math.dist(path[0][:2], path[-1][:2]) < .01:return True, ''
        entry = self.routes.get(robot)
        signature = (job['id'], job['index'], tuple(path[-1]),job.get('formation_plan'))
        if not entry or entry['signature'] != signature:
            # In-place turns belong to the on-board trajectory. Humble's
            # EasyTrafficLight graph cannot interpolate zero-length XY lanes;
            # dense yaw-only samples can crash its C++ planner.
            unique = [list(path[0])]
            for point in path[1:]:
                if math.dist(unique[-1][:2], point[:2]) >= .01:unique.append(list(point))
            if len(unique)<2:return True,''
            unique[-1]=list(path[-1])
            # Nav2 grid samples are geometry, not independent traffic stops.
            # Reuse the formation geometry simplifier for individual routes.
            unique=simplify_formation_path(unique)
            handle.follow_new_path(traffic_waypoints(unique))
            self.routes[robot] = {'job': job['id'], 'signature': signature, 'path': unique, 'index': 0,
                                  'transform':list(self.owner.maps.alignment[robot])}
            member['state'] = 'NEGOTIATING'
            return False, '等待 Open-RMF 交通规划返回'
        instruction = self.instruction(handle.waiting_at, 0)
        if instruction == rmf.easy_traffic_light.WaitingInstruction.Resume:
            member['state'] = 'READY'
            return True, ''
        return False, '等待 Open-RMF 交通协商放行'

    def resumed(self, robot, states):
        if self.formation_reservation and self.group_wait:return not self.formation_reservation.paused
        if self.group_wait:
            kind, blocked, order = self.group_wait
            active = self.owner.missions.formation.active if kind == 'formation' else self.owner.missions.follow['active']
            if active:
                member = self.members[blocked];entry = self.routes.get(blocked)
                pose = self.pose(blocked, states)
                if self.available and entry and pose is not None:
                    if not all(self.waiting_stopped(r,states) for r in order if self.owner.missions.jobs.get(r,{}).get('traffic_paused')):return False
                    if self.instruction(member['handle'].waiting_after, entry['index'], pose) != rmf.easy_traffic_light.WaitingInstruction.Resume:return False
            for member in order:self.set_paused(member,False,'Open-RMF 已放行')
            self.group_wait = None
            return True
        member = self.members.get(robot, {})
        handle = member.get('handle');entry = self.routes.get(robot)
        pose = self.pose(robot, states)
        if not self.available or not handle or not entry or pose is None:return True
        if self.owner.missions.jobs.get(robot,{}).get('traffic_paused') and not self.waiting_stopped(robot,states):return False
        checkpoint=max(entry['index'],entry.get('reported_checkpoint',0))
        instruction = (self.instruction(handle.waiting_at,0) if entry.get('rebasing') else
                       self.instruction(handle.waiting_after,checkpoint,pose))
        if instruction is REBASE_ROUTE or instruction==rmf.easy_traffic_light.WaitingInstruction.WaitingError:
            self.rebase_route(robot,pose)
            return False
        if instruction==rmf.easy_traffic_light.WaitingInstruction.Resume:entry.pop('rebasing',None)
        return instruction == rmf.easy_traffic_light.WaitingInstruction.Resume

    def rebase_route(self, robot, pose):
        entry=self.routes[robot]
        path=[list(pose)]
        for point in entry['path'][entry['index']+1:]:
            if math.dist(path[-1][:2],point[:2])>=.01:path.append(list(point))
        if len(path)<2:return
        self.members[robot]['handle'].follow_new_path(traffic_waypoints(path))
        entry.update(path=path,index=0)
        entry['rebasing']=True
        for key in ('reported_checkpoint','wait_checkpoint','instruction'):entry.pop(key,None)
        self.members[robot]['state']='NEGOTIATING'
        self.set_paused(robot,True,'Open-RMF 路径重新协商；保留当前导航动作')
        self.record('route_rebased',robot,pose=pose,points=len(path))

    def waiting_stopped(self, robot, states):
        state=states.get(robot,{})
        control=self.owner.missions.control(state)
        nav=self.owner.missions.nav(state)
        return bool(nav.get('task_id')==self.owner.missions.jobs.get(robot,{}).get('request')
                    and nav.get('traffic_paused') and state.get('fresh',{}).get('control')
                    and control.get('velocity_age',99)<.5 and max(abs(v) for v in control.get('velocity',[1.,1.]))<.02)

    def set_paused(self, robot, paused, reason):
        job=self.owner.missions.jobs.get(robot)
        if not job or job['phase']!='EXECUTING' or not job.get('request') or bool(job.get('traffic_paused'))==paused:return
        job['traffic_paused']=paused;job['message']=reason if paused else ''
        job['traffic_command_pending']=paused
        self.owner.missions.send('traffic_pause',job['request'],robot_id=robot,paused=paused,reason=reason)
        self.record('pause' if paused else 'resume',robot,reason=reason)

    def pause(self, robot):
        if not self.available:return
        mission = self.owner.missions
        job = mission.jobs.get(robot)
        if not job or job['phase'] != 'EXECUTING':return
        state = self.owner.snapshots().get(robot, {})
        if not mission.nav(state).get('navigation_active') and not mission.control(state).get('nav_active'):return
        if mission.formation.active and robot in mission.formation.saved['order']:
            self.group_wait = ('formation', robot, list(mission.formation.saved['order']))
            for member in self.group_wait[2]:self.set_paused(member,True,'Open-RMF 编队交通等待')
        elif mission.follow['active'] and robot in mission.follow['order']:
            self.group_wait = ('follow', robot, list(mission.follow['order']))
            for member in self.group_wait[2]:self.set_paused(member,True,'Open-RMF 跟随队列交通等待')
        else:self.set_paused(robot,True,'Open-RMF 交通等待')

    def tick(self, states):
        self.enroll()
        while not self.events.empty():
            kind, robot, value = self.events.get()
            member = self.members[robot]
            if kind == 'registered':member.update(handle=value, state='IDLE')
            elif kind == 'blockers':member['blockers'] = value
            elif kind == 'pause':
                member['state'] = 'WAITING'
            elif kind == 'resume':member['state'] = 'READY'
        # The callback also fires while an asynchronous replacement plan is
        # being installed. The checkpoint instruction below confirms whether
        # the current executing route actually needs to pause.
        refresh_idle = time.monotonic()-self.last_idle >= 1.
        if refresh_idle:
            self.last_idle = time.monotonic()
            self.available = any(name.startswith('rmf_traffic_blockade_node') for name, namespace in self.owner.get_node_names_and_namespaces())
        group=self.formation_reservation
        if group and not self.owner.missions.formation.active:
            group.clear();self.formation_reservation=None;self.group_wait=None;group=None
            # Put stopped members back into individual traffic scheduling.
            for r,member in self.members.items():
                p=self.pose(r,states)
                if member.get('handle') and p is not None:member['handle'].update_idle_location('fleet_map',p)
        if self.group_wait and not group:self.resumed(self.group_wait[1],states)
        for robot,job in self.owner.missions.jobs.items():
            pending=job.get('traffic_command_pending')
            if job['phase']!='EXECUTING' or pending is None:continue
            nav=self.owner.missions.nav(states.get(robot,{}))
            if nav.get('task_id')==job['request'] and nav.get('traffic_paused')==pending:
                job.pop('traffic_command_pending',None)
            else:self.owner.missions.send('traffic_pause',job['request'],robot_id=robot,paused=pending,reason=job['message'])
        if group:group.tick(states)
        for robot, member in self.members.items():
            if group and robot in group.order:
                member['state']='GROUP_WAITING' if group.paused else 'GROUP_MOVING' if group.admitted else 'GROUP_NEGOTIATING'
                continue
            handle = member['handle'];pose = self.pose(robot, states)
            if not handle or pose is None:continue
            job = self.owner.missions.jobs.get(robot, {})
            entry = self.routes.get(robot)
            if entry and job.get('id') == entry['job'] and job.get('phase') == 'EXECUTING':
                # Resume is asynchronous on the vehicle. Reporting movement
                # before its ACK makes RMF pause it again on the next tick.
                if job.get('traffic_command_pending') is not None:continue
                path = entry['path']
                if job.get('traffic_paused'):
                    member['state']='WAITING'
                    if not self.group_wait and self.resumed(robot,states):self.set_paused(robot,False,'Open-RMF 已放行')
                    continue
                if math.dist(path[-1][:2], pose[:2]) < .1:
                    self.instruction(handle.waiting_at, len(path)-1)
                    member['state'] = 'ARRIVED'
                    continue
                # RMF expects the last checkpoint passed, not the closest
                # checkpoint (which can still be ahead of the robot).
                while entry['index']<len(path)-2:
                    a,b=path[entry['index']],path[entry['index']+1]
                    if sum((pose[k]-b[k])*(b[k]-a[k]) for k in (0,1))<0:break
                    entry['index']+=1
                speed=abs(self.owner.missions.control(states.get(robot,{})).get('velocity',[0.,0.])[0])
                stopping_distance=.03+.5*speed+speed*speed/(2*.5)
                checkpoint=entry['index']
                # Report commitment past checkpoints that cannot still be
                # stopped at, as required by EasyTrafficLight.moving_from.
                waiting=entry.get('wait_checkpoint')
                if waiting is not None and waiting>checkpoint:
                    checkpoint=waiting-1
                else:
                    while checkpoint<len(path)-2 and math.dist(path[checkpoint+1][:2],pose[:2])<=stopping_distance:
                        checkpoint+=1
                # Commitment reported to RMF cannot move backwards when the
                # on-board trajectory brakes or reverses around a bend.
                checkpoint=max(checkpoint,entry.get('reported_checkpoint',0))
                instruction = self.instruction(handle.moving_from, checkpoint, pose)
                if instruction is REBASE_ROUTE or instruction==rmf.easy_traffic_light.MovingInstruction.MovingError:
                    self.rebase_route(robot,pose)
                    continue
                if instruction is None:continue
                entry['reported_checkpoint']=checkpoint
                if instruction==rmf.easy_traffic_light.MovingInstruction.WaitAtNextCheckpoint:
                    entry['wait_checkpoint']=checkpoint+1
                else:entry.pop('wait_checkpoint',None)
                signature=(checkpoint,str(instruction))
                if entry.get('instruction')!=signature:
                    entry['instruction']=signature
                    self.record('instruction',robot,checkpoint=checkpoint,passed_checkpoint=entry['index'],
                                instruction=str(instruction),pose=pose,stopping_distance=stopping_distance)
                # Nav2 already brakes and holds at the final goal. Inhibiting
                # earlier can strand it outside its configured XY tolerance.
                wait_next=(instruction==rmf.easy_traffic_light.MovingInstruction.WaitAtNextCheckpoint
                           and checkpoint+1<len(path)-1
                           and math.dist(path[checkpoint+1][:2],pose[:2])<=stopping_distance)
                if instruction==rmf.easy_traffic_light.MovingInstruction.PauseImmediately or wait_next:
                    self.pause(robot)
                else:member['state'] = 'MOVING'
            elif entry and job.get('phase') == 'RMF_PAUSED':member['state'] = 'WAITING'
            elif refresh_idle and (not entry or entry.get('job')!=job.get('id') or job.get('phase') in ('COMPLETED', 'STOPPED', 'FAILED', 'INVALIDATED')):
                self.routes.pop(robot, None)
                handle.update_idle_location('fleet_map', pose)
                member['state'] = 'IDLE'
                # Dynamic followers continue using GoalUpdater. Their current
                # physical occupancy is registered, without replacing Nav2.

    def registered(self, robot):return bool(self.members.get(robot, {}).get('handle'))

    def snapshot(self):
        return {'backend': 'open_rmf_easy_traffic_light', 'connected': self.available,
                'formation_reservation':{'members':self.formation_reservation.order,'radius':self.formation_reservation.radius,'admitted':self.formation_reservation.admitted} if self.formation_reservation else None,
                'events':list(self.audit[-20:]),
                'fallback': None if self.available else '原有车辆顺序与路径冲突仲裁',
                'robots': {r: {'registered': bool(v['handle']), 'state': v['state'], 'blockers': v['blockers']} for r, v in self.members.items()}}
