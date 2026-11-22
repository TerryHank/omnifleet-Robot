"""OpenCV Zoo BlazePose video tracking with GPU detection and landmarks."""
from pathlib import Path
from types import MethodType, SimpleNamespace
import sys
import time
import numpy as np
import yaml
from .pose_actions import classify_pose, hip_region, visible
from .pose_preprocess import preprocess_pose
from .pose_smoothing import PoseSmoothing
from .trt_net import TensorRTNet


class PosePipeline:
    def __init__(self, zoo_root, model_root, tracker_config):
        for name in ['person_detection_mediapipe','pose_estimation_mediapipe']:
            sys.path.insert(0,str(Path(zoo_root)/name))
        from mp_persondet import MPPersonDet
        from mp_pose import MPPose
        from ultralytics.trackers.bot_sort import BOTSORT
        from ultralytics.engine.results import Boxes
        root=Path(model_root)
        self.person = MPPersonDet(str(root/'person_detection_mediapipe_2023mar.onnx'))
        self.pose = MPPose(str(root/'pose_estimation_mediapipe_2023mar.onnx'))
        self.pose._preprocess=MethodType(preprocess_pose,self.pose)
        for model,name in [(self.person,'person_body_fp32'),(self.pose,'pose_body_fp32')]:
            model.model = TensorRTNet(root/'mediapipe_tensorrt'/(name+'.engine'),
                                     model.model.getUnconnectedOutLayersNames())
        settings=yaml.safe_load(Path(tracker_config).read_text())
        settings['track_high_thresh']=settings['track_low_thresh']
        settings['new_track_thresh']=settings['track_low_thresh']
        self.tracker=BOTSORT(SimpleNamespace(**settings))
        # Retain the existing robot's bounded optical-flow workload.
        self.tracker.gmc.downscale=4
        self.tracker.gmc.feature_params.update(maxCorners=200,minDistance=4)
        self.tracker.gmc.reset_params()
        self.boxes_type=Boxes
        self.previous_rois=[]
        self.previous_shape=None
        self.detector_ran=False
        self.landmark_filters={}

    def infer(self, image, timestamp=None):
        height,width=image.shape[:2]
        timestamp = time.monotonic() if timestamp is None else timestamp
        if self.previous_shape != image.shape[:2]:
            self.landmark_filters.clear()
        observations=[];boxes=[]
        next_rois=[]
        for person,result,roi_filter in self.track_poses(image):
            points=result[1][:33].copy()
            visible=points[(points[:,3]>=.5)&(points[:,4]>=.5),:2]
            if not len(visible):
                continue
            low=np.maximum(visible.min(0)-12,0)
            high=np.minimum(visible.max(0)+12,[width,height])
            if np.any(high<=low):
                continue
            score=float(min(person[-1],result[-1]))
            observations.append(dict(pose=points,mask=result[3]>0,foreground_result=None))
            boxes.append([*low,*high,score,0.])
            next_roi=self.landmark_roi(result[1],width,height)
            if next_roi is not None:
                radius=np.linalg.norm(person[4:6]-person[6:8])
                next_roi[4:8]=roi_filter.update(next_roi[4:8].reshape(2,2),timestamp,radius).ravel()
                next_rois.append((self.stable_roi(person,next_roi),roi_filter))
        self.previous_rois=next_rois
        self.previous_shape=image.shape[:2]
        boxes=np.asarray(boxes,dtype=np.float32).reshape(-1,6)
        tracked=self.tracker.update(self.boxes_type(boxes,image.shape[:2]),image)
        tracks=[];actions=[]
        filters={}
        for box in tracked:
            track=dict(observations[int(box[-1])],id=int(box[4]),
                       bbox=box[:4].tolist(),confidence=float(box[5]))
            points=track['pose']
            # Keep control on the current frame. The display and RGB-D
            # anchor use the smoothed coordinates without delaying actions.
            action=classify_pose(points)
            scale=np.linalg.norm(points[11,:2]-points[12,:2])
            pose_filter=self.landmark_filters.get(track['id']) or PoseSmoothing(1.,3.)
            filters[track['id']]=pose_filter
            points[:,:3]=pose_filter.update(points[:,:3],timestamp,scale,(points[:,3:5]>=.5).all(axis=1))
            track['hip_center'],track['hip_roi']=hip_region(points,image.shape)
            track['pose_action']=action;tracks.append(track)
            actions.append(dict(owner=track['id'],points=points[[11,12,13,14,15,16],:3],
                                gesture=action,score=track['confidence'],pose_action=True))
        self.landmark_filters=filters
        return tracks,actions

    @staticmethod
    def landmark_roi(landmarks, width, height):
        # BlazePose auxiliary landmarks 33 and 34 supply the center and scale/
        # rotation point. MediaPipe video mode expands the square by 1.25.
        center,scale=landmarks[33:35,:2]
        vector=1.25*(scale-center)
        radius=np.linalg.norm(vector)
        if not np.isfinite(radius) or radius < 2 or radius > max(width,height):
            return None
        low,high=center-radius,center+radius
        if np.any(high<=0) or np.any(low>=[width,height]):
            return None
        # Build the same 13-value input that MPPose accepts from MPPersonDet.
        point=center+vector
        return np.array([*low,*high,*center,*point,*center,*point,1.],dtype=np.float32)

    @staticmethod
    def stable_roi(current, proposed):
        # Repeatedly fitting small changes in the auxiliary points can make
        # keypoints drift even on an identical image. Keep the ROI until the
        # center or scale changes enough to need a different crop.
        radius=np.linalg.norm(current[4:6]-current[6:8])
        new_radius=np.linalg.norm(proposed[4:6]-proposed[6:8])
        offset=np.linalg.norm(current[4:6]-proposed[4:6])
        if offset <= .2*radius and .75*radius <= new_radius <= 1.3*radius:
            kept=current.copy()
            kept[-1]=1.
            return kept
        return proposed

    @staticmethod
    def valid_pose(result):
        if result is None:
            return False
        points=result[1]
        if not visible(points, [11,12,23,24]):
            return True
        # Floor objects in this view can yield high confidence with a nearly
        # horizontal or inverted torso. Check the torso's projected direction.
        torso=points[[23,24],:2].mean(0)-points[[11,12],:2].mean(0)
        return torso[1] >= .30*np.linalg.norm(torso)

    def track_poses(self, image):
        previous=self.previous_rois if self.previous_shape==image.shape[:2] else []
        poses=[]
        for roi,roi_filter in previous:
            result=self.pose.infer(image,roi.copy())
            if self.valid_pose(result) and self.landmark_roi(result[1],image.shape[1],image.shape[0]) is not None:
                poses.append((roi,result,roi_filter))
        self.detector_ran=not previous or len(poses) != len(previous)
        if not self.detector_ran:
            return poses

        # When one pose is lost, keep successful tracks and add only detections
        # whose auxiliary center differs from the already tracked people.
        for person,result in self.detect_poses(image):
            center,scale=result[1][33:35,:2]
            radius=np.linalg.norm(scale-center)
            if any(np.linalg.norm(center-existing[1][33,:2]) < .25*radius for existing in poses):
                continue
            poses.append((person,result,PoseSmoothing(.6,1.8)))
        return poses

    def detect_poses(self, image):
        height,width=image.shape[:2]
        self.person.score_threshold=.5
        poses=[]
        for person in self.person.infer(image):
            result=self.pose.infer(image,person.copy())
            if self.valid_pose(result):
                poses.append((person,result))
        if poses or width < 1.5*height:
            return poses

        # Wide-angle images shrink distant people when resized to 224x224.
        # Search overlapping fixed windows, then run pose on the original frame.
        self.person.score_threshold=.4
        for x0,y0 in ((width//4,height//4),(width//4,0),(0,0),(width//2,0)):
            for person in self.person.infer(image[y0:,x0:x0+width//2]):
                person[:12]+=np.tile([x0,y0],6)
                result=self.pose.infer(image,person.copy())
                if self.valid_pose(result):
                    poses.append((person,result))
            if poses:
                break
        return poses

    def close(self):
        self.person.model.close()
        self.pose.model.close()
