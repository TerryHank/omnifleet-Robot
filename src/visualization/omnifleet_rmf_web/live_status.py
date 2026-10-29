import copy
import json
import threading
import time

from rclpy.qos import DurabilityPolicy, QoSProfile
from rcl_interfaces.srv import GetParameters
from rmf_task_msgs.msg import DispatchStates
from rmf_task_msgs.srv import GetDispatchStates
from rmf_traffic_msgs.msg import Participants, ScheduleQueries
from rosidl_runtime_py.convert import message_to_ordereddict
from std_msgs.msg import String


class LiveStatus:
    def __init__(self, node):
        self.node = node
        self.lock = threading.Lock()
        self.report = None
        self.report_at = None
        self.report_count = 0
        self.dispatch = None
        self.dispatch_at = None
        self.dispatch_count = 0
        self.rpc_at = None
        self.rpc_success = False
        self.rpc_count = 0
        self.participants = None
        self.queries = None
        self.pending = None
        self.pending_at = 0
        self.schedule_client = None
        self.schedule_service = None
        self.schedule_pending = None
        self.schedule_pending_at = 0
        self.schedule_rpc_at = None
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.subscriptions = [
            node.create_subscription(String, '/omnifleet/rmf/connection_status', self.receive_report, 10),
            node.create_subscription(DispatchStates, '/dispatch_states', self.receive_dispatch, 10),
            node.create_subscription(Participants, '/rmf_traffic/participants', self.receive_participants, latched),
            node.create_subscription(ScheduleQueries, '/rmf_traffic/registered_queries', self.receive_queries, latched),
        ]
        self.client = node.create_client(GetDispatchStates, '/get_dispatches')
        self.timer = node.create_timer(2.0, self.query_dispatches)

    def receive_report(self, message):
        try:
            report = json.loads(message.data)
            if report.get('schema') != 1 or not isinstance(report.get('robots'), dict):
                return
        except (ValueError, AttributeError):
            return
        with self.lock:
            self.report = report
            self.report_at = time.monotonic()
            self.report_count += 1

    def receive_dispatch(self, message):
        with self.lock:
            self.dispatch = message_to_ordereddict(message)
            self.dispatch_at = time.monotonic()
            self.dispatch_count += 1

    def receive_participants(self, message):
        with self.lock:
            self.participants = message_to_ordereddict(message)

    def receive_queries(self, message):
        with self.lock:
            self.queries = message_to_ordereddict(message)

    def query_dispatches(self):
        self.query_schedule()
        now = time.monotonic()
        if self.pending is not None and not self.pending.done():
            if now - self.pending_at <= 3.0:
                return
            self.pending.cancel()
        if self.client.service_is_ready():
            self.pending_at = now
            self.pending = self.client.call_async(GetDispatchStates.Request())
            self.pending.add_done_callback(self.dispatch_reply)

    def query_schedule(self):
        services = [name for name, types in self.node.get_service_names_and_types()
                    if name.startswith('/rmf_traffic_schedule_node_') and name.endswith('/get_parameters')
                    and 'rcl_interfaces/srv/GetParameters' in types]
        if len(services) != 1:
            return
        now = time.monotonic()
        if self.schedule_pending is not None and not self.schedule_pending.done():
            if now - self.schedule_pending_at <= 3:
                return
            self.schedule_pending.cancel()
        if services[0] != self.schedule_service:
            if self.schedule_client is not None:
                self.node.destroy_client(self.schedule_client)
            self.schedule_service = services[0]
            self.schedule_client = self.node.create_client(GetParameters, self.schedule_service)
        if self.schedule_client.service_is_ready():
            self.schedule_pending_at = now
            self.schedule_pending = self.schedule_client.call_async(GetParameters.Request(names=['use_sim_time']))
            self.schedule_pending.add_done_callback(self.schedule_reply)

    def schedule_reply(self, future):
        if not future.cancelled() and future.exception() is None and future.result().values:
            with self.lock:
                self.schedule_rpc_at = time.monotonic()

    def dispatch_reply(self, future):
        if future.cancelled() or future.exception() is not None:
            return
        response = future.result()
        with self.lock:
            self.rpc_at = time.monotonic()
            self.rpc_success = response.success
            self.rpc_count += 1
            if response.success:
                self.dispatch = message_to_ordereddict(response.states)

    def snapshot(self):
        now = time.monotonic()
        with self.lock:
            report = copy.deepcopy(self.report)
            report_age = None if self.report_at is None else now - self.report_at
            rpc_age = None if self.rpc_at is None else now - self.rpc_at
            dispatch = copy.deepcopy(self.dispatch)
            schedule_age = None if self.schedule_rpc_at is None else now - self.schedule_rpc_at
            central = {
                'bridge_age_seconds': report_age,
                'bridge_message_count': self.report_count,
                'dispatcher_rpc_age_seconds': rpc_age,
                'dispatcher_response_count': self.rpc_count,
                'dispatcher_connected': self.rpc_success and rpc_age is not None and rpc_age <= 6,
                'dispatch_topic_age_seconds': None if self.dispatch_at is None else now - self.dispatch_at,
                'dispatch_topic_message_count': self.dispatch_count,
                'dispatch': dispatch,
                'participants': copy.deepcopy(self.participants),
                'queries': copy.deepcopy(self.queries),
            }
        fresh = report_age is not None and report_age <= 3.0
        central['bridge_fresh'] = fresh
        central['domain_id'] = report.get('central_domain_id') if report else None
        central['schedule_rpc_age_seconds'] = schedule_age
        central['schedule_connected'] = schedule_age is not None and schedule_age <= 6
        central['source_wall_time_seconds'] = report.get('wall_time_seconds') if report else None
        allowed = {
            'navigation': ('task_id', 'source', 'phase', 'navigation_active', 'local_ready', 'readiness_reason', 'control_mode', 'tf_age_ms', 'localization_status', 'message'),
            'control': ('control_mode', 'manual_active', 'local_override', 'fleet_enabled', 'estop', 'contact', 'control_gate_ready', 'safety_reason'),
        }
        robots = []
        robot_reports = report.get('robots', {}) if report else {}
        for key, robot in robot_reports.items():
            source_age = report_age
            source_fresh = source_age is not None and source_age <= 3.0
            samples = {}
            for kind in ('pose', 'navigation', 'control', 'voltage'):
                sample = robot.get('samples', {}).get(kind)
                if sample is None:
                    samples[kind] = None
                    continue
                age = sample['age_seconds'] + robot['ipc_age_seconds'] + source_age
                value = sample['value']
                if kind in allowed:
                    value = {field: value[field] for field in allowed[kind] if field in value}
                samples[kind] = {'value': value, 'age_seconds': age, 'fresh': source_fresh and 0 <= age <= 3.0, 'message_count': robot.get('message_counts', {}).get(kind, 0)}
            robots.append({
                'robot_id': key, 'name': robot['assigned_robot_name'],
                'namespace': robot['assigned_namespace'], 'domain_id': robot['domain_id'],
                'online': all(samples[k] is not None and samples[k]['fresh'] for k in ('pose', 'navigation', 'control')),
                'transport_connected': all(samples[k] is not None and samples[k]['fresh'] for k in ('navigation', 'control')),
                'dispatch_enabled': robot['dispatch_enabled'], 'rmf_registered': robot['rmf_registered'],
                'battery_soc': robot.get('battery_soc'), 'samples': samples,
                'map': {**{k: v for k, v in robot['map'].items() if k not in ('image_base64', 'sample_monotonic')}, 'age_seconds': now - robot['map']['sample_monotonic']} if robot.get('map') and 'sample_monotonic' in robot['map'] else robot.get('map'),
                'state_source': 'central_broadcast_discovery',
            })
        return {'schema': 1, 'server_time_seconds': time.time(), 'central': central, 'robots': robots}

    def close(self):
        if self.schedule_pending is not None and not self.schedule_pending.done():
            self.schedule_pending.cancel()
        if self.schedule_client is not None:
            self.node.destroy_client(self.schedule_client)
        self.node.destroy_timer(self.timer)
        if self.pending is not None and not self.pending.done():
            self.pending.cancel()
        self.node.destroy_client(self.client)
        for subscription in self.subscriptions:
            self.node.destroy_subscription(subscription)
