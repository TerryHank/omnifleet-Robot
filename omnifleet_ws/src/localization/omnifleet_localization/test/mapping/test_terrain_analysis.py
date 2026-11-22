import numpy as np

from omnifleet_localization.terrain_analysis import TERRAIN_LAYERS, analyze_terrain


def grid_points(width, height, resolution, z_value):
    points = []
    for row in range(height):
        for column in range(width):
            z = z_value(column, row)
            points.append(
                ((column + 0.5) * resolution, (row + 0.5) * resolution, z)
            )
    return np.asarray(points, dtype=np.float32)


def analyze(points, width=6, height=6, resolution=0.1, **overrides):
    options = {
        "width": width,
        "height": height,
        "resolution": resolution,
        "origin_x": 0.0,
        "origin_y": 0.0,
        "static_occupancy": np.zeros(width * height, dtype=np.int8),
        "hole_fill_iterations": 0,
        "max_slope_deg": 15.0,
        "max_roughness": 0.05,
        "max_step_height": 0.10,
    }
    options.update(overrides)
    return analyze_terrain(points, **options)


def test_flat_surface_is_fully_traversable():
    points = grid_points(6, 6, 0.1, lambda _x, _y: 0.0)
    layers, cost = analyze(points)

    assert tuple(layers) == TERRAIN_LAYERS
    assert np.allclose(layers["elevation"], 0.0)
    assert np.allclose(layers["slope"], 0.0)
    assert np.allclose(layers["roughness"], 0.0)
    assert np.allclose(layers["step_height"], 0.0)
    assert np.allclose(layers["traversability"], 1.0)
    assert np.all(cost == 0)


def test_step_above_vehicle_limit_becomes_lethal():
    points = grid_points(6, 6, 0.1, lambda x, _y: 0.0 if x < 3 else 0.20)
    layers, cost = analyze(points)

    assert np.all(layers["step_height"][:, 2:4] >= 0.19)
    assert np.all(cost[:, 2:4] == 100)


def test_unmeasured_cells_remain_unknown():
    points = grid_points(2, 2, 0.1, lambda _x, _y: 0.0)
    layers, cost = analyze(points, width=6, height=6)

    assert np.count_nonzero(np.isfinite(layers["elevation"])) == 4
    assert np.all(cost[3:, 3:] == -1)
