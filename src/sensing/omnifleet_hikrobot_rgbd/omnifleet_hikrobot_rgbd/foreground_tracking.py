"""Foreground observations shared by object trackers and person BoT-SORT.

Depth results retain the measured native samples. Semantic-only results never
claim measured range. GMC must receive the original image, not appearance().
"""
import time
import cv2
import numpy as np
from .depth_foreground import depth_foreground, foreground_frame, _semantic_at
from .aligned_depth import aligned_depth_foreground


def semantic_foreground(mask, bbox, rgb_size):
    x,y,w,h = bbox
    x0,y0=max(0.,x),max(0.,y)
    x1,y1=min(rgb_size[0],x+w),min(rgb_size[1],y+h)
    if x1<=x0 or y1<=y0:return None
    scale=min(1.,128/max(x1-x0,y1-y0))
    mw,mh=max(1,round((x1-x0)*scale)),max(1,round((y1-y0)*scale))
    u,v=np.meshgrid(x0+(np.arange(mw)+.5)*(x1-x0)/mw,y0+(np.arange(mh)+.5)*(y1-y0)/mh)
    roi=_semantic_at(mask,np.stack([u,v],axis=-1),rgb_size).astype(np.uint8)*255
    bx,by,bw,bh=cv2.boundingRect(roi)
    if not bw or not bh:return None
    rows,cols=np.nonzero(roi)
    return dict(mask_roi=roi,mask_box_xywh=[x0,y0,x1-x0,y1-y0],rgb_size=rgb_size,
        bbox_xywh=[x0+bx*(x1-x0)/mw,y0+by*(y1-y0)/mh,bw*(x1-x0)/mw,bh*(y1-y0)/mh],
        centroid_rgb=[x0+float(np.median(cols))*(x1-x0)/mw,y0+float(np.median(rows))*(y1-y0)/mh],
        depth_m=None,source='semantic_only',semantic_used=True,depth_sample_count=0)


def summary(result, stamp=None, depth_stamp=None):
    if result is None:return dict(available=False,source='unavailable',depth_m=None)
    output=dict(available=True,source=result['source'],semantic_used=result['semantic_used'],
        ambiguous=not result['semantic_used'],bbox_xywh=list(map(float,result['bbox_xywh'])),
        centroid_rgb=list(map(float,result['centroid_rgb'])),depth_m=result['depth_m'],
        sampled_count=result['depth_sample_count'],source_stamp=stamp,depth_stamp=depth_stamp)
    if result.get('depth_m') is not None:
        output.update(projection_backend=result.get('projection_backend','numpy'),rgb_xyz_m=result['rgb_xyz_m'].tolist(),
            native_depth_mm_range=[int(result['native_mm'].min()),int(result['native_mm'].max())],
            projected_grid_pixels=result['projected_grid_pixels'])
    return output


class ForegroundQuery:
    def __init__(self, minimum=.2, maximum=3.5):
        self.minimum,self.maximum=minimum,maximum
        self.depth=self.depth_k=self.rgb_k=self.transform=self.rgb_size=self.distortion=None
        self.stamp=self.depth_stamp=None
        self.projector=None
        self.depth_is_aligned=False
        self.calls,self.elapsed_ms=0,0.

    def query(self,bbox,semantic_mask=None,prior=None,use_depth=True):
        started=time.perf_counter();result=None
        if self.rgb_size is None:return None
        if use_depth and self.depth is not None and self.depth_k is not None and self.rgb_k is not None and self.transform is not None:
            if self.depth_is_aligned:
                result=aligned_depth_foreground(self.depth,bbox,self.rgb_size,self.rgb_k,
                    semantic_mask=semantic_mask,min_depth_m=self.minimum,max_depth_m=self.maximum,
                    rgb_distortion=self.distortion)
            else:
                result=depth_foreground(self.depth,bbox,self.rgb_size,self.depth_k,self.rgb_k,self.transform,
                    semantic_mask=semantic_mask,depth_prior_m=prior,min_depth_m=self.minimum,
                    max_depth_m=self.maximum,rgb_distortion=self.distortion,projector=self.projector)
        if result is None and semantic_mask is not None:
            result=semantic_foreground(semantic_mask,bbox,self.rgb_size)
        self.calls+=1;self.elapsed_ms+=(time.perf_counter()-started)*1000
        return result

    @staticmethod
    def appearance(image,result):
        return image if result is None else foreground_frame(image,result)

    def describe(self,result):return summary(result,self.stamp,self.depth_stamp)
