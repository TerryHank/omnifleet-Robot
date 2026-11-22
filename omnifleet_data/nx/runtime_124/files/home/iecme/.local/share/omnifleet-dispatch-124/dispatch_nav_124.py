"""Expose the existing Ackermann Nav2 stack to OmniFleet's leased RMF client."""
import json
import math
import threading
import time
import uuid

import rclpy
from action_msgs.msg import GoalStatus, GoalStatusArray
from geometry_msgs.msg import Twist
from nav2_msgs.action import NavigateThroughPoses, NavigateToPose
from omnifleet_navigation_interfaces.action import ExecuteNavigation
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data
from rclpy.time import Time
from std_msgs.msg import Float32, String
from std_srvs.srv import SetBool, Trigger
from tf2_ros import Buffer, TransformException, TransformListener

from fleet_lease import FleetLease


class DispatchNavigation(Node):
    def __init__(self):
        super().__init__('omnifleet_124_dispatch_navigation')
        self.group = ReentrantCallbackGroup()
        self.lock = threading.RLock()
        self.lease = FleetLease()
        self.epoch = uuid.uuid4().hex
        self.enabled = self.busy = self.stopping = self.paused = False
        self.backend_goal = None
        self.backend_status = {}
        self.phase = 'idle'
        self.velocity = None
        self.velocity_at = None
        self.stopped_since = None
        self.tf = Buffer()
        self.tf_listener = TransformListener(self.tf, self)
        self.single = ActionClient(self, NavigateToPose, '/navigate_to_pose', callback_group=self.group)
        self.route = ActionClient(self, NavigateThroughPoses, '/navigate_through_poses', callback_group=self.group)
        self.dispatch_subscriptions = []
        for endpoint in ('navigate_to_pose', 'navigate_through_poses', 'follow_path'):
            self.dispatch_subscriptions.append(self.create_subscription(
                GoalStatusArray, f'/{endpoint}/_action/status',
                lambda msg, name=endpoint: self.track(name, msg),
                QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL),
                callback_group=self.group))
        self.dispatch_subscriptions += [
            self.create_subscription(String, '/navigation/fleet/heartbeat', self.heartbeat, 10, callback_group=self.group),
            self.create_subscription(String, '/navigation/fleet/traffic_pause', self.traffic, 10, callback_group=self.group),
        ]
        self.voltage = self.create_publisher(Float32, '/voltage', qos_profile_sensor_data)
        self.dispatch_subscriptions.extend([
            self.create_subscription(Twist, '/omnifleet_a2/chassis/velocity_raw',
                                     self.record_velocity, qos_profile_sensor_data, callback_group=self.group),
            self.create_subscription(Float32, '/omnifleet_a2/chassis/voltage',
                                     self.forward_voltage, qos_profile_sensor_data, callback_group=self.group),
        ])
        self.pubs = [
            self.create_publisher(String, name, 10)
            for name in ('/navigation/status','/navigation/local_status','/navigation/fleet/local_status')
        ]
        self.publishers_select = [
            self.create_publisher(String, name, QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
            for name in ('/planner_selector','/controller_selector')
        ]
        self.dispatch_services = [
            self.create_service(SetBool,'/navigation/allow_fleet',self.enable,callback_group=self.group),
            self.create_service(Trigger,'/navigation/fleet/acquire',self.acquire,callback_group=self.group),
            self.create_service(Trigger,'/navigation/stop',self.stop,callback_group=self.group),
            self.create_service(Trigger,'/navigation/ensure_ready',self.ensure_ready,callback_group=self.group),
        ]
        self.action = ActionServer(self,ExecuteNavigation,'/navigation/execute',
            execute_callback=self.execute,goal_callback=self.admit,
            cancel_callback=lambda _:CancelResponse.ACCEPT,callback_group=self.group)
        self.create_timer(.1,self.tick,callback_group=self.group)
        self.publishers_select[0].publish(String(data='GridBased'))
        self.publishers_select[1].publish(String(data='FollowPath'))

    def forward_voltage(self, message):
        if math.isfinite(message.data):
            self.voltage.publish(message)

    def record_velocity(self, message):
        speed = (message.linear.x, message.angular.z)
        now = time.monotonic()
        if not all(math.isfinite(value) for value in speed):
            return
        with self.lock:
            stopped = max(map(abs, speed)) < .01
            continuous = self.velocity_at is not None and now-self.velocity_at < .5
            if not stopped:
                self.stopped_since = None
            elif self.stopped_since is None or not continuous:
                self.stopped_since = now
            self.velocity = speed
            self.velocity_at = now

    def track(self, endpoint, message):
        with self.lock:
            self.backend_status[endpoint] = any(
                item.status in (GoalStatus.STATUS_ACCEPTED,GoalStatus.STATUS_EXECUTING,GoalStatus.STATUS_CANCELING)
                for item in message.status_list)

    def pose_snapshot(self):
        try:
            message=self.tf.lookup_transform('map','base_link',Time())
            stamp=Time.from_msg(message.header.stamp).nanoseconds
            p=message.transform.translation
            q=message.transform.rotation
            yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
            return (self.get_clock().now().nanoseconds-stamp)/1e6,[p.x,p.y,yaw],stamp
        except TransformException:
            return None,None,0

    def pose_age(self):
        return self.pose_snapshot()[0]

    def ready(self):
        age=self.pose_age()
        return (age is not None and -100. <= age <= 800.
                and self.single.server_is_ready() and self.route.server_is_ready())

    def enable(self, request, response):
        with self.lock:
            self.enabled=bool(request.data)
            if not self.enabled:
                self.lease.revoke()
                self.stopping=True
        response.success=True
        response.message='Fleet permission updated'
        return response

    def acquire(self, request, response):
        with self.lock:
            token=self.lease.acquire(time.monotonic()) if (
                self.enabled and not self.busy and not any(self.backend_status.values()) and self.ready()) else None
        response.success=bool(token)
        response.message=json.dumps({'epoch':token}) if token else 'Vehicle not ready or control already in use'
        return response

    def ensure_ready(self, request, response):
        response.success=self.ready()
        response.message='Nav2 and localization ready' if response.success else 'Waiting for Nav2 or localization'
        return response

    def stop(self, request, response):
        with self.lock:
            self.stopping=True
            self.lease.revoke()
            self.enabled=False
        response.success=True
        response.message='Fleet-owned navigation stop requested'
        return response

    def heartbeat(self, message):
        try:
            data=json.loads(message.data)
        except ValueError:
            return
        with self.lock:
            if self.enabled:
                self.lease.renew(data,time.monotonic())

    def traffic(self, message):
        try:
            data=json.loads(message.data)
            if not isinstance(data,dict):
                return
        except ValueError:
            return
        with self.lock:
            if (self.busy and data.get('task_id')==self.lease.task_id
                    and data.get('epoch')==self.lease.epoch
                    and data.get('revision')==self.lease.revision
                    and type(data.get('paused')) is bool):
                self.paused=data['paused']

    def admit(self, request):
        with self.lock:
            if (not self.enabled or self.busy or any(self.backend_status.values()) or not self.ready()
                    or not self.lease.matches(request,time.monotonic())
                    or request.source!=request.FLEET or request.follow_trail
                    or not 1<=len(request.waypoints)<=100):
                return GoalResponse.REJECT
            for point in request.waypoints:
                p=point.pose.pose.position
                q=point.pose.pose.orientation
                data=(p.x,p.y,p.z,q.x,q.y,q.z,q.w,point.dwell_seconds)
                if (point.pose.header.frame_id!='map' or not all(math.isfinite(v) for v in data)
                        or point.dwell_seconds<0 or math.hypot(q.x,q.y,q.z,q.w)<1e-6):
                    return GoalResponse.REJECT
            self.busy=True
            self.paused=self.stopping=False
            self.phase='queued'
        return GoalResponse.ACCEPT

    @staticmethod
    def wait(future, timeout=None):
        done=threading.Event()
        future.add_done_callback(lambda _:done.set())
        return future.result() if done.wait(timeout) else None

    def ended(self, goal):
        return (goal.is_cancel_requested or self.stopping or not self.enabled
                or not self.lease.matches(goal.request,time.monotonic()))

    def tick(self):
        with self.lock:
            now=time.monotonic()
            fresh=self.lease.fresh(now)
            if (self.backend_goal is not None and (self.stopping or not fresh or self.paused)):
                goal=self.backend_goal
                self.backend_goal=None
                goal.cancel_goal_async()
            health,pose,pose_stamp=self.pose_snapshot()
            ready=self.ready()
            active=self.busy or any(self.backend_status.values())
            status={
                'robot_id':'robot_124','local_pose':pose,'pose_stamp_ns':pose_stamp,
                'task_id':self.lease.task_id,'source':'FLEET' if self.busy else 'NONE',
                'phase':self.phase,'navigation_active':active,'nav_active':active,
                'local_ready':ready,'fleet_control_available':ready,'control_gate_ready':ready,
                'control_mode':'FLEET' if self.enabled else 'LOCAL','fleet_enabled':self.enabled,
                'local_override':False,'manual_active':False,'estop':False,'contact':None,
                'traffic_paused':self.paused,'traffic_suspended':self.paused,
                'tf_age_ms':health,'localization_epoch':self.epoch,
                'fleet_lease_fresh':fresh,'fleet_lease_task_id':self.lease.task_id,
                'fleet_lease_revision':self.lease.revision,'fleet_lease_sequence':self.lease.sequence,
                'selected_planner':'GridBased','selected_controller':'FollowPath',
                'message':'Nav2 Ackermann ready' if ready else 'Waiting for Nav2 and map TF',
            }
            if self.velocity_at is not None:
                age=now-self.velocity_at
                if age<.5:
                    status.update(velocity=self.velocity, velocity_age=age,
                                  stopped_seconds=now-self.stopped_since if self.stopped_since is not None else 0.)
        message=String(data=json.dumps(status))
        for publisher in self.pubs:
            publisher.publish(message)

    def execute(self, goal):
        queue=list(goal.request.waypoints)
        passed=0
        try:
            while queue:
                with self.lock:
                    if self.ended(goal):
                        break
                    paused=self.paused
                    self.phase='traffic_paused' if paused else 'navigating'
                if paused:
                    time.sleep(.05)
                    continue
                end=next((i+1 for i,p in enumerate(queue) if p.kind==p.STOP),len(queue))
                batch=queue[:end]
                poses=[p.pose for p in batch]
                for pose in poses:
                    pose.header.stamp=self.get_clock().now().to_msg()
                if len(poses)==1:
                    outgoing=self.single.send_goal_async(NavigateToPose.Goal(pose=poses[0]))
                else:
                    outgoing=self.route.send_goal_async(NavigateThroughPoses.Goal(poses=poses))
                handle=self.wait(outgoing,5.)
                if handle is None or not handle.accepted:
                    if handle is None:
                        def cancel_late(f):
                            late=f.result()
                            if late and late.accepted:
                                late.cancel_goal_async()
                        outgoing.add_done_callback(cancel_late)
                    goal.abort()
                    return ExecuteNavigation.Result(code='NAV2_REJECTED',message='Native Nav2 did not accept the route')
                with self.lock:
                    self.backend_goal=handle
                result=handle.get_result_async()
                while not result.done():
                    with self.lock:
                        cancel=self.ended(goal)
                    if cancel:
                        handle.cancel_goal_async()
                    time.sleep(.08)
                with self.lock:
                    self.backend_goal=None
                    if self.ended(goal):
                        break
                    paused=self.paused
                if result.result().status!=GoalStatus.STATUS_SUCCEEDED:
                    if paused:
                        continue
                    goal.abort()
                    return ExecuteNavigation.Result(code='NAV2_FAILED',message='Native Nav2 ended before reaching the route target')
                passed+=len(batch)
                queue=queue[end:]
                goal.publish_feedback(ExecuteNavigation.Feedback(task_id=goal.request.task_id,
                    phase='navigating',message='Reached waypoint',passed_points=passed,tf_age_ms=self.pose_age() or 0.))
                until=time.monotonic()+float(batch[-1].dwell_seconds)
                while time.monotonic()<until and not self.ended(goal):
                    time.sleep(.05)
            with self.lock:
                if queue or self.ended(goal):
                    if goal.is_cancel_requested:
                        goal.canceled()
                    else:
                        goal.abort()
                    return ExecuteNavigation.Result(code='STOPPED',message='Fleet control ended')
            goal.succeed()
            return ExecuteNavigation.Result(success=True,code='SUCCEEDED',message='Native Ackermann Nav2 reached the route')
        finally:
            with self.lock:
                self.backend_goal=None
                self.busy=False
                self.phase='idle'


def main():
    rclpy.init()
    node=DispatchNavigation()
    executor=MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        if node.backend_goal:
            node.backend_goal.cancel_goal_async()
        executor.shutdown(timeout_sec=2)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__=='__main__':
    main()
