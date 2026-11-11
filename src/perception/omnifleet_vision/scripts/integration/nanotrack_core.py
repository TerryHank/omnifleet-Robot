"""NanoTrack visual updates with detector IDs; people retain BoT-SORT."""
from pathlib import Path
from types import SimpleNamespace, MethodType
import time

import cv2
import numpy as np
import yaml

from vision_integration_core import IoUTracker, bbox_iou
from nanotrack_tracker import NanoTracker


def source_stamp(payload, fallback):
    if not isinstance(payload,dict):return fallback
    value = payload.get('source_stamp', payload.get('stamp', fallback))
    if isinstance(value, dict):
        return float(value['sec']) + float(value.get('nanosec', value.get('nsec', 0))) * 1e-9
    return float(value)


def foreground_box(predicted,foreground):
    """Clip the visual prediction to foreground; never grow it to the search ROI."""
    x,y,w,h=predicted;fx,fy,fw,fh=foreground
    left,top=max(x,fx),max(y,fy)
    right,bottom=min(x+w,fx+fw),min(y+h,fy+fh)
    return [left,top,right-left,bottom-top] if right-left>=2 and bottom-top>=2 else predicted


class NanoFactory:
    def __init__(self, root, runtime='auto', verify_template=False):
        self.root = Path(root)
        self.verify_template=verify_template
        targets = cv2.dnn.getAvailableTargets(cv2.dnn.DNN_BACKEND_CUDA)
        self.cuda = runtime != 'cpu' and cv2.dnn.DNN_TARGET_CUDA_FP16 in targets
        self.runtime = 'cuda_fp16' if self.cuda else 'cpu'
        self.preloaded = None

    def new_tracker(self):
        backend = cv2.dnn.DNN_BACKEND_CUDA if self.cuda else cv2.dnn.DNN_BACKEND_OPENCV
        target = cv2.dnn.DNN_TARGET_CUDA_FP16 if self.cuda else cv2.dnn.DNN_TARGET_CPU
        return NanoTracker(self.root, backend, target, verify_template=self.verify_template)

    def preload(self):
        self.preloaded = self.new_tracker()
        image = np.full((192, 192, 3), 127, np.uint8)
        self.preloaded.init(image, (64, 64, 64, 64))
        self.preloaded.update(image)

    def create(self, image, bbox):
        tracker = self.preloaded if self.preloaded is not None else self.new_tracker()
        tracker.init(image, tuple(int(round(v)) for v in bbox))
        return tracker


class KcfFactory:
    cuda=False
    runtime='cpu'

    def create(self,image,bbox):
        class Kcf:
            def __init__(self):self.tracker=cv2.TrackerKCF_create()
            def init(self,image,bbox):self.tracker.init(image,tuple(int(round(v)) for v in bbox))
            def update(self,image):return self.tracker.update(image)
            def getTrackingScore(self):return 0.
        tracker=Kcf();tracker.init(image,bbox)
        return tracker


class HybridTracks:
    def __init__(self, factory, person_config, timeout=1., iou_threshold=.3, foreground=None):
        self.factory, self.person_config, self.timeout = factory, person_config, timeout
        self.association = IoUTracker(iou_threshold=iou_threshold, timeout=timeout)
        self.visual, self.identities, self.visual_boxes = {}, {}, {}
        self.retired=[]
        self.next_id = 1
        self.people, self.person_tracker, self.last_people = [], None, None
        self.inference_ms = 0.
        self.foreground = foreground

    def observation(self,image,item,bbox=None):
        if self.foreground is None:return image,dict(item,bbox=bbox or item['bbox'])
        return self.foreground(image,item,bbox or item['bbox'])

    def identity(self, kind, value):
        key = (kind, int(value))
        if key not in self.identities:
            self.identities[key] = self.next_id
            self.next_id += 1
        return self.identities[key]

    def _person_update(self, detections, image, sx, sy, now):
        if not detections and self.person_tracker is None:
            return
        if self.person_tracker is None:
            import torch
            torch.set_num_threads(1)
            from ultralytics.trackers.bot_sort import BOTSORT
            settings = SimpleNamespace(**yaml.safe_load(Path(self.person_config).read_text()))
            self.person_tracker = BOTSORT(settings)
            gmc = self.person_tracker.gmc
            gmc.downscale = 4
            gmc.feature_params.update(maxCorners=200, minDistance=4)
            gmc.reset_params()
            if self.factory.cuda:
                from omnifleet_person_follow.cuda_gmc import apply_sparseoptflow
                gmc.apply_sparseoptflow = MethodType(apply_sparseoptflow, gmc)
        from ultralytics.engine.results import Boxes
        values = []
        for item in detections:
            x,y,w,h = item['bbox']
            values.append([x*sx,y*sy,(x+w)*sx,(y+h)*sy,item['confidence'],0])
        boxes = Boxes(np.asarray(values, np.float32).reshape(-1,6), image.shape[:2])
        rows = self.person_tracker.update(boxes, image)
        self.people = []
        for row in rows:
            item = dict(detections[int(row[-1])])
            item.update(track_id=self.identity('person', row[4]),
                        bbox=[float(row[0]/sx),float(row[1]/sy),float((row[2]-row[0])/sx),float((row[3]-row[1])/sy)],
                        tracker='BoT-SORT', tracking_score=float(row[5]))
            self.people.append(item)
        self.last_people = now

    def detect(self, detections, image, sx, sy, now):
        # Detector boxes own association IDs. Foreground geometry may be only a
        # visible surface; feeding its changing extent back into IoU association
        # would repeatedly create IDs for the same color/object detection.
        objects = [d for d in detections if d['class'] != 'person']
        people = [self.observation(image,d)[1] for d in detections if d['class']=='person']
        tracks = self.association.update(objects, now)
        for item in tracks:
            key = item['track_id']
            item=dict(item,track_id=self.identity('object',key))
            appearance,observed=self.observation(image,item)
            if key not in self.visual:
                x,y,w,h = observed['bbox']
                if self.retired:
                    tracker=self.retired.pop()
                    tracker.init(appearance,tuple(int(round(v)) for v in [x*sx,y*sy,w*sx,h*sy]))
                else:tracker = self.factory.create(appearance, [x*sx,y*sy,w*sx,h*sy])
                self.visual[key] = tracker
            elif key in self.visual_boxes and bbox_iou(item['bbox'],self.visual_boxes[key]) < self.association.iou_threshold:
                x,y,w,h = item['bbox']
                self.visual[key].init(appearance,tuple(int(round(v)) for v in [x*sx,y*sy,w*sx,h*sy]))
        self._person_update(people, image, sx, sy, now)
        self._expire(now)

    def _expire(self, now):
        self.association._expire(now)
        self.retired.extend(value for key,value in self.visual.items() if key not in self.association._tracks)
        self.visual = {key:value for key,value in self.visual.items() if key in self.association._tracks}
        self.visual_boxes = {key:value for key,value in self.visual_boxes.items() if key in self.visual}
        alive = {('object', key) for key in self.association._tracks}
        if self.person_tracker is not None:
            alive.update(('person', int(t.track_id)) for t in self.person_tracker.tracked_stracks + self.person_tracker.lost_stracks)
        self.identities = {key:value for key,value in self.identities.items() if key in alive}

    def update(self, image, sx, sy, now):
        self._expire(now)
        output = []
        start = time.perf_counter()
        for key, tracker in self.visual.items():
            item = dict(self.association._tracks[key].detection)
            item['track_id']=self.identity('object',key)
            search=self.visual_boxes.get(key,item['bbox'])
            appearance,observed=self.observation(image,item,search)
            ok, box = tracker.update(appearance)
            if not ok:
                continue
            x,y,w,h = box
            item.update(bbox=[x/sx,y/sy,w/sx,h/sy], track_id=self.identity('object',key),
                        tracker='NanoTrack', tracking_score=float(tracker.getTrackingScore()),
                        detection_age_s=now-self.association._tracks[key].last_seen)
            if observed.get('foreground',{}).get('available'):
                item.update(bbox=foreground_box(item['bbox'],observed['bbox']),foreground=observed['foreground'],center=observed['center'])
            self.visual_boxes[key] = [x/sx,y/sy,w/sx,h/sy]
            output.append(item)
        self.inference_ms = (time.perf_counter()-start)*1000.
        if self.last_people is not None and now-self.last_people <= self.timeout:
            output.extend(self.people)
        return sorted(output, key=lambda item:item['track_id'])
