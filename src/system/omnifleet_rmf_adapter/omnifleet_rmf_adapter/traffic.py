"""Conservative corridor admission for the existing WSL mission executor."""
import copy
import json
import math
import re
import time

from .map_hub import compose

TERMINAL = ('STOPPED', 'COMPLETED', 'FAILED', 'INVALIDATED')
BODY_MARGIN = .45


def point_distance(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    t = max(0., min(1., ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy)


def crosses(path, zone):
    radius = zone['width']/2 + BODY_MARGIN
    # Sample at <= 5 cm and expand by that spacing, including segment interiors.
    for a, b in zip(path, path[1:] or path):
        steps = max(1, math.ceil(math.dist(a[:2], b[:2])/.05))
        for i in range(steps+1):
            p = [a[k]+(b[k]-a[k])*i/steps for k in (0, 1)]
            if point_distance(p, zone['a'], zone['b']) <= radius+.05:return True
    return False


def waiting_pose(zone, side):
    a, b = zone['a'], zone['b']
    yaw = math.atan2(b[1]-a[1], b[0]-a[0])
    distance = zone['width']/2 + BODY_MARGIN + .5
    endpoint, direction = (a, -1.) if side == 'a' else (b, 1.)
    return [endpoint[0]+direction*distance*math.cos(yaw),
            endpoint[1]+direction*distance*math.sin(yaw), yaw if side == 'a' else yaw+math.pi]


class Traffic:
    def __init__(self, owner):
        self.owner = owner
        self.path = owner.file.parent/'traffic.json'
        self.saved = json.loads(self.path.read_text()) if self.path.exists() else {
            'zones': [], 'binding': None, 'locks': {}, 'settings': {}}
        self.saved.setdefault('revision',0)
        self.poses, self.unknown, self.zones, self.reason = {}, [], [], ''

    def persist(self):
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.saved, ensure_ascii=False, indent=2))
        temporary.replace(self.path)

    def binding(self, states):
        reference = self.owner.config.get('central', {}).get('reference_robot') or next(iter(self.owner.maps.names))
        return [reference, self.owner.nav(states.get(reference, {})).get('localization_epoch')]

    def pose(self, robot, states):
        state = states.get(robot, {})
        sample = state.get('samples', {}).get('pose', {})
        if (robot not in self.owner.maps.valid_robots or not state.get('online')
                or not state.get('fresh', {}).get('pose')
                or sample.get('age_seconds', 0)+state.get('ipc_age_seconds', 0) > .5):return None
        p = sample.get('value', {})
        values = [p.get(k) for k in ('x', 'y', 'yaw')]
        if not all(type(v) in (int, float) and math.isfinite(v) for v in values):return None
        return compose(self.owner.maps.alignment[robot], values)

    def idle(self, robot, states):
        state = states.get(robot, {})
        control=self.owner.control(state);velocity=control.get('velocity',[])
        wheels=(len(velocity)==2 and all(type(v) in (int,float) and math.isfinite(v) for v in velocity)
                and abs(velocity[0])<.02 and abs(velocity[1])<.05 and control.get('velocity_age',99)<.5)
        return (wheels and self.pose(robot, states) is not None and state.get('fresh', {}).get('control')
                and self.owner.stopped(state) and not self.owner.nav(state).get('navigation_active')
                and self.owner.jobs.get(robot, {}).get('phase', 'STOPPED') in TERMINAL)

    def configure(self, packet, states):
        if packet.get('traffic_revision',0)!=self.saved['revision']:raise ValueError('通道配置已被另一个前端修改，请刷新后重试')
        if self.owner.follow['active'] or self.owner.formation.active:
            raise ValueError('请先停止跟随或编队，再配置窄道')
        if not all(self.idle(r, states) for r in self.owner.maps.names):
            raise ValueError('所有已接入车辆须定位有效、结束任务并停稳，才能修改通道')
        zones = packet.get('zones')
        if not isinstance(zones, list) or len(zones) > 16:raise ValueError('通道数量须为0～16')
        validated = []
        for z in zones:
            if not isinstance(z, dict) or not isinstance(z.get('id'), str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,39}', z['id']):
                raise ValueError('通道ID须以英文字母开头，仅含字母、数字、下划线或横线')
            for key in ('a', 'b'):
                if not isinstance(z.get(key), list) or len(z[key]) != 2 or not all(type(v) in (int, float) and math.isfinite(v) for v in z[key]):
                    raise ValueError('通道两端须为共享地图中的有限x、y坐标')
            if not .2 <= math.dist(z['a'], z['b']) <= 100:raise ValueError('通道长度须为0.2～100m')
            if type(z.get('width')) not in (int, float) or not math.isfinite(z['width']) or not .2 <= z['width'] <= 20:
                raise ValueError('通道宽度须为0.2～20m')
            validated.append({k: copy.deepcopy(z[k]) for k in ('id', 'a', 'b', 'width')})
        if len({z['id'] for z in validated}) != len(validated):raise ValueError('通道ID不能重复')
        if self.saved['locks']:raise ValueError('通道仍被占用或停止未确认，不能删除或修改')
        if any(crosses([self.pose(r, states)], z) for r in self.owner.maps.names for z in self.saved['zones']):
            raise ValueError('车辆仍在原通道内，不能修改保护区域')
        self.saved.update(zones=validated, binding=self.binding(states),revision=self.saved['revision']+1)
        self.persist();self.tick(states)
        return {'phase': 'saved', 'message': '通道已保存；没有发车。一次仅放行一辆，已占用者不被抢占'}

    def settings(self, robot, packet):
        title = packet.get('title', '').strip() if isinstance(packet.get('title', ''), str) else ''
        if len(title) > 80:raise ValueError('任务标题最多80字')
        values = {k: packet.get(k, 0) for k in ('task_priority', 'local_priority', 'not_before')}
        if any(type(values[k]) is not int or not 0 <= values[k] <= 100 for k in ('task_priority', 'local_priority')):
            raise ValueError('优先级须为0～100的整数，数值越大越优先')
        if type(values['not_before']) not in (int, float) or not math.isfinite(values['not_before']) or values['not_before'] < 0:
            raise ValueError('计划时间无效')
        self.saved['settings'][robot] = dict(values, title=title)
        job = self.owner.jobs.get(robot)
        if job and job['phase'] not in TERMINAL:
            job.update(**self.saved['settings'][robot])
        self.persist()
        return {'phase': 'saved', 'message': '计划时间已保存；优先顺序由车辆列表决定'}

    def order(self):
        formation = self.owner.formation
        preferred = (formation.saved['order'] if formation.active else self.owner.follow['order']
                     if self.owner.follow['active'] else self.saved.get('order', self.owner.follow['order']))
        return list(dict.fromkeys([r for r in preferred if r in self.owner.maps.names]+list(self.owner.maps.names)))

    def rank(self, robot):
        order = self.order()
        return order.index(robot) if robot in order else len(order)

    def priority(self, robot):
        dispatch = self.owner.goal_dispatch.state
        if dispatch['active']:
            pose = self.poses.get(robot)
            distance = math.dist(pose[:2], dispatch['goal'][:2]) if pose else math.inf
            return distance, self.rank(robot)
        return 0., self.rank(robot)

    def set_order(self, packet):
        if packet.get('order_revision', 0) != self.saved.get('order_revision', 0):
            raise ValueError('车辆顺序已被另一个前端修改，请刷新后重试')
        order = packet.get('order')
        if (not isinstance(order, list) or any(not isinstance(r, str) for r in order)
                or len(order) != len(set(order)) or set(order) != set(self.owner.maps.names)):
            raise ValueError('顺序须完整包含所有已接入车辆，且不能重复；新车接入后请刷新')
        if self.owner.follow['active'] or self.owner.formation.active:
            raise ValueError('请先停止跟随或编队，再调整车辆顺序')
        self.saved.update(order=list(order), order_revision=self.saved.get('order_revision', 0)+1)
        self.persist()
        self.owner.follow['order'] = list(order)
        return {'phase': 'saved', 'message': '车辆顺序已同步：领车优先，其后按列表顺序；不抢占正在执行的任务'}

    def tick(self, states):
        self.poses = {r: p for r in self.owner.maps.names if (p := self.pose(r, states)) is not None}
        self.unknown = [r for r in self.owner.maps.names if r not in self.poses]
        self.reason = ''
        if self.saved['zones']:
            if self.binding(states) != self.saved['binding']:self.reason = '参考地图会话已变化，请停稳并重新标定通道'
            elif self.unknown:self.reason = '车辆位置无法确认：'+', '.join(self.unknown)
        changed = False
        zones = []
        for zone in self.saved['zones']:
            occupants = [r for r, p in self.poses.items() if crosses([p], zone)]
            lock = self.saved['locks'].get(zone['id'])
            if lock and not self.reason and lock['robot'] not in occupants and self.idle(lock['robot'], states):
                self.saved['locks'].pop(zone['id']);lock = None;changed = True
            intrusion = [r for r in occupants if not lock or r != lock['robot']]
            if self.reason or intrusion:
                for r, job in list(self.owner.jobs.items()):
                    if job['phase'] == 'EXECUTING' and (self.reason or r in intrusion or (lock and r == lock['robot'])):
                        self.owner.stop(r, self.reason or '通道存在未获路权车辆：'+', '.join(intrusion), 'FAILED')
            zones.append({**zone, 'owner': lock['robot'] if lock else None, 'occupants': occupants,
                          'state': 'BLOCKED' if self.reason or intrusion else 'OCCUPIED' if lock else 'FREE',
                          'message': self.reason or ('通道内车辆：'+', '.join(intrusion) if intrusion else ''),
                          'wait_a': waiting_pose(zone, 'a'), 'wait_b': waiting_pose(zone, 'b')})
        self.zones = zones
        if changed:self.persist()

    def acquire(self, robot, job, path, reserve=True):
        if not self.saved['zones']:return True, ''
        needed = [z for z in self.zones if crosses(path, z) or z['id'] == job.get('corridor')]
        job['resources'] = [z['id'] for z in needed]
        if self.reason:return False, self.reason
        for zone in needed:
            if zone['owner'] and zone['owner'] != robot:return False, '等待通道 '+zone['id']+'：'+zone['owner']+' 持有路权'
            if any(r != robot for r in zone['occupants']):return False, '通道 '+zone['id']+' 尚有其他车辆，不能放行'
        if not reserve:return True, ''
        changed = False
        for zone in needed:
            if zone['id'] not in self.saved['locks']:
                self.saved['locks'][zone['id']] = {'robot': robot, 'job_id': job['id'], 'acquired_at': time.time()}
                zone['owner'] = robot;zone['state'] = 'OCCUPIED';changed = True
        if changed:self.persist()
        return True, ''

    def recover(self, packet, states):
        if packet.get('acknowledge') != '通道已清空':raise ValueError('须现场确认通道已清空')
        if not all(self.idle(r, states) for r in self.owner.maps.names):raise ValueError('所有车辆须定位有效、结束任务并停稳')
        if any(crosses([self.pose(r, states)], z) for r in self.owner.maps.names for z in self.saved['zones']):
            raise ValueError('仍有车辆在通道保护范围内，不能释放')
        self.saved.update(locks={}, binding=self.binding(states));self.persist();self.tick(states)
        return {'phase': 'saved', 'message': '已确认通道清空并重新绑定当前参考地图；旧任务不会续跑'}

    def snapshot(self):
        zones=copy.deepcopy(self.zones)
        for zone in zones:
            zone['queue']=[r for r,j in sorted(self.owner.jobs.items(),key=lambda item:(self.priority(item[0]),item[1]['priority']))
                           if j['phase'] not in TERMINAL and zone['id'] in j.get('resources',[]) and zone['owner']!=r]
        return {'zones': zones, 'settings': copy.deepcopy(self.saved['settings']),
                'message': self.reason, 'policy': 'distance_then_order' if self.owner.goal_dispatch.state['active'] else 'vehicle_order', 'order': self.order(),
                'order_revision': self.saved.get('order_revision', 0), 'order_configured': 'order' in self.saved,
                'revision':self.saved['revision'], 'scope': '列表第1辆为领车且新任务路权最高，后续车辆按拖动顺序依次降低；已进入冲突区或正在执行的车辆不抢占；本地避障与停车确认继续生效'}

    def rows(self):
        rows = []
        order = self.order()
        for robot in order:
            job = self.owner.jobs.get(robot, {})
            route = self.owner.saved['routes'].get(robot, {})
            points = job.get('points') or route.get('points', [])
            target = points[-1]['pose'] if points else None
            settings = self.saved['settings'].get(robot, {})
            rows.append({'car': robot, 'title': job.get('title', settings.get('title', '')),
                         'pose': self.poses.get(robot), 'init_pose': job.get('init_pose'),
                         'target_pose': compose(self.owner.maps.alignment[robot], target) if target and robot in self.owner.maps.valid_robots else None,
                         'task_priority': len(order)-order.index(robot),
                         'local_priority': len(order)-order.index(robot), 'dispatch_index': order.index(robot)+1,
                         'distance_to_dispatch_goal': self.priority(robot)[0] if self.owner.goal_dispatch.state['active'] and robot in self.poses else None,
                         'not_before': job.get('not_before', settings.get('not_before', 0)),
                         'created_at': job.get('created_at'), 'phase': job.get('phase', 'IDLE'),
                         'message': job.get('message', ''), 'resources': job.get('resources', [])})
        return rows
