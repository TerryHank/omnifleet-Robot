"""MediaPipe anatomical landmarks to the requested robot actions."""
import numpy as np


POSE_EDGES = [(11,12),(11,13),(13,15),(12,14),(14,16),(11,23),
              (12,24),(23,24),(23,25),(25,27),(24,26),(26,28)]
ACTION_CODES = {'both_up':11, 'cross_stop':5, 'forward':101,
                'reverse':102, 'neutral':0}


def visible(points, indices):
    values = np.asarray(points)[indices]
    return bool(np.isfinite(values).all() and (values[:,3:5] >= .5).all())


def hip_region(points, shape):
    if not visible(points, [23,24]):
        return None, None
    center = np.mean(points[[23,24],:2], axis=0)
    height, width = shape[:2]
    if not (0 <= center[0] < width and 0 <= center[1] < height):
        return None, None
    radius = float(np.clip(np.linalg.norm(points[23,:2]-points[24,:2])*.3, 8, 64))
    low = np.maximum(center-radius, 0)
    high = np.minimum(center+radius, [width,height])
    return center.tolist(), [*low.tolist(), *(high-low).tolist()]


def classify_pose(points):
    """Input is unmirrored camera pixels; left/right belong to the person."""
    p = np.asarray(points)
    if p.shape != (33,5) or not visible(p,[11,12]):
        return 'neutral'
    ls,rs,le,re,lw,rw = p[[11,12,13,14,15,16],:2]
    left_visible = visible(p,[13,15])
    right_visible = visible(p,[14,16])
    scale = max(1.,float(np.linalg.norm(ls-rs)))
    direction = np.sign(ls[0]-rs[0])
    torso_top = min(ls[1],rs[1])-.6*scale
    # Wrist order reverses across the torso when the arms cross.
    crossed = direction*(lw[0]-rw[0]) < -.08*scale
    close = np.linalg.norm((lw+rw)/2-(ls+rs)/2) < 1.5*scale
    if left_visible and right_visible and crossed and close and min(lw[1],rw[1]) > torso_top:
        return 'cross_stop'
    shoulder_mid_x = (ls[0]+rs[0])*.5
    wrists_on_both_sides = direction*(lw[0]-shoulder_mid_x) > 0 > direction*(rw[0]-shoulder_mid_x)
    if (left_visible and right_visible and wrists_on_both_sides
            and lw[1] < min(ls[1]-.65*scale, le[1])
            and rw[1] < min(rs[1]-.65*scale, re[1])):
        return 'both_up'
    lateral = []
    arms = [(ls,le,lw,direction,left_visible),(rs,re,rw,-direction,right_visible)]
    for shoulder,elbow,wrist,side,valid in arms:
        lateral.append(valid and side*(wrist[0]-shoulder[0]) > .65*scale
                       and side*(elbow[0]-shoulder[0]) > .25*scale
                       and abs(wrist[1]-shoulder[1]) < .6*scale)
    if lateral == [True,False]:
        return 'forward'
    if lateral == [False,True]:
        return 'reverse'
    return 'neutral'
