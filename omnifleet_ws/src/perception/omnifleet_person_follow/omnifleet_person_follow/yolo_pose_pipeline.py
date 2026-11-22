"""YOLO26 GPU poses with the existing tracker, smoothing and control schema."""
from pathlib import Path
from types import SimpleNamespace
import time

import cv2
import numpy as np
import yaml
from .pose_actions import classify_pose, hip_region, visible
from .pose_smoothing import PoseSmoothing
from .trt_net import TensorRTNet


# COCO's 17 measured joints mapped to the existing 33-slot display schema.
COCO_TO_POSE = [0,2,5,7,8,11,12,13,14,15,16,23,24,25,26,27,28]
LEFT_BODY = [11,13,15,23,25,27]
RIGHT_BODY = [12,14,16,24,26,28]


def correct_body_sides(pose, now, previous=None):
    # Compare the left-to-right shoulder and hip axes. Translation of the
    # person does not affect the comparison between consecutive frames.
    axes = np.array([pose[a,:2]-pose[b,:2] if visible(pose,[a,b]) else [0.,0.]
                     for a,b in [(11,12),(23,24)]])
    eye_order = pose[2,0]-pose[5,0] if visible(pose,[0,2,5]) else 0.
    body_order = axes[0,0] or axes[1,0]
    if eye_order and body_order:
        agreement = eye_order * body_order
    elif previous is not None and now-previous[1] <= .35:
        agreement = float(np.sum(axes * previous[0]))
        if not agreement:
            return previous
    else:
        return None
    if agreement < 0:
        pose[LEFT_BODY+RIGHT_BODY] = pose[RIGHT_BODY+LEFT_BODY]
        axes = -axes
    return axes, now


class YoloPosePipeline:
    def __init__(self, engine, tracker_config):
        from ultralytics.engine.results import Boxes
        from ultralytics.trackers.bot_sort import BOTSORT
        self.model = TensorRTNet(engine, ['output0'])
        settings = yaml.safe_load(Path(tracker_config).read_text())
        settings['track_high_thresh'] = settings['track_low_thresh']
        settings['new_track_thresh'] = settings['track_low_thresh']
        self.tracker = BOTSORT(SimpleNamespace(**settings))
        self.tracker.gmc.downscale = 8
        self.tracker.gmc.feature_params.update(maxCorners=200,minDistance=4)
        self.tracker.gmc.reset_params()
        self.boxes_type = Boxes
        self.filters = {}
        self.body_sides = {}
        self.shape = None
        self.detector_ran = True
        self.backend = Path(engine).name.split('.')[0] + ' TensorRT FP16 GPU'

    def infer(self, image):
        timestamp = time.monotonic()
        if self.shape is not None and self.shape != image.shape[:2]:
            self.tracker.reset()
            self.filters.clear()
            self.body_sides.clear()
        self.shape = image.shape[:2]
        boxes, keypoints = self.detect(image)
        tracked = self.tracker.update(self.boxes_type(boxes,image.shape[:2]),image)
        tracks, actions, filters = [], [], {}
        body_sides = {}
        for box in tracked:
            index, identity = int(box[-1]), int(box[4])
            joints = keypoints[index]
            pose = np.zeros((33,5),np.float32)
            pose[COCO_TO_POSE,:2] = joints[:,:2]
            pose[COCO_TO_POSE,3] = joints[:,2]
            pose[COCO_TO_POSE,4] = joints[:,2]
            body_sides[identity] = correct_body_sides(pose,timestamp,self.body_sides.get(identity))
            action = classify_pose(pose)
            smoother = self.filters.get(identity) or PoseSmoothing(1.,3.)
            scale = np.linalg.norm(pose[11,:2]-pose[12,:2])
            pose[:,:3] = smoother.update(pose[:,:3],timestamp,scale,(pose[:,3:5]>=.5).all(1))
            filters[identity] = smoother
            center, region = hip_region(pose,image.shape)
            tracks.append(dict(id=identity,bbox=box[:4].tolist(),confidence=float(box[5]),
                               pose=pose,pose_action=action,hip_center=center,hip_roi=region,
                               mask=None,foreground_result=None))
            actions.append(dict(owner=identity,points=pose[[11,12,13,14,15,16],:3],
                                gesture=action,score=float(box[5]),pose_action=True))
        self.filters = filters
        self.body_sides = body_sides
        return tracks, actions

    def detect(self, image):
        height, width = image.shape[:2]
        _, _, input_height, input_width = self.model.input_shape
        ratio = min(input_height / height, input_width / width)
        resized_width, resized_height = round(width * ratio), round(height * ratio)
        half_x, half_y = (input_width - resized_width) / 2, (input_height - resized_height) / 2
        left, top = round(half_x - .1), round(half_y - .1)
        resized = cv2.resize(image, (resized_width, resized_height))
        padded = cv2.copyMakeBorder(resized, top, round(half_y + .1), left, round(half_x + .1),
                                    cv2.BORDER_CONSTANT, value=(114, 114, 114))
        self.model.setInput(cv2.dnn.blobFromImage(padded, scalefactor=1 / 255., swapRB=True))
        rows = self.model.forward(['output0'])[0][0]
        rows = rows[(rows[:, 4] > .5) & (rows[:, 5] == 0)]
        boxes = rows[:, :6].copy()
        boxes[:, :4] = (boxes[:, :4] - [left, top, left, top]) / ratio
        boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, width)
        boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, height)
        joints = rows[:, 6:].reshape(-1, 17, 3).copy()
        joints[:, :, :2] = (joints[:, :, :2] - [left, top]) / ratio
        joints[:, :, 0] = np.clip(joints[:, :, 0], 0, width)
        joints[:, :, 1] = np.clip(joints[:, :, 1], 0, height)
        return boxes, joints

    def close(self):
        self.model.close()
