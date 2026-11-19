"""Register current occupancy wall samples; reject weak or ambiguous matches."""
import json
import os
from omnifleet_rmf_adapter.state import connection_states
from omnifleet_rmf_adapter.registration import registration_pair
from omnifleet_rmf_adapter.alignment_validation import overlap_region_metrics, overlap_grid_margin
import math
from pathlib import Path
import cv2
import numpy as np
from scipy.signal import fftconvolve
from scipy.spatial import cKDTree
from rclpy.serialization import deserialize_message
from nav_msgs.msg import OccupancyGrid

data = Path(os.environ['OMNIFLEET_DATA'])
source_robot,reference_robot = registration_pair(json.loads(Path(os.environ['OMNIFLEET_CONFIG']).read_text()))
report = json.loads((data/'connection_status.json').read_text())
def walls(robot):
    grid = deserialize_message((data/'vehicle-cache'/robot/'map.cdr').read_bytes(),OccupancyGrid)
    rows,cols = np.where(np.array(grid.data).reshape(grid.info.height,grid.info.width)>=65)
    q=grid.info.origin.orientation
    yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
    r=np.array([[math.cos(yaw),-math.sin(yaw)],[math.sin(yaw),math.cos(yaw)]])
    xy=np.column_stack((cols+.5,rows+.5))*grid.info.resolution
    xy=xy@r.T+[grid.info.origin.position.x,grid.info.origin.position.y]
    assert len(xy)>80, robot+' needs more occupied observations'
    return xy

source,target = walls(source_robot),walls(reference_robot)
resolution=.05;size=1000;center=size//2
def raster(points):
    out=np.zeros((size,size),dtype=np.float32)
    c=np.rint(points/resolution).astype(int)+center
    valid=np.all((c>=0)&(c<size),axis=1);c=c[valid]
    out[c[:,1],c[:,0]]=1
    return cv2.GaussianBlur(out,(0,0),1.2)

reference=raster(target);tree=cKDTree(target)
seeds=[]
for degree in range(-180,180,5):
    angle=math.radians(degree);r=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    rotated=source@r.T
    score=fftconvolve(reference,raster(rotated)[::-1,::-1],mode='same')
    for _ in range(2):
        y,x=np.unravel_index(np.argmax(score),score.shape)
        shift=np.array([x-center,y-center])*resolution
        distance=tree.query(rotated+shift)[0]
        seeds.append((float(np.mean(distance<.18)),angle,shift))
        score[max(0,y-20):y+21,max(0,x-20):x+21]=0

fits=[]
for _,angle,shift in sorted(seeds,key=lambda v:-v[0])[:24]:
    r=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    t=shift.copy()
    for _ in range(30):
        p=source@r.T+t;d,index=tree.query(p);keep=d<.3
        if keep.sum()<30:break
        a,b=source[keep],target[index[keep]];ac,bc=a.mean(axis=0),b.mean(axis=0)
        u,_,vt=np.linalg.svd((a-ac).T@(b-bc));rr=vt.T@u.T
        if np.linalg.det(rr)<0:vt[-1]*=-1;rr=vt.T@u.T
        tt=bc-ac@rr.T
        delta=np.linalg.norm(tt-t)+np.linalg.norm(rr-r);r,t=rr,tt
        if delta<1e-6:break
    moved=source@r.T+t;d=tree.query(moved)[0];reverse=cKDTree(moved).query(target)[0]
    overlap=float(np.mean(d<.15));reverse_overlap=float(np.mean(reverse<.15))
    rms=float(np.sqrt(np.mean(d[d<.3]**2)))
    fit={'transform':[float(t[0]),float(t[1]),float(math.atan2(r[1,0],r[0,0]))],
         'source_overlap':overlap,'target_overlap':reverse_overlap,'rms_m':rms,
         'score':min(overlap,reverse_overlap)-rms}
    if not any(np.linalg.norm(np.array(f['transform'][:2])-t)<.2 and abs(math.atan2(math.sin(f['transform'][2]-fit['transform'][2]),math.cos(f['transform'][2]-fit['transform'][2])))<.08 for f in fits):fits.append(fit)
fits.sort(key=lambda f:-f['score'])
best=fits[0];margin=best['score']-fits[1]['score'] if len(fits)>1 else 1.
for fit in fits:
    angle=fit['transform'][2]
    rotation=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    fit['overlap_region']=overlap_region_metrics(source@rotation.T+fit['transform'][:2],target)
best['overlap_region_margin']=overlap_grid_margin(fits)
validated=min(best['source_overlap'],best['target_overlap'])>=.55 and best['rms_m']<.12 and margin>.05
result={'validated':validated,'method':'occupied-grid FFT yaw search and trimmed rigid ICP',
        'epochs':{r:connection_states(report)[r]['samples']['navigation']['value']['localization_epoch'] for r in (reference_robot,source_robot)},
        'transforms':{reference_robot:[0.,0.,0.],source_robot:best['transform']},'best':best,'distinct_candidate_margin':margin,
        'wall_samples':{source_robot:len(source),reference_robot:len(target)},'candidates':fits[:8]}
(data/'alignment/map-registration.json').write_text(json.dumps(result,indent=2))
# The 2D result is only a candidate; the 3D validator owns the committed transform.
print(json.dumps(result,indent=2))
