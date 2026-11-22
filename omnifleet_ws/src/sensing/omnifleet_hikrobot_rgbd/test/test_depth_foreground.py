import numpy as np
import cv2
import pytest
from omnifleet_hikrobot_rgbd.depth_foreground import depth_foreground,foreground_frame


KD=np.array([[200.,0,160.],[0,200.,120.],[0,0,1.]])
KR=np.array([[400.,0,320.],[0,400.,240.],[0,0,1.]])
T=np.eye(4)
BOX=[160,100,280,260]


def scene():
    value=np.full((240,320),3000,np.uint16)
    value[70:150,100:180]=1500
    return value


def segment(depth,box=BOX,**kwargs):
    return depth_foreground(depth,box,(640,480),KD,KR,T,**kwargs)


def test_separates_foreground_and_returns_measured_depth():
    depth=scene();original=depth.copy()
    result=segment(depth,seed_rgb=(280,220))
    assert result['depth_m']==pytest.approx(1.5)
    assert result['depth_sample_count']<=256
    assert np.all(result['native_mm']==1500)
    assert np.array_equal(depth,original)
    x,y,w,h=result['bbox_xywh']
    assert 194<=x<=206 and 134<=y<=146
    assert 148<=w<=172 and 148<=h<=172


def test_same_depth_distractor_is_not_the_seed_component():
    depth=scene();depth[70:150,220:260]=1500
    result=segment(depth,[160,100,400,260],seed_rgb=(280,220))
    x,y,w,h=result['bbox_xywh']
    assert x+w<400


def test_holes_are_not_fabricated_depth_samples():
    depth=scene();depth[100:115,135:150]=0
    result=segment(depth,seed_rgb=(280,220))
    assert result is not None
    uv=result['native_uv']
    assert np.all(depth[uv[:,1],uv[:,0]]>0)
    assert np.all(result['native_mm']==depth[uv[:,1],uv[:,0]])


def test_global_reference_band_limits_neighbor_chain_leakage():
    depth=np.tile((1000+np.arange(320)*8).astype(np.uint16),(240,1))
    result=depth_foreground(depth,[40,40,220,100],(320,240),KD,KD,T,
                            seed_rgb=(80,80),max_reference_diff_mm=250)
    seed_depth=depth[80,80]*.001
    assert np.max(np.abs(result['sampled_depth_m']-seed_depth))<=.251
    assert result['foreground_grid_pixels']<result['projected_grid_pixels']/2


def test_existing_person_letterbox_mask_separates_same_depth_background():
    depth=np.full((240,320),2000,np.uint16)
    mask=np.zeros((512,512),bool)
    mask[176:304,160:288]=True  # RGB[200:360,140:300] at gain0.8 + top64
    result=segment(depth,semantic_mask=mask)
    assert result['semantic_used']
    x,y,w,h=result['bbox_xywh']
    assert x>=194 and x+w<=366 and y>=134 and y+h<=306


def test_factory_transform_is_used_instead_of_resolution_only_scaling():
    transform=T.copy();transform[0,3]=.05
    result=depth_foreground(scene(),BOX,(640,480),KD,KR,transform,seed_rgb=(293,220))
    assert result['bbox_xywh'][0]>208
    assert result['depth_m']==pytest.approx(1.5)


def test_rgb_optical_depth_contains_the_extrinsic_z_translation():
    transform=T.copy();transform[2,3]=.1
    result=depth_foreground(scene(),BOX,(640,480),KD,KR,transform)
    assert result['depth_m']==pytest.approx(1.6)


def test_empty_depth_and_empty_semantics_return_no_measurement():
    assert segment(np.zeros((240,320),np.uint16)) is None
    assert segment(scene(),semantic_mask=np.zeros((512,512),bool)) is None


def test_small_grid_is_bounded_for_full_size_camera():
    depth=np.full((800,1280),2000,np.uint16)
    kd=np.array([[900.,0,640],[0,900.,400],[0,0,1.]])
    kr=np.array([[1371.,0,960],[0,1371.,540],[0,0,1.]])
    result=depth_foreground(depth,[200,100,1400,800],(1920,1080),kd,kr,T)
    assert result['projected_grid_pixels']<=128*128
    assert max(result['mask_roi'].shape)<=128
    assert result['depth_sample_count']<=16*16


def test_foreground_conditioned_tracker_image_preserves_source_and_object():
    result=segment(scene(),seed_rgb=(280,220))
    image=np.full((480,640,3),(40,80,180),np.uint8);original=image.copy()
    prepared=foreground_frame(image,result)
    assert np.array_equal(image,original)
    assert np.array_equal(prepared[220,280],image[220,280])
    assert np.array_equal(prepared[0,0],[127,127,127])


def test_distortion_path_keeps_native_measurements():
    result=segment(scene(),rgb_distortion=np.zeros(5))
    assert result['depth_m']==pytest.approx(1.5)
    assert np.all(result['native_mm']==1500)
