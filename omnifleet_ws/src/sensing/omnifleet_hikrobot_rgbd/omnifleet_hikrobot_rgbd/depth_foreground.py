"""Depth-connected foreground prototype; no ROS, learned model or motion policy.

Boxes are RGB xywh. semantic_mask, if supplied, is in full RGB coordinates or
the existing YOLO letterbox coordinates. Depth is native 16UC1 millimetres.
"""
import time
import cv2
import numpy as np


def _semantic_at(mask, uv, rgb_size):
    height, width = mask.shape
    gain = min(width / rgb_size[0], height / rgb_size[1])
    left = round((width - round(rgb_size[0]*gain))/2-.1)
    top = round((height - round(rgb_size[1]*gain))/2-.1)
    x = (uv[...,0]*gain+left).astype(int).clip(0,width-1)
    y = (uv[...,1]*gain+top).astype(int).clip(0,height-1)
    return mask[y,x].astype(bool)


def depth_foreground(depth_mm, bbox_xywh, rgb_size, depth_k, rgb_k, depth_to_rgb,
                     semantic_mask=None, seed_rgb=None, depth_prior_m=None,
                     max_neighbor_diff_mm=100., max_reference_diff_mm=250.,
                     max_side=128, min_depth_m=.2, max_depth_m=5., rgb_distortion=None,
                     projector=None):
    """Return a coarse RGB ROI mask, refined observation and <=256 depth samples.

    Local floating-range flood fill is additionally limited around the current
    seed depth, preventing unbounded ramp leakage. The output mask is geometric,
    not a semantic object guarantee. None means no measured component was found.
    """
    started = time.perf_counter()
    depth = np.asarray(depth_mm)
    if depth.ndim != 2 or depth.dtype.kind != 'u' or depth.dtype.itemsize != 2:
        raise ValueError('Expected native 16UC1 millimetre depth')
    if min(max_neighbor_diff_mm,max_reference_diff_mm,max_side) <= 0:
        raise ValueError('Foreground thresholds and grid size must be positive')
    width,height = rgb_size
    x,y,w,h = map(float,bbox_xywh)
    x0,y0,x1,y1 = max(0.,x),max(0.,y),min(width,x+w),min(height,y+h)
    if x0 >= x1 or y0 >= y1:return None
    kd,kr,t = np.asarray(depth_k),np.asarray(rgb_k),np.asarray(depth_to_rgb)
    rotation,translation = t[:3,:3],t[:3,3]
    corners = np.array([[x0,y0],[x1,y0],[x0,y1],[x1,y1]],float)
    if rgb_distortion is not None:
        rays=np.c_[cv2.undistortPoints(corners.reshape(-1,1,2),kr,np.asarray(rgb_distortion)).reshape(-1,2),np.ones(4)]
    else:rays=np.c_[corners,np.ones(4)]@np.linalg.inv(kr).T
    a,b = rays@rotation,-rotation.T@translation
    if np.any(a[:,2] <= 0):return None
    limits=np.array([min_depth_m,max_depth_m])
    endpoints=a[:,None,:]*((limits[None,:]-b[2])/a[:,2,None])[:,:,None]+b
    projected=endpoints.reshape(-1,3)@kd.T
    uv=projected[:,:2]/projected[:,2:3]
    low,high=np.floor(uv.min(axis=0)).astype(int)-1,np.ceil(uv.max(axis=0)).astype(int)+2
    u0,v0=max(0,low[0]),max(0,low[1])
    u1,v1=min(depth.shape[1],high[0]),min(depth.shape[0],high[1])
    if u0 >= u1 or v0 >= v1:return None
    stride=max(1,int(np.ceil(max(u1-u0,v1-v0)/max_side)))
    u,v=np.meshgrid(np.arange(u0,u1,stride),np.arange(v0,v1,stride))
    shape=u.shape
    raw=depth[v,u]
    valid=(raw>0)&(raw<65535)&(raw>=min_depth_m*1000)&(raw<=max_depth_m*1000)
    if projector is not None:
        xyz,uv=projector(u,v,raw,kd,kr,rotation,translation,rgb_distortion,
                         (depth.shape[1],depth.shape[0]),rgb_size)
    else:
        native=np.c_[u.ravel(),v.ravel(),np.ones(u.size)]@np.linalg.inv(kd).T*(raw.ravel()[:,None]*.001)
        xyz=native@rotation.T+translation
        projected=xyz@kr.T
        with np.errstate(divide='ignore',invalid='ignore'):uv=projected[:,:2]/projected[:,2:3]
        if rgb_distortion is not None:
            uv=cv2.projectPoints(xyz,np.zeros(3),np.zeros(3),kr,np.asarray(rgb_distortion))[0].reshape(-1,2)
    valid=valid.ravel()&(xyz[:,2]>0)&np.isfinite(uv).all(axis=1)
    valid &= (uv[:,0]>=x0)&(uv[:,0]<x1)&(uv[:,1]>=y0)&(uv[:,1]<y1)
    safe_uv=np.where(np.isfinite(uv),uv,0.)
    if semantic_mask is not None:valid &= _semantic_at(np.asarray(semantic_mask),safe_uv,rgb_size)
    candidates=np.flatnonzero(valid)
    if not candidates.size:return None
    seed=np.asarray(seed_rgb if seed_rgb is not None else [(x0+x1)/2,(y0+y1)/2])
    score=np.sum(((uv[candidates]-seed)/np.array([x1-x0,y1-y0]))**2,axis=1)
    if depth_prior_m is not None:
        score += .25*((xyz[candidates,2]-depth_prior_m)/(max_reference_diff_mm*.001))**2
    index=candidates[np.argmin(score)]
    seed_z=xyz[index,2]*1000.
    allowed=valid&(np.abs(xyz[:,2]*1000.-seed_z)<=max_reference_diff_mm)
    barrier=np.ones((shape[0]+2,shape[1]+2),np.uint8)
    barrier[1:-1,1:-1]=(~allowed.reshape(shape)).astype(np.uint8)
    surface=(xyz[:,2].reshape(shape)*1000).astype(np.float32)
    cv2.floodFill(surface,barrier,(int(index%shape[1]),int(index//shape[1])),0,
                  loDiff=max_neighbor_diff_mm,upDiff=max_neighbor_diff_mm,
                  flags=4|cv2.FLOODFILL_MASK_ONLY|(255<<8))
    component=barrier[1:-1,1:-1]==255
    rows,cols=np.nonzero(component)
    # One actual native measurement per occupied cell of a16x16 grid.
    cells=(rows*16//shape[0])*16+(cols*16//shape[1])
    _,first=np.unique(cells,return_index=True)
    indices=(rows[first]*shape[1]+cols[first])
    values=xyz[indices]
    z=np.median(values[:,2]);mad=np.median(np.abs(values[:,2]-z))
    indices=indices[np.abs(values[:,2]-z)<=max(.03,3*1.4826*mad)]
    values=xyz[indices]
    if not len(values):return None
    scale=min(1.,max_side/max(x1-x0,y1-y0))
    mw,mh=max(1,round((x1-x0)*scale)),max(1,round((y1-y0)*scale))
    mask=np.zeros((mh,mw),np.uint8)
    hits=uv[component.ravel()]
    mx=((hits[:,0]-x0)*mw/(x1-x0)).astype(int).clip(0,mw-1)
    my=((hits[:,1]-y0)*mh/(y1-y0)).astype(int).clip(0,mh-1)
    mask[my,mx]=255
    # Raster footprint only; no missing or interpolated depth is used for range.
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    if semantic_mask is not None:
        gx,gy=np.meshgrid(x0+(np.arange(mw)+.5)*(x1-x0)/mw,y0+(np.arange(mh)+.5)*(y1-y0)/mh)
        mask[~_semantic_at(np.asarray(semantic_mask),np.stack([gx,gy],axis=-1),rgb_size)]=0
    bx,by,bw,bh=cv2.boundingRect(mask)
    if bw==0 or bh==0:return None
    result_xyz=np.median(values,axis=0)
    return dict(projection_backend='orbbec_sdk_cpp' if projector is not None else 'numpy',
                mask_roi=mask,mask_box_xywh=[x0,y0,x1-x0,y1-y0],rgb_size=rgb_size,
                bbox_xywh=[x0+bx*(x1-x0)/mw,y0+by*(y1-y0)/mh,bw*(x1-x0)/mw,bh*(y1-y0)/mh],
                centroid_rgb=np.median(hits,axis=0),rgb_xyz_m=result_xyz,depth_m=float(result_xyz[2]),
                native_uv=np.c_[u.ravel()[indices],v.ravel()[indices]],native_mm=raw.ravel()[indices],
                sampled_depth_m=values[:,2],depth_sample_count=len(indices),foreground_grid_pixels=len(rows),
                projected_grid_pixels=u.size,semantic_used=semantic_mask is not None,
                source='depth_continuity',elapsed_ms=(time.perf_counter()-started)*1000.)


def foreground_frame(image, result, neutral=(127,127,127)):
    """Experimental appearance input for SOT; keep the original frame for GMC.

    The caller must benchmark tracking quality: standard NanoTrack has no native
    mask input. This operation changes its visual input, not the network itself.
    image must be the original RGB or its direct resize, without letterbox padding.
    """
    output=np.full_like(image,neutral[0]) if len(set(neutral))==1 else np.empty_like(image)
    if len(set(neutral))!=1:output[:]=neutral
    x,y,w,h=result['mask_box_xywh'];rw,rh=result['rgb_size']
    sx,sy=image.shape[1]/rw,image.shape[0]/rh
    x0,y0=max(0,round(x*sx)),max(0,round(y*sy))
    x1,y1=min(image.shape[1],round((x+w)*sx)),min(image.shape[0],round((y+h)*sy))
    if x0>=x1 or y0>=y1:return output
    alpha=cv2.resize(result['mask_roi'],(x1-x0,y1-y0),interpolation=cv2.INTER_LINEAR).astype(np.float32)/255.
    alpha=cv2.GaussianBlur(alpha,(3,3),0)[:,:,None]
    patch=image[y0:y1,x0:x1].astype(np.float32)
    output[y0:y1,x0:x1]=(patch*alpha+np.asarray(neutral,dtype=np.float32)*(1-alpha)).astype(image.dtype)
    return output
