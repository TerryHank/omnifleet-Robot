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

def offsets(kind,spacing,count):
    if kind not in ('column','row','line') or count not in (1,2):
        raise ValueError('this deployment supports one/two robots, column/row/line')
    return [[0.,0.,0.]]+([[-spacing,0.,0.] if kind!='row' else [0.,spacing,0.]] if count==2 else [])

def closest_approach(a,av,b,bv,horizon):
    dx,dy=b[0]-a[0],b[1]-a[1]
    vx,vy=bv[0]-av[0],bv[1]-av[1]
    vv=vx*vx+vy*vy
    t=max(0.,min(horizon,-(dx*vx+dy*vy)/vv)) if vv>1e-10 else 0.
    return math.hypot(dx+t*vx,dy+t*vy),t

def world_velocity(p,v):
    return [v[0]*math.cos(p[2]),v[0]*math.sin(p[2])]

def safe_velocity(own,target,peers,clearance=.2,horizon=1.):
    """Conservative swept disks; unknown/stale peers fail closed in fleet mode."""
    if own.get('pose') is None:
        return [0.,0.],'own pose unavailable'
    for peer in peers:
        if peer.get('pose') is None or peer.get('age',99)>.8:
            return [0.,0.],'peer pose stale'
        limit=own['radius']+peer['radius']+clearance+abs(target[0])*own.get('age',0)+abs(peer['velocity'][0])*peer.get('age',0)
        count=max(1,math.ceil(horizon/.05));distance=float('inf')
        for candidate in (peer['velocity'],[0.,0.]):
            for i in range(count+1):
                t=horizon*i/count
                a=integrate_twist(own['pose'],target,t);b=integrate_twist(peer['pose'],candidate,t)
                distance=min(distance,math.dist(a[:2],b[:2]))
        # Additional sampling margin covers motion between adjacent arc samples.
        limit+=(abs(target[0])+abs(peer['velocity'][0]))*horizon/count/2
        if distance<limit:
            return [0.,0.],'predicted inter-robot distance below safety margin'
    return list(target),''

def integrate_twist(p,velocity,seconds):
    v,w=velocity;theta=p[2]+w*seconds
    if abs(w)<1e-8:return [p[0]+v*seconds*math.cos(p[2]),p[1]+v*seconds*math.sin(p[2]),theta]
    return [p[0]+v/w*(math.sin(theta)-math.sin(p[2])),p[1]-v/w*(math.cos(theta)-math.cos(p[2])),theta]
