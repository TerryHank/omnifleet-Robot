"""FP32 execution of the same MediaPipe Full landmark model and projection."""
# ROI transform adapted from MediaPipe ImageToTensorOpenCvConverter, v0.10.18.
# Copyright 2020 The MediaPipe Authors. SPDX-License-Identifier: Apache-2.0
# https://www.apache.org/licenses/LICENSE-2.0
from pathlib import Path
from types import SimpleNamespace
import cv2
import numpy as np
from mediapipe.framework.formats import landmark_pb2, classification_pb2
from .trt_net import TensorRTNet


class HandFullGpu:
    def __init__(self, engine):
        self.net = TensorRTNet(engine, ('Identity', 'Identity_1', 'Identity_2', 'Identity_3'))

    def reset(self):
        pass

    def process(self, inputs):
        result = self._process(inputs)
        if result.landmarks is None:
            return result
        results = [result]
        for angle in (-np.deg2rad(20), np.deg2rad(20)):
            roi = type(inputs['roi'])()
            roi.CopyFrom(inputs['roi'])
            roi.rotation += angle
            extra = self._process(dict(image=inputs['image'], roi=roi))
            if extra.landmarks is not None:
                results.append(extra)
        for field in ('landmarks', 'world'):
            values = np.mean([[[p.x,p.y,p.z] for p in getattr(r,field).landmark]
                              for r in results], axis=0)
            for point,value in zip(getattr(result,field).landmark,values):
                point.x,point.y,point.z = map(float,value)
        return result

    def _process(self, inputs):
        image, roi = inputs['image'], inputs['roi']
        height, width = image.shape[:2]
        cx, cy = roi.x_center*width, roi.y_center*height
        rw, rh = roi.width*width, roi.height*height
        angle = float(roi.rotation)
        cosine, sine = np.cos(angle), np.sin(angle)
        corners = cv2.boxPoints(((cx,cy),(rw,rh),angle*180/np.pi))
        target = np.array([[0,224],[0,0],[224,0],[224,224]],np.float32)
        warp = cv2.getPerspectiveTransform(corners,target)
        crop = cv2.warpPerspective(image,warp,(224,224),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
        tensor = np.ascontiguousarray(crop.transpose(2,0,1)[None],dtype=np.float32)/255.
        self.net.setInput(tensor)
        points, presence, side, world = self.net.forward(self.net.output_names)
        out = SimpleNamespace(landmarks=None,world=None,side=None,score=float(presence.item()))
        if out.score < .5:
            return out
        values=points.reshape(21,3)
        x=(values[:,0]/224.-.5)*rw
        y=(values[:,1]/224.-.5)*rh
        values[:,0]=(cosine*x-sine*y+cx)/width
        values[:,1]=(sine*x+cosine*y+cy)/height
        values[:,2]=values[:,2]/(224.*.4)*roi.width
        out.landmarks=landmark_pb2.NormalizedLandmarkList(landmark=[
            landmark_pb2.NormalizedLandmark(x=float(p[0]),y=float(p[1]),z=float(p[2])) for p in values])
        metric=world.reshape(21,3).copy()
        x,y=metric[:,0].copy(),metric[:,1].copy()
        metric[:,0]=cosine*x-sine*y
        metric[:,1]=sine*x+cosine*y
        out.world=landmark_pb2.LandmarkList(landmark=[
            landmark_pb2.Landmark(x=float(p[0]),y=float(p[1]),z=float(p[2])) for p in metric])
        probability=float(side.item())
        out.side=classification_pb2.ClassificationList(classification=[classification_pb2.Classification(
            index=int(probability<.5),score=max(probability,1-probability),label='Right' if probability<.5 else 'Left')])
        return out

    def close(self):
        self.net.close()
