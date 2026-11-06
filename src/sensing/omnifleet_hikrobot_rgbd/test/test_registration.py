import struct

import numpy as np
import pytest

from omnifleet_hikrobot_rgbd.camera_node import register_depth, rgb_chunk


def test_identity_preserves_depth_and_invalid_pixels():
    depth = np.array([[0, 500, 1000], [65535, 800, 1200]], dtype=np.uint16)
    result = register_depth(depth, np.eye(3), np.eye(3), np.eye(4), (3, 2))
    np.testing.assert_array_equal(result, [[0, 500, 1000], [0, 800, 1200]])


def test_metric_baseline_projects_to_one_pixel_at_one_metre():
    depth = np.zeros((3, 5), dtype=np.uint16)
    depth[1, 1] = 1000
    k = np.array([[100., 0., 0.], [0., 100., 0.], [0., 0., 1.]])
    transform = np.eye(4)
    transform[0, 3] = .01
    result = register_depth(depth, k, k, transform, (5, 3))
    assert result[1, 2] == 1000
    assert np.count_nonzero(result) == 1


def test_registered_depth_is_color_camera_z():
    depth = np.zeros((3, 3), dtype=np.uint16)
    depth[0, 0] = 1000
    transform = np.eye(4)
    transform[2, 3] = .1
    result = register_depth(depth, np.eye(3), np.eye(3), transform, (3, 3))
    assert result[0, 0] == 1100


def test_rgb_chunk_dimensions_and_planes():
    data = struct.pack('<8I', 0x02180021, 2, 1, 6, 0, 0, 0, 0) + bytes(range(6))
    assert rgb_chunk(data) == (bytes(range(6)), 2, 1)


@pytest.mark.parametrize('data', [bytes(4), struct.pack('<8I', 0x02180021, 2, 1, 6, 0, 0, 0, 0)])
def test_truncated_chunk_is_rejected(data):
    with pytest.raises(ValueError):
        rgb_chunk(data)
