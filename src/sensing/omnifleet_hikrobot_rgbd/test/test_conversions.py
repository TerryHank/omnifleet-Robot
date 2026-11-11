import numpy as np

from omnifleet_hikrobot_rgbd.camera_node import colorize_depth, depth_c16, planar_rgb_to_bgr, scaled_intrinsics


def test_planar_rgb_to_bgr():
    result = planar_rgb_to_bgr(bytes([1, 2, 3, 4, 5, 6]), 2, 1)
    assert result.tolist() == [[[5, 3, 1], [6, 4, 2]]]


def test_depth_c16():
    result = depth_c16(bytes([1, 0, 2, 1]), 2, 1)
    assert result.dtype == np.dtype("uint16")
    assert result.tolist() == [[1, 258]]


def test_scaled_intrinsics():
    assert scaled_intrinsics(100, 200, 50, 60, 1000, 500, 500, 250) == (50, 100, 25, 30)


def test_depth_visualization_preserves_metric_data_and_masks_invalid_samples():
    depth = np.array([[0, 200, 800, 1500, 65535]], dtype=np.uint16)
    original = depth.copy()
    result = colorize_depth(depth)
    assert result.shape == (1, 5, 3)
    assert result.dtype == np.uint8
    assert not result[0, 0].any() and not result[0, 4].any()
    assert result[0, 1:4].any()
    np.testing.assert_array_equal(depth, original)
