import numpy as np
import pytest
from omnifleet_hikrobot_rgbd.depth_query import rgb_pixel_to_depth, rgb_mask_to_depth

K = np.array([[100.,0.,50.],[0.,100.,50.],[0.,0.,1.]])


def test_rgb_pixel_uses_factory_baseline_instead_of_resolution_scaling():
    depth = np.zeros((100,100),np.uint16)
    depth[50,50] = 1000
    transform = np.eye(4)
    transform[0,3] = .1
    value = rgb_pixel_to_depth(depth,(60,50),K,K,transform)
    assert value['depth_uv'] == (50,50)
    assert value['raw_depth_mm'] == 1000
    np.testing.assert_allclose(value['rgb_xyz_m'],[.1,0.,1.])
    assert value['inspected_pixels'] < depth.size / 10


def test_rotation_translation_and_different_intrinsics_round_trip():
    depth = np.zeros((80,100),np.uint16)
    depth[45,30] = 850
    rgb_k = np.array([[200.,0.,100.],[0.,210.,80.],[0.,0.,1.]])
    angle = .06
    transform = np.eye(4)
    transform[:3,:3] = [[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]]
    transform[:3,3] = [.0267,-.00077,-.0026]
    native = np.linalg.inv(K) @ [30.,45.,1.] * .85
    expected = transform[:3,:3] @ native + transform[:3,3]
    pixel = rgb_k @ expected
    pixel = pixel[:2] / pixel[2]
    value = rgb_pixel_to_depth(depth,pixel,K,rgb_k,transform)
    assert value['depth_uv'] == (30,45)
    np.testing.assert_allclose(value['rgb_xyz_m'],expected,atol=1e-12)


def test_coincident_projections_return_visible_nearer_surface():
    depth = np.zeros((100,100),np.uint16)
    depth[50,50],depth[50,40] = 1000,500
    transform = np.eye(4)
    transform[0,3] = .1
    value = rgb_pixel_to_depth(depth,(60,50),K,K,transform)
    assert value['raw_depth_mm'] == 500
    assert value['depth_uv'] == (40,50)


def test_invalid_and_unobserved_pixels_do_not_invent_depth():
    depth = np.zeros((100,100),np.uint16)
    depth[50,50] = 65535
    assert rgb_pixel_to_depth(depth,(50,50),K,K,np.eye(4)) is None
    assert rgb_pixel_to_depth(depth,(5000,5000),K,K,np.eye(4)) is None
    assert rgb_pixel_to_depth(depth,(float('nan'),50),K,K,np.eye(4)) is None
    with pytest.raises(ValueError):
        rgb_pixel_to_depth(depth.astype(float),(50,50),K,K,np.eye(4))


def test_mask_grid_reads_at_most_256_raw_points_and_rejects_background_outliers():
    depth = np.full((32,32),1400,np.uint16)
    mask = np.zeros((32,32),bool)
    mask[8:24,8:24] = True
    depth[mask] = 1000
    depth[8:10,8:24] = 1400
    depth[12:14,12:14] = 0
    before = depth.copy()
    k = np.array([[100.,0,16],[0,100.,16],[0,0,1.]])
    value = rgb_mask_to_depth(depth,mask,[4,4,28,28],(32,32),k,k,np.eye(4))
    assert value['grid_size'] == 16 and value['sampled_count'] <= 256
    assert value['inlier_count'] <= value['mask_valid_count'] < value['sampled_count']
    assert value['depth_m'] == 1. and value['raw_depth_mm'] == 1000
    np.testing.assert_array_equal(depth,before)


def test_mask_sampling_projects_native_grid_with_factory_translation():
    depth = np.full((100,100),1000,np.uint16)
    mask = np.zeros((100,100),bool)
    mask[30:70,30:70] = True
    transform = np.eye(4)
    transform[0,3] = .1
    value = rgb_mask_to_depth(depth,mask,[30,30,70,70],(100,100),K,K,transform)
    u,v = value['depth_uv']
    assert mask[v,u+10]
    assert value['sampled_count'] <= 256 and value['depth_m'] == 1.
    assert -0.2 <= value['rgb_xyz_m'][0] <= .2


def test_mask_sampling_invalid_data_returns_none():
    assert rgb_mask_to_depth(np.zeros((100,100),np.uint16),np.ones((100,100),bool),
                             [20,20,80,80],(100,100),K,K,np.eye(4)) is None
    assert rgb_mask_to_depth(np.ones((100,100),np.uint16)*1000,np.zeros((100,100),bool),
                             [20,20,80,80],(100,100),K,K,np.eye(4)) is None
