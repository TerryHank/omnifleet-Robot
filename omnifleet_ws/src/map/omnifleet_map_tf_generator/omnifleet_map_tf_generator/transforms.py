"""Planar map-frame transforms shared by navigation and fleet code."""
import math

def angle(value):
    return math.atan2(math.sin(value), math.cos(value))

def pose(value):
    if not isinstance(value,(list,tuple)) or len(value)!=3:
        raise ValueError('pose requires [x, y, yaw]')
    result=[float(v) for v in value]
    if not all(math.isfinite(v) and abs(v)<100000 for v in result):
        raise ValueError('pose contains invalid values')
    result[2]=angle(result[2])
    return result

def compose(a,b):
    c,s=math.cos(a[2]),math.sin(a[2])
    return [a[0]+c*b[0]-s*b[1],a[1]+s*b[0]+c*b[1],angle(a[2]+b[2])]

def inverse(a):
    c,s=math.cos(a[2]),math.sin(a[2])
    return [-c*a[0]-s*a[1],s*a[0]-c*a[1],-a[2]]
