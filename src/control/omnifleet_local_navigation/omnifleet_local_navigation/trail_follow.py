"""Lease-bound predecessor targets through the native Nav2 GoalUpdater tree."""
import json
import math
import time
from types import SimpleNamespace

from geometry_msgs.msg import Pose

from .formation_follow import FormationFollow


def receive_trail(node, message):
    job=node.current_job
    if not job or job.backend!='trail_follow' or node.policy.canceling:return
    try:
        data=json.loads(message.data)
        if (data.get('mode','trail')!='trail' or data['task_id']!=job.ticket.task_id or data['epoch']!=job.ticket.command_epoch or
            data['revision']!=job.ticket.revision or data['localization_epoch']!=node.epoch or
            not node.fleet_enabled or not node.fleet_lease.matches(job.ticket,time.monotonic())):return
        sequence=data['sequence'];values=data['poses'];velocity=data.get('predecessor_velocity',[0.,0.])
        distance=data.get('follow_distance',0.)
        rate=data.get('range_rate',0.)
        if type(rate) not in (int,float) or not math.isfinite(rate):return
        if type(distance) not in (int,float) or not math.isfinite(distance) or distance<0:return
        if not isinstance(velocity,list) or len(velocity)!=2 or not all(type(v) in (int,float) and math.isfinite(v) for v in velocity):return
        if type(sequence) is not int or sequence<=node.execution.follow.sequence:return
        if not isinstance(values,list) or not 1<=len(values)<=100:return
        points=[]
        for value in values:
            if not isinstance(value,list) or len(value)!=3 or not all(type(v) in (int,float) and math.isfinite(v) for v in value):return
            pose=Pose();pose.position.x,pose.position.y=map(float,value[:2])
            pose.orientation.z=math.sin(value[2]/2);pose.orientation.w=math.cos(value[2]/2)
            points.append(SimpleNamespace(pose=pose))
        node.execution.follow.update(points,sequence,velocity,distance,rate)
    except (ValueError,TypeError,KeyError):return


class TrailFollow(FormationFollow):
    """One native Nav2 task tracks the latest predecessor-relative target."""
    label='领车跟随'
    target_frame='follow_target'

    def start(self, points):
        super().start(points)
        self.predecessor_velocity=[0.,0.];self.follow_distance=0.;self.range_rate=0.

    def update(self, points, sequence, velocity=None, distance=0., rate=0.):
        super().update(points[-1],sequence)
        self.predecessor_velocity=list(velocity or [0.,0.])
        self.follow_distance=distance;self.range_rate=rate

    def catalog(self):
        return {**super().catalog(),'control_mode':'nav2_goal_updater',
                'controller_id':self.route.controller_id,
                'follow_distance':self.follow_distance,
                'predecessor_velocity':self.predecessor_velocity,'range_rate':self.range_rate}
