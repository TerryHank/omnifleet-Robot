"""OpenCV Zoo hand ROI geometry, rotating only the final crop at native scale.

Retains the original bilinear warp, INTER_AREA resize and postprocess coordinates.
Geometry follows the Apache-2.0 OpenCV Zoo MediaPipe hand sample.
"""
import time
import cv2
import numpy as np


def hand_preprocess(self,image,palm):
    started=time.perf_counter()
    def crop_box(box,shape,rotation):
        size=box[1]-box[0]
        shift=self.PALM_BOX_PRE_SHIFT_VECTOR if rotation else self.PALM_BOX_SHIFT_VECTOR
        box=box+np.asarray(shift)*size
        center=box.sum(axis=0)/2
        factor=self.PALM_BOX_PRE_ENLARGE_FACTOR if rotation else self.PALM_BOX_ENLARGE_FACTOR
        box=np.array([center-size*factor/2,center+size*factor/2]).astype(np.int32)
        box[:,0]=np.clip(box[:,0],0,shape[1]);box[:,1]=np.clip(box[:,1],0,shape[0])
        width,height=box[1]-box[0]
        side=int(np.linalg.norm([height,width])) if rotation else int(max(height,width))
        left,top=(side-width)//2,(side-height)//2
        return box,box[0]-[left,top],int(left),int(top),side
    first,bias,left,top,side=crop_box(palm[:4].reshape(2,2),image.shape,True)
    landmarks=palm[4:18].reshape(7,2)-bias
    p1=landmarks[self.PALM_LANDMARKS_INDEX_OF_PALM_BASE]
    p2=landmarks[self.PALM_LANDMARKS_INDEX_OF_MIDDLE_FINGER_BASE]
    radians=np.pi/2-np.arctan2(-(p2[1]-p1[1]),p2[0]-p1[0])
    radians-=2*np.pi*np.floor((radians+np.pi)/(2*np.pi))
    angle=np.rad2deg(radians)
    rotation=cv2.getRotationMatrix2D((first-bias).sum(axis=0)/2,angle,1.)
    homogeneous=np.c_[landmarks,np.ones(len(landmarks))]
    rotated=np.array([np.dot(homogeneous,rotation[0]),np.dot(homogeneous,rotation[1])])
    second,_,left2,top2,side2=crop_box(np.array([rotated.min(axis=1),rotated.max(axis=1)]),(side,side),False)
    local=rotation.copy()
    local[:,2]+=rotation[:,:2]@[left,top]-second[0]
    source=image[first[0,1]:first[1,1],first[0,0]:first[1,0]]
    width,height=map(int,second[1]-second[0])
    crop=cv2.warpAffine(source,local,(width,height))
    crop=cv2.copyMakeBorder(crop,top2,side2-height-top2,left2,side2-width-left2,cv2.BORDER_CONSTANT,value=(0,0,0))
    blob=cv2.resize(crop,tuple(self.input_size),interpolation=cv2.INTER_AREA)
    blob=cv2.cvtColor(blob,cv2.COLOR_BGR2RGB).astype(np.float32)/255.
    self.preprocess_ms=(time.perf_counter()-started)*1000
    return blob[np.newaxis],second,angle,rotation,bias
