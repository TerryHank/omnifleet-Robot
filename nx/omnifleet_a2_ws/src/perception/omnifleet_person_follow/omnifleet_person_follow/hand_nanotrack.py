"""Track palm appearance; landmark inference alone supplies gesture commands."""
import cv2
import numpy as np
from .nanotrack_tracker import NanoTracker


class HandNanoTrack:
    def __init__(self, model_root):
        cuda = cv2.dnn.DNN_TARGET_CUDA in cv2.dnn.getAvailableTargets(cv2.dnn.DNN_BACKEND_CUDA)
        backend = cv2.dnn.DNN_BACKEND_CUDA if cuda else cv2.dnn.DNN_BACKEND_OPENCV
        target = cv2.dnn.DNN_TARGET_CUDA if cuda else cv2.dnn.DNN_TARGET_CPU
        self.tracker = NanoTracker(model_root, backend, target, verify_template=False)
        self.backend = 'NanoTrack CUDA FP32' if cuda else 'NanoTrack CPU'
        image = np.full((192,192,3),127,np.uint8)
        self.tracker.init(image,(64,64,64,64))
        self.tracker.update(image)
        self.reset()

    def reset(self):
        self.active = False
        self.owner = None
        self.box = None
        self.score = None
        self.unconfirmed = False
        self.refresh_on_anchor = False

    def anchor(self, image, points, center, size, owner):
        # The palm changes less than the finger silhouette when 1/2/palm changes.
        palm = points[[0,1,2,5,9,13,17],:2]
        low, high = palm.min(0), palm.max(0)
        padding = (high-low)*.15
        low = np.maximum(low-padding,0.)
        high = np.minimum(high+padding,np.array(image.shape[1::-1])-1.)
        extent = high-low
        if not np.isfinite(extent).all() or min(extent)<2:
            self.reset()
            return
        box=tuple([*low,*extent])
        if not self.active or self.owner != owner or self.refresh_on_anchor:
            self.tracker.init(image,box)
        else:
            # Correct geometry without rebuilding a validated palm template.
            self.tracker.center=(low+high).astype(np.float32)/2
            self.tracker.size=extent.astype(np.float32)
            self.tracker.last_box=tuple(map(int,box))
        self.offset = (np.asarray(center)-(low+high)/2)/extent
        self.roi_scale = float(size/np.sqrt(extent.prod()))
        self.owner, self.active = owner, True
        self.box = [*low.tolist(),*extent.tolist()]
        self.unconfirmed = False
        self.refresh_on_anchor = False

    def predict(self, image, regions):
        if not self.active:
            return None
        if self.owner not in regions:
            self.reset()
            return None
        self.refresh_on_anchor = self.refresh_on_anchor or self.unconfirmed
        self.unconfirmed = True
        ok, box = self.tracker.update(image)
        values = np.asarray(box,dtype=float)
        if not ok or not np.isfinite(values).all() or min(values[2:])<=0:
            self.reset()
            return None
        self.box = values.tolist()
        self.score = float(self.tracker.getTrackingScore())
        x,y,w,h = values
        center = np.array([x+w/2,y+h/2])+self.offset*np.array([w,h])
        size = max(160.,self.roi_scale*np.sqrt(w*h))
        return self.owner,float(center[0]),float(center[1]),float(size)

    def status(self):
        return dict(active=self.active,owner=self.owner,bbox=self.box,
                    score=self.score,backend=self.backend)

    def close(self):
        self.tracker = None
        self.reset()
