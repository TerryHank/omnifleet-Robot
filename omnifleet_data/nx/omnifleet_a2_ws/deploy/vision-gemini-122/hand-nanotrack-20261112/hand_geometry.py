"""Pose coordinates independent of image roll, translation and hand scale."""
import numpy as np


def canonical_hand(points):
    points=np.asarray(points,dtype=float)
    horizontal=points[5]-points[17]
    scale=max(float(np.linalg.norm(horizontal)),1e-9)
    horizontal=horizontal/scale
    vertical=points[9]-points[0]
    vertical=vertical-horizontal*np.dot(vertical,horizontal)
    vertical=vertical/max(float(np.linalg.norm(vertical)),1e-9)
    normal=np.cross(horizontal,vertical)
    basis=np.column_stack((horizontal,vertical,normal))
    return (points-points[0])@basis/scale


def image_rotation(points):
    points=np.asarray(points)
    axis=points[[5,9,13,17],:2].mean(0)-points[0,:2]
    return float(np.arctan2(axis[0],-axis[1]))
