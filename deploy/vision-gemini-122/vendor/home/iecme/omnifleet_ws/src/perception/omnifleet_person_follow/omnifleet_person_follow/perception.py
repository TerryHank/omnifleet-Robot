"""TensorRT person masks/BoT-SORT and CUDA MediaPipe 21-point hands."""
from pathlib import Path
from types import MethodType
import sys
import time
import threading
import warnings
import yaml
from queue import Queue, Empty, Full
import cv2
import numpy as np
from .core import classify_hand, hand_owner
from .cuda_wait import blocking_cuda_wait
from .person_masks import person_masks
from omnifleet_hikrobot_rgbd.foreground_tracking import semantic_foreground


class Perception:
    def __init__(self, engine, tracker, zoo_root, model_root, image_size, confidence, gestures_enabled=True):
        self.cuda_blocking_sync = blocking_cuda_wait()
        self.inference_stream = None
        import torch
        torch.set_num_threads(1)
        self.torch = torch
        from ultralytics import YOLO
        from ultralytics.engine.results import Boxes
        self.boxes_type = Boxes
        self.detector = YOLO(engine, task='segment')
        self.tracker, self.image_size, self.confidence = tracker, image_size, confidence
        tracker_settings = yaml.safe_load(Path(tracker).read_text())
        self.candidate_confidence = float(tracker_settings['track_low_thresh'])
        self.tracker_name = tracker_settings['tracker_type']
        self.camera_warp = np.eye(2, 3)
        self.tracker_ms, self.gmc_ms, self.gmc_flow_ms = 0., 0., 0.
        self.gmc_backend = 'CPU sparseOptFlow'
        self.gestures_enabled = gestures_enabled
        self.timings,self.model_timings = {},{}
        self.hand_backend = 'disabled'
        if not gestures_enabled:
            return
        for name in ('palm_detection_mediapipe','handpose_estimation_mediapipe'):
            sys.path.insert(0,str(Path(zoo_root)/name))
        from mp_palmdet import MPPalmDet
        from mp_handpose import MPHandPose
        backend,target = cv2.dnn.DNN_BACKEND_CUDA,cv2.dnn.DNN_TARGET_CUDA_FP16
        self.palm = MPPalmDet(str(Path(model_root)/'palm_detection_mediapipe_2023feb.onnx'),backendId=backend,targetId=target)
        self.hand = MPHandPose(str(Path(model_root)/'handpose_estimation_mediapipe_2023feb.onnx'),backendId=backend,targetId=target)
        accelerated = 0
        for network,name in [(self.palm,'palm'),(self.hand,'hand')]:
            engine_path = Path(model_root)/'mediapipe_tensorrt'/f'{name}.engine'
            if engine_path.is_file():
                try:
                    from .trt_net import TensorRTNet
                    network.model = TensorRTNet(engine_path,network.model.getUnconnectedOutLayersNames())
                    accelerated += 1
                except Exception as error:
                    warnings.warn(f'TensorRT {name} unavailable, retaining OpenCV CUDA: {error}')
        self.hand_backend = 'TensorRT FP16 hands' if accelerated==2 else 'OpenCV CUDA FP16 hands' if not accelerated else 'TensorRT/OpenCV CUDA hands'
        from .hand_preprocess import hand_preprocess
        self.hand._preprocess=MethodType(hand_preprocess,self.hand)
        self.cached_hands,self.acquisition_index = [],0
        self.timings = {}
        self.model_timings = {}
        self.hand_jobs,self.hand_results = Queue(maxsize=1),Queue(maxsize=1)
        self.hand_stop = threading.Event()
        self.hand_ms,self.hand_age_ms = 0.,None
        self.hand_error = ''
        self.hand_worker = threading.Thread(target=self.hand_run,name='person-follow-hands',daemon=True)
        self.hand_worker.start()

    def people(self, image, foreground=None, locked_id=None):
        self.model_timings = dict(tracker_backend=self.tracker_name,
            detector_candidate_threshold=self.candidate_confidence)
        predictor = self.detector.predictor
        if predictor is None:
            result = self.detector.predict(image, imgsz=self.image_size,
                                         rect=False, device=0, conf=self.candidate_confidence, classes=[0], max_det=20, verbose=False)[0]
            self.cuda_blocking_sync = blocking_cuda_wait()
            self.inference_stream = self.torch.cuda.Stream()
            backend = self.detector.predictor.model.backend
            for name,binding in backend.bindings.items():
                backend.context.set_tensor_address(name,binding.ptr)
            from types import SimpleNamespace
            from ultralytics.trackers.bot_sort import BOTSORT
            tracker = BOTSORT(SimpleNamespace(**yaml.safe_load(Path(self.tracker).read_text())))
            self.detector.predictor.trackers = [tracker]
            if hasattr(tracker, 'gmc'):
                tracker.gmc.downscale = 4
                tracker.gmc.feature_params.update(maxCorners=200, minDistance=4)
                tracker.gmc.reset_params()
                if (getattr(tracker.gmc,'method',None)=='sparseOptFlow' and
                        hasattr(cv2.cuda,'SparsePyrLKOpticalFlow_create') and cv2.cuda.getCudaEnabledDeviceCount()>0):
                    from .cuda_gmc import apply_sparseoptflow
                    tracker.gmc.apply_sparseoptflow=MethodType(apply_sparseoptflow,tracker.gmc)
                    self.gmc_backend = 'CUDA PyrLK; CPU features/RANSAC'
                apply = tracker.gmc.apply
                def record_warp(*args, **kwargs):
                    started = time.perf_counter()
                    self.camera_warp = apply(*args, **kwargs)
                    self.gmc_ms = (time.perf_counter()-started)*1000
                    self.gmc_flow_ms = getattr(tracker.gmc,'cuda_flow_ms',0.)
                    return self.camera_warp
                tracker.gmc.apply = record_warp
            self.model_timings.update({'person_'+name+'_ms': round(float(value),2) for name,value in result.speed.items()})
            if result.masks is None:
                return []
            boxes = result.boxes.data.cpu().numpy()
            masks = result.masks.data.cpu().numpy() > .5
        else:
            # Reuse the configured predictor and CPU tracker result directly.
            # The high-level track() path copies CPU tracks back to CUDA, then
            # callers copy them to CPU again; neither copy is needed here.
            with self.torch.inference_mode(), self.torch.cuda.stream(self.inference_stream):
                started = time.perf_counter()
                tensor = predictor.preprocess([image])
                preprocessed = time.perf_counter()
                backend = predictor.model.backend
                backend.context.set_tensor_address('images',int(tensor.data_ptr()))
                if not backend.context.execute_async_v3(self.inference_stream.cuda_stream):
                    raise RuntimeError('TensorRT asynchronous inference failed')
                prediction = [backend.bindings[name].data for name in sorted(backend.output_names)]
                inferred = time.perf_counter()
                sizes = [value.numel() for value in prediction]
                merged = self.torch.cat([value.reshape(-1) for value in prediction]).cpu().numpy()
                detections = merged[:sizes[0]].reshape(prediction[0].shape)[0]
                prototypes = merged[sizes[0]:].reshape(prediction[1].shape)[0]
                mask_started = time.perf_counter()
                boxes,masks = person_masks(detections,prototypes,
                                          image.shape,self.image_size,self.candidate_confidence)
                mask_decode_ms = (time.perf_counter()-mask_started)*1000
                self.model_timings.update(person_preprocess_ms=round((preprocessed-started)*1000,2),
                    person_inference_ms=round((inferred-preprocessed)*1000,2),
                    mask_decode_ms=round(mask_decode_ms,3),
                    person_postprocess_ms=round((time.perf_counter()-inferred)*1000,2))
        observations=[]
        if foreground is not None:
            chosen=None
            previous=getattr(self,'foreground_tracks',{}).get(locked_id)
            if previous is not None and len(boxes):
                low=np.maximum(boxes[:,:2],previous[:2]);high=np.minimum(boxes[:,2:4],previous[2:])
                intersection=np.maximum(0,high-low).prod(axis=1)
                area=(boxes[:,2:4]-boxes[:,:2]).prod(axis=1)
                overlap=intersection/np.maximum(1,area+np.prod(previous[2:]-previous[:2])-intersection)
                chosen=int(np.argmax(overlap))
            elif len(boxes) and time.monotonic()-getattr(self,'foreground_candidate_at',0.)>=.1:
                chosen=getattr(self,'foreground_candidate_index',0)%len(boxes)
                self.foreground_candidate_at=time.monotonic()
                self.foreground_candidate_index=chosen+1
            for index,(box,mask) in enumerate(zip(boxes,masks)):
                x,y,x2,y2=box[:4]
                result=foreground.query([x,y,x2-x,y2-y],mask,use_depth=index==chosen)
                observations.append(result)
                # Missing depth on a leg must not make the whole-body control
                # box collapse to the torso. Track the existing person semantic
                # foreground; range uses measured connected points inside it.
                outline=semantic_foreground(mask,[x,y,x2-x,y2-y],foreground.rgb_size)
                if outline is not None:
                    x,y,w,h=outline['bbox_xywh'];boxes[index,:4]=[x,y,x+w,y+h]
            self.model_timings.update(foreground_ms=round(foreground.elapsed_ms,3),
                foreground_queries=foreground.calls,foreground_tracking=True,additional_segmentation_models=0)
        tracking_started=time.perf_counter()
        self.camera_warp=np.eye(2,3)
        # Refined foreground observations go into BoT-SORT; GMC keeps raw RGB.
        tracked=self.detector.predictor.trackers[0].update(self.boxes_type(boxes,image.shape[:2]),image)
        self.tracker_ms=(time.perf_counter()-tracking_started)*1000
        self.model_timings.update(tracker_ms=round(self.tracker_ms,3),gmc_ms=round(self.gmc_ms,3),
            optical_flow_ms=round(self.gmc_flow_ms,3),gmc_backend=self.gmc_backend)
        if not len(tracked):return []
        indices=tracked[:,-1].astype(int)
        boxes=tracked[:,:7];masks=masks[indices]
        self.foreground_tracks={int(box[4]):box[:4].copy() for box in boxes}
        if not len(boxes):
            return []
        return [dict(id=int(box[4]), bbox=box[:4].tolist(), confidence=float(box[5]), mask=mask,
                     foreground_result=observations[int(index)] if observations else None)
                for box,mask,index in zip(boxes,masks,indices)]

    def hands(self, image, tracks, locked_id):
        wanted = [t for t in tracks if locked_id is None or t['id'] == locked_id]
        if not wanted:
            self.cached_hands = []
            return []
        hands = []
        # The previous 21 points define the next palm ROI: run the palm
        # detector only when a hand/owner needs acquisition or tracking fails.
        for cached in self.cached_hands:
            track = next((t for t in wanted if t['id'] == cached['owner']), None)
            if track is None:
                continue
            points = cached['points']
            palm_points = points[[0, 5, 9, 13, 17, 1, 2], :2]
            palm = np.r_[palm_points.min(axis=0), palm_points.max(axis=0), palm_points.reshape(-1), 1.]
            hand = self.hand.infer(image, palm)
            if hand is not None:
                self.accept_hand(hand, image, tracks, locked_id, hands)
        missing = {t['id'] for t in wanted} - {hand['owner'] for hand in hands}
        if missing:
            # Search one missing person's crop per frame, rotating between IDs.
            # This keeps small hands larger at the palm model's input without
            # multiplying detector calls by the number of people in the scene.
            candidates = [t for t in wanted if t['id'] in missing]
            track = candidates[self.acquisition_index % len(candidates)]
            self.acquisition_index += 1
            x1, y1, x2, y2 = track['bbox']
            pad_x, pad_y = (x2-x1)*.1, (y2-y1)*.05
            x1, y1 = max(0, int(x1-pad_x)), max(0, int(y1-pad_y))
            x2, y2 = min(image.shape[1], int(x2+pad_x)), min(image.shape[0], int(y2+pad_y))
            crop = image[y1:y2, x1:x2]
            if not crop.size:
                return hands
            ratio = min(1., 640. / max(crop.shape[:2]))
            small = cv2.resize(crop, None, fx=ratio, fy=ratio) if ratio < 1. else crop
            for palm in self.palm.infer(small):
                palm = palm.copy()
                palm[:18] /= ratio
                palm[:4] += [x1, y1, x1, y1]
                palm[4:18] += np.tile([x1, y1], 7)
                owner = hand_owner(palm[4:6], tracks, image.shape)
                if owner != track['id']:
                    continue
                hand = self.hand.infer(image, palm)
                if hand is not None:
                    self.accept_hand(hand, image, tracks, locked_id, hands)
        # At most one command hand per person; preserve the strongest network confidence.
        by_owner = {}
        for hand in hands:
            if hand['owner'] not in by_owner or hand['score'] > by_owner[hand['owner']]['score']:
                by_owner[hand['owner']] = hand
        self.cached_hands = list(by_owner.values())
        return self.cached_hands

    def accept_hand(self, result, image, tracks, locked_id, hands):
        points = np.asarray(result[4:67]).reshape(21, 3)
        owner = hand_owner(points[0, :2], tracks, image.shape)
        if owner is None or (locked_id is not None and owner != locked_id):
            return
        world = np.asarray(result[67:130]).reshape(21, 3)
        hands.append(dict(owner=owner, points=points, gesture=classify_hand(points, world), score=float(result[-1])))

    def infer(self, image, locked_id, foreground=None):
        start = time.perf_counter()
        tracks = self.people(image) if foreground is None else self.people(image,foreground,locked_id)
        detected = time.perf_counter()
        if not self.gestures_enabled:
            self.timings = dict(person_track_ms=round((detected-start)*1000,2),
                hand_ms=0.,hand_async=False,hand_updated=False,
                cuda_blocking_sync=self.cuda_blocking_sync,trt_async=True,**self.model_timings)
            return tracks,[]
        self.put_latest(self.hand_jobs,(image,tracks,locked_id,detected))
        hands,hand_updated = [],False
        try:
            owner,results,submitted,elapsed,error = self.hand_results.get_nowait()
            self.hand_error = error
            if owner == locked_id:
                hands,hand_updated = results,True
                self.hand_ms,self.hand_age_ms = elapsed,(time.perf_counter()-submitted)*1000
        except Empty:
            pass
        self.timings = {'person_track_ms': round((detected - start) * 1000, 2),
                        'hand_preprocess_backend':'CPU cropped warp',
                        'hand_ms': round(self.hand_ms,2),'hand_async':True,
                        'last_hand_preprocess_ms':round(getattr(self.hand,'preprocess_ms',0.),3),
                        'cuda_blocking_sync':self.cuda_blocking_sync,
                        'trt_async':True,
                        'hand_age_ms':self.hand_age_ms,'hand_error':self.hand_error,
                        'hand_updated': hand_updated, **self.model_timings}
        return tracks, hands

    @staticmethod
    def put_latest(queue,item):
        try:
            queue.put_nowait(item)
        except Full:
            try:queue.get_nowait()
            except Empty:pass
            queue.put_nowait(item)

    def hand_run(self):
        blocking_cuda_wait()
        while not self.hand_stop.is_set():
            try:image,tracks,owner,submitted = self.hand_jobs.get(timeout=.2)
            except Empty:continue
            started = time.perf_counter()
            try:
                hands = self.hands(image,tracks,owner)
                self.hand_error = ''
            except Exception as error:
                hands,self.hand_error = [],str(error)
            self.put_latest(self.hand_results,(owner,hands,submitted,(time.perf_counter()-started)*1000,self.hand_error))

    def close(self):
        if not self.gestures_enabled:
            return
        self.hand_stop.set()
        self.hand_worker.join(timeout=3.)
        for network in (self.palm,self.hand):
            if hasattr(network.model,'close'):
                network.model.close()
