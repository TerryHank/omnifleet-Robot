import math

import numpy as np

from omnifleet_localization.conservative_projection import (
    bridge_small_obstacle_gaps,
    clip_ray_at_guards,
    conservative_scan_segments,
    expand_cells,
    obstacle_support_cells,
    rasterize_segment,
)


def test_obstacle_is_preferred_over_nearer_ground_in_same_bin():
    xyz = np.asarray([[1.0, 0.0, 0.0], [2.0, 0.0, 0.3]], dtype=np.float32)
    occupied, segments = conservative_scan_segments(
        xyz,
        np.asarray([True, False]),
        np.asarray([False, True]),
        (0.0, 0.0, 0.0),
        0.1,
        math.radians(1.0),
        0.1,
        8.0,
        0.2,
    )
    assert occupied == {(20, 0)}
    assert segments
    assert all(cell[0] <= 18 for cell in rasterize_segment(next(iter(segments))))


def test_ground_uses_farthest_endpoint_when_no_obstacle_exists():
    xyz = np.asarray([[1.0, 0.0, 0.0], [3.0, 0.0, 0.0]], dtype=np.float32)
    occupied, segments = conservative_scan_segments(
        xyz,
        np.asarray([True, True]),
        np.asarray([False, False]),
        (0.0, 0.0, 0.0),
        0.1,
        math.radians(1.0),
        0.1,
        8.0,
        0.2,
    )
    assert not occupied
    assert segments == {((0, 0), (30, 0))}


def test_wall_guard_stops_neighboring_free_ray_without_becoming_a_wall():
    guards = expand_cells({(5, 0)}, 1)
    ray = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
    clipped = clip_ray_at_guards(ray, guards, (0, 0))
    assert clipped == [(0, 0), (1, 0), (2, 0), (3, 0)]
    assert guards == {(4, 0), (5, -1), (5, 0), (5, 1), (6, 0)}


def test_low_intensity_thin_returns_are_not_structural_or_quality_supported():
    xyz = np.asarray(
        [[1.00, 0.00, 0.32], [1.02, 0.00, 0.33], [1.04, 0.00, 0.34]],
        dtype=np.float32,
    )
    strong, quality = obstacle_support_cells(
        xyz,
        np.ones(3, dtype=bool),
        xyz[:, 2],
        np.zeros(3, dtype=np.float32),
        0.025,
        neighborhood_radius=1,
        vertical_span_min=0.20,
        quality_intensity_min=1.0,
    )
    assert not strong
    assert not quality


def test_vertical_wall_structure_is_supported_even_with_dark_returns():
    xyz = np.asarray(
        [[1.00, 0.00, 0.20], [1.00, 0.00, 0.55], [1.00, 0.00, 0.90]],
        dtype=np.float32,
    )
    strong, quality = obstacle_support_cells(
        xyz,
        np.ones(3, dtype=bool),
        xyz[:, 2],
        np.zeros(3, dtype=np.float32),
        0.025,
        neighborhood_radius=1,
        vertical_span_min=0.20,
        quality_intensity_min=1.0,
    )
    assert strong == {(40, 0)}
    assert not quality


def test_moderate_intensity_low_object_is_quality_supported():
    xyz = np.asarray([[1.0, 0.0, 0.15]], dtype=np.float32)
    strong, quality = obstacle_support_cells(
        xyz,
        np.ones(1, dtype=bool),
        xyz[:, 2],
        np.asarray([3.0], dtype=np.float32),
        0.025,
    )
    assert not strong
    assert quality == {(40, 0)}


def test_short_wall_gap_is_bridged_without_dilation():
    assert bridge_small_obstacle_gaps({(0, 0), (2, 0)}, 2) == {
        (0, 0),
        (1, 0),
        (2, 0),
    }
    assert bridge_small_obstacle_gaps({(0, 0), (3, 0)}, 2) == {
        (0, 0),
        (3, 0),
    }
