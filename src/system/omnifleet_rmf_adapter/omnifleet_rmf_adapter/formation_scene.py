"""Snapshot the shared environment without inserting formation members as static peers."""
import math
import numpy as np
from .map_hub import peer_grid,reported_peer_bounds
from .elastic_trajectory import model,transform

def footprint_cells(grid,origin,pose,footprint):
    from .map_hub import compose,inverse
    body=[compose(inverse(origin),transform(pose,[*v,0.]))[:2] for v in footprint]
    resolution=grid.info.resolution
    body=[[x/resolution,y/resolution] for x,y in body]
    axes=[(1.,0.),(0.,1.)]+[(a[1]-b[1],b[0]-a[0]) for a,b in zip(body,body[1:]+body[:1])]
    projections=[(min(x*nx+y*ny for x,y in body),max(x*nx+y*ny for x,y in body)) for nx,ny in axes]
    for y in range(max(0,math.floor(min(p[1] for p in body))),min(grid.info.height,math.floor(max(p[1] for p in body))+1)):
        for x in range(max(0,math.floor(min(p[0] for p in body))),min(grid.info.width,math.floor(max(p[0] for p in body))+1)):
            if all((x+.5)*nx+(y+.5)*ny+(abs(nx)+abs(ny))*.5>=lo and
                   (x+.5)*nx+(y+.5)*ny-(abs(nx)+abs(ny))*.5<=hi for (nx,ny),(lo,hi) in zip(axes,projections)):
                yield y*grid.info.width+x

def scene(maps,states,order,profiles,poses):
    grid=maps.merged_map
    if grid is None:raise ValueError('共享地图尚未收到')
    q,p=grid.info.origin.orientation,grid.info.origin.position
    origin=[p.x,p.y,math.atan2(2*q.w*q.z,1-2*q.z*q.z)]
    cells=np.asarray(grid.data).copy()
    # Bring native lethal observations into the joint scene, without copying
    # inflation or turning participating teammates into stationary obstacles.
    from .map_hub import compose,inverse
    for (robot,key),native in getattr(maps,'costmaps',{}).items():
        if robot not in order or not states.get(robot,{}).get('fresh',{}).get(key):continue
        alignment=maps.alignment[robot]
        peers=[(compose(inverse(alignment),p),radius,reported_peer_bounds(states.get(r,{})))
               for r,(p,radius) in maps.obstacles.items() if r in order]
        excluded=np.asarray(peer_grid(native,peers).data)==100
        indexes=np.flatnonzero((np.asarray(native.data)==100)&~excluded)
        q,p=native.info.origin.orientation,native.info.origin.position
        native_origin=compose(alignment,[p.x,p.y,math.atan2(2*q.w*q.z,1-2*q.z*q.z)])
        to_grid=compose(inverse(origin),native_origin);c,s=math.cos(to_grid[2]),math.sin(to_grid[2])
        x=(indexes%native.info.width+.5)*native.info.resolution
        y=(indexes//native.info.width+.5)*native.info.resolution
        peer=getattr(maps,'peer_maps',{}).get(robot)
        if peer is not None:
            q,p=peer.info.origin.orientation,peer.info.origin.position
            peer_origin=[p.x,p.y,math.atan2(2*q.w*q.z,1-2*q.z*q.z)]
            q,p=native.info.origin.orientation,native.info.origin.position
            relative=compose(inverse(peer_origin),[p.x,p.y,math.atan2(2*q.w*q.z,1-2*q.z*q.z)])
            pc,ps=math.cos(relative[2]),math.sin(relative[2])
            px=np.floor((relative[0]+pc*x-ps*y)/peer.info.resolution).astype(int)
            py=np.floor((relative[1]+ps*x+pc*y)/peer.info.resolution).astype(int)
            inside=(px>=0)&(py>=0)&(px<peer.info.width)&(py<peer.info.height)
            teammate=np.zeros(len(indexes),dtype=bool)
            teammate[inside]=np.asarray(peer.data)[py[inside]*peer.info.width+px[inside]]==100
            x,y=x[~teammate],y[~teammate]
        ix=np.floor((to_grid[0]+c*x-s*y)/grid.info.resolution).astype(int)
        iy=np.floor((to_grid[1]+s*x+c*y)/grid.info.resolution).astype(int)
        valid=(ix>=0)&(iy>=0)&(ix<grid.info.width)&(iy<grid.info.height)
        cells[iy[valid]*grid.info.width+ix[valid]]=100
    # Teammates also appear as laser returns in SLAM, not just in peer_map.
    # Clear only each known current body, as Nav2 footprint clearing does.
    # Joint planning still checks every member against every other member.
    for robot,profile,pose in zip(order,profiles,poses):
        footprint=model(robot,profile,pose,pose)['footprint']
        for index in footprint_cells(grid,origin,pose,footprint):cells[index]=0
    peers=[(pose,radius,reported_peer_bounds(states.get(robot,{})))
           for robot,(pose,radius) in maps.obstacles.items() if robot not in order]
    overlay=peer_grid(grid,peers)
    cells=np.maximum(cells,np.asarray(overlay.data)).tolist()
    return {'width':grid.info.width,'height':grid.info.height,'resolution':grid.info.resolution,
            'origin':origin,'data':cells,'allow_unknown':all(p.get('allow_unknown',False) for p in profiles)}
