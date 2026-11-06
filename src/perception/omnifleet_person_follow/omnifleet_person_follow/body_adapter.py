"""Real body/face ROIs and measured base-frame distance for native C++ backoff."""
import json
import math
import time
import numpy as np
from ai_msgs.msg import Attribute, PerceptionTargets, Roi, Target
from geometry_msgs.msg import Twist
from std_msgs.msg import Header, String
from rclpy.time import Time
from visualization_msgs.msg import Marker, MarkerArray


GESTURE_CODES = {'okay': 11, 'open_palm': 5, 'one': 101, 'victory': 102, 'three': 103, 'four': 104}


def body_targets(tracks, header, hands=(), hand_updated=False):
    result = PerceptionTargets(header=Header(stamp=header.stamp, frame_id=header.frame_id), fps=-1)
    for track in tracks:
        x0, y0, x1, y1 = map(int, track['bbox'])
        roi = Roi(type='body', confidence=float(track['confidence']))
        roi.rect.x_offset, roi.rect.y_offset = max(0, x0), max(0, y0)
        roi.rect.width, roi.rect.height = max(0, x1-x0), max(0, y1-y0)
        rois = [roi]
        if track.get('face_bbox') is not None:
            fx0, fy0, fx1, fy1 = map(int, track['face_bbox'])
            face = Roi(type='face', confidence=float(track['face_confidence']))
            face.rect.x_offset, face.rect.y_offset = fx0, fy0
            face.rect.width, face.rect.height = fx1-fx0, fy1-fy0
            rois.append(face)
        attributes = []
        if track.get('range_base_m') is not None:
            attributes = [Attribute(type='range_base_m', value=float(track['range_base_m']), confidence=1.),
                          Attribute(type='range_age_s', value=float(track['range_age_s']), confidence=1.)]
        if track.get('bearing_rad') is not None:
            attributes.append(Attribute(type='bearing_rad', value=float(track['bearing_rad']), confidence=1.))
        if hand_updated:
            observed = next((hand for hand in hands if hand['owner'] == track['id']), None)
            # No visible hand while the camera rotates away is not a release.
            code = GESTURE_CODES.get(observed['gesture'], 0) if observed else -1
            attributes.append(Attribute(type='hand_gesture_observation', value=float(code), confidence=1.))
        result.targets.append(Target(type='person', track_id=int(track['id']), rois=rois, attributes=attributes))
    owners = {track['id'] for track in tracks}
    for hand in hands:
        # 101-104 are robot104 extensions; upstream OK/Palm codes stay unchanged.
        gesture = GESTURE_CODES.get(hand['gesture'])
        if gesture is None or hand['owner'] not in owners:
            continue
        points = np.asarray(hand['points'])[:, :2]
        x0, y0 = np.floor(points.min(axis=0)).astype(int)
        x1, y1 = np.ceil(points.max(axis=0)).astype(int)
        roi = Roi(type='hand', confidence=float(hand['score']))
        roi.rect.x_offset, roi.rect.y_offset = max(0, int(x0)), max(0, int(y0))
        roi.rect.width, roi.rect.height = max(1, int(x1)-roi.rect.x_offset), max(1, int(y1)-roi.rect.y_offset)
        result.targets.append(Target(type='hand', track_id=int(hand['owner']), rois=[roi], attributes=[
            Attribute(type='gesture', value=float(gesture), confidence=float(hand['score'])),
            Attribute(type='body_track_id', value=float(hand['owner']), confidence=1.)]))
    return result


class BodyTrackingAdapter:
    def __init__(self, node):
        self.node = node
        from .face_rois import FaceRois
        self.face_detector = None
        if hasattr(node, 'declare_parameter'):
            model = node.declare_parameter('face_model_path', '').value
            if model:
                self.face_detector = FaceRois(model)
        self.face_ms, self.face_count = 0., 0
        self.state, self.track_id = 'IDLE', None
        self.native = dict(state='INITING', track_id=0, serial_lost_num=0)
        self.input_frames, self.command_at = 0, None
        self.command = dict(linear_x=0., angular_z=0.)
        self.input_pub = node.create_publisher(PerceptionTargets, '/vision/body_tracking/targets', 1)
        node.create_subscription(String, '/vision/body_tracking/native_status', self.on_state, 1)
        node.create_subscription(Twist, '/vision/body_tracking/cmd_vel', self.on_command, 1)
        node.operator_message = '1前进、2后退；3顺时针一圈、4逆时针一圈，转完停车；五指张掌停止'
        node.goal_marker_pub.publish(MarkerArray(markers=[Marker(header=Header(frame_id=node.global_frame),action=Marker.DELETEALL)]))

    def on_state(self, message):
        self.native = json.loads(message.data)
        self.state = {'INITING':'IDLE', 'TRACKING':'TRACKING', 'LOST':'LOST'}[self.native['state']]
        if self.native.get('rotation_done'):
            self.state = 'IDLE'
        self.track_id = int(self.native['track_id']) if self.state != 'IDLE' else None

    def on_command(self, message):
        self.command = dict(linear_x=message.linear.x, angular_z=message.angular.z)
        self.command_at = time.monotonic()

    def detect_faces(self, image, tracks):
        started = time.perf_counter()
        self.face_count = self.face_detector.detect(image, tracks, self.track_id) if self.face_detector else 0
        self.face_ms = (time.perf_counter()-started)*1000

    def publish(self, tracks, header, info, transform_point, hands=()):
        prepared = []
        now = time.monotonic()
        for track in tracks:
            item = dict(track)
            if track['id'] == self.track_id:
                try:
                    transform = self.node.tf.lookup_transform('base_link', header.frame_id, Time())
                    if info is not None and info.k[0] > 0 and info.k[4] > 0:
                        x0,y0,x1,y1 = track['bbox']
                        ray = [((x0+x1)*.5-info.k[2])/info.k[0], ((y0+y1)*.5-info.k[5])/info.k[4], 1.]
                        direction = transform_point(ray,transform)-transform_point([0.,0.,0.],transform)
                        item['bearing_rad'] = math.atan2(direction[1], direction[0])
                    if track.get('xyz') is not None:
                        age = now-track['position_time']
                        if 0. <= age <= .35:
                            point = transform_point(track['xyz'], transform)
                            item.update(range_base_m=math.hypot(point[0],point[1]), range_age_s=age)
                except Exception as error:
                    self.node.coordinate_error = 'Body target base transform: '+str(error)
            prepared.append(item)
        updated = getattr(getattr(self.node, 'perception', None), 'timings', {}).get('hand_updated', False)
        self.input_pub.publish(body_targets(prepared, header, hands, hand_updated=updated))
        self.input_frames += 1

    def tick(self):
        self.node.manager.state, self.node.manager.track_id = self.state, self.track_id
        self.node.manager.follow_distance = self.native.get('target_distance_m', 1.0)
        self.node.following.range_m = self.native.get('range_base_m')
        self.node.following.mode = (self.native.get('control_mode', self.native.get('distance_mode', self.native['state'])) if self.state == 'TRACKING' else self.native['state'])
        self.node.navigation.message = 'Body Tracking: '+self.native['state']
        self.node.current_goal = None

    def annotate(self, status):
        status.update(controller_backend='body_tracking_cpp', strategy='native_body_tracking_depth_follow_pd',
                      gesture_controls={'okay':'lock_and_follow', 'open_palm':'stop_and_unlock',
                                        'one':'forward', 'victory':'backward', 'three':'spin_cw_once', 'four':'spin_ccw_once'},
                      state=self.state, track_id=self.track_id, body_tracking=self.native,
                      motion_enabled=self.native.get('motion_enabled', self.node.enable_motion),
                      follow_control_state=(self.native.get('control_mode', self.native.get('distance_mode', self.native['state'])) if self.state == 'TRACKING' or self.native.get('rotation_done') else self.native['state']), lock_source='official_body_tracking',
                      body_tracking_input_frames=self.input_frames,
                      body_tracking_input_topic='/vision/body_tracking/targets',
                      velocity_request=self.command,
                      velocity_request_age_ms=(time.monotonic()-self.command_at)*1000 if self.command_at else None,
                      depth_display_only=False, depth_backoff_enabled=True, depth_display_m=status.get('target_depth_m'),
                      forward_requires_face_head=False,
                      face_detection_ms=round(self.face_ms, 3), face_count=self.face_count,
                      face_backend=self.face_detector.backend if self.face_detector else 'disabled',
                      metric_distance_control=True, follow_distance_m=self.native.get('target_distance_m', 1.0), person_range_m=self.native.get('range_base_m'),
                      nav2_controller=None, nav_goal=None, obstacle_avoidance='Not used: original body_tracking',
                      search_phase='OFF', navigation_actions=0, goal_updates=0)
