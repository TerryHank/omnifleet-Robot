"""Detect palms in person rectangles, then track and classify complete hands."""
from pathlib import Path
import sys
import cv2
import numpy as np
sys.path.insert(0,str(Path.home()/'omnifleet_ws/.env/hand-runtime'))
from mediapipe.framework.formats import rect_pb2
from .core import classify_gesture
from .hand_full_gpu import HandFullGpu
from .hand_geometry import canonical_hand,image_rotation
from .hand_nanotrack import HandNanoTrack
from .palm_detector import PalmDetector


def complete_hand_roi(points):
    angle = image_rotation(points)
    cosine, sine = np.cos(angle), np.sin(angle)
    matrix = np.array([[cosine,-sine],[sine,cosine]])
    aligned = points[:,:2]@matrix
    low, high = aligned.min(0), aligned.max(0)
    center = ((low+high)/2)@matrix.T
    return float(center[0]),float(center[1]),max(2.,float(max(high-low)*1.6)),angle


class HandOnlyDetector:
    def __init__(self, nanotrack_root=None):
        self.gpu = True
        root = Path.home()/'omnifleet_data/ml_models/omnifleet_vision/vendor'
        self.model = HandFullGpu(root/'mediapipe_tensorrt/hand_full_fp32.engine')
        self.model.process(dict(image=np.zeros((224,224,3),np.uint8),
            roi=rect_pb2.NormalizedRect(x_center=.5,y_center=.5,width=1.,height=1.)))
        self.palm = PalmDetector(root/'mediapipe_tensorrt/palm_full_fp32.engine')
        self.hand_tracker = HandNanoTrack(nanotrack_root or str(root/'nanotrack_v2'))
        self.allowed_gestures = {'one','victory','okay','open_palm'}
        self.debug = {}
        self.reset()

    def reset(self):
        self.hand_tracker.reset()
        self.world = None
        self.owner = None
        self.rotation = 0.
        self.model.reset()

    def _infer_roi(self, rgb, owner, cx, cy, size, rotation):
        height, width = rgb.shape[:2]
        if not np.isfinite([cx,cy,size,rotation]).all() or size <= 1:
            return None
        result = self.model.process(dict(image=rgb,roi=rect_pb2.NormalizedRect(
            x_center=cx/width,y_center=cy/height,width=size/width,height=size/height,rotation=rotation)))
        self.debug['attempts'].append(dict(owner=owner,roi=[cx,cy,size],rotation=rotation,
            presence=result.score,found=result.landmarks is not None))
        if result.landmarks is None:
            return None
        points = np.asarray([[p.x*width,p.y*height,p.z*width] for p in result.landmarks.landmark])
        return dict(owner=owner,result=result,points=points)

    def infer(self, image, people):
        height, width = image.shape[:2]
        regions = {}
        for person in people:
            x1,y1,x2,y2 = person['bbox']
            pad = np.clip((y2-y1)*.45,160,320)/2
            regions[person['id']] = (max(0,int(x1-pad)),max(0,int(y1-pad)),
                                     min(width,int(x2+pad)),min(height,int(y2+pad)))
        self.debug = dict(people=len(people),boxes=[p['bbox'] for p in people],attempts=[],
            palm_backend=self.palm.backend,palm_candidates=0,search='NanoTrack',nanotrack=self.hand_tracker.status())
        if not regions:
            self.reset()
            self.debug['nanotrack'] = self.hand_tracker.status()
            return []
        rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        predicted = self.hand_tracker.predict(image,regions)
        found = self._infer_roi(rgb,*predicted,self.rotation) if predicted is not None else None
        if found is None:
            self.debug['search'] = 'Full palm detection'
            candidates = []
            for owner,(left,top,right,bottom) in regions.items():
                if right <= left or bottom <= top:
                    continue
                palms = self.palm.detect(image[top:bottom,left:right])
                self.debug['palm_candidates'] += len(palms)
                for palm in palms:
                    for scale in (1.,2.):
                        candidate = self._infer_roi(rgb,owner,palm['cx']+left,palm['cy']+top,
                                                    palm['size']*scale,palm['rotation'])
                        if candidate is not None:
                            candidates.append(candidate)
                            break
            if not candidates:
                self.world = None
                self.debug['nanotrack'] = self.hand_tracker.status()
                return []
            found = max(candidates,key=lambda c:c['result'].score)
        # Recenter all 21 points before final classification, both during
        # acquisition and tracking, so the landmark crop includes fingertips.
        refined = self._infer_roi(rgb,found['owner'],*complete_hand_roi(found['points']))
        if refined is not None:
            found = refined
        owner,result,points = found['owner'],found['result'],found['points']
        world = canonical_hand([[p.x,p.y,p.z] for p in result.world.landmark])
        if self.owner == owner and self.world is not None:
            world = .5*world+.5*self.world
        gesture = classify_gesture(points,world)
        low,high = points[:,:2].min(0),points[:,:2].max(0)
        cx,cy = (low+high)/2
        size = max(160.,float(max(high-low)*1.6))
        self.rotation = image_rotation(points)
        self.hand_tracker.anchor(image,points,(cx,cy),size,owner)
        self.owner = owner
        self.world = world if gesture in self.allowed_gestures else None
        self.debug.update(selected_presence=result.score,gesture=gesture,nanotrack=self.hand_tracker.status())
        if gesture not in self.allowed_gestures:
            return []
        side = result.side.classification[0]
        return [dict(owner=owner,points=points,gesture=gesture,side=side.label.lower(),score=side.score)]

    def close(self):
        self.hand_tracker.close()
        self.palm.close()
        self.model.close()
