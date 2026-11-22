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
        image, roi = inputs['image'], inputs['roi']
        height, width = image.shape[:2]
        cx, cy = roi.x_center*width, roi.y_center*height
        rw, rh = roi.width*width, roi.height*height
        corners = cv2.boxPoints(((cx,cy),(rw,rh),0.))
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
        values[:,0]=(values[:,0]/224.-.5)*roi.width+roi.x_center
        values[:,1]=(values[:,1]/224.-.5)*roi.height+roi.y_center
        values[:,2]=values[:,2]/(224.*.4)*roi.width
        out.landmarks=landmark_pb2.NormalizedLandmarkList(landmark=[
            landmark_pb2.NormalizedLandmark(x=float(p[0]),y=float(p[1]),z=float(p[2])) for p in values])
        out.world=landmark_pb2.LandmarkList(landmark=[
            landmark_pb2.Landmark(x=float(p[0]),y=float(p[1]),z=float(p[2])) for p in world.reshape(21,3)])
        probability=float(side.item())
        out.side=classification_pb2.ClassificationList(classification=[classification_pb2.Classification(
            index=int(probability<.5),score=max(probability,1-probability),label='Right' if probability<.5 else 'Left')])
        return out

    def close(self):
        self.net.close()
