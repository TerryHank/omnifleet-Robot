import numpy as np
import pytest
import cv2
from omnifleet_hikrobot_rgbd.aligned_depth import aligned_depth_foreground
from omnifleet_hikrobot_rgbd.foreground_tracking import ForegroundQuery

K=np.array([[500.,0,320.],[0,500.,240.],[0,0,1.]])

def scene():
    depth=np.full((480,640),3000,np.uint16)
    depth[140:340,220:420]=1200
    return depth

def test_direct_samples_are_real_and_reject_background_and_holes():
    depth=scene();depth[210:250,300:340]=0;before=depth.copy()
    result=aligned_depth_foreground(depth,[170,90,300,300],(640,480),K)
    assert result['depth_m']==pytest.approx(1.2)
    assert result['depth_sample_count']<=256
    assert result['projected_grid_pixels']==256
    assert np.array_equal(depth,before)
    assert np.all(result['native_mm']==1200)
    uv=result['native_uv'];assert np.array_equal(result['native_mm'],depth[uv[:,1],uv[:,0]])
    assert abs(result['rgb_xyz_m'][0])<.1 and abs(result['rgb_xyz_m'][1])<.1

def test_mask_maps_rgb_pixels_without_extrinsic_projection():
    depth=scene();mask=np.zeros((480,640),bool);mask[140:340,220:420]=True
    q=ForegroundQuery(.2,3.5);q.depth=depth;q.depth_k=K;q.rgb_k=K
    q.transform=np.eye(4);q.transform[0,3]=10. # Must be ignored for registered data.
    q.rgb_size=(640,480);q.depth_is_aligned=True
    q.projector=lambda *args:pytest.fail('Aligned depth must not call the point projector')
    result=q.query([170,90,300,300],mask)
    assert result['depth_m']==pytest.approx(1.2)
    assert result['projection_backend']=='aligned_depth_direct'
    assert q.describe(result)['sampled_count']<=256

def test_no_depth_or_outside_roi_never_fabricates_a_measurement():
    assert aligned_depth_foreground(np.zeros((480,640),np.uint16),[100,100,50,50],(640,480),K) is None
    assert aligned_depth_foreground(scene(),[700,100,50,50],(640,480),K) is None
    with pytest.raises(ValueError):aligned_depth_foreground(scene()[:400],[100,100,50,50],(640,480),K)


def test_raw_rgb_lens_coordinates_are_batch_mapped_to_ideal_aligned_depth():
    depth=np.full((480,640),1500,np.uint16);d=np.array([.1,0,0,0,0.])
    result=aligned_depth_foreground(depth,[20,30,180,180],(640,480),K,rgb_distortion=d)
    u,v=np.meshgrid(20+(np.arange(16)+.5)*180/16,30+(np.arange(16)+.5)*180/16)
    expected=cv2.undistortPoints(np.stack([u,v],axis=-1).reshape(-1,1,2),K,d,P=K).reshape(-1,2).astype(int)
    assert np.array_equal(result['native_uv'],expected)
    assert result['depth_m']==pytest.approx(1.5)
