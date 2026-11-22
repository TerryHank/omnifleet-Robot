"""Native array decoding of YOLO26 end-to-end person detections/masks."""
import cv2
import numpy as np


def person_masks(detections,prototypes,image_shape,image_size,confidence):
    selected=detections[(detections[:,4]>confidence)&(detections[:,5]==0)][:20].copy()
    if not len(selected):
        return selected[:,:6],np.empty((0,image_size,image_size),bool)
    proto=np.asarray(prototypes,dtype=np.float32)
    logits=cv2.gemm(selected[:,6:].astype(np.float32),proto.reshape(proto.shape[0],-1),1,None,0)
    masks=[]
    for row,logit in zip(selected,logits.reshape(-1,*proto.shape[1:])):
        mask=cv2.resize(logit,(image_size,image_size),interpolation=cv2.INTER_LINEAR)>0
        x1,y1,x2,y2=np.ceil(row[:4]).astype(int).clip(0,image_size)
        mask[:y1]=False;mask[y2:]=False;mask[:,:x1]=False;mask[:,x2:]=False
        masks.append(mask)
    masks=np.asarray(masks)
    keep=masks.any(axis=(1,2))
    selected,masks=selected[keep],masks[keep]
    height,width=image_shape[:2]
    gain=min(image_size/width,image_size/height)
    left=round((image_size-round(width*gain))/2-.1)
    top=round((image_size-round(height*gain))/2-.1)
    selected[:,[0,2]]=((selected[:,[0,2]]-left)/gain).clip(0,width)
    selected[:,[1,3]]=((selected[:,[1,3]]-top)/gain).clip(0,height)
    return selected[:,:6],masks
