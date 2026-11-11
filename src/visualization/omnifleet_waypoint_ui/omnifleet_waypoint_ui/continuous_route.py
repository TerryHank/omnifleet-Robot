"""Continuous waypoint blocks; action ownership survives cancel/accept races."""
import copy
import json
import math
import time
import uuid
from pathlib import Path
from xml.sax.saxutils import quoteattr

from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry, OccupancyGrid, Path as NavPath
from nav2_msgs.action import ComputePathThroughPoses, NavigateThroughPoses
from rclpy.action import ActionClient
from rcl_interfaces.srv import GetParameters
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, qos_profile_sensor_data
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage
from .localization_health import LocalizationHealth


def yaw(pose):
    q = pose.orientation
    return math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))


def oriented_route(points, start_yaw=None):
    result = copy.deepcopy(points)
    reference = start_yaw if start_yaw is not None else (yaw(result[0].pose) if result else 0.)
    for i, point in enumerate(result):
        if point.kind == "stop" or i == len(result)-1:
            reference = yaw(point.pose)
            continue
        following = next((p for p in result[i+1:] if math.hypot(p.pose.position.x-point.pose.position.x, p.pose.position.y-point.pose.position.y) > 1e-4), None)
        if following:
            direction = math.atan2(following.pose.position.y-point.pose.position.y, following.pose.position.x-point.pose.position.x)
            angle = min((direction, direction+math.pi), key=lambda a: abs(math.atan2(math.sin(a-reference), math.cos(a-reference))))
            point.pose.orientation.x = point.pose.orientation.y = 0.
            point.pose.orientation.z, point.pose.orientation.w = math.sin(angle/2), math.cos(angle/2)
            reference = angle
    return result


def split_blocks(points):
    blocks, start = [], 0
    for i, point in enumerate(points):
        if point.kind == "stop" or i == len(points)-1:
            blocks.append((start, i+1))
            start = i+1
    return blocks


def topic(node, suffix):
    prefix = node.frame_id.rpartition('/')[0]
    return ('/'+prefix if prefix else '')+'/'+suffix.lstrip('/')


def path_valid(grid, path, allow_unknown=False):
    if grid.info.resolution <= 0 or not path.poses or len(grid.data) != grid.info.width*grid.info.height:
        return False
    angle = yaw(grid.info.origin)
    cs, sn = math.cos(angle), math.sin(angle)
    def free(x,y):
        dx,dy=x-grid.info.origin.position.x,y-grid.info.origin.position.y
        ix,iy=math.floor((cs*dx+sn*dy)/grid.info.resolution),math.floor((-sn*dx+cs*dy)/grid.info.resolution)
        if not (0<=ix<grid.info.width and 0<=iy<grid.info.height):
            return False
        value=grid.data[iy*grid.info.width+ix]
        return 0<=value<99 or (value==-1 and allow_unknown)
    previous = path.poses[0].pose.position
    for pose in path.poses:
        p=pose.pose.position
        steps=max(1,math.ceil(math.hypot(p.x-previous.x,p.y-previous.y)/(grid.info.resolution*.5)))
        if any(not free(previous.x+(p.x-previous.x)*k/steps,previous.y+(p.y-previous.y)*k/steps) for k in range(steps+1)):
            return False
        previous=p
    return True


class ContinuousRoute:
    def __init__(self, node):
        self.n = node
        self.navigator = ActionClient(node, NavigateThroughPoses, "navigate_through_poses")
        self.planner = ActionClient(node, ComputePathThroughPoses, "compute_path_through_poses")
        self.parameters = node.create_client(GetParameters, topic(node, 'planner_server/get_parameters'))
        self.configuration_pending = False
        self.allow_unknown = False
        self.active = False
        self.phase = "idle"
        self.epoch = 0
        self.requests = {}
        self.points = []
        self.states = []
        self.block = 0
        self.controller = "FollowPath"
        self.health = LocalizationHealth()
        self.pose = self.odom = None
        self.grid = None
        self.executed_path = None
        self.run_id = ""
        self.bt_file = None
        self.cancel_reason = ""
        self.finished_at = None
        self.preflight_only = False
        latched = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        node.create_subscription(String, topic(node, "controller_selector"), lambda m: setattr(self, 'controller', m.data), latched)
        node.create_subscription(OccupancyGrid, topic(node, "global_costmap/costmap"), lambda m: setattr(self, 'grid', (time.monotonic(),m)), latched)
        node.create_subscription(Odometry, topic(node, "lidar_odometry/pose"), lambda m: setattr(self, 'pose', (time.monotonic(), m)), qos_profile_sensor_data)
        node.create_subscription(Odometry, topic(node, "odom"), lambda m: setattr(self, 'odom', (time.monotonic(), m)), qos_profile_sensor_data)
        node.create_subscription(String, topic(node, "omnifleet_t2/waypoints/execution_state"), self.on_execution_state, 10)
        node.create_subscription(TFMessage, topic(node, "tf"), self.on_tf, qos_profile_sensor_data)
        self.zero = node.create_publisher(Twist, topic(node, "cmd_vel"), 1)
        node.create_timer(.05, self.tick)

    def on_tf(self, message):
        base = self.n.frame_id.rpartition("/")[0]
        base = (base+"/" if base else "")+"base_link"
        for transform in message.transforms:
            if transform.header.frame_id == self.n.frame_id and transform.child_frame_id == base:
                stamp = transform.header.stamp.sec+transform.header.stamp.nanosec*1e-9
                self.health.observe(stamp, time.monotonic())

    def catalog(self):
        return {'tf_age_ms': self.health.age_ms, 'localization_status': self.health.reason, 'run_id': self.run_id, 'phase': self.phase, 'block': self.block+1 if self.active else 0,
                'blocks': len(getattr(self, 'blocks', [])), 'waypoint_states': self.states,
                'remaining_wait': max(0., getattr(self, 'wait_until', 0.)-time.monotonic()) if self.phase == 'waiting' else 0.,
                'planner_id': getattr(self, 'planner_id', ''), 'controller_id': getattr(self, 'controller_id', '')}

    def inputs_ready(self):
        now = time.monotonic()
        return bool(self.health.ready(time.time(),now) and self.pose and now-self.pose[0]<.5 and self.grid and now-self.grid[0]<3)

    def set_phase(self, phase, text):
        self.phase = phase
        self.n.publish_status(text)
        self.n.publish_catalog()

    def start(self, points, preflight_only=False):
        if self.n.navigation_active or self.requests:
            self.n.publish_status("已有任务或取消请求尚未结束，不能重复开始")
            return
        if not points or not self.navigator.server_is_ready() or not self.planner.server_is_ready():
            self.n.publish_status("不能开始：请添加航点并等待多点导航和规划服务就绪")
            return
        if not self.inputs_ready():
            self.n.publish_status("不能开始："+self.health.reason+"；需要新鲜位姿与代价地图")
            return
        self.epoch += 1
        self.run_id = uuid.uuid4().hex
        self.active = self.n.navigation_active = True
        self.preflight_only = preflight_only
        self.points = oriented_route(points, yaw(self.pose[1].pose.pose))
        self.blocks = split_blocks(self.points)
        self.states = ['待通过']*len(points)
        self.block = self.preflight_index = 0
        self.planner_id, self.controller_id = self.n.preview_planner_id, self.controller
        self.radius = self.n.pass_radius
        self.n.preview_revision += 1
        self.n.preview_dirty = False
        if self.n.preview_goal_handle:
            self.n.preview_goal_handle.cancel_goal_async()
        self.preview = NavPath()
        self.preview.header.frame_id = self.n.frame_id
        self.initial_pose = copy.deepcopy(self.pose[1].pose.pose)
        self.set_phase('preplanning', '开始前检查整条路线；规划通过之前不会行驶')
        self.configuration_pending = True
        self.configuration_deadline = time.monotonic()+8
        epoch = self.epoch
        future = self.parameters.call_async(GetParameters.Request(names=[self.planner_id+'.allow_unknown']))
        def configured(f):
            if epoch != self.epoch or not self.active:
                return
            self.configuration_pending = False
            try:
                values = f.result().values
                if len(values)!=1 or values[0].type!=1:
                    raise RuntimeError('不能读取当前规划器的未知区域策略')
                self.allow_unknown = values[0].bool_value
                self.plan_next_block()
            except Exception as error:
                self.stop(f'读取规划配置失败：{error}', failed=True)
        future.add_done_callback(configured)

    def stamped(self, pose):
        value = PoseStamped()
        value.header.frame_id = self.n.frame_id
        value.header.stamp = self.n.get_clock().now().to_msg()
        value.pose = copy.deepcopy(pose)
        return value

    def submit(self, client, goal, result_fn, role, feedback=None):
        key = uuid.uuid4().hex
        entry = {'epoch': self.epoch, 'role': role, 'handle': None, 'deadline': time.monotonic()+10,
                 'cancel': False, 'cancel_sent': False, 'result': result_fn}
        self.requests[key] = entry
        try:
            f = client.send_goal_async(goal, feedback_callback=feedback)
            f.add_done_callback(lambda future: self.accepted(key, future))
        except Exception as error:
            self.requests.pop(key, None)
            self.stop(f"请求发送失败：{error}", failed=True)

    def accepted(self, key, future):
        entry = self.requests.get(key)
        if not entry:
            return
        try:
            handle = future.result()
            if not handle.accepted:
                raise RuntimeError('action请求被拒绝')
            entry['handle'] = handle
            entry['deadline'] = time.monotonic()+15 if entry['role'] == 'plan' else float('inf')
            handle.get_result_async().add_done_callback(lambda f: self.result(key, f))
            if entry['cancel'] or entry['epoch'] != self.epoch:
                self.cancel(entry)
        except Exception as error:
            self.requests.pop(key, None)
            if entry['epoch'] == self.epoch and not entry['cancel']:
                self.stop(f"提交失败：{error}", failed=True)

    def result(self, key, future):
        entry = self.requests.pop(key, None)
        if not entry or entry['cancel'] or entry['epoch'] != self.epoch:
            return
        try:
            wrapped = future.result()
            if wrapped.status != 4:
                raise RuntimeError(f"action状态={wrapped.status}")
            entry['result'](wrapped.result)
        except Exception as error:
            self.stop(f"{entry['role']}失败：{error}", failed=True)

    def cancel(self, entry):
        entry['cancel'] = True
        if entry['handle'] and not entry['cancel_sent']:
            entry['cancel_sent'] = True
            f = entry['handle'].cancel_goal_async()
            def replied(future):
                try:
                    reply = future.result()
                    if reply.return_code not in (0, 3):
                        entry['cancel_sent'] = False
                except Exception:
                    entry['cancel_sent'] = False
            f.add_done_callback(replied)

    def plan_next_block(self):
        start, end = self.blocks[self.preflight_index]
        goal = ComputePathThroughPoses.Goal()
        goal.planner_id = self.planner_id
        goal.use_start = True
        goal.start = self.stamped(self.initial_pose if start == 0 else self.points[start-1].pose)
        goal.goals = [self.stamped(p.pose) for p in self.points[start:end]]
        self.submit(self.planner, goal, self.planned_block, 'plan')

    def planned_block(self, result):
        if not result.path.poses:
            raise RuntimeError('规划返回空路径')
        if not self.grid or time.monotonic()-self.grid[0]>3 or not path_valid(self.grid[1],result.path,self.allow_unknown):
            raise RuntimeError('预规划路径经过阻塞或未知栅格，或代价地图不新鲜')
        self.preview.poses.extend(result.path.poses)
        self.preflight_index += 1
        if self.preflight_index < len(self.blocks):
            self.plan_next_block()
            return
        self.preview.header.stamp = self.n.get_clock().now().to_msg()
        self.n.path_pub.publish(self.preview)
        self.n.preview_state = 'ready'
        self.n.preview_effective_planner = self.planner_id
        self.n.preview_pose_count = len(self.preview.poses)
        self.n.preview_waypoint_count = len(self.points)
        if self.preflight_only:
            self.finish('preview_ready', '整条路线已通过静止规划检查；未发送导航目标')
        else:
            self.send_block()

    def make_tree(self):
        folder = Path.home()/'.local/share/omnifleet_t2/continuous-routes'
        folder.mkdir(parents=True, exist_ok=True)
        self.bt_file = folder/(self.run_id+f'-{self.block}.xml')
        prefix = self.n.frame_id.rpartition('/')[0]
        base = prefix+'/base_link' if prefix else 'base_link'
        run = self.run_id+f'-{self.block}'
        text = f'''<root main_tree_to_execute="MainTree"><BehaviorTree ID="MainTree">
<ContinuousRouteControl goals="{{goals}}" path="{{path}}" pass_radius="{self.radius}" allow_unknown="{str(self.allow_unknown).lower()}" global_frame={quoteattr(self.n.frame_id)} base_frame={quoteattr(base)} robot_prefix={quoteattr(prefix)} run_id={quoteattr(run)}>
<ComputePathThroughPoses goals="{{continuous_plan_goals}}" path="{{path}}" planner_id={quoteattr(self.planner_id)}/>
<FollowPath path="{{path}}" controller_id={quoteattr(self.controller_id)}/>
</ContinuousRouteControl></BehaviorTree></root>'''
        self.bt_file.write_text(text)
        return str(self.bt_file)

    def send_block(self):
        start, end = self.blocks[self.block]
        goal = NavigateThroughPoses.Goal()
        goal.poses = [self.stamped(p.pose) for p in self.points[start:end]]
        goal.behavior_tree = self.make_tree()
        self.states[start] = '启动检查中'
        self.set_phase('preplanning', f'提交第{self.block+1}/{len(self.blocks)}连续段，航点{start+1}到{end}；等待数据与路径检查')
        self.submit(self.navigator, goal, self.block_done, 'navigation')

    def on_execution_state(self, message):
        try:
            value = json.loads(message.data)
            if value.get('run_id') != self.run_id+f'-{self.block}':
                return
            if value.get('state') == 'failed':
                reason = '连续导航失败：'+str(value.get('reason', '执行检查失败'))
                if self.active:
                    self.stop(reason, failed=True)
                elif self.phase == 'failed':
                    self.cancel_reason = reason
                    self.n.publish_status(reason)
                return
            if not self.active:
                return
            start, end = self.blocks[self.block]
            remaining = int(value['remaining'])
            if not 1 <= remaining <= end-start:
                return
            first = end-remaining
            for i in range(start, first):
                self.states[i] = '已通过'
            if self.phase in ('preplanning','tracking','replanning'):
                self.states[first] = '停靠对齐中' if first == end-1 else '正在通过'
                self.phase = value['state'] if value['state'] in ('tracking','replanning') else self.phase
                self.n.publish_catalog()
        except (ValueError, KeyError, TypeError):
            return

    def block_done(self, _result):
        self.stop_since = None
        self.stop_deadline = time.monotonic()+5
        self.set_phase('stopping', '段末到点成功，确认底盘停止后开始停靠计时')
        if self.bt_file:
            self.bt_file.unlink(missing_ok=True)
            self.bt_file = None

    def stop(self, reason, failed=False):
        if not self.active:
            return
        if self.phase in ('canceling', 'cancel_unconfirmed'):
            # Cleanup/duplicate stop must not overwrite the original failure.
            if failed and not self.failed:
                self.failed, self.cancel_reason = True, reason
            for entry in list(self.requests.values()):
                self.cancel(entry)
            return
        self.cancel_reason = reason
        self.failed = failed
        self.epoch += 1
        self.configuration_pending = False
        self.cancel_deadline = time.monotonic()+5
        for entry in list(self.requests.values()):
            self.cancel(entry)
        self.set_phase('canceling', reason+'；正在取消全部相关请求')

    def finish(self, phase, text):
        self.active = self.n.navigation_active = False
        self.phase = phase
        if self.bt_file:
            self.bt_file.unlink(missing_ok=True)
            self.bt_file = None
        self.n.publish_status(text)
        self.n.publish_catalog()
        if self.n.preview_planner_id != getattr(self,'planner_id',self.n.preview_planner_id):
            self.n.request_route_preview()

    def tick(self):
        fresh = self.health.check(time.time(), time.monotonic())
        if not self.active:
            return
        now = time.monotonic()
        if self.configuration_pending and now > self.configuration_deadline:
            self.stop('读取规划配置超时，路线未启动', failed=True)
        for entry in list(self.requests.values()):
            if now > entry['deadline'] and not entry['cancel']:
                self.stop('请求超时，已要求取消；未确认取消前不会继续', failed=True)
                break
        if self.phase in ('canceling','cancel_unconfirmed'):
            self.zero.publish(Twist())
            for entry in list(self.requests.values()):
                self.cancel(entry)
            if not self.requests:
                self.finish('failed' if self.failed else 'canceled', self.cancel_reason+'；相关请求已结束')
            elif now > self.cancel_deadline and self.phase != 'cancel_unconfirmed':
                self.set_phase('cancel_unconfirmed', '取消未确认，已停止发后续段；请检查服务或重启导航栈')
            return
        if not fresh or not self.pose or now-self.pose[0] > .5:
            self.stop(self.health.reason+'；MOLA位姿/TF不新鲜，停止路线', failed=True)
            return
        if self.phase in ('stopping','waiting'):
            self.zero.publish(Twist())
            stopped = self.odom and now-self.odom[0] < .4 and abs(self.odom[1].twist.twist.linear.x) < .02 and abs(self.odom[1].twist.twist.angular.z) < .05
            if self.phase == 'stopping':
                self.stop_since = (self.stop_since or now) if stopped else None
                if self.stop_since and now-self.stop_since >= .3:
                    start, end = self.blocks[self.block]
                    self.states[end-1] = '等待中'
                    self.wait_until = now+self.points[end-1].dwell_seconds
                    self.set_phase('waiting', f'航点{end}已停稳，等待{self.points[end-1].dwell_seconds:g}秒')
                elif now > self.stop_deadline:
                    self.stop('段末未确认底盘停止', failed=True)
            elif not stopped:
                self.stop('停靠期间底盘反馈不满足停止条件', failed=True)
            elif now >= self.wait_until:
                _, end = self.blocks[self.block]
                self.states[end-1] = '已停靠'
                self.block += 1
                if self.block == len(self.blocks):
                    self.finish('completed', '整条路线完成：途经点已通过，停靠点及最终点已完成')
                else:
                    self.send_block()
            elif now-getattr(self, 'last_wait_report', 0.) >= .25:
                self.last_wait_report = now
                self.n.publish_catalog()
