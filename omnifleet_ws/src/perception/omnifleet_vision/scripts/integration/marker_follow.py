"""Decoded marker identity, KCF continuity and explicit range-source selection."""
from collections import deque
import cv2
import numpy as np
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import String
from sensor_msgs.msg import Range
from rclpy.time import Time
import json
from foreground_ros import RosForeground


class MarkerFollow:
    def __init__(self, node, kind):
        self.node, self.kind = node, kind
        self.source = node.declare_parameter('distance_source', 'depth').value
        self.identity, self.tracker, self.box = None, None, None
        self.foreground = RosForeground(node)
        self.pending_depth = deque(maxlen=24)
        self.foreground.wake = self.on_native_depth
        self.publisher = node.create_publisher(String, '/vision/'+kind+'/tracks', 1)
        self.range_publisher = node.create_publisher(Range, '/vision/'+kind+'/follow/range', 1)
        self.callback = node.add_on_set_parameters_callback(self.parameters)

    def parameters(self, parameters):
        result = SetParametersResult(successful=True)
        for parameter in parameters:
            if parameter.name == 'distance_source':
                choices = ('depth', 'rgb') if self.kind == 'apriltag' else ('depth',)
                if parameter.value not in choices:
                    return SetParametersResult(successful=False, reason='Unsupported marker distance_source')
        for parameter in parameters:
            if parameter.name == 'distance_source':
                self.source = parameter.value
        return result

    def on_native_depth(self):
        if self.source != 'depth' or not self.foreground.depths:
            return
        latest = self.foreground.image_stamp(self.foreground.depths[-1])
        while self.pending_depth and self.pending_depth[0][0] <= latest:
            stamp, size, box, corners, frame_id = self.pending_depth.popleft()
            self.foreground.prepare(stamp, size)
            if self.foreground.depth is None:
                continue
            mask = None
            if corners is not None:
                mask = np.zeros((size[1], size[0]), np.uint8)
                cv2.fillConvexPoly(mask, corners, 255)
            geometry = self.foreground.describe(self.foreground.query(box, mask))
            if geometry.get('depth_m') is None:
                continue
            measurement = Range(min_range=.2, max_range=3.5, range=float(geometry['depth_m']))
            measurement.header.frame_id = frame_id
            measurement.header.stamp = Time(seconds=geometry['depth_stamp']).to_msg()
            self.range_publisher.publish(measurement)

    def process(self, image, message, result, debug):
        stamp = message.header.stamp.sec+message.header.stamp.nanosec*1e-9
        candidates = result.get('detections', [])
        key = lambda item: str(item['id']) if self.kind == 'apriltag' else item.get('text', '')
        candidates = [item for item in candidates if key(item)]
        if self.identity is None and candidates:
            self.identity = key(candidates[0])
        detection = next((item for item in candidates if key(item) == self.identity), None)
        observed = detection is not None
        if observed:
            points = np.asarray(detection['corners'], np.float32).reshape(-1, 2)
            x, y, w, h = cv2.boundingRect(points)
            x, y = max(0, x), max(0, y)
            box = (x, y, min(w, image.shape[1]-x), min(h, image.shape[0]-y))
            self.tracker = cv2.TrackerKCF_create()
            self.tracker.init(image, box)
            self.tracker.update(image)
            self.box = box
        elif self.tracker is not None:
            ok, box = self.tracker.update(image)
            self.box = box if ok else None
            if self.box is not None:
                x, y, w, h = self.box
                for item in result.get('visible_tags', candidates):
                    points = np.asarray(item['corners'], np.float32).reshape(-1, 2)
                    if key(item) != self.identity and cv2.pointPolygonTest(points, (x+w/2, y+h/2), False) >= 0:
                        self.box, self.tracker = None, None
                        break
        tracks = []
        if self.box is None:
            self.pending_depth.clear()
        if self.box is not None:
            x, y, w, h = self.box
            geometry = dict(available=False, depth_m=None, projection_backend=self.source)
            if self.source == 'rgb':
                position = detection.get('position_m') if observed else None
                if position is not None:
                    geometry.update(available=True, depth_m=float(position[2]), depth_stamp=stamp,
                                    rgb_xyz_m=position, sampled_count=0, projection_backend='rgb_pnp')
            else:
                self.foreground.prepare(stamp, (image.shape[1], image.shape[0]))
                mask = None
                if observed:
                    mask = np.zeros(image.shape[:2], np.uint8)
                    cv2.fillConvexPoly(mask, points.astype(np.int32), 255)
                geometry = self.foreground.describe(self.foreground.query(self.box, mask))
                if self.foreground.depth is None:
                    self.pending_depth.append((stamp, (image.shape[1], image.shape[0]),
                        tuple(self.box), points.astype(np.int32) if observed else None,
                        message.header.frame_id))
            tracks = [dict(track_id=1, code_identity=self.identity, **{'class':self.kind},
                           bbox=list(self.box), center=[x+w/2, y+h/2], foreground=geometry,
                           tracker='marker_kcf', tracking_score=0., decoded_this_frame=observed)]
        payload = dict(source_stamp=stamp, frame_id=message.header.frame_id,
                       image_width=message.width, image_height=message.height,
                       tracks=tracks, tracker=self.kind+'_kcf', runtime='cpu',
                       distance_source=self.source, code_identity=self.identity,
                       foreground_depth_ready=self.foreground.color_info is not None if self.source=='rgb' else self.foreground.depth is not None)
        self.publisher.publish(String(data=json.dumps(payload, separators=(',', ':'))))
        measurement = Range(min_range=.2, max_range=3.5, range=float('nan'))
        measurement.header.frame_id = message.header.frame_id
        measurement.header.stamp = message.header.stamp
        if tracks and tracks[0]['foreground'].get('depth_m') is not None:
            geometry = tracks[0]['foreground']
            measurement.range = float(geometry['depth_m'])
            measurement.header.stamp = Time(seconds=geometry['depth_stamp']).to_msg()
        if self.source != 'depth' or not tracks or np.isfinite(measurement.range):
            self.range_publisher.publish(measurement)
        result.update(tracks=tracks, distance_source=self.source, code_identity=self.identity)
        if tracks:
            x, y, w, h = map(int, self.box)
            cv2.rectangle(debug, (x,y), (x+w,y+h), (0,255,255), 2)
        return debug, result
