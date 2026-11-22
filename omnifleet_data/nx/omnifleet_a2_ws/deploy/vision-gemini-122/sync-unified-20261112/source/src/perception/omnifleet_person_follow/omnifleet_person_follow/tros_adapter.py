"""104 perception and display bridge; following decisions belong to official TROS."""
import math
import re
import time

from ai_msgs.msg import Attribute, PerceptionTargets, Roi, Target
from geometry_msgs.msg import Point, PoseStamped
from std_msgs.msg import Header, String
from std_srvs.srv import SetBool
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from rclpy.time import Time
from tf2_ros import TransformException
from visualization_msgs.msg import Marker, MarkerArray


def parse_status(text):
    match = re.search(r'(?:FollowStatus |follow status: )([A-Z_]+)', text)
    name = match[1] if match else 'DISABLED'
    fields = dict(re.findall(r':(id|dist|round)=([\d.]+)', text))
    state = ('PAUSED' if name == 'DISABLED' else 'LOST' if name.startswith('LOST')
             else 'TRACKING' if name.startswith('TRACKING') or name == 'WILL_BE_LOST' else 'IDLE')
    identity = int(fields.get('id', 0)) or None
    return name, state, identity, float(fields['dist']) if 'dist' in fields else None


def make_target(track, xyz, intrinsics):
    x0, y0, x1, y1 = map(float, track['bbox'])
    optical = track['xyz']
    target = Target(type='person', track_id=int(track['id']))
    roi = Roi(type='person', confidence=float(track['confidence']))
    roi.rect.x_offset, roi.rect.y_offset = max(0, int(x0)), max(0, int(y0))
    roi.rect.width, roi.rect.height = max(0, int(x1-x0)), max(0, int(y1-y0))
    target.rois = [roi]
    for name, value in [('x_cm', xyz[0]*100), ('y_cm', xyz[1]*100),
                        ('width_cm', (x1-x0)*optical[2]/intrinsics[0]*100),
                        ('height_cm', (y1-y0)*optical[2]/intrinsics[4]*100),
                        ('y_offset', xyz[2]*100)]:
        target.attributes.append(Attribute(type=name, value=float(value), confidence=float(track['confidence'])))
    return target


class TrosAdapter:
    def __init__(self, node):
        self.node = node
        self.name, self.state, self.track_id, self.distance = 'DISABLED', 'PAUSED', None, None
        self.raw_status = 'FollowStatus DISABLED'
        self.goal, self.goal_at, self.actions, self.input_frames = None, 0., 0, 0
        self.desired, self.applied, self.future = None, False, None
        self.input_pub = node.create_publisher(PerceptionTargets, '/vision/person_follow/tros_targets', 1)
        self.enable = node.create_client(SetBool, '/vision/person_follow/enable_follow')
        latched = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.TRANSIENT_LOCAL)
        node.create_subscription(String, '/vision/person_follow/tros_status', self.on_status, latched)
        node.create_subscription(PoseStamped, '/vision/person_follow/nav_goal', self.on_goal, 1)

    def on_status(self, message):
        self.raw_status = message.data
        self.name, self.state, identity, self.distance = parse_status(message.data)
        if identity is not None:
            self.track_id = identity
        elif self.state in ('PAUSED', 'IDLE'):
            self.track_id = None
        self.applied = self.name != 'DISABLED'

    def on_goal(self, message):
        self.goal, self.goal_at = message, time.monotonic()
        self.actions += 1

    def control(self, request):
        operation = request.get('op')
        if operation not in ('lock', 'resume', 'pause'):
            raise ValueError('官方跟随操作只能是 resume 或 pause')
        if operation != 'pause' and not self.node.enable_motion:
            self.node.operator_message = '当前 enable_motion=false，仅识别；官方运动未启用'
            return
        self.desired = operation != 'pause'
        self.node.operator_message = '正在启动官方人物选择与跟随' if self.desired else '正在暂停官方跟随'

    def publish(self, tracks, header, info, transform_point):
        message = PerceptionTargets(header=Header(stamp=header.stamp, frame_id='rgbd_view_z_up'))
        if info is not None:
            try:
                transform = self.node.tf.lookup_transform('rgbd_view_z_up', header.frame_id, Time())
            except TransformException as error:
                self.node.coordinate_error = str(error)
                self.input_pub.publish(message)
                return
            for track in tracks:
                xyz = track.get('xyz')
                if xyz is None or time.monotonic()-track['position_time'] > .3:
                    continue
                point = transform_point(xyz, transform)
                if all(math.isfinite(float(value)) for value in point):
                    message.targets.append(make_target(track, point, info.k))
        self.input_pub.publish(message)
        self.input_frames += 1

    def tick(self):
        if self.future is not None and self.future.done():
            result = self.future.result()
            if result is not None:
                self.node.operator_message = result.message
                if result.success:
                    self.applied = self.future_desired
            self.future = None
        if self.desired is not None and self.desired != self.applied and self.future is None and self.enable.service_is_ready():
            self.future_desired = self.desired
            self.future = self.enable.call_async(SetBool.Request(data=self.desired))
        self.node.manager.state, self.node.manager.track_id = self.state, self.track_id
        self.node.following.range_m = self.distance if self.state == 'TRACKING' else None
        self.node.following.mode = self.name
        self.node.navigation.message = self.raw_status
        self.node.current_goal = None
        marker = Marker(header=self.goal.header if self.goal is not None else Header(frame_id='map'))
        marker.action = Marker.DELETEALL
        markers = [marker]
        if self.goal is not None and self.state in ('TRACKING', 'LOST') and time.monotonic()-self.goal_at < 1.:
            position = self.goal.pose.position
            self.node.current_goal = dict(x=position.x, y=position.y, task='tros')
            marker = Marker(header=self.goal.header, ns='tros_goal', id=0, type=Marker.SPHERE, action=Marker.ADD)
            marker.pose.position = Point(x=position.x, y=position.y, z=.45)
            marker.pose.orientation.w = 1.
            marker.scale.x = marker.scale.y = marker.scale.z = .16
            marker.color.r, marker.color.g, marker.color.a = 1., .8, 1.
            markers = [marker]
        self.node.goal_marker_pub.publish(MarkerArray(markers=markers))

    def annotate(self, status):
        status.update(controller_backend='tros_person_following_cpp', state=self.state,
                      mode='follow' if self.state in ('TRACKING', 'LOST') else self.state.lower(),
                      track_id=self.track_id, person_range_m=self.distance if self.state == 'TRACKING' else None,
                      follow_control_state=self.name, search_phase=self.name if self.state in ('IDLE', 'LOST') else 'OFF',
                      navigation_message=self.raw_status, tros_goal_messages=self.actions,
                      goal_updates=0, lock_source='official_tros_selection',
                      tros_input_frames=self.input_frames, tros_input_topic='/vision/person_follow/tros_targets')
