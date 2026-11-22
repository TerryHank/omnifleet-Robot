"""Keep the followed identity across short tracker-ID breaks, without a ReID network."""
import cv2
import numpy as np


class FollowIdentity:
    def __init__(self):
        self.identity = self.tracker_id = None
        self.bbox = self.histogram = self.depth = None
        self.depth_time = self.seen = self.updated = 0.
        self.velocity = np.zeros(2)
        self.rebindings = 0
        self.reason = ''

    @staticmethod
    def appearance(image, bbox):
        x0, y0, x1, y1 = bbox
        width, height = x1-x0, y1-y0
        x0, x1 = int(x0+width*.2), int(x1-width*.2)
        y0, y1 = int(y0+height*.2), int(y0+height*.7)
        crop = image[max(0,y0):max(0,y1), max(0,x0):max(0,x1)]
        if not crop.size:
            return None
        hsv = cv2.cvtColor(cv2.resize(crop, (32, 48)), cv2.COLOR_BGR2HSV)
        histogram = cv2.calcHist([hsv], [0,1], None, [16,8], [0,180,0,256])
        return cv2.normalize(histogram, histogram, alpha=1., norm_type=cv2.NORM_L1)

    def apply(self, tracks, image, locked_id, now, warp, positions):
        for track in tracks:
            track['tracker_id'] = track['id']
        if locked_id != self.identity:
            self.identity, self.tracker_id = locked_id, locked_id
            self.bbox = self.histogram = self.depth = None
            self.velocity[:] = 0
            self.reason = ''
        if locked_id is None:
            return
        elapsed = max(0., now-self.updated)
        gap = now-self.seen
        if self.bbox is not None:
            x0,y0,x1,y1 = self.bbox
            corners = np.array([[x0,y0,1.],[x1,y0,1.],[x1,y1,1.],[x0,y1,1.]]) @ warp.T
            self.bbox = np.r_[corners.min(axis=0), corners.max(axis=0)]
            self.bbox += np.tile(self.velocity*elapsed, 2)
        self.updated = now
        selected = next((track for track in tracks if track['tracker_id'] == self.tracker_id), None)
        if selected is None and self.bbox is not None and gap <= 2.:
            matches = []
            width, height = self.bbox[2:]-self.bbox[:2]
            center = (self.bbox[:2]+self.bbox[2:])*.5
            for track in tracks:
                if track['confidence'] < .7:
                    continue
                bbox = np.asarray(track['bbox'])
                size = (bbox[2:]-bbox[:2]) / np.maximum([width,height], 1.)
                displacement = np.linalg.norm((bbox[:2]+bbox[2:])*.5-center)/max(height, 1.)
                if np.any(size < .5) or np.any(size > 2.) or displacement > .8:
                    continue
                histogram = self.appearance(image, bbox)
                if histogram is None or self.histogram is None:
                    continue
                appearance = cv2.compareHist(self.histogram, histogram, cv2.HISTCMP_BHATTACHARYYA)
                if appearance > .4:
                    continue
                position = positions.get(track['tracker_id'])
                depth_difference = 0.
                if (position is not None and self.depth is not None and
                        now-position['position_time'] < .5 and now-self.depth_time <= 2.):
                    depth_difference = abs(float(position['xyz'][2])-self.depth)
                    if depth_difference > .5+gap:
                        continue
                score = displacement + appearance + .2*abs(np.log(size)).sum() + .1*depth_difference
                matches.append((score, track))
            matches.sort(key=lambda item:item[0])
            if matches and (len(matches) == 1 or matches[1][0]-matches[0][0] >= .15):
                selected = matches[0][1]
                self.reason = f"tracker {self.tracker_id} -> {selected['tracker_id']}; follow ID {locked_id} retained"
                self.tracker_id = selected['tracker_id']
                self.rebindings += 1
        if selected is None:
            return
        observed = np.asarray(selected['bbox'], dtype=float)
        if self.bbox is not None and 0. < elapsed <= .2 and gap <= .2:
            innovation = ((observed[:2]+observed[2:])-(self.bbox[:2]+self.bbox[2:]))*.5
            self.velocity += .2*innovation/elapsed
            self.velocity = np.clip(self.velocity, -(observed[3]-observed[1]), observed[3]-observed[1])
        elif gap > .2:
            self.velocity[:] = 0
        histogram = self.appearance(image, observed)
        if histogram is not None and selected['confidence'] >= .7:
            self.histogram = histogram if self.histogram is None else .9*self.histogram+.1*histogram
        self.bbox, self.seen = observed, now
        selected['id'] = locked_id
        # A surviving old tracker ID must not collide with the remapped follow ID.
        tracks[:] = [track for track in tracks if track is selected or track['id'] != locked_id]

    def observe_depth(self, positions):
        position = positions.get(self.identity)
        if position is not None:
            self.depth = float(position['xyz'][2])
            self.depth_time = position['position_time']
