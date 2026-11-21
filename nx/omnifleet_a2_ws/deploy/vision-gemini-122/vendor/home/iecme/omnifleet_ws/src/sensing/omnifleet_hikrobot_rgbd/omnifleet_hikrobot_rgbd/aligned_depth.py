"""Direct16x16 measured-depth sampling in the RGB-aligned pixel plane."""
import time
import cv2
import numpy as np
from .depth_foreground import _semantic_at


def aligned_depth_foreground(depth_mm,bbox_xywh,rgb_size,rgb_k,semantic_mask=None,
                             min_depth_m=.2,max_depth_m=5.,rgb_distortion=None):
    started=time.perf_counter()
    width,height=rgb_size
    depth=np.asarray(depth_mm)
    if depth.shape!=(height,width) or depth.dtype.kind!='u' or depth.dtype.itemsize!=2:
        raise ValueError('Aligned16UC1 depth must have the RGB image dimensions')
    x,y,w,h=map(float,bbox_xywh)
    x0,y0,x1,y1=max(0.,x),max(0.,y),min(width,x+w),min(height,y+h)
    if x0>=x1 or y0>=y1:return None
    w,h=x1-x0,y1-y0
    u,v=np.meshgrid(x0+(np.arange(16)+.5)*w/16,y0+(np.arange(16)+.5)*h/16)
    uv=np.stack([u,v],axis=-1)
    sample_uv=uv
    # Hardware D2C is in the ideal RGB pixel plane. Raw RGB CameraInfo retains
    # lens distortion while aligned depth reports zero distortion. Correct the
    #256 lookup coordinates in one native batch, without any3D point search.
    if rgb_distortion is not None and np.any(rgb_distortion):
        sample_uv=cv2.undistortPoints(uv.reshape(-1,1,2),np.asarray(rgb_k),
            np.asarray(rgb_distortion),P=np.asarray(rgb_k)).reshape(16,16,2)
    columns=sample_uv[...,0].astype(int);rows=sample_uv[...,1].astype(int)
    inside=(columns>=0)&(columns<width)&(rows>=0)&(rows<height)
    columns=columns.clip(0,width-1);rows=rows.clip(0,height-1)
    # One NumPy indexed gather of256 actual aligned depth pixels.
    raw=depth[rows,columns]
    valid=(raw>0)&(raw<65535)&(raw>=min_depth_m*1000)&(raw<=max_depth_m*1000)
    valid &= inside
    if semantic_mask is not None:valid &= _semantic_at(np.asarray(semantic_mask),uv,rgb_size)
    candidates=np.flatnonzero(valid)
    if not candidates.size:return None
    score=((u.ravel()[candidates]-(x0+x1)/2)/w)**2+((v.ravel()[candidates]-(y0+y1)/2)/h)**2
    seed=int(candidates[np.argmin(score)])
    allowed=valid&(np.abs(raw.astype(float)-float(raw.ravel()[seed]))<=250.)
    barrier=np.ones((18,18),np.uint8);barrier[1:-1,1:-1]=(~allowed).astype(np.uint8)
    cv2.floodFill(raw.astype(np.float32),barrier,(seed%16,seed//16),0,
                  loDiff=100.,upDiff=100.,flags=4|cv2.FLOODFILL_MASK_ONLY|(255<<8))
    component=barrier[1:-1,1:-1]==255
    indices=np.flatnonzero(component)
    z=raw.ravel()[indices].astype(float)*.001
    median=float(np.median(z));mad=float(np.median(np.abs(z-median)))
    indices=indices[np.abs(z-median)<=max(.03,3*1.4826*mad)]
    if not len(indices):return None
    values=raw.ravel()[indices].astype(float)*.001
    mask=np.zeros((16,16),np.uint8);mask.ravel()[indices]=255
    bx,by,bw,bh=cv2.boundingRect(mask)
    hits=uv.reshape(-1,2)[indices];center=np.median(hits,axis=0);z=float(np.median(values))
    intrinsic=np.asarray(rgb_k)
    if rgb_distortion is not None:
        ray=cv2.undistortPoints(center.reshape(1,1,2),intrinsic,np.asarray(rgb_distortion)).reshape(2)
    else:ray=np.array([(center[0]-intrinsic[0,2])/intrinsic[0,0],(center[1]-intrinsic[1,2])/intrinsic[1,1]])
    xyz=np.array([ray[0]*z,ray[1]*z,z])
    return dict(projection_backend='aligned_depth_direct',mask_roi=mask,
        mask_box_xywh=[x0,y0,w,h],rgb_size=rgb_size,
        bbox_xywh=[x0+bx*w/16,y0+by*h/16,bw*w/16,bh*h/16],
        centroid_rgb=center,rgb_xyz_m=xyz,depth_m=z,
        native_uv=np.column_stack([columns.ravel()[indices],rows.ravel()[indices]]),
        native_mm=raw.ravel()[indices],sampled_depth_m=values,depth_sample_count=len(indices),
        foreground_grid_pixels=int(component.sum()),projected_grid_pixels=256,
        semantic_used=semantic_mask is not None,source='aligned_depth_continuity',
        elapsed_ms=(time.perf_counter()-started)*1000.)
