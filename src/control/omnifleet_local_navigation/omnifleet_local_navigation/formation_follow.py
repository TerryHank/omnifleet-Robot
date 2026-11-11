"""Lease-bound formation target updates using Humble's native GoalUpdater/Nav2."""
import copy
import hashlib
import json
import math
from pathlib import Path
import time
from types import SimpleNamespace
import xml.etree.ElementTree as ET

from geometry_msgs.msg import Pose, PoseStamped, TransformStamped, Twist
from nav2_msgs.action import NavigateToPose
from tf2_ros import TransformBroadcaster


def receive_formation(node, message):
    job=node.current_job
    if not job or job.backend!='formation_follow' or node.policy.canceling:return
    try:
        data=json.loads(message.data)
        if (data.get('mode')!='formation' or data['task_id']!=job.ticket.task_id or
            data['epoch']!=job.ticket.command_epoch or data['revision']!=job.ticket.revision or
            data['localization_epoch']!=node.epoch or not node.fleet_enabled or
            not node.fleet_lease.matches(job.ticket,time.monotonic())):return
        sequence=data['sequence'];values=data['poses']
        if type(sequence) is not int or sequence<=node.execution.formation.sequence:return
        if not isinstance(values,list) or len(values)!=1:return
        value=values[0]
        if not isinstance(value,list) or len(value)!=3 or not all(type(v) in (int,float) and math.isfinite(v) for v in value):return
        pose=Pose();pose.position.x,pose.position.y=map(float,value[:2])
        pose.orientation.z=math.sin(value[2]/2);pose.orientation.w=math.cos(value[2]/2)
        node.execution.formation.update(SimpleNamespace(pose=pose),sequence)
    except (ValueError,TypeError,KeyError):return


def formation_tree(planner,controller,base='base_link'):
    tree=ET.fromstring('''<root main_tree_to_execute="MainTree"><BehaviorTree ID="MainTree">
      <KeepRunningUntilFailure><ForceSuccess>
      <PipelineSequence name="FormationWithReplanning">
        <PlannerSelector selected_planner="{selected_planner}" topic_name="/planner_selector"/>
        <ControllerSelector selected_controller="{selected_controller}" topic_name="/controller_selector"/>
        <RateController hz="2.0">
          <GoalUpdater input_goal="{goal}" output_goal="{updated_goal}">
            <ComputePathToPose goal="{updated_goal}" path="{path}" planner_id="{selected_planner}"/>
          </GoalUpdater>
        </RateController>
        <KeepRunningUntilFailure>
          <ReactiveFallback>
            <FormationPoseReached goal="{updated_goal}"/>
            <FollowPath path="{path}" controller_id="{selected_controller}" goal_checker_id="general_goal_checker"/>
          </ReactiveFallback>
        </KeepRunningUntilFailure>
      </PipelineSequence>
      </ForceSuccess></KeepRunningUntilFailure>
      </BehaviorTree></root>''')
    tree.find('.//PlannerSelector').set('default_planner',planner)
    tree.find('.//ControllerSelector').set('default_controller',controller)
    tree.find('.//FormationPoseReached').set('robot_base_frame',base)
    text=ET.tostring(tree,encoding='unicode')
    folder=Path.home()/'.local/share/omnifleet_t2/formation';folder.mkdir(parents=True,exist_ok=True)
    path=folder/(hashlib.sha256(text.encode()).hexdigest()[:16]+'.xml')
    path.write_text(text)
    return str(path)


class FormationFollow:
    label='编队'
    target_frame='formation_target'

    def __init__(self, route):
        self.route=route
        self.publisher=route.n.create_publisher(PoseStamped,'/goal_update',10)
        self.tf=TransformBroadcaster(route.n)

    def start(self, points):
        self.point=copy.deepcopy(points[-1]);self.sequence=-1
        self.started=time.monotonic();self.received=None;self.submitted=False;self.blocked=False;self.updates=0

    def update(self, point, sequence):
        self.point=point;self.sequence=sequence;self.received=time.monotonic();self.updates+=1

    def catalog(self):
        current=self.route.n.local_pose
        away=current is not None and math.hypot(current[0]-self.point.pose.position.x,current[1]-self.point.pose.position.y)>.25
        return {'backend':'nav2_goal_updater','updates':self.updates,'sequence':self.sequence,
                'blocked':self.blocked,'waiting_for_path':bool(away and not self.route.n.nav_status.get('follow_path',False)),
                'update_age':None if self.received is None else time.monotonic()-self.received}

    def tick(self, now):
        route=self.route
        if now-(self.received if self.received is not None else self.started)>.8:
            self.blocked=True;route.zero.publish(Twist())
            route.stop(self.label+'动态目标超过0.8秒未更新；停止，不寻找或追逐旧目标',failed=True);return
        if self.received is None:
            route.zero.publish(Twist());return
        if not self.submitted:
            if not route.single.server_is_ready():
                self.blocked=True;route.stop('本车Nav2动态导航接口未就绪',failed=True);return
            goal=NavigateToPose.Goal();goal.pose=route.stamped(self.point.pose)
            prefix=route.n.frame_id.rpartition('/')[0]
            goal.behavior_tree=formation_tree(route.planner_id,route.controller_id,(prefix+'/' if prefix else '')+'base_link')
            self.submitted=True;route.submit(route.single,goal,self.finished,'navigation')
        target=route.stamped(self.point.pose)
        self.publisher.publish(target)
        transform=TransformStamped();transform.header=target.header;transform.child_frame_id=self.target_frame
        transform.transform.translation.x=target.pose.position.x;transform.transform.translation.y=target.pose.position.y
        transform.transform.rotation=target.pose.orientation
        self.tf.sendTransform(transform)

    def finished(self, result):
        self.blocked=True
        self.route.stop('本车'+self.label+'动态Nav2任务结束；停止并等待重新开始',failed=True)
