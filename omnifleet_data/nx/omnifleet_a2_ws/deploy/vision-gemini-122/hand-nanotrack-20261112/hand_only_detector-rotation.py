"""Find complete hands inside expanded person rectangles on rectified RGB."""
from pathlib import Path
import sys
import cv2
import numpy as np
sys.path.insert(0, str(Path.home() / 'omnifleet_ws/.env/hand-runtime'))
from google.protobuf import text_format
from mediapipe.python.solution_base import SolutionBase
from mediapipe.framework import calculator_pb2
from mediapipe.framework.formats import rect_pb2
from .core import classify_gesture
from .hand_nanotrack import HandNanoTrack
from .hand_geometry import canonical_hand,image_rotation

class HandOnlyDetector:
    def __init__(self, nanotrack_root=None):
        engine = Path.home() / 'omnifleet_data/ml_models/omnifleet_vision/vendor/mediapipe_tensorrt/hand_full_fp32.engine'
        self.gpu = engine.is_file()
        self.debug = {}
        self.hand_tracker = HandNanoTrack(nanotrack_root or str(engine.parent.parent/'nanotrack_v2'))
        config = text_format.Parse('''
            input_stream: "image"
            input_stream: "roi"
            node { calculator: "HandLandmarkCpu"
              input_stream: "IMAGE:image"
              input_stream: "ROI:roi"
              output_stream: "LANDMARKS:landmarks"
              output_stream: "WORLD_LANDMARKS:world"
              output_stream: "HANDEDNESS:side"
            }
            output_stream: "landmarks"
            output_stream: "world"
            output_stream: "side"
        ''', calculator_pb2.CalculatorGraphConfig())
        if self.gpu:
            from .hand_full_gpu import HandFullGpu
            self.model = HandFullGpu(engine)
            self.model.process({'image': np.zeros((224,224,3), np.uint8),
                'roi': rect_pb2.NormalizedRect(x_center=.5,y_center=.5,width=1.,height=1.)})
        else:
            self.model = SolutionBase(graph_config=config, outputs=['landmarks', 'world', 'side'])
        self.center = None
        self.previous = None
        self.world = None
        self.index = 0
        self.owner = None
        self.size = 240.
        self.rotation = 0.
        self.allowed_gestures = {'one','victory','okay','open_palm'}
        self.search_steps = 4 if self.gpu else 1

    def reset(self):
        self.hand_tracker.reset()
        self.rotation = 0.
        self.center = None
        self.world = None
        self.owner = None
        self.model.reset()

    def infer(self, image, people):
        height, width = image.shape[:2]
        if self.owner is not None and self.owner not in {p['id'] for p in people}:
            self.rotation = 0.
        regions, search, candidates = {}, [], []
        for person in people:
            x1, y1, x2, y2 = person['bbox']
            w, h = x2-x1, y2-y1
            size = float(np.clip(h*.45, 160, 320))
            pad = size/2
            regions[person['id']] = (max(0, x1-pad), max(0, y1-pad),
                                    min(width, x2+pad), min(height, y2+pad))
            if self.center is not None and self.owner == person['id']:
                candidates.append((person['id'], *self.center, self.size))
            for fy in (.15, .35, .55, .8):
                for fx in (.8, .2, .5):
                    search.append((person['id'], x1+w*fx, y1+h*fy, size))
        if not regions:
            self.hand_tracker.reset()
            self.debug = dict(people=0,boxes=[],attempts=[],nanotrack=self.hand_tracker.status())
            self.center = None
            self.world = None
            return []
        # Candidate centers guide rectangle search; model input retains every pixel.
        thumbnail = cv2.resize(image, (width//4, height//4))
        colors = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2YCrCb)
        hint = cv2.inRange(colors, np.array([0,132,75]), np.array([255,180,135]))
        hint = cv2.morphologyEx(hint, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8))
        contours = cv2.findContours(hint, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        hints = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w*h < 12:
                continue
            cx, cy = (x+w/2)*4, (y+h/2)*4
            for owner, (left, top, right, bottom) in regions.items():
                if left <= cx <= right and top <= cy <= bottom:
                    hints.append((owner, cx, cy, float(np.clip(max(w,h)*6.4,240,480))))
                    break
        chosen = []
        for item in sorted(hints, key=lambda item:item[2]):
            if not any(np.hypot(item[1]-a[1],item[2]-a[2]) < 60 for a in chosen):
                chosen.append(item)
            if len(chosen) == 3:
                break
        predicted = self.hand_tracker.predict(image, regions)
        if predicted is not None:
            candidates = [predicted]
        if not candidates:
            if self.search_steps > 1:
                candidates = chosen[:self.search_steps]
                remaining = self.search_steps-len(candidates)
                candidates += [search[(self.index+i) % len(search)] for i in range(remaining)]
                self.index += remaining
            else:
                windows = chosen + search
                candidates = [windows[self.index % len(windows)]]
                self.index += 1
        else:
            # A missed landmark result can search the remaining windows now,
            # while NanoTrack preserves position for the next frame.
            remaining = self.search_steps-1
            extra = chosen[:max(0,remaining-1)]
            extra += [search[self.index % len(search)]] if remaining else []
            self.index += 1
            candidates = candidates[:1]+extra
        self.debug = dict(people=len(people), boxes=[t['bbox'] for t in people], attempts=[], nanotrack=self.hand_tracker.status())
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        for owner, cx, cy, size in candidates:
            left, top, right, bottom = regions[owner]
            size = min(size, right-left, bottom-top)
            cx = float(np.clip(cx, left+size/2, right-size/2))
            cy = float(np.clip(cy, top+size/2, bottom-size/2))
            result = self.model.process({'image': rgb, 'roi': rect_pb2.NormalizedRect(
                x_center=cx/width, y_center=cy/height, width=size/width,
                height=size/height, rotation=self.rotation if self.gpu else 0.)})
            attempt = dict(roi=[cx,cy,size], presence=getattr(result, 'score',None), found=result.landmarks is not None)
            self.debug['attempts'].append(attempt)
            if result.landmarks is None:
                continue
            points = np.asarray([[p.x*width, p.y*height, p.z*width] for p in result.landmarks.landmark])
            world = np.asarray([[p.x, p.y, p.z] for p in result.world.landmark])
            world = canonical_hand(world)
            if self.owner == owner and self.world is not None:
                world = .5*world + .5*self.world
            gesture = classify_gesture(points, world)
            attempt['gesture'] = gesture
            low, high = points[:,:2].min(0), points[:,:2].max(0)
            if gesture in self.allowed_gestures:
                self.center = tuple((low+high)/2)
                self.size = max(160., float(max(high-low)*1.6))
                self.owner, self.world = owner, world
                self.rotation = image_rotation(points)
                self.hand_tracker.anchor(image,points,self.center,self.size,owner)
                self.debug['nanotrack'] = self.hand_tracker.status()
                side = result.side.classification[0]
                return [dict(owner=owner, points=points, gesture=gesture,
                    side=side.label.lower(), score=side.score)]
        self.center = None
        self.world = None
        return []

    def close(self):
        self.hand_tracker.close()
        self.model.close()
