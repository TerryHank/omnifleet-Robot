"""Tracked gesture ownership, depth fusion and D-Robotics-derived follow states.

State/loss prediction adaptation of tros_person_following, Apache-2.0,
202e8c8a04dc41e3d3771daa131b852cc24f7c0d. See NOTICE.md for retained scope.
"""
from collections import deque
from dataclasses import dataclass, field
import math
import numpy as np


def classify_hand(landmarks, world_landmarks=None):
    screen = np.asarray(landmarks, dtype=np.float32).reshape(21, -1)[:, :2]
    # MediaPipe already returns metric 3D hand points. Use them for finger
    # bends so camera foreshortening does not turn a straight finger into a fist.
    points = (screen if world_landmarks is None else
              np.asarray(world_landmarks, dtype=np.float32).reshape(21, 3))
    wrist = points[0]
    extended = []
    for pip, dip, tip in ((6, 7, 8), (10, 11, 12), (14, 15, 16), (18, 19, 20)):
        a, b = wrist - points[pip], points[dip] - points[tip]
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        cosine = float(np.dot(a, b) / norm) if norm > 1e-6 else -1.
        extended.append(cosine > .65 and np.linalg.norm(points[tip] - wrist) > np.linalg.norm(points[pip] - wrist))
    palm_width = np.linalg.norm(points[5] - points[17])
    if (extended == [False, True, True, True] and palm_width > 1e-6 and
            np.linalg.norm(points[4] - points[8]) < .35 * palm_width):
        return 'okay'
    thumb_a, thumb_b = points[1]-points[2], points[3]-points[4]
    thumb_norm = np.linalg.norm(thumb_a)*np.linalg.norm(thumb_b)
    thumb_extended = (thumb_norm > 1e-6 and np.dot(thumb_a,thumb_b)/thumb_norm > .65 and
                      np.linalg.norm(points[4]-wrist) > 1.15*np.linalg.norm(points[2]-wrist))
    if all(extended):
        thumb_open = thumb_extended or (palm_width > 1e-6 and
            np.linalg.norm(points[4]-points[5]) > .55*palm_width and
            np.linalg.norm(points[4]-wrist) > np.linalg.norm(points[2]-wrist))
        return 'open_palm' if thumb_open else 'four'
    if ((extended == [True,True,True,False] and not thumb_extended) or
            (extended == [True,True,False,False] and thumb_extended)):
        return 'three'
    if extended == [True,False,False,False] and not thumb_extended:
        return 'one'
    if extended == [True, True, False, False]:
        return 'victory'
    thumb_up = (np.linalg.norm(points[4] - wrist) > np.linalg.norm(points[2] - wrist) * 1.15 and
                screen[4, 1] < screen[3, 1] < screen[2, 1])
    if not any(extended) and thumb_up:
        return 'thumbs_up'
    if not any(extended) and not thumb_extended:
        return 'fist'
    return 'unknown'


def mask_coordinates(x, y, image_shape, mask_shape):
    """Original-image pixel to YOLO's letterboxed mask pixel."""
    height, width = image_shape[:2]
    mh, mw = mask_shape
    gain = min(mw / width, mh / height)
    left, top = round((mw - round(width * gain)) / 2 - .1), round((mh - round(height * gain)) / 2 - .1)
    return ((np.asarray(x) * gain + left).astype(int).clip(0, mw - 1),
            (np.asarray(y) * gain + top).astype(int).clip(0, mh - 1))


def hand_owner(wrist, tracks, image_shape):
    """Require unambiguous wrist membership; never borrow a bystander's hand."""
    x, y = wrist
    owners = []
    for track in tracks:
        x1, y1, x2, y2 = track['bbox']
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            continue
        mask = track['mask']
        mx, my = mask_coordinates(x, y, image_shape, mask.shape)
        if mask[max(0, my-2):my+3, max(0, mx-2):mx+3].any():
            owners.append(track['id'])
    return owners[0] if len(owners) == 1 else None


def depth_position(track, depth, intrinsic, image_shape, minimum=.2, maximum=1.5):
    """Median of original measured mask pixels; no filled depth or generated cloud."""
    height, width = image_shape[:2]
    if depth.shape != (height, width):
        raise ValueError('Registered depth must have the RGB image dimensions')
    x1, y1, x2, y2 = np.asarray(track['bbox'], int)
    y, x = np.mgrid[max(0, y1):min(height, y2):3, max(0, x1):min(width, x2):3]
    if not x.size:
        return None
    mx, my = mask_coordinates(x, y, image_shape, track['mask'].shape)
    z = depth[y, x].astype(np.float32) * .001
    valid = track['mask'][my, mx] & (z >= minimum) & (z <= maximum)
    if not valid.any():
        return None
    fx, fy, cx, cy = intrinsic
    return np.array([np.median((x[valid] - cx) * z[valid] / fx),
                     np.median((y[valid] - cy) * z[valid] / fy), np.median(z[valid])])


def target_rgb_pixel(track, image_shape):
    """Box centre, moved onto the nearest measured person-mask pixel if needed."""
    x1, y1, x2, y2 = track['bbox']
    center = np.array([(x1+x2)/2., (y1+y2)/2.])
    mask = track['mask']
    mx, my = mask_coordinates(*center, image_shape, mask.shape)
    if mask[my, mx]:
        return center
    y, x = np.nonzero(mask)
    if not x.size:
        return None
    h, w = image_shape[:2]
    mh, mw = mask.shape
    gain = min(mw/w, mh/h)
    left, top = round((mw-round(w*gain))/2-.1), round((mh-round(h*gain))/2-.1)
    pixels = np.c_[(x-left)/gain, (y-top)/gain]
    valid = (pixels[:, 0] >= x1) & (pixels[:, 0] < x2) & (pixels[:, 1] >= y1) & (pixels[:, 1] < y2)
    pixels = pixels[valid]
    return None if not len(pixels) else pixels[np.argmin(np.sum((pixels-center)**2, axis=1))]


def trailing_goal(robot, person, distance):
    direction = np.asarray(person[:2], float) - np.asarray(robot[:2], float)
    length = np.linalg.norm(direction)
    if length <= distance:
        return [float(robot[0]), float(robot[1]), math.atan2(direction[1], direction[0])]
    xy = np.asarray(person[:2]) - direction / length * distance
    return [float(xy[0]), float(xy[1]), math.atan2(direction[1], direction[0])]


@dataclass
class FollowManager:
    follow_distance: float = 1.
    tracking_to_lost_timeout: float = 1.
    prediction_window: float = 6.
    prediction_lead: float = 2.
    prediction_max_distance: float = 3.
    prediction_timeout: float = 5.
    state: str = 'IDLE'
    track_id: int | None = None
    last_seen: float = 0.
    history: deque = field(default_factory=deque)
    lost_since: float | None = None
    candidates: dict = field(default_factory=dict)
    last_bbox: list | None = None
    relock_reason: str = ''

    def auto_lock(self, tracks, now, width):
        if self.state != 'IDLE' or self.track_id is not None or not tracks:
            return None
        track = min(tracks,key=lambda t:(abs((t['bbox'][0]+t['bbox'][2])/2-width/2),-t.get('confidence',0.)))
        self.track_id,self.state = track['id'],'TRACKING'
        self.last_seen,self.lost_since,self.last_bbox = now,None,track['bbox']
        self.history.clear();self.candidates.clear()
        self.relock_reason = 'auto_person_detection'
        return track

    def gesture(self, gesture, owner):
        if owner is None or gesture == 'unknown':
            return None
        if self.track_id is None:
            if gesture != 'thumbs_up':
                return None
            self.track_id, self.state = owner, 'TRACKING'
            self.history.clear()
            self.candidates.clear()
            self.lost_since = None
            return 'locked'
        if self.state == 'LOST' and gesture == 'thumbs_up':
            if owner != self.track_id:
                self.history.clear()
            self.track_id, self.state = owner, 'TRACKING'
            self.candidates.clear()
            self.lost_since = None
            self.relock_reason = 'explicit_thumbs_up'
            return 'relocked'
        if owner != self.track_id:
            return None
        if gesture == 'victory':
            self.track_id, self.state = None, 'IDLE'
            self.history.clear()
            self.candidates.clear()
            self.lost_since = None
            return 'ended'
        if gesture == 'open_palm':
            if self.state == 'PAUSED':
                return None
            self.state = 'PAUSED'
            return 'paused'
        if gesture == 'thumbs_up':
            if self.state == 'TRACKING':
                return None
            self.state = 'TRACKING'
            return 'resumed'
        return None

    def observe(self, tracks, now):
        track = next((t for t in tracks if t['id'] == self.track_id), None)
        if track is not None:
            self.last_bbox = track.get('bbox', self.last_bbox)
        usable = track is not None and track.get('world') is not None and now-track.get('position_time', now) <= self.tracking_to_lost_timeout
        if usable and self.state == 'LOST' and self.history:
            usable = self.relock_separation(track['world'], now) <= self.relock_distance(now)
        if usable:
            self.last_seen = track.get('position_time', now)
            if not self.history or self.last_seen > self.history[-1][0]:
                self.history.append((self.last_seen, np.asarray(track['world'], float)))
            while len(self.history) > 2 and now-self.history[0][0] > self.prediction_window:
                self.history.popleft()
            if self.state == 'LOST':
                self.state, self.lost_since = 'TRACKING', None
                self.relock_reason = 'same_id_spatial_continuity'
                self.candidates.clear()
        elif self.state == 'TRACKING' and now-self.last_seen >= self.tracking_to_lost_timeout:
            self.state = 'LOST'
            self.lost_since = now
            self.candidates.clear()
        if self.state == 'LOST':
            replacement = self.relock_candidate(tracks, now)
            if replacement is not None:
                self.track_id, self.state = replacement['id'], 'TRACKING'
                self.last_seen = replacement.get('position_time', now)
                self.history.append((self.last_seen, np.asarray(replacement['world'], float)))
                self.last_bbox = replacement.get('bbox', self.last_bbox)
                self.lost_since = None
                self.candidates.clear()
                self.relock_reason = 'new_id_spatial_motion_continuity'
                track = replacement
        return track

    def relock_reference(self, now):
        predicted = self.predicted_position(now)
        return predicted if predicted is not None else self.history[-1][1] if self.history else None

    def relock_distance(self, now):
        elapsed = now-(self.lost_since if self.lost_since is not None else now)
        return 1.5 if elapsed < 2. else 3. if elapsed < 5. else 5.

    def relock_separation(self, point, now):
        references = [self.history[-1][1], self.relock_reference(now)]
        return min(np.linalg.norm(np.asarray(point)[:2]-reference[:2]) for reference in references)

    def relock_candidate(self, tracks, now):
        reference = self.relock_reference(now)
        if reference is None:
            return None
        choices = []
        visible = {track['id'] for track in tracks}
        self.candidates = {identity:history for identity,history in self.candidates.items()
                           if identity in visible and now-history[-1][0] <= 2.}
        for track in tracks:
            if track['id'] == self.track_id or track.get('world') is None or track.get('confidence', 0.) < .5:
                continue
            stamp = track.get('position_time', now)
            if now-stamp > self.tracking_to_lost_timeout:
                continue
            point = np.asarray(track['world'], float)
            history = self.candidates.setdefault(track['id'], deque())
            if not history or stamp > history[-1][0]:
                history.append((stamp, point))
            while len(history) > 1 and stamp-history[0][0] > 2.:
                history.popleft()
            distance = self.relock_separation(point, now)
            movement = np.linalg.norm(point[:2]-history[0][1][:2])
            if len(history) >= 2 and movement > .2 and distance <= self.relock_distance(now):
                choices.append((track['confidence']/(1+distance), track))
        return max(choices, key=lambda item:item[0])[1] if choices else None

    def predicted_position(self, now):
        # D-Robotics predictTargetPose: recent velocity, limited extrapolation.
        if (len(self.history) < 2 or now - self.last_seen > self.prediction_timeout or
                now - self.history[-1][0] > self.prediction_timeout):
            return None
        first, last = self.history[0], self.history[-1]
        dt = last[0] - first[0]
        if dt <= .01:
            return None
        delta = (last[1] - first[1]) / dt * (now - last[0] + self.prediction_lead)
        length = np.linalg.norm(delta[:2])
        if length > self.prediction_max_distance:
            delta *= self.prediction_max_distance / length
        return last[1] + delta

    def target(self, track, now):
        if self.state == 'TRACKING':
            if track is not None and track.get('world') is not None and now-track.get('position_time', now) <= self.tracking_to_lost_timeout:
                return track['world']
            # Retain the last measurement in the upstream pending-loss window;
            # a single dropped depth/detection frame must not cancel/restart Nav2.
            if self.history and now - self.history[-1][0] <= self.tracking_to_lost_timeout:
                return self.history[-1][1]
        if self.state == 'LOST':
            return self.predicted_position(now)
        return None
