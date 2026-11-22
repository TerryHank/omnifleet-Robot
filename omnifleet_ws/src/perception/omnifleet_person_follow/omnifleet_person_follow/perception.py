"""TensorRT person masks/BoT-SORT and CUDA MediaPipe 21-point hands."""
from pathlib import Path
from types import MethodType
import sys
import time
import threading
import warnings
import yaml
from .hand_only_detector import HandOnlyDetector
from queue import Queue, Empty, Full
import cv2
import numpy as np
from .core import HAND_LOCK_SECONDS, choose_person_hand, classify_gesture, classify_hand, hand_distance, hand_owner
from .cuda_wait import blocking_cuda_wait
from .person_masks import person_masks
from omnifleet_hikrobot_rgbd.foreground_tracking import semantic_foreground


class Perception:
    def __init__(self, engine, tracker, zoo_root, model_root, image_size, confidence,
                 gestures_enabled=True, hand_overlay=None):
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
        self.hand_overlay = hand_overlay
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
        self.hand_locks = {}
        self.next_palm_search = 0.
        self.timings = {}
        self.model_timings = {}
        self.hand_jobs,self.hand_results = Queue(maxsize=1),Queue(maxsize=1)
        self.hand_stop = threading.Event()
        self.hand_ms,self.hand_age_ms = 0.,None
        self.hand_error = ''
        self.hand_only_detector = HandOnlyDetector(str(Path(model_root)/'nanotrack_v2'))
        self.hand_worker = threading.Thread(target=self.hand_run,name='person-follow-hands',daemon=True)
        self.hand_worker.start()

    def people(self, image, foreground=None, locked_id=None, boxes_only=False):
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
            settings = yaml.safe_load(Path(self.tracker).read_text())
            # Associate the existing person candidates instead of discarding them
            # before their hand can provide an explicit OK/digit observation.
            settings['track_high_thresh'] = self.candidate_confidence
            settings['new_track_thresh'] = self.candidate_confidence
            tracker = BOTSORT(SimpleNamespace(**settings))
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
        if boxes_only:
            return [dict(id=index+1, bbox=box[:4].tolist(), confidence=float(box[4]))
                    for index, box in enumerate(boxes)]
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
            self.hand_locks.clear()
            return []
        hands = []
        # The previous 21 points define the next palm ROI: run the palm
        # detector only when a hand/owner needs acquisition or tracking fails.
        for cached in self.cached_hands:
            track = next((t for t in wanted if t['id'] == cached['owner']), None)
            if track is None:
                continue
            hand = self.infer_hand(image, self.palm_from_points(cached['points']))
            if hand is not None:
                self.accept_hand(hand, image, tracks, locked_id, hands)
        commands = {'one', 'victory', 'okay', 'open_palm'}
        now = time.perf_counter()
        missing = {t['id'] for t in wanted}
        for hand in hands:
            lock = self.hand_locks.get(hand['owner'])
            if lock is not None and lock.command and now - lock.seen <= HAND_LOCK_SECONDS:
                acquired = hand_distance(hand, lock) is not None
            else:
                acquired = hand['gesture'] in commands
            if acquired:
                missing.discard(hand['owner'])
        if missing and now >= self.next_palm_search:
            self.next_palm_search = now + .17
            # Search one missing person's crop per frame, rotating between IDs.
            # This keeps small hands larger at the palm model's input without
            # multiplying detector calls by the number of people in the scene.
            candidates = [t for t in wanted if t['id'] in missing]
            track = candidates[self.acquisition_index % len(candidates)]
            sweep = self.acquisition_index // len(candidates)
            self.acquisition_index += 1
            lock = self.hand_locks.get(track['id'])
            locked_hand = lock if lock and lock.command and now - lock.seen <= HAND_LOCK_SECONDS else None
            for region, tight in ((sweep % 3, False), (sweep % 2, True)):
                start = len(hands)
                self.acquire_hands(image, tracks, track, locked_id, region, tight, hands)
                if any(hand['gesture'] in commands and
                       (locked_hand is None or hand_distance(hand, locked_hand) is not None)
                       for hand in hands[start:]):
                    break
        selected, locks = [], {}
        for track in wanted:
            owner = track['id']
            candidates = [hand for hand in hands if hand['owner'] == owner]
            hand, lock = choose_person_hand(candidates, self.hand_locks.get(owner), now, commands)
            if lock is not None:
                locks[owner] = lock
            if hand is not None:
                selected.append(hand)
        self.hand_locks = locks
        self.cached_hands = selected
        return self.cached_hands

    def standalone_hands(self, image, tracks):
        return self.hand_only_detector.infer(image, tracks)

    @staticmethod
    def palm_from_points(points):
        palm = points[[0, 5, 9, 13, 17, 1, 2], :2]
        return np.r_[palm.min(axis=0), palm.max(axis=0), palm.reshape(-1), 1.]

    def acquire_hands(self, image, tracks, track, locked_id, region, tight, hands):
        x1, y1, x2, y2 = track['bbox']
        width, height = x2-x1, y2-y1
        pad_x, pad_y = width*.18, height*.05
        if region < 2:
            y2 = y1 + height*(.46 if tight else .58)
            if region == 0:
                x2 = x1 + width*.66
            else:
                x1 = x2 - width*.66
        x1, y1 = max(0, int(x1-pad_x)), max(0, int(y1-pad_y))
        x2, y2 = min(image.shape[1], int(x2+pad_x)), min(image.shape[0], int(y2+pad_y))
        crop = image[y1:y2, x1:x2]
        if not crop.size:
            return
        ratio = 2. if max(crop.shape[:2]) < 160 else 1.
        if ratio > 1.:
            crop = cv2.resize(crop, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_CUBIC)
        for palm in self.palm.infer(crop)[:2]:
            palm = palm.copy()
            palm[:18] /= ratio
            palm[:4] += [x1, y1, x1, y1]
            palm[4:18] += np.tile([x1, y1], 7)
            if hand_owner(palm[4:6], tracks, image.shape) != track['id']:
                continue
            hand = self.infer_hand(image, palm)
            if hand is None:
                continue
            # A palm proposal can initially clip the extended fingertips.
            # Recenter on the recovered wrist/knuckles in the same source frame.
            for _ in range(2):
                points = hand[4:67].reshape(21, 3)
                refined = self.infer_hand(image, self.palm_from_points(points))
                if refined is None or np.linalg.norm(refined[4:6] - points[0, :2]) > max(
                        16., np.linalg.norm(points[5, :2] - points[17, :2]) * .75):
                    break
                hand = refined
            self.accept_hand(hand, image, tracks, locked_id, hands)

    def infer_hand(self, image, palm):
        box = palm[:4].reshape(2, 2)
        size = float(max(box[1] - box[0]))
        if not 0. < size <= 46.:
            return self.hand.infer(image, palm)
        # The landmark model rotates and rounds the ROI before resizing.
        # Upscale only the tiny palm patch to keep those rounding errors small.
        center = box.mean(axis=0)
        margin = int(np.ceil(size * 2.5))
        x1, y1 = np.maximum(np.floor(center).astype(int) - margin, 0)
        x2, y2 = np.minimum(np.ceil(center).astype(int) + margin, image.shape[1::-1])
        patch = image[y1:y2, x1:x2]
        if not patch.size:
            return None
        enlarged = cv2.resize(patch, None, fx=2., fy=2., interpolation=cv2.INTER_CUBIC)
        offset = np.array([x1, y1])
        local = palm.copy()
        local[:18] = (local[:18] - np.tile(offset, 9)) * 2.
        result = self.hand.infer(enlarged, local)
        if result is not None:
            result[:4] = result[:4] * .5 + np.tile(offset, 2)
            points = result[4:67].reshape(21, 3)
            points *= .5
            points[:, :2] += offset
        return result

    def accept_hand(self, result, image, tracks, locked_id, hands, standalone=False):
        points = np.asarray(result[4:67]).reshape(21, 3)
        owner = 1 if standalone else hand_owner(points[0, :2], tracks, image.shape)
        if owner is None or (locked_id is not None and owner != locked_id):
            return
        world = np.asarray(result[67:130]).reshape(21, 3)
        gesture = classify_gesture(points, world)
        if gesture == 'unknown' and max(np.ptp(points[:, :2], axis=0)) <= 45.:
            # At long range the inferred depth of the fingers is noisy. A
            # clearly open palm in the image can still end the current follow.
            if classify_hand(points) == 'open_palm':
                gesture = 'open_palm'
        handedness = float(result[130])
        side = 'left' if handedness <= .2 else 'right' if handedness >= .8 else None
        hands.append(dict(owner=owner, points=points, gesture=gesture, side=side, score=float(result[-1])))

    def infer(self, image, locked_id, foreground=None, hand_only=False):
        start = time.perf_counter()
        tracks = self.people(image) if hand_only or foreground is None else self.people(image,foreground,locked_id)
        detected = time.perf_counter()
        if not self.gestures_enabled:
            self.timings = dict(person_track_ms=round((detected-start)*1000,2),
                hand_ms=0.,hand_async=False,hand_updated=False,
                cuda_blocking_sync=self.cuda_blocking_sync,trt_async=True,**self.model_timings)
            return tracks,[]
        self.hand_only_detector.allowed_gestures = ({'okay','open_palm'}
            if getattr(self, 'follow_active', False) else {'one','victory','okay','open_palm'})
        hand_owner_key = 'hand_only' if hand_only else locked_id
        hand_tracks = [dict(id=t['id'], bbox=t['bbox']) for t in tracks] if hand_only else tracks
        self.put_latest(self.hand_jobs,(image,hand_tracks,hand_owner_key,detected))
        hands,hand_updated = [],False
        try:
            owner,results,submitted,elapsed,error = self.hand_results.get_nowait()
            self.hand_error = error
            if owner == hand_owner_key:
                hands,hand_updated = results,True
                self.hand_ms,self.hand_age_ms = elapsed,(time.perf_counter()-submitted)*1000
        except Empty:
            pass
        self.timings = {'person_track_ms': round((detected - start) * 1000, 2),
                        'hand_preprocess_backend': 'MediaPipe-compatible ROI warp' if hand_only else 'CPU cropped warp',
                        'hand_model_backend': ('TensorRT FP32 Full' if self.hand_only_detector.gpu else 'MediaPipe Full CPU') if hand_only else self.hand_backend,
                        'hand_search_debug': self.hand_only_detector.debug if hand_only else {},
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

    @staticmethod
    def rectify_hand_region(image, maps, tracks):
        height, width = image.shape[:2]
        boxes = np.asarray([track['bbox'] for track in tracks])
        low = boxes[:, :2].min(axis=0)
        high = boxes[:, 2:].max(axis=0)
        pad = np.maximum((high-low)*.24, 64)
        x1, y1 = np.maximum(np.floor(low-pad), 0).astype(int)
        x2, y2 = np.minimum(np.ceil(high+pad), (width, height)).astype(int)
        region = np.s_[y1:y2, x1:x2]
        rectified = np.zeros_like(image)
        rectified[region] = cv2.remap(image, maps[0][region], maps[1][region],
                                      interpolation=cv2.INTER_LINEAR)
        return rectified

    def hand_run(self):
        blocking_cuda_wait()
        if self.hand_overlay is not None:
            from omnifleet_hikrobot_rgbd.local_frames import native_color_geometry, read_native_mjpeg
        previous_job = None
        last_hand_only = None
        last_native_stamp = None
        next_extra = 0.
        while not self.hand_stop.is_set():
            paired = True
            try:
                image, tracks, owner, submitted = self.hand_jobs.get(
                    timeout=.02 if previous_job is not None else .2)
                previous_job = (tracks, owner, submitted) if tracks and owner != 'hand_only' and self.hand_overlay is not None else None
                next_extra = time.perf_counter() + .065
            except Empty:
                if previous_job is None:
                    continue
                tracks, owner, submitted = previous_job
                now = time.perf_counter()
                if now - submitted > .28:
                    previous_job = None
                    continue
                if now < next_extra:
                    continue
                next_extra = now + .085
                try:
                    packet = read_native_mjpeg()
                    if packet is None or packet[0] == last_native_stamp:
                        continue
                    last_native_stamp, jpeg = packet
                    image = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
                    if image is None:
                        continue
                    size = image.shape[1], image.shape[0]
                    _, maps = native_color_geometry(size, size)
                    image = self.rectify_hand_region(image, maps, tracks)
                except (OSError, ValueError, cv2.error) as error:
                    self.hand_error = str(error)
                    continue
                paired = False
            started = time.perf_counter()
            try:
                hand_only = owner == 'hand_only'
                if hand_only != last_hand_only:
                    self.cached_hands.clear()
                    self.hand_locks.clear()
                    self.next_palm_search = 0.
                    self.hand_only_detector.reset()
                    last_hand_only = hand_only
                hands = self.standalone_hands(image, tracks) if hand_only else self.hands(image,tracks,owner)
                if hand_only and getattr(self, 'follow_active', False):
                    hands = [hand for hand in hands if hand['gesture'] in ('okay', 'open_palm')]
                self.hand_error = ''
            except Exception as error:
                hands,self.hand_error = [],str(error)
            if paired:
                self.put_latest(self.hand_results,(owner,hands,submitted,(time.perf_counter()-started)*1000,self.hand_error))
            if self.hand_overlay is not None:
                self.hand_overlay(hands, image.shape)

    def close(self):
        if not self.gestures_enabled:
            return
        self.hand_stop.set()
        self.hand_worker.join(timeout=3.)
        if not self.hand_worker.is_alive():
            self.hand_only_detector.close()
        for network in (self.palm,self.hand):
            if hasattr(network.model,'close'):
                network.model.close()
