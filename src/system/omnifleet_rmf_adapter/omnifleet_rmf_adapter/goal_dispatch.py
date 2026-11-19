"""Distance-first, one-at-a-time visits to a shared-map target."""
import copy
import math
import uuid

from .map_hub import compose, inverse
from .traffic import TERMINAL


class GoalDispatch:
    def __init__(self, owner):
        self.owner = owner
        self.state = {'active': False, 'phase': 'IDLE', 'goal': None,
                      'mode': 'nearest', 'pending': [], 'arrived': [], 'completed': [], 'current': None,
                      'message': '', 'ranking': []}

    def ranking(self, robots, states, destinations):
        result = []
        for robot in robots:
            pose = self.owner.traffic.pose(robot, states)
            if pose is None:continue
            try: _,_,length=self.owner.roads.itinerary(robot,pose,destinations)
            except ValueError:continue
            result.append({'robot': robot, 'distance':length,'order': self.owner.traffic.rank(robot)+1})
        return sorted(result, key=lambda row: (row['distance'] if row['distance'] is not None else math.inf,
                                               row['order']))

    def command(self, request, states):
        if request['op'] == 'dispatch_stop':
            self.stop('操作者停止目标调度')
            return {'phase': 'accepted', 'message': self.state['message']}
        from .missions import points
        destinations=points(request['points'] if 'points' in request else [request['point']])
        goal=destinations[-1]['pose']
        if request.get('road_revision',self.owner.roads.data['revision'])!=self.owner.roads.data['revision']:
            raise ValueError('路网已更新，请刷新路线后派车')
        if not self.owner.roads.data['edges']:raise ValueError('请先保存路网并连接路段，再派车')
        if not self.owner.rmf_dispatch.api.get_subscription_count():
            raise ValueError('Open-RMF Dispatcher 未连接')
        mode = request.get('mode', 'nearest')
        if mode not in ('nearest', 'all'):
            raise ValueError('请选择最近车辆或全部车辆')
        candidates = [r for r in self.owner.maps.names if self.available(r, states)] if mode == 'nearest' else [
            r for r in self.owner.maps.names if states.get(r, {}).get('online')
            and r in self.owner.maps.valid_robots and self.owner.config['robots'][r].get('motion_enabled', False)]
        ranking = self.ranking(candidates, states, destinations)
        if not ranking:
            raise ValueError('没有可沿路网到达目标的就绪车辆，请检查路点连通性和车辆状态')
        if self.owner.follow['active'] or self.owner.formation.active:
            self.owner.command({'op': 'follow_stop'}, states)
        self.stop('新调度目标替换旧目标')
        members = [row['robot'] for row in ranking]
        self.state = {'id': uuid.uuid4().hex, 'active': True, 'phase': 'WAITING', 'goal': goal,
                      'mode': mode, 'pending': list(members), 'arrived': [], 'completed': [], 'current': None,
                      'origins': {}, 'leg': 'OUTBOUND',
                      'destinations':destinations,
                      'message': '目标已接收，按距离优先、列表顺序其次依次放行', 'ranking': ranking,
                      'epochs': {r: self.owner.nav(states[r]).get('localization_epoch') for r in members}}
        self.tick(states)
        return {'phase': 'accepted', 'message': self.state['message'], 'selected': members}

    def available(self, robot, states):
        owner = self.owner
        state = states.get(robot, {})
        return (owner.ready(robot, states) and owner.traffic.pose(robot, states) is not None
                and owner.config['robots'][robot].get('motion_enabled', False)
                and not owner.formation.manual_active(owner.control(state))
                and owner.jobs.get(robot, {}).get('phase', 'STOPPED') in TERMINAL
                and not owner.nav(state).get('navigation_active') and owner.stopped(state))

    def stop(self, message):
        state = self.state
        request_id = state.pop('rmf_request', None)
        if request_id:
            record = self.owner.rmf_dispatch.pending.get(request_id)
            if record and record['phase']=='QUEUED':
                record.update(phase='STOPPED', message=message)
        current = state['current']
        if state['active'] and current:
            job = self.owner.jobs.get(current, {})
            if job.get('dispatch_id') == state.get('id'):
                self.owner.stop(current, message)
        state.update(active=False, phase='STOPPED', pending=[], message=message)

    def tick(self, states):
        state, owner = self.state, self.owner
        if not state['active']:
            return
        if state.get('rmf_request'):
            record=owner.rmf_dispatch.pending.get(state['rmf_request'],{})
            if record.get('phase') in ('FAILED','STOPPED','INVALIDATED'):
                state.update(active=False,phase=record['phase'],message=record['message'])
            return
        state['ranking'] = self.ranking(state['pending'], states, state['destinations'])
        current = state['current']
        if current:
            job = owner.jobs.get(current, {})
            if job.get('dispatch_id') != state['id']:
                self.stop('当前车辆已被其他任务接管；目标调度已结束')
                return
            phase = job['phase']
            if phase == 'COMPLETED':
                if state['leg'] == 'OUTBOUND':
                    state['arrived'].append(current)
                    if state['mode'] == 'all':
                        if not self.enqueue(current, state['origins'][current], states, '返回出发位置'):
                            return
                        state.update(leg='RETURNING', phase='RETURNING', message=current+'：已到达目标，正在返回出发位置')
                        return
                state['completed'].append(current)
                state['current'] = None
            elif phase in ('STOPPED', 'FAILED', 'INVALIDATED', 'CANCEL_UNCONFIRMED'):
                state.update(active=False, phase='FAILED', message=current+'：'+job.get('message', phase))
                return
            else:
                state.update(phase='RETURNING' if state['leg']=='RETURNING' else phase,
                             message=current+'：'+(job.get('message') or ('正在返回出发位置' if state['leg']=='RETURNING' else '正在前往目标')))
                return
        if not state['pending']:
            state.update(active=False, phase='COMPLETED', message='参与车辆已依次到达目标并返回' if state['mode']=='all' else '最近车辆已到达目标')
            return
        ranking = self.ranking(state['pending'], states, state['destinations'])
        state['ranking'] = ranking
        if not ranking:
            state.update(active=False,phase='FAILED',message='剩余车辆无法沿路网到达目标')
            return
        robot = ranking[0]['robot']
        if owner.nav(states.get(robot, {})).get('localization_epoch') != state['epochs'][robot]:
            state.update(active=False, phase='INVALIDATED', message=robot+'：定位会话已变化，请重新发布目标')
            return
        if not self.available(robot, states):
            reason=owner.nav(states.get(robot,{})).get('readiness_reason')
            state.update(phase='WAITING', message='等待 '+robot+'：'+reason if reason else '等待 '+robot+' 的导航、定位、调度许可或当前任务结束')
            return
        if not self.enqueue(robot, state['goal'], states, '调度目标'):
            return

    def enqueue(self, robot, goal, states, name):
        state, owner = self.state, self.owner
        if owner.nav(states[robot]).get('localization_epoch') != state['epochs'][robot]:
            state.update(active=False, phase='INVALIDATED', message=robot+'：定位会话已变化，请重新发布目标')
            return False
        request = {'op':'dispatch_visit','dispatch_id':state['id'],
                   'shared_points':[{'name':name,'pose':goal}] if name=='返回出发位置' else state['destinations'],
                   'returning':name=='返回出发位置','road_revision':owner.roads.data['revision']}
        if state['mode']=='all':request['robot_id']=robot
        try: result=owner.rmf_dispatch.submit(request,states)
        except ValueError as error:
            state.update(active=False,phase='FAILED',message=str(error))
            return False
        state.update(rmf_request=result['rmf_request_id'],phase='QUEUED',message='等待 Open-RMF 分配')
        return True

    def awarded(self, packet, states):
        state, owner, robot = self.state, self.owner, packet['robot_id']
        if (not state['active'] or state['id'] != packet['dispatch_id']
                or state.get('rmf_request') != packet['id']):
            raise ValueError('调度请求已取消或替换')
        if not self.available(robot,states) or owner.nav(states[robot]).get('localization_epoch') != state['epochs'].get(robot):
            raise ValueError('获配车辆或地图状态已变化')
        returning = state.get('current') == robot and robot in state['arrived']
        if packet['road_revision']!=owner.roads.data['revision']:raise ValueError('竞标期间路网已修改，请重新派车')
        names,route,_=owner.roads.itinerary(robot,owner.traffic.pose(robot,states),packet['shared_points'],returning)
        local=[{**p,'pose':compose(inverse(owner.maps.alignment[robot]),p['pose'])} for p in route]
        owner.enqueue(robot,local,'dispatch',state['epochs'][robot])
        owner.jobs[robot].update(dispatch_id=state['id'],road_nodes=names)
        state.update(road_nodes=names,road_revision=packet['road_revision'])
        if not returning:
            state['origins'][robot]=owner.traffic.pose(robot,states)
            if state['mode']=='nearest':state['pending']=[]
            else:state['pending'].remove(robot)
        state.pop('rmf_request',None)
        state.update(current=robot,leg='RETURNING' if returning else 'OUTBOUND',phase='ARMING',
                     message='Open-RMF 已分配给 '+robot)
        return {'phase':'accepted','message':state['message']}

    def snapshot(self):
        return copy.deepcopy(self.state)
