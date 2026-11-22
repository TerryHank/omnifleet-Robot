"""A2 fleet task API forwarding to the existing Ackermann Nav2 actions."""
import json
import math
import os
from pathlib import Path
import time
from types import SimpleNamespace
import uuid
from collections import deque

import rclpy
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from rclpy.clock import Clock, ClockType
from rclpy.qos import QoSProfile, DurabilityPolicy, qos_profile_sensor_data
from rclpy.task import Future
from action_msgs.msg import GoalStatusArray
from action_msgs.srv import CancelGoal
from unique_identifier_msgs.msg import UUID
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, Twist
from lifecycle_msgs.srv import GetState
from nav_msgs.msg import Odometry
from nav2_msgs.action import NavigateToPose, NavigateThroughPoses
from std_msgs.msg import String, Bool
from std_srvs.srv import SetBool, Trigger
from omnifleet_navigation_interfaces.action import ExecuteNavigation, ExecuteFormation
from omnifleet_local_navigation.fleet_lease import FleetLease


def formation(request):return isinstance(request,ExecuteFormation.Goal)
def source(request):return ExecuteNavigation.Goal.FLEET if formation(request) else request.source
def dynamic(request):return formation(request) or request.follow_trail
def action_type(request):return ExecuteFormation if formation(request) else ExecuteNavigation


class A2Gateway(Node):
    def __init__(self):
        super().__init__('omnifleet_a2_navigation')
        self.steady_clock=Clock(clock_type=ClockType.STEADY_TIME)
        self.group = ReentrantCallbackGroup()
        self.lease = FleetLease()
        self.enabled = False
        self.active = self.backend = None
        self.owned_uuid = None
        self.generation = 0
        self.pose_at = self.velocity_at = self.wheel_at = 0.
        self.passed = 0
        self.velocity = [0., 0.]
        self.wheel_velocity = [0., 0.]
        self.velocity_history = deque(maxlen=5)
        self.stopped_at = time.monotonic()
        self.phase = 'idle'
        self.message = 'Ackermann Nav2 task gateway'
        self.foreign_active = False
        self.statuses = {}
        self.session_path = Path.home()/'omnifleet_a2_data/run/localization-session.json'
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        processes = Path('/sys/fs/cgroup/system.slice/omnifleet-t2-mola.service/cgroup.procs').read_text().split()
        mola_pid = next(pid for pid in processes if Path('/proc/'+pid+'/cmdline').read_bytes().split(b'\0')[0].endswith(b'/mola-cli'))
        self.mola_instance = Path('/proc/sys/kernel/random/boot_id').read_text().strip()+':'+mola_pid
        saved = json.loads(self.session_path.read_text()) if self.session_path.exists() else {}
        self.epoch = saved['epoch'] if saved.get('mola_instance') == self.mola_instance else uuid.uuid4().hex
        self.save_session()
        self.owned_path = Path(os.environ['RRC_ROBOT_WS']).parent/'omnifleet_a2_data/run/fleet-owned-goal.json'
        self.owned_path.parent.mkdir(parents=True, exist_ok=True)
        self.states = {}
        self.state_pending = {}
        self.follow_target = None
        self.follow_at = 0.
        self.follow_sequence = -1
        self.follow_updates = 0
        self.follow_blocked = False
        self.follow_pub = self.create_publisher(PoseStamped, '/goal_update', 10)
        self.create_subscription(String, '/navigation/fleet/follow_trail', self.follow_update, 1)
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.status_pub = self.create_publisher(String, '/navigation/status', qos)
        self.control_pub = self.create_publisher(String, '/navigation/local_status', qos)
        self.selectors = []
        for name, value in [('planner', 'GridBased'), ('controller', 'FollowPath')]:
            p = self.create_publisher(String, '/'+name+'_selector', qos)
            p.publish(String(data=value))
            self.selectors.append(p)
        self.create_subscription(Odometry, '/lidar_odometry/pose', self.pose, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/lidar_odometry/nav_odom', self.speed, qos_profile_sensor_data)
        self.create_subscription(Twist, '/omnifleet_a2/chassis/velocity_raw', self.wheel_speed, qos_profile_sensor_data)
        self.create_subscription(PoseWithCovarianceStamped, '/initialpose', self.relocalize, 10)
        self.nav_clients = {}
        self.cancel_clients = {}
        for kind, typ in [('navigate_to_pose', NavigateToPose), ('navigate_through_poses', NavigateThroughPoses)]:
            topic = '/navigation_backend/'+kind
            self.nav_clients[kind] = ActionClient(self, typ, topic, callback_group=self.group)
            self.cancel_clients[kind] = self.create_client(CancelGoal, topic+'/_action/cancel_goal', callback_group=self.group)
            self.create_subscription(GoalStatusArray, topic+'/_action/status', lambda m,k=kind:self.backend_status(k,m), qos)
        self.state_clients = {name:self.create_client(GetState, '/'+name+'/get_state', callback_group=self.group)
                              for name in ['controller_server','planner_server','smoother_server','bt_navigator']}
        self.create_service(SetBool, '/navigation/allow_fleet', self.allow, callback_group=self.group)
        self.create_service(Trigger, '/navigation/fleet/acquire', self.acquire, callback_group=self.group)
        self.create_service(Trigger, '/navigation/stop', self.stop_service, callback_group=self.group)
        self.create_subscription(String, '/navigation/fleet/heartbeat', self.heartbeat, 1)
        self.traffic_paused=False;self.traffic_sequence=-1;self.stop_holding=False
        self.hold_pub=self.create_publisher(Bool,'/navigation/fleet/hold',1)
        self.create_subscription(String,'/navigation/fleet/traffic_pause',self.traffic_pause,1)
        self.server = ActionServer(self, ExecuteNavigation, '/navigation/execute', self.execute,
                                   goal_callback=self.accept, cancel_callback=self.cancel,
                                   handle_accepted_callback=self.accepted, callback_group=self.group)
        self.formation_server = ActionServer(self, ExecuteFormation, '/navigation/formation', self.execute,
                                   goal_callback=self.accept, cancel_callback=self.cancel,
                                   handle_accepted_callback=self.accepted, callback_group=self.group)
        self.create_timer(.1, self.tick,clock=self.steady_clock)
        self.create_timer(.5, self.poll_states,clock=self.steady_clock)

    def save_session(self):
        temporary = self.session_path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'mola_instance':self.mola_instance,'epoch':self.epoch}))
        temporary.replace(self.session_path)

    def pose(self, message):
        self.pose_at = time.monotonic()

    def speed(self, message):
        now = time.monotonic()
        self.velocity_at = now
        self.velocity = [message.twist.twist.linear.x, message.twist.twist.angular.z]
        self.velocity_history.append(self.velocity)
        averaged = [sum(v[i] for v in self.velocity_history)/len(self.velocity_history) for i in (0,1)]
        if any(abs(v) >= .01 for v in averaged):
            self.stopped_at = now

    def wheel_speed(self, message):
        self.wheel_at = time.monotonic()
        self.wheel_velocity = [message.linear.x, message.angular.z]
        if abs(message.linear.x) >= .01 or abs(message.angular.z) >= .01:
            self.stopped_at = self.wheel_at

    def relocalize(self, message):
        self.epoch = uuid.uuid4().hex
        self.save_session()
        self.enabled = False
        self.lease.revoke()
        self.stop_owned('Localization session changed')

    def backend_status(self, kind, message):
        self.statuses[kind] = [bytes(s.goal_info.goal_id.uuid) for s in message.status_list if s.status in (1,2,3)]
        owned = self.owned_uuid
        self.foreign_active = any(g != owned for values in self.statuses.values() for g in values)

    def poll_states(self):
        now = time.monotonic()
        for name, client in self.state_clients.items():
            pending = self.state_pending.get(name)
            if pending and now-pending[1] > 1.:
                client.remove_pending_request(pending[0])
                self.state_pending.pop(name, None)
            if name in self.state_pending or not client.service_is_ready():
                continue
            future = client.call_async(GetState.Request())
            self.state_pending[name] = (future, now)
            def done(future, name=name):
                if self.state_pending.get(name, (None,))[0] is not future:
                    return
                self.state_pending.pop(name, None)
                if not future.cancelled() and future.exception() is None:
                    self.states[name] = (future.result().current_state.id, time.monotonic())
            future.add_done_callback(done)

    def follow_update(self, message):
        if not self.active or not dynamic(self.active.request):
            return
        request = self.active.request
        try:
            data = json.loads(message.data)
            if data.get('mode','trail') != ('formation' if formation(request) else 'trail'):return
            if (source(request) != ExecuteNavigation.Goal.FLEET or data['task_id'] != request.task_id
                    or data['epoch'] != request.command_epoch or data['revision'] != request.revision
                    or data['localization_epoch'] != self.epoch
                    or not self.lease.matches(request, time.monotonic())):
                return
            sequence, poses = data['sequence'], data['poses']
            if type(sequence) is not int or sequence <= self.follow_sequence or len(poses) != 1:
                return
            values = poses[0]
            if len(values) != 3 or not all(type(v) in (int, float) and math.isfinite(v) for v in values):
                return
            target = PoseStamped()
            target.header.frame_id = 'map'
            target.pose.position.x, target.pose.position.y = map(float, values[:2])
            target.pose.orientation.z, target.pose.orientation.w = math.sin(values[2]/2), math.cos(values[2]/2)
            self.follow_target, self.follow_sequence = target, sequence
            self.follow_at = time.monotonic()
            self.follow_updates += 1
        except (ValueError, TypeError, KeyError):
            return

    def ready(self):
        now = time.monotonic()
        return (now-self.pose_at < 1. and now-self.velocity_at < 1. and now-self.wheel_at < 1.
                and all(c.server_is_ready() for c in self.nav_clients.values())
                and all(n in self.states and self.states[n][0] == 3 and now-self.states[n][1] < 2.
                        for n in self.state_clients))

    def allow(self, request, response):
        if not request.data:
            self.enabled = False
            self.lease.revoke()
            if self.active and source(self.active.request) == ExecuteNavigation.Goal.FLEET:
                self.stop_owned('Fleet control released')
            response.success = True
        else:
            response.success = bool(self.ready() and not self.active and not self.foreign_active)
            self.enabled = response.success
        response.message = 'Fleet enabled' if self.enabled else 'Fleet disabled or navigation unavailable'
        return response

    def acquire(self, request, response):
        epoch = self.lease.acquire(time.monotonic()) if self.enabled and self.ready() and not self.active and not self.foreign_active and time.monotonic()-self.stopped_at >= .3 else None
        response.success = bool(epoch)
        response.message = json.dumps({'epoch':epoch, 'timeout_seconds':self.lease.timeout})
        return response

    def heartbeat(self, message):
        if self.enabled:
            try:self.lease.renew(json.loads(message.data), time.monotonic())
            except (ValueError, TypeError):pass

    def traffic_pause(self,message):
        if not self.active or source(self.active.request)!=ExecuteNavigation.Goal.FLEET:return
        request=self.active.request
        try:
            data=json.loads(message.data)
            if (not self.enabled or not self.lease.matches(request,time.monotonic()) or
                data['task_id']!=request.task_id or data['epoch']!=request.command_epoch or data['revision']!=request.revision or
                type(data['sequence']) is not int or data['sequence']<=self.traffic_sequence or type(data['paused']) is not bool):return
            self.traffic_sequence=data['sequence'];self.traffic_paused=data['paused']
            self.hold_pub.publish(Bool(data=self.traffic_paused))
        except (ValueError,TypeError,KeyError):return

    def stop_owned(self, reason):
        self.stop_holding=True
        if self.active and source(self.active.request)==1:self.hold_pub.publish(Bool(data=True))
        self.generation += 1
        self.message = reason
        if self.backend:
            self.backend.cancel_goal_async()

    def stop_service(self, request, response):
        self.stop_owned('Operator stop requested')
        for client in self.cancel_clients.values():
            if client.service_is_ready():client.call_async(CancelGoal.Request())
        response.success = True
        response.message = 'Nav2 cancellation requested; see local_status for stop confirmation'
        return response

    def accept(self, request):
        if self.active or self.foreign_active or not self.ready() or not 1 <= len(request.waypoints) <= 100:
            return GoalResponse.REJECT
        if dynamic(request) and source(request) != ExecuteNavigation.Goal.FLEET:
            return GoalResponse.REJECT
        if source(request) == ExecuteNavigation.Goal.FLEET:
            if not self.enabled or not self.lease.matches(SimpleNamespace(**{k:getattr(request,k) for k in ['command_epoch','task_id','revision']}), time.monotonic()):
                return GoalResponse.REJECT
        elif source(request) != ExecuteNavigation.Goal.LOCAL:
            return GoalResponse.REJECT
        for point in request.waypoints:
            p, q = point.pose.pose.position, point.pose.pose.orientation
            values = [p.x,p.y,p.z,q.x,q.y,q.z,q.w,point.dwell_seconds]
            if (point.pose.header.frame_id != 'map' or not all(math.isfinite(v) for v in values)
                    or abs(q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w-1.) > .01
                    or point.kind not in (point.PASS,point.STOP) or not 0 <= point.dwell_seconds <= 600.):
                return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def accepted(self, handle):
        self.active = handle
        self.passed = 0
        self.traffic_paused=False;self.traffic_sequence=-1;self.stop_holding=False
        self.follow_target = None
        self.follow_sequence, self.follow_updates = -1, 0
        self.follow_at = time.monotonic()
        self.follow_blocked = False
        handle.execute()

    def cancel(self, handle):
        self.stop_owned('Task canceled')
        return CancelResponse.ACCEPT

    async def delay(self, seconds):
        future = Future()
        timer = self.create_timer(seconds, lambda:future.set_result(True) if not future.done() else None, callback_group=self.group,clock=self.steady_clock)
        try:await future
        finally:self.destroy_timer(timer)

    async def execute(self, handle):
        request = handle.request
        generation = self.generation
        result = action_type(request).Result(success=False, code='CANCELED', message='Task canceled')
        passed = 0
        try:
            if dynamic(request):
                while self.follow_target is None and generation == self.generation and not handle.is_cancel_requested:
                    await self.delay(.05)
            groups, segment = [], []
            for i, point in enumerate(request.waypoints):
                segment.append(point)
                if point.kind == point.STOP or i == len(request.waypoints)-1:
                    groups.append(segment)
                    segment = []
            for points in groups:
                if generation != self.generation or handle.is_cancel_requested:break
                kind = 'navigate_to_pose' if len(points) == 1 else 'navigate_through_poses'
                goal = NavigateToPose.Goal() if len(points) == 1 else NavigateThroughPoses.Goal()
                poses = [p.pose for p in points]
                for pose in poses:pose.header.stamp = self.get_clock().now().to_msg()
                if len(points) == 1:goal.pose = poses[0]
                else:goal.poses = poses
                if dynamic(request):
                    kind = 'navigate_to_pose'
                    goal = NavigateToPose.Goal(pose=self.follow_target)
                    goal.behavior_tree = str(Path(__file__).with_name('ackermann_follow.xml'))
                self.phase = 'tracking'
                goal_id = UUID(uuid=list(uuid.uuid4().bytes))
                self.owned_uuid = bytes(goal_id.uuid)
                temporary = self.owned_path.with_suffix('.tmp')
                temporary.write_text(json.dumps({'kind':kind,'uuid':[int(v) for v in goal_id.uuid]}))
                temporary.replace(self.owned_path)
                self.backend = await self.nav_clients[kind].send_goal_async(goal, goal_uuid=goal_id)
                if not self.backend.accepted:
                    self.owned_path.unlink(missing_ok=True)
                    result.code, result.message = 'NAV2_REJECTED', 'Ackermann Nav2 rejected task'
                    break
                if generation != self.generation or handle.is_cancel_requested:self.backend.cancel_goal_async()
                outcome = await self.backend.get_result_async()
                self.owned_path.unlink(missing_ok=True)
                self.backend = None
                if generation != self.generation or handle.is_cancel_requested:break
                if outcome.status != 4:
                    result.code, result.message = 'NAV2_FAILED', 'Ackermann Nav2 status '+str(outcome.status)
                    break
                passed += len(points)
                self.passed = passed
                if points[-1].dwell_seconds:
                    until = time.monotonic()+points[-1].dwell_seconds
                    while time.monotonic() < until and generation == self.generation and not handle.is_cancel_requested:
                        await self.delay(.1)
                    if generation != self.generation or handle.is_cancel_requested:break
            else:
                result.success, result.code, result.message = True, 'OK', 'Ackermann navigation completed'
            if handle.is_cancel_requested:handle.canceled()
            elif result.success:handle.succeed()
            else:handle.abort()
            return result
        except Exception as error:
            self.stop_owned('Task exception: '+str(error))
            if handle.is_active:handle.abort()
            return action_type(request).Result(success=False, code='ERROR', message=str(error))
        finally:
            self.active = self.backend = None
            self.traffic_paused=False;self.stop_holding=False
            self.owned_uuid = None
            self.phase = 'idle'

    def tick(self):
        now = time.monotonic()
        owned = self.owned_uuid
        self.foreign_active = any(g != owned for values in self.statuses.values() for g in values)
        if self.enabled and self.lease.epoch and not self.lease.fresh(now):
            self.enabled = False
            self.lease.revoke()
            if self.active and source(self.active.request) == ExecuteNavigation.Goal.FLEET:
                self.stop_owned('Fleet lease expired')
        if self.active and dynamic(self.active.request):
            if now-self.follow_at > .8 and not self.follow_blocked:
                self.follow_blocked = True
                self.stop_owned('Follow target not updated for 0.8 seconds')
            elif self.follow_target is not None and not self.follow_blocked:
                self.follow_target.header.stamp = self.get_clock().now().to_msg()
                self.follow_pub.publish(self.follow_target)
        self.hold_pub.publish(Bool(data=bool(self.active and source(self.active.request)==1 and (self.traffic_paused or self.stop_holding or not self.enabled or not self.lease.fresh(now)))))
        active = bool(self.active or self.foreign_active)
        ready = self.ready()
        control = {'robot_id':os.environ['OMNIFLEET_ROBOT_ID'], 'nav_active':active, 'control_gate_ready':ready,
                   'velocity':self.wheel_velocity, 'velocity_age':max(now-self.velocity_at, now-self.wheel_at), 'stopped_seconds':now-self.stopped_at,
                   'manual_active':self.foreign_active, 'control_mode':'FLEET' if self.active and source(self.active.request) == 1 else 'LOCAL'}
        status = {**control, 'velocity':self.velocity, 'local_ready':ready, 'readiness_reason':'' if ready else 'Waiting for active Ackermann Nav2 and live MOLA',
                  'localization_epoch':self.epoch, 'navigation_active':active, 'local_override':self.foreign_active,
                  'fleet_control_available':True, 'fleet_enabled':self.enabled, 'fleet_lease_fresh':self.lease.fresh(now),
                  'fleet_lease_sequence':self.lease.sequence, 'fleet_lease_task_id':self.lease.task_id,
                  'fleet_lease_revision':self.lease.revision, 'traffic_paused':self.traffic_paused, 'phase':self.phase, 'message':self.message,
                  'selected_planner':'GridBased', 'selected_controller':'FollowPath', 'tf_age_ms':(now-self.pose_at)*1000.}
        status['formation_stream' if self.active and formation(self.active.request) else 'follow_stream'] = {'backend':'nav2_goal_updater', 'updates':self.follow_updates,
                                   'sequence':self.follow_sequence, 'blocked':self.follow_blocked,
                                   'update_age':now-self.follow_at if self.follow_updates else None}
        self.status_pub.publish(String(data=json.dumps(status)))
        self.control_pub.publish(String(data=json.dumps(control)))
        if self.active and self.active.is_active:
            self.active.publish_feedback(action_type(self.active.request).Feedback(task_id=self.active.request.task_id, phase=self.phase,
                message=self.message, passed_points=self.passed, tf_age_ms=float(status['tf_age_ms'])))


def main():
    rclpy.init()
    node = A2Gateway()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:
        if rclpy.ok():node.stop_owned('Gateway shutdown')
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()


if __name__ == '__main__':main()
