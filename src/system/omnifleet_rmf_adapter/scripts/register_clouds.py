import json
import os
from omnifleet_rmf_adapter.state import connection_states
from omnifleet_rmf_adapter.cloud_quality import cloud_xyz,point_xyz
from omnifleet_rmf_adapter.registration import registration_pair,run_stage
from omnifleet_rmf_adapter.alignment_validation import independently_corroborated
import math
from pathlib import Path
import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import PointCloud2

data=Path(os.environ['OMNIFLEET_DATA'])
source_robot,reference_robot=registration_pair(json.loads(Path(os.environ['OMNIFLEET_CONFIG']).read_text()))
folder=data/'alignment'
state=connection_states(json.loads((data/'connection_status.json').read_text()))
def cloud(robot,kind='raw'):
    suffix='-keyframe' if kind=='keyframes' else ''
    msg=deserialize_message((folder/(robot+suffix+'-cloud.cdr')).read_bytes(),PointCloud2)
    capture=json.loads((folder/(robot+suffix+'-capture.json')).read_text())
    assert capture['epoch']==state[robot]['samples']['navigation']['value']['localization_epoch']
    pose=capture['pose']
    if kind=='keyframes':
        assert msg.header.frame_id=='map'
        xyz=point_xyz(msg);radius=np.linalg.norm(xyz[:,:2]-[pose['x'],pose['y']],axis=1)
        xyz=xyz[(radius>.5)&(radius<18)&(xyz[:,2]>-.8)&(xyz[:,2]<2.8)]
    else:
        assert msg.header.frame_id=='rslidar'
        xyz=cloud_xyz(msg);xyz += [-.041,0.,.15]
        yaw=pose['yaw'];r=np.array([[math.cos(yaw),-math.sin(yaw),0],[math.sin(yaw),math.cos(yaw),0],[0,0,1]])
        xyz=xyz@r.T+[pose['x'],pose['y'],0]
    p=o3d.geometry.PointCloud(o3d.utility.Vector3dVector(xyz)).voxel_down_sample(.08)
    p.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=.3,max_nn=30))
    return p

def register_pair(source,target):
    reg=o3d.pipelines.registration
    def feature(p):
        d=p.voxel_down_sample(.2);d.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=.5,max_nn=40))
        return d,reg.compute_fpfh_feature(d,o3d.geometry.KDTreeSearchParamHybrid(radius=1.,max_nn=80))
    s,sf=feature(source);t,tf=feature(target)
    seeds=[]
    for item in json.loads((folder/'map-registration.json').read_text())['candidates']:
        x,y,a=item['transform'];m=np.eye(4);m[:2,:2]=[[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]];m[:2,3]=[x,y];seeds.append(m)
    for seed in range(3):
        if hasattr(o3d.utility,'random'):o3d.utility.random.seed(seed)
        result=reg.registration_ransac_based_on_feature_matching(s,t,sf,tf,True,.3,reg.TransformationEstimationPointToPoint(False),3,
            [reg.CorrespondenceCheckerBasedOnEdgeLength(.9),reg.CorrespondenceCheckerBasedOnDistance(.3)],reg.RANSACConvergenceCriteria(50000,.999))
        seeds.append(result.transformation)
    
    fits=[]
    for initial in seeds:
        result=reg.registration_icp(source,target,.25,initial,reg.TransformationEstimationPointToPlane(),reg.ICPConvergenceCriteria(max_iteration=80))
        m=result.transformation
        # Floor-level map alignment is planar; reject flipped or tilted solutions.
        if m[2,2]<.98 or abs(m[2,3])>.2:continue
        p=np.asarray(source.points)@m[:3,:3].T+m[:3,3]
        d=cKDTree(np.asarray(target.points)).query(p)[0]
        reverse=cKDTree(p).query(np.asarray(target.points))[0]
        valid=d<.15;reversed_valid=reverse<.15
        fit={'transform':[float(m[0,3]),float(m[1,3]),float(math.atan2(m[1,0],m[0,0]))],
             'fitness':float(np.mean(valid)),'reverse_fitness':float(np.mean(reversed_valid)),
             'inlier_rmse_m':float(np.sqrt(np.mean(d[valid]**2))) if valid.any() else 999.,
             'full_transform':m.tolist()}
        fit['score']=min(fit['fitness'],fit['reverse_fitness'])-fit['inlier_rmse_m']
        if not any(np.linalg.norm(np.array(f['transform'][:2])-m[:2,3])<.2 and abs(math.atan2(math.sin(f['transform'][2]-fit['transform'][2]),math.cos(f['transform'][2]-fit['transform'][2])))<.08 for f in fits):fits.append(fit)
    fits.sort(key=lambda f:-f['score'])
    assert fits,'No planar point cloud match'
    return fits

def check(source,target,fits):
    from omnifleet_rmf_adapter.alignment_validation import validate_projection
    return validate_projection(np.asarray(source.points),np.asarray(target.points),fits)

keyframes=all((folder/(robot+'-keyframe-capture.json')).exists() for robot in (source_robot,reference_robot))
raw_current=all((folder/(robot+'-capture.json')).exists() and
                json.loads((folder/(robot+'-capture.json')).read_text()).get('capture_kind')=='current_raw_lidar' and
                json.loads((folder/(robot+'-capture.json')).read_text()).get('epoch')==state[robot]['samples']['navigation']['value']['localization_epoch']
                for robot in (source_robot,reference_robot))
initial_kind='raw' if raw_current else 'keyframes' if keyframes else 'raw'
source,target=cloud(source_robot,initial_kind),cloud(reference_robot,initial_kind)
fits=register_pair(source,target);best,margin,validated=check(source,target,fits)
map_result=json.loads((folder/'map-registration.json').read_text())
corroborated=independently_corroborated(best,margin,map_result)
validated=validated or corroborated
raw_attempt={'validated':validated,'best':best,'distinct_candidate_margin':margin}
method=('current MOLA keyframe map' if initial_kind=='keyframes' else 'current raw LiDAR')+' FPFH/RANSAC and point-to-plane ICP, checked bidirectionally in 3D and in the XY navigation projection'
if not validated and initial_kind!='keyframes':
    if not keyframes:run_stage(Path(__file__).parent/'capture_keyframe_maps.py',timeout=130.)
    source,target=cloud(source_robot,'keyframes'),cloud(reference_robot,'keyframes')
    fits=register_pair(source,target);best,margin,validated=check(source,target,fits)
    corroborated=independently_corroborated(best,margin,map_result)
    validated=validated or corroborated
    method='current MOLA keyframe map FPFH/RANSAC and point-to-plane ICP, checked bidirectionally in 3D and in the XY navigation projection'
result={'validated':validated,'method':method,'raw_attempt':raw_attempt,
        'validation_basis':'independent_map_and_cloud_agreement' if corroborated else 'bidirectional_cloud_overlap',
        'epochs':{r:state[r]['samples']['navigation']['value']['localization_epoch'] for r in (reference_robot,source_robot)},
        'transforms':{reference_robot:[0.,0.,0.],source_robot:best['transform']},'best':best,
        'distinct_candidate_margin':margin,'points':{source_robot:len(source.points),reference_robot:len(target.points)},'candidates':fits}
(folder/'cloud-registration.json').write_text(json.dumps(result,indent=2))
o3d.io.write_point_cloud(str(folder/(source_robot+'-map.ply')),source)
o3d.io.write_point_cloud(str(folder/(reference_robot+'-map.ply')),target)
print(json.dumps(result,indent=2))
