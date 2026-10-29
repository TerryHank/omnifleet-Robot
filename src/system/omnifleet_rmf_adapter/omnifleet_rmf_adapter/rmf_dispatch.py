"""The existing mission executor as an Open-RMF bidding and dispatch fleet."""
import copy
import json
import math
import time
import uuid

from rclpy.qos import QoSProfile, DurabilityPolicy
from rmf_task_msgs.msg import ApiRequest, ApiResponse, BidNotice, BidResponse, DispatchCommand, DispatchAck, DispatchStates, TaskSummary
from .map_hub import compose, inverse


MOTION_OPS = ('single_goal', 'route_add', 'route_start', 'formation_start', 'follow_start')
TERMINAL = ('COMPLETED', 'STOPPED', 'FAILED', 'INVALIDATED')


class RmfDispatch:
    def __init__(self, owner):
        self.owner = owner
        self.session = uuid.uuid4().hex
        self.pending, self.tasks = {}, {}
        latched = QoSProfile(depth=20, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.api = owner.create_publisher(ApiRequest, '/task_api_requests', latched)
        self.bids = owner.create_publisher(BidResponse, '/rmf_task/bid_response', 20)
        self.acks = owner.create_publisher(DispatchAck, '/rmf_task/dispatch_ack', latched)
        self.summaries = owner.create_publisher(TaskSummary, '/task_summaries', 20)
        owner.create_subscription(ApiResponse, '/task_api_responses', self.response, latched)
        owner.create_subscription(BidNotice, '/rmf_task/bid_notice', self.bid, 20)
        owner.create_subscription(DispatchCommand, '/rmf_task/dispatch_request', self.award, latched)
        owner.create_subscription(DispatchStates, '/dispatch_states', self.dispatch_states, 20)
        self.last_publish = 0.

    def fleet(self, robot):return 'omnifleet_'+robot

    def submit(self, packet, states):
        identifier = packet.get('id') or 'rmf-'+uuid.uuid4().hex
        if identifier in self.pending:return {'phase': 'queued', 'message': 'Open-RMF 正在分配任务'}
        request = copy.deepcopy(packet)
        request['id'] = identifier
        request['rmf_session'] = self.session
        record = {'request_id': identifier, 'packet': request, 'phase': 'QUEUED', 'submitted_at': time.time(), 'message': '等待 Open-RMF 竞标分配'}
        self.pending[identifier] = record
        return {'phase': 'queued', 'message': '任务已提交 Open-RMF，等待分配', 'rmf_request_id': identifier}

    def send_next(self):
        # Humble's auctioneer must finish its current bid before the next
        # request is published; otherwise rapidly appended goals lose bids.
        if any(v.get('sent_at') and v['phase'] in ('QUEUED', 'ASSIGNED') for v in self.pending.values()):return
        record = next((v for v in self.pending.values() if v['phase'] == 'QUEUED' and not v.get('sent_at')), None)
        if not record:return
        identifier, request = record['request_id'], record['packet']
        task = {'category': 'compose', 'description': {'category': 'omnifleet', 'phases': [
            {'activity': {'category': 'perform_action', 'description': {'category': 'omnifleet_motion', 'description': request}}}]},
            'unix_millis_earliest_start_time': int(time.time()*1000)}
        self.api.publish(ApiRequest(request_id=identifier, json_msg=json.dumps({'type': 'dispatch_task_request', 'request': task})))
        record['sent_at'] = time.time()

    def response(self, message):
        record = self.pending.get(message.request_id)
        if not record:return
        value = json.loads(message.json_msg)
        if value.get('success'):
            task = value.get('state', {}).get('booking', {}).get('id')
            if task:record['task_id'] = task;self.tasks[task] = record
        else:
            record.update(phase='FAILED', message='Open-RMF 未分配：'+json.dumps(value.get('errors', []), ensure_ascii=False))
            self.owner.ui_results[record['request_id']] = {'phase': 'rejected', 'message': record['message']}

    def bid(self, notice):
        try:
            request = json.loads(notice.request)
            description = request['description']
            if description.get('category') != 'omnifleet':return
            packet = description['phases'][0]['activity']['description']['description']
            if packet.get('rmf_session') != self.session:return
            record = self.pending.get(packet['id'])
            if not record or record['phase'] != 'QUEUED':return
            record['task_id'] = notice.task_id;self.tasks[notice.task_id] = record
            states = self.owner.snapshots()
            order = self.owner.missions.traffic.order()
            chosen = packet.get('robot_id') or (packet.get('order') or [None])[0]
            robots = [chosen] if chosen else order
            if not chosen:
                idle = [r for r in robots if self.owner.missions.jobs.get(r, {}).get('phase', 'STOPPED') in TERMINAL]
                if idle:robots = idle
            for robot in robots:
                if robot not in self.owner.maps.names:continue
                # Explicit assignments retain existing admission checks in Missions.
                # Automatic allocation considers currently online members.
                if not chosen and not states.get(robot, {}).get('online'):continue
                pose = self.owner.maps.state.get('poses', {}).get(robot, [0., 0., 0.])
                goals = packet.get('shared_points') or []
                distance = math.dist(pose[:2], goals[0]['pose'][:2]) if goals else 0.
                cost = distance/.2+self.owner.missions.traffic.rank(robot)*.001
                active = self.owner.missions.jobs.get(robot, {}).get('phase', 'STOPPED') not in TERMINAL
                if not chosen and active:
                    job = self.owner.missions.jobs[robot]
                    remaining = job.get('path') or [pose, *[p['pose'] for p in job.get('points', [])[job.get('index', 0):]]]
                    cost += sum(math.dist(a[:2], b[:2]) for a, b in zip(remaining, remaining[1:]))/.2
                response = BidResponse(task_id=notice.task_id, has_proposal=True)
                response.proposal.fleet_name = self.fleet(robot)
                response.proposal.expected_robot_name = self.owner.config['central']['assignments'][robot]['robot_name']
                response.proposal.prev_cost = 0.;response.proposal.new_cost = cost
                finish = time.time()+cost+1.
                response.proposal.finish_time.sec = int(finish)
                response.proposal.finish_time.nanosec = int((finish-int(finish))*1e9)
                self.bids.publish(response)
        except (KeyError, TypeError, ValueError):return

    def award(self, message):
        robot = next((r for r in self.owner.maps.names if self.fleet(r) == message.fleet_name), None)
        if robot is None:return
        record = self.tasks.get(message.task_id)
        success = False;errors = []
        if message.type == DispatchCommand.TYPE_REMOVE:
            if record:record.update(phase='STOPPED', message='Open-RMF 已取消任务')
            if record and record.get('robot') == robot:
                op = record['packet']['op']
                if op in ('formation_start', 'follow_start'):self.owner.missions.command({'op': op.replace('_start', '_stop')}, self.owner.snapshots())
                else:self.owner.missions.stop(robot, 'Open-RMF 取消任务')
            success = True
        elif record and record['phase'] not in ('QUEUED', 'ASSIGNED'):
            success = record['phase'] not in ('FAILED', 'STOPPED')
        elif record:
            packet = copy.deepcopy(record['packet'])
            packet['robot_id'] = robot
            packet['_rmf_awarded'] = True
            record.update(robot=robot, phase='ASSIGNED', assigned_at=time.time())
            try:
                if packet.get('shared_points'):
                    points = [{**point, 'pose': compose(inverse(self.owner.maps.alignment[robot]), point['pose'])} for point in packet.pop('shared_points')]
                    if packet.pop('kind', 'single') == 'single':packet.update(op='single_goal', point=points[0])
                    else:
                        self.owner.missions.command({'op': 'route_save', 'robot_id': robot, 'points': points}, self.owner.snapshots())
                        packet.update(op='route_start')
                self.owner.missions.current_rmf_task_id = message.task_id
                result = self.owner.missions.command(packet, self.owner.snapshots())
                job = self.owner.missions.jobs.get(robot)
                if job and packet['op'] not in ('formation_start', 'follow_start'):
                    if job.get('replacement'):job['replacement']['rmf_task_id'] = message.task_id
                    else:job['rmf_task_id'] = message.task_id
                record.update(phase='EXECUTING', message='Open-RMF 已分配，由车端导航执行')
                self.owner.ui_results[record['request_id']] = {**result, 'rmf_task_id': message.task_id, 'assigned_robot': robot}
                success = True
            except (ValueError, RuntimeError, TypeError, KeyError) as error:
                record.update(phase='FAILED', message=str(error));errors.append(str(error))
                self.owner.ui_results[record['request_id']] = {'phase': 'rejected', 'message': str(error), 'rmf_task_id': message.task_id}
            finally:self.owner.missions.current_rmf_task_id = None
        self.acks.publish(DispatchAck(dispatch_id=message.dispatch_id, success=success, errors=errors))

    def dispatch_states(self, message):
        for value in [*message.active, *message.finished]:
            record = self.tasks.get(value.task_id)
            if record:
                record['dispatch_status'] = value.status
                if value.status == value.STATUS_FAILED_TO_ASSIGN:
                    record.update(phase='FAILED', message='Open-RMF 未找到可分配车辆：'+'；'.join(value.errors))
                    self.owner.ui_results[record['request_id']] = {'phase': 'rejected', 'message': record['message']}

    def cancel_pending(self, robot=None, group=None, routes_only=False):
        for record in self.pending.values():
            packet = record['packet']
            if record['phase'] != 'QUEUED':continue
            if group and packet['op'] not in ((group,) if isinstance(group, str) else group):continue
            if routes_only and packet['op'] not in ('single_goal', 'route_add', 'route_start'):continue
            chosen = packet.get('robot_id') or (packet.get('order') or [None])[0]
            if robot and chosen != robot:continue
            record.update(phase='STOPPED', message='操作者取消尚未开始的 RMF 任务')
            self.owner.ui_results[record['request_id']] = {'phase': 'accepted', 'message': record['message']}

    def tick(self, states):
        if self.api.get_subscription_count() == 0:
            for record in self.pending.values():
                if record['phase'] == 'QUEUED' and record.get('sent_at'):
                    record.update(phase='FAILED', message='Open-RMF 分配服务连接中断，请重新提交任务')
                    self.owner.ui_results[record['request_id']] = {'phase': 'rejected', 'message': record['message']}
        self.send_next()
        for record in self.pending.values():
            if record['phase'] != 'EXECUTING':continue
            packet = record['packet'];robot = record['robot']
            takeover=getattr(self.owner.missions,'pending_cooperative',None)
            if takeover and takeover['request'].get('id')==record['request_id']:
                record.update(group_phase='HANDOVER',message='协同优先接管：结束原任务并确认停稳')
                continue
            if packet['op'] in ('formation_start', 'follow_start'):
                group = self.owner.missions.formation.snapshot() if packet['op'] == 'formation_start' else self.owner.missions.follow
                label = {'WAIT_TRAIL':'等待领车轨迹', 'FOLLOWING':'跟随中', 'WAIT_MAP':'等待地图', 'HANDOVER':'等待队列交接', 'BLOCKED':'跟随受阻', 'RMF_PAUSED':'等待 RMF 交通恢复'}.get(group['phase'], '编组运行中')
                record.update(group_phase=group['phase'], members=list(packet['order']), message=group.get('message') or label)
                if packet['op'] == 'formation_start':record['position_errors'] = group['position_errors']
                if not group['active']:record.update(phase='FAILED' if group['phase'] == 'FAILED' else 'STOPPED', message=group.get('message', '编组已停止'))
            else:
                job = self.owner.missions.jobs.get(robot, {})
                if job.get('rmf_task_id') == record.get('task_id'):
                    record.update(phase=job.get('phase', 'EXECUTING'), message=job.get('message', ''), progress=job.get('index', 0), points=len(job.get('points', [])))
                    if record['phase'] not in TERMINAL:record['phase'] = 'EXECUTING'
                elif job and not job.get('replacement'):record.update(phase='STOPPED', message='已由新的任务替换')
        if time.monotonic()-self.last_publish >= 1.:
            self.last_publish = time.monotonic()
            for task_id, record in self.tasks.items():
                robot = record.get('robot')
                if not robot:continue
                summary = TaskSummary(fleet_name=self.fleet(robot), task_id=task_id, robot_name=self.owner.config['central']['assignments'][robot]['robot_name'],
                    state={'QUEUED': 0, 'EXECUTING': 1, 'COMPLETED': 2, 'FAILED': 3, 'INVALIDATED': 3, 'STOPPED': 4}.get(record['phase'], 0), status=record.get('message', ''))
                summary.task_profile.task_id = task_id
                summary.submission_time.sec = int(record['submitted_at'])
                summary.start_time.sec = int(record.get('assigned_at', 0))
                if record['phase'] in TERMINAL:
                    record.setdefault('finished_at', time.time());summary.end_time.sec = int(record['finished_at'])
                self.summaries.publish(summary)
        while len(self.pending) > 128:
            key = next((k for k, v in self.pending.items() if v['phase'] in TERMINAL), None)
            if key is None:break
            task = self.pending.pop(key).get('task_id')
            if task:self.tasks.pop(task, None)

    def snapshot(self):
        return {'backend': 'open_rmf_dispatcher', 'connected': self.api.get_subscription_count() > 0,
                'tasks': [{k: v for k, v in value.items() if k != 'packet'} for value in self.pending.values()]}
