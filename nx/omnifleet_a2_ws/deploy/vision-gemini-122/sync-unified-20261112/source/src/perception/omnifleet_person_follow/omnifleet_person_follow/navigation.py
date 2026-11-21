"""One owned public NavigateToPose goal, updated by Humble GoalUpdater."""
import time
from pathlib import Path
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient


class DynamicNavigation:
    def __init__(self, node, action, update_topic, tree, enabled):
        self.node, self.tree, self.enabled = node, tree, enabled
        self.client = ActionClient(node, NavigateToPose, action)
        self.publisher = node.create_publisher(PoseStamped, update_topic, 1)
        self.handle = None
        self.pending = False
        self.canceling = False
        self.wanted = False
        self.generation = 0
        self.latest = None
        self.failed = False
        self.completed = False
        self.task, self.task_key = 'follow', None
        self.completed_pose = None
        self.outcome = ''
        self.retry_at = 0.
        self.last_update_time, self.last_update_geometry = float('-inf'), None
        self.message = '识别演示，运动输出关闭' if not enabled else '等待跟随目标'
        self.actions_sent = self.updates_sent = 0

    def update(self, pose, task='follow', token=None, spin_angle=None):
        self.latest = pose
        previous_wanted = self.wanted
        self.wanted = pose is not None
        if pose is None:
            self.stop()
            self.task_key = None
            return
        key = (task, token)
        if key != self.task_key:
            self.task, self.task_key = task, key
            self.failed, self.completed, self.outcome = False, False, ''
            self.stop()
        if not self.enabled:
            return
        if not previous_wanted:
            self.failed = False
        if self.failed:
            if self.outcome != 'aborted' or time.monotonic() < self.retry_at:
                return
            self.failed,self.completed = False,False
        if self.completed:
            if task == 'search' or self.completed_pose is None:
                return
            if self.geometry(self.completed_pose) == self.geometry(pose):
                return
            self.completed = False
        if self.handle is not None:
            if not self.canceling and task in ('follow','backoff'):
                self.publish_latest()
            return
        if self.pending or self.canceling:
            return
        if not self.client.server_is_ready():
            self.message = '本机导航仲裁 Action 未就绪'
            return
        goal = NavigateToPose.Goal()
        goal.pose = pose
        goal.behavior_tree = self.tree if task in ('follow','backoff','approach') else self.center_tree(spin_angle) if task == 'center' else ''
        self.pending = True
        self.actions_sent += 1
        generation = self.generation
        self.client.send_goal_async(goal).add_done_callback(lambda future: self.accepted(future, generation))

    def accepted(self, future, generation):
        self.pending = False
        try:
            handle = future.result()
            if not handle.accepted:
                self.failed = True
                self.outcome = 'rejected'
                self.message = '导航仲裁拒绝了跟随任务'
                return
            self.handle = handle
            handle.get_result_async().add_done_callback(lambda future: self.finished(future, handle))
            if generation != self.generation or not self.wanted:
                self.stop()
            else:
                self.message = {'follow':'Nav2动态跟随运行中','backoff':'Nav2动态后退拉开距离','center':'Nav2人物居中转向','approach':'Nav2接近人物获取深度','search':'Nav2主动搜索运行中'}[self.task]
                if self.task in ('follow','backoff'):
                    self.publish_latest(force=True)
        except Exception as error:
            self.failed = True
            self.message = str(error)

    @staticmethod
    def geometry(pose):
        p,q = pose.pose.position,pose.pose.orientation
        return p.x,p.y,q.z,q.w

    @staticmethod
    def center_tree(angle):
        angle = round(float(angle)/.05)*.05
        folder = Path.home()/'.local/share/omnifleet_t2/person-follow-turns'
        folder.mkdir(parents=True,exist_ok=True)
        path = folder/f'turn_{round(angle*1000)}.xml'
        if not path.exists():
            path.write_text(f'<root main_tree_to_execute="MainTree"><BehaviorTree ID="MainTree">'
                            f'<Spin spin_dist="{angle:.3f}" time_allowance="10.0"/>'
                            '</BehaviorTree></root>')
        return str(path)

    def publish_latest(self, force=False):
        geometry = self.geometry(self.latest)
        now = time.monotonic()
        if not force and (geometry == self.last_update_geometry or now-self.last_update_time < .4):
            return
        self.latest.header.stamp = self.node.get_clock().now().to_msg()
        self.publisher.publish(self.latest)
        self.last_update_geometry,self.last_update_time = geometry,now
        self.updates_sent += 1

    def stop(self):
        self.generation += 1
        if self.handle is not None and not self.canceling:
            self.canceling = True
            self.handle.cancel_goal_async()
            self.message = '已请求取消自己的跟随目标'

    def finished(self, future, handle):
        if self.handle is handle:
            if not self.canceling:
                try:
                    status = getattr(future.result(), 'status', 6)
                except Exception:
                    status = 6
                self.failed = status != 4
                self.completed = True
                self.completed_pose = self.latest
                self.outcome = 'succeeded' if status == 4 else 'canceled' if status == 5 else 'aborted'
                if self.outcome == 'aborted':
                    self.retry_at = time.monotonic()+2.
            self.handle = None
            self.canceling = False
            self.message = f'{self.task} 导航任务结束：{self.outcome or "已取消"}'
