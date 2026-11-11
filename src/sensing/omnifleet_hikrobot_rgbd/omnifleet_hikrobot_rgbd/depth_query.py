"""On-demand RGB-pixel lookup in rectified native 16UC1 millimetre depth."""
import numpy as np
from functools import lru_cache


@lru_cache(maxsize=8)
def _calibration_inverse(values):
    return np.linalg.inv(np.frombuffer(values,dtype=np.float64).reshape(3,3))


def rgb_pixel_to_depth(depth_mm, rgb_pixel, depth_k, rgb_k, depth_to_rgb,
                       min_depth_m=.2, max_depth_m=1.5, max_error_px=3.):
    """Return a measured sample for an RGB pixel, or None if no sample matches.

    Intrinsics are 3x3; depth_to_rgb is the factory 4x4 transform in metres.
    Only a small native-depth ROI along the RGB ray's epipolar segment is
    inspected. No registered image, point cloud, interpolation or hole filling
    is created. max_error_px bounds the returned sample's RGB reprojection
    distance. rgb_xyz_m/depth_m are in the RGB optical frame; raw_depth_mm and
    depth_uv describe the actual native measurement.
    """
    depth = np.asarray(depth_mm)
    if depth.ndim != 2 or depth.dtype.kind != 'u' or depth.dtype.itemsize != 2:
        raise ValueError('depth_mm must be a native 16UC1 millimetre image')
    pixel = np.asarray(rgb_pixel, dtype=float)
    if pixel.shape != (2,) or not np.isfinite(pixel).all():
        return None
    kd, kr, transform = np.asarray(depth_k), np.asarray(rgb_k), np.asarray(depth_to_rgb)
    rotation, translation = transform[:3, :3], transform[:3, 3]
    ray = np.linalg.solve(kr, np.r_[pixel, 1.])
    a, b = rotation.T @ ray, -rotation.T @ translation
    if a[2] <= 1e-9:
        return None
    limits = np.array([min_depth_m, max_depth_m])
    endpoints = a[None, :] * ((limits - b[2]) / a[2])[:, None] + b
    projected = endpoints @ kd.T
    projected = projected[:, :2] / projected[:, 2:3]
    margin = int(np.ceil(max_error_px * max(kd[0, 0]/kr[0, 0], kd[1, 1]/kr[1, 1]))) + 1
    low = np.floor(projected.min(axis=0)).astype(int) - margin
    high = np.ceil(projected.max(axis=0)).astype(int) + margin + 1
    x0, y0 = max(0, low[0]), max(0, low[1])
    x1, y1 = min(depth.shape[1], high[0]), min(depth.shape[0], high[1])
    if x0 >= x1 or y0 >= y1:
        return None
    roi = depth[y0:y1, x0:x1]
    valid = ((roi > 0) & (roi < 65535) &
             (roi >= min_depth_m*1000.) & (roi <= max_depth_m*1000.))
    y, x = np.nonzero(valid)
    if not x.size:
        return None
    z = roi[y, x].astype(float) * .001
    native = np.c_[x+x0, y+y0, np.ones(x.size)] @ np.linalg.inv(kd).T * z[:, None]
    rgb = native @ rotation.T + translation
    uv = rgb @ kr.T
    with np.errstate(divide='ignore', invalid='ignore'):
        uv = uv[:, :2] / uv[:, 2:3]
    error = np.sum((uv-pixel)**2, axis=1)
    candidates = np.flatnonzero((rgb[:, 2] > 0) & (error <= max_error_px**2))
    if not candidates.size:
        return None
    # Nearest reprojection, resolving coincident samples to the visible surface.
    nearest = error[candidates].min()
    tied = candidates[error[candidates] <= nearest + 1e-9]
    best = tied[np.argmin(rgb[tied, 2])]
    return dict(depth_m=float(rgb[best, 2]), rgb_xyz_m=rgb[best],
                raw_depth_mm=int(roi[y[best], x[best]]),
                depth_uv=(int(x[best]+x0), int(y[best]+y0)),
                reprojection_error_px=float(np.sqrt(error[best])),
                inspected_pixels=int(roi.size))


def rgb_mask_to_depth(depth_mm, rgb_mask, rgb_bbox, rgb_size, depth_k, rgb_k,
                      depth_to_rgb, grid_size=16, min_depth_m=.2, max_depth_m=1.5, rgb_distortion=None):
    """Sample at most grid_size² native pixels, project and retain RGB-mask hits.

    The grid covers the locked person's depth ROI, bounded using the factory
    transform and valid depth interval. Every retained XYZ comes from an actual
    native depth sample. The returned location is its robust median; no aligned
    image or per-RGB-pixel lookup loop is needed.
    """
    depth, mask = np.asarray(depth_mm), np.asarray(rgb_mask, dtype=bool)
    if depth.ndim != 2 or depth.dtype.kind != 'u' or depth.dtype.itemsize != 2:
        raise ValueError('depth_mm must be a native 16UC1 millimetre image')
    x1,y1,x2,y2 = np.asarray(rgb_bbox, dtype=float)
    if not np.isfinite([x1,y1,x2,y2]).all() or x2 <= x1 or y2 <= y1 or mask.size == 0:
        return None
    kd, kr, transform = np.asarray(depth_k), np.asarray(rgb_k), np.asarray(depth_to_rgb)
    rotation, translation = transform[:3,:3], transform[:3,3]
    rgb_inverse = _calibration_inverse(np.asarray(kr,dtype=np.float64).tobytes())
    depth_inverse = _calibration_inverse(np.asarray(kd,dtype=np.float64).tobytes())
    corners = np.array([[x1,y1],[x2,y1],[x1,y2],[x2,y2]], dtype=float)
    if rgb_distortion is not None:
        import cv2
        rays = np.c_[cv2.undistortPoints(corners.reshape(-1,1,2), kr,
                     np.asarray(rgb_distortion)).reshape(-1,2), np.ones(4)]
    else:
        rays = np.c_[corners, np.ones(4)] @ rgb_inverse.T
    a, b = rays @ rotation, -rotation.T @ translation
    if np.any(a[:,2] <= 1e-9):
        return None
    z = np.array([min_depth_m,max_depth_m])
    endpoints = a[:,None,:] * ((z[None,:]-b[2])/a[:,2,None])[:,:,None] + b
    projected = endpoints.reshape(-1,3) @ kd.T
    projected = projected[:,:2] / projected[:,2:3]
    low, high = np.floor(projected.min(axis=0)).astype(int)-1, np.ceil(projected.max(axis=0)).astype(int)+1
    u0,v0 = max(0,low[0]),max(0,low[1])
    u1,v1 = min(depth.shape[1],high[0]),min(depth.shape[0],high[1])
    if u0 >= u1 or v0 >= v1:
        return None
    us = np.unique(np.floor(u0+(np.arange(grid_size)+.5)*(u1-u0)/grid_size).astype(int))
    vs = np.unique(np.floor(v0+(np.arange(grid_size)+.5)*(v1-v0)/grid_size).astype(int))
    u,v = np.meshgrid(us,vs)
    u,v = u.ravel(),v.ravel()
    sampled_count = u.size
    raw = depth[v,u]
    valid = (raw > 0) & (raw < 65535) & (raw >= min_depth_m*1000.) & (raw <= max_depth_m*1000.)
    if not valid.any():
        return None
    u,v,raw = u[valid],v[valid],raw[valid]
    native = np.c_[u,v,np.ones(u.size)] @ depth_inverse.T * (raw[:,None]*.001)
    rgb = native @ rotation.T + translation
    projected = rgb @ kr.T
    with np.errstate(divide='ignore',invalid='ignore'):
        uv = projected[:,:2] / projected[:,2:3]
    if rgb_distortion is not None:
        uv = cv2.projectPoints(rgb, np.zeros(3), np.zeros(3), kr,
                               np.asarray(rgb_distortion))[0].reshape(-1,2)
    width,height = rgb_size
    valid = ((rgb[:,2] > 0) & np.isfinite(uv).all(axis=1) &
             (uv[:,0] >= max(0,x1)) & (uv[:,0] < min(width,x2)) &
             (uv[:,1] >= max(0,y1)) & (uv[:,1] < min(height,y2)))
    u,v,raw,rgb,uv = u[valid],v[valid],raw[valid],rgb[valid],uv[valid]
    if not u.size:
        return None
    mh,mw = mask.shape
    gain = min(mw/width,mh/height)
    left,top = round((mw-round(width*gain))/2-.1),round((mh-round(height*gain))/2-.1)
    mx = (uv[:,0]*gain+left).astype(int).clip(0,mw-1)
    my = (uv[:,1]*gain+top).astype(int).clip(0,mh-1)
    valid = mask[my,mx]
    u,v,raw,rgb = u[valid],v[valid],raw[valid],rgb[valid]
    if not u.size:
        return None
    mask_valid_count = u.size
    median_z = np.median(rgb[:,2])
    mad = np.median(np.abs(rgb[:,2]-median_z))
    inliers = np.abs(rgb[:,2]-median_z) <= max(.03,3*1.4826*mad)
    rgb,u,v,raw = rgb[inliers],u[inliers],v[inliers],raw[inliers]
    xyz = np.median(rgb,axis=0)
    representative = np.argmin(np.sum((rgb-xyz)**2,axis=1))
    return dict(depth_m=float(xyz[2]),rgb_xyz_m=xyz,grid_size=int(grid_size),
                sampled_count=int(sampled_count),mask_valid_count=int(mask_valid_count),
                inlier_count=int(rgb.shape[0]),depth_mad_m=float(mad),
                depth_uv=(int(u[representative]),int(v[representative])),
                raw_depth_mm=int(raw[representative]),inspected_pixels=int(sampled_count))
