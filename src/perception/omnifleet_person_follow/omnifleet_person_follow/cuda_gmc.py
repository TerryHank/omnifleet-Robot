"""BoT-SORT sparse optical flow on CUDA; retain CPU feature selection/RANSAC."""
import copy
import time
import cv2
import numpy as np


class CudaSparseFlow:
    def __init__(self):
        self.previous=cv2.cuda_GpuMat();self.current=cv2.cuda_GpuMat()
        self.points=cv2.cuda_GpuMat();self.stream=cv2.cuda_Stream()
        self.flow=cv2.cuda.SparsePyrLKOpticalFlow_create(winSize=(21,21),maxLevel=3,iters=30)

    def __call__(self,previous,current,points):
        self.previous.upload(previous,self.stream);self.current.upload(current,self.stream)
        self.points.upload(np.ascontiguousarray(points.reshape(1,-1,2)),self.stream)
        matched,status,_=self.flow.calc(self.previous,self.current,self.points,None,stream=self.stream)
        result,valid=matched.download(self.stream),status.download(self.stream)
        self.stream.waitForCompletion()
        return result.reshape(-1,1,2),valid.reshape(-1,1)


def apply_sparseoptflow(self,raw_frame):
    height,width,channels=raw_frame.shape
    frame=cv2.cvtColor(raw_frame,cv2.COLOR_BGR2GRAY) if channels==3 else raw_frame
    matrix=np.eye(2,3)
    if self.downscale>1:frame=cv2.resize(frame,(width//self.downscale,height//self.downscale))
    keypoints=cv2.goodFeaturesToTrack(frame,mask=None,**self.feature_params)
    if self.initializedFirstFrame and self.prevKeyPoints is not None:
        if not hasattr(self,'cuda_flow'):self.cuda_flow=CudaSparseFlow()
        started=time.perf_counter()
        matched,status=self.cuda_flow(self.prevFrame,frame,self.prevKeyPoints)
        self.cuda_flow_ms=(time.perf_counter()-started)*1000
        good=status.ravel().astype(bool)
        previous,current=self.prevKeyPoints[good],matched[good]
        if len(previous)>4:
            fitted,_=cv2.estimateAffinePartial2D(previous,current,cv2.RANSAC)
            if fitted is not None:
                matrix=fitted
                matrix[:,2]*=self.downscale
    self.prevFrame=frame.copy();self.prevKeyPoints=copy.copy(keypoints)
    self.initializedFirstFrame=True
    return matrix
