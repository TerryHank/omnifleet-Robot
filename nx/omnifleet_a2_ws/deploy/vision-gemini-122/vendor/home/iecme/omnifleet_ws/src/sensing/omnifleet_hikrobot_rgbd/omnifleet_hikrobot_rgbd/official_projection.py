"""Batch native depth projection through the installed official Orbbec SDK."""
import ctypes
from pathlib import Path
import numpy as np
import cv2
from ament_index_python.packages import get_package_prefix

_library=None

def project_depth(u,v,raw,kd,kr,rotation,translation,distortion,depth_size,rgb_size):
    global _library
    if _library is None:
        path=Path(get_package_prefix('orbbec_camera'))/'lib/libomnifleet_orbbec_projection.so'
        _library=ctypes.CDLL(str(path))
        _library.omnifleet_orbbec_project.argtypes=[ctypes.c_void_p,ctypes.c_size_t,
            *([ctypes.c_void_p]*5),*([ctypes.c_int]*4),ctypes.c_void_p]
        _library.omnifleet_orbbec_project.restype=ctypes.c_int
    pixels=np.ascontiguousarray(np.column_stack([u.ravel(),v.ravel(),raw.ravel()]),np.float32)
    params=[np.ascontiguousarray(a,np.float64) for a in [kd,kr,rotation,translation]]
    coefficients=np.zeros(8,np.float64)
    if distortion is not None:
        values=np.asarray(distortion).ravel();coefficients[:min(8,len(values))]=values[:8]
    params.append(coefficients)
    output=np.empty((len(pixels),5),np.float32)
    result=_library.omnifleet_orbbec_project(pixels.ctypes.data,len(pixels),
        *(p.ctypes.data for p in params),*depth_size,*rgb_size,output.ctypes.data)
    if result:raise RuntimeError('Official Orbbec coordinate conversion failed')
    xyz=output[:,:3].astype(np.float64)
    uv=output[:,3:].astype(np.float64)
    # SDK1.10.35 calibration2dTo2d returns ideal pixels even when distortion is
    # populated. Raw RGB retains its lens distortion; apply the existing camera
    # calibration once, in OpenCV's native batch implementation.
    if np.any(coefficients):
        uv=cv2.projectPoints(xyz,np.zeros(3),np.zeros(3),params[1],coefficients)[0].reshape(-1,2)
    return xyz,uv
