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

    def ranking(self, robots, states, goal):
        result = []
        for robot in robots:
            pose = self.owner.traffic.pose(robot, states)
            result.append({'robot': robot, 'distance': math.dist(pose[:2], goal[:2]) if pose else None,
                           'order': self.owner.traffic.rank(robot) + 1})
        return sorted(result, key=lambda row: (row['distance'] if row['distance'] is not None else math.inf,
                                               row['order']))

    def command(self, request, states):
        if request['op'] == 'dispatch_stop':
            self.stop('操作者停止目标调度')
            return {'phase': 'accepted', 'message': self.state['message']}
        from .missions import points
        goal = points([request['point']])[0]['pose']
        mode = request.get('mode', 'nearest')
        if mode not in ('nearest', 'all'):
            raise ValueError('请选择最近车辆或全部车辆')
        candidates = [r for r in self.owner.maps.names if self.available(r, states)] if mode == 'nearest' else [
            r for r in self.owner.maps.names if states.get(r, {}).get('online')
            and r in self.owner.maps.valid_robots and self.owner.config['robots'][r].get('motion_enabled', False)]
        ranking = self.ranking(candidates, states, goal)
        if not ranking:
            raise ValueError('没有可接收目标的在线空闲车辆；请查看车辆导航、定位和调度许可')
        if self.owner.follow['active'] or self.owner.formation.active:
            self.owner.command({'op': 'follow_stop'}, states)
        self.stop('新调度目标替换旧目标')
        members = [row['robot'] for row in ranking] if mode == 'all' else [ranking[0]['robot']]
        self.state = {'id': uuid.uuid4().hex, 'active': True, 'phase': 'WAITING', 'goal': goal,
                      'mode': mode, 'pending': list(members), 'arrived': [], 'completed': [], 'current': None,
                      'origins': {}, 'leg': 'OUTBOUND',
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
        state['ranking'] = self.ranking(state['pending'], states, state['goal'])
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
        ranking = self.ranking(state['pending'], states, state['goal'])
        state['ranking'] = ranking
        robot = ranking[0]['robot']
        if owner.nav(states.get(robot, {})).get('localization_epoch') != state['epochs'][robot]:
            state.update(active=False, phase='INVALIDATED', message=robot+'：定位会话已变化，请重新发布目标')
            return
        if not self.available(robot, states):
            reason=owner.nav(states.get(robot,{})).get('readiness_reason')
            state.update(phase='WAITING', message='等待 '+robot+'：'+reason if reason else '等待 '+robot+' 的导航、定位、调度许可或当前任务结束')
            return
        state['origins'][robot] = owner.traffic.pose(robot, states)
        if not self.enqueue(robot, state['goal'], states, '调度目标'):
            return
        state['pending'].remove(robot)
        state.update(current=robot, leg='OUTBOUND', phase='ARMING', message=robot+'：已按距离路权放行，准备前往目标')
        owner.event(state['message'])

    def enqueue(self, robot, goal, states, name):
        state, owner = self.state, self.owner
        if owner.nav(states[robot]).get('localization_epoch') != state['epochs'][robot]:
            state.update(active=False, phase='INVALIDATED', message=robot+'：定位会话已变化，请重新发布目标')
            return False
        local = compose(inverse(owner.maps.alignment[robot]), goal)
        owner.enqueue(robot, [{'name': name, 'pose': local}], 'dispatch', state['epochs'][robot])
        owner.jobs[robot]['dispatch_id'] = state['id']
        return True

    def snapshot(self):
        return copy.deepcopy(self.state)
