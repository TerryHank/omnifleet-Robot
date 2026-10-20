import math

import numpy as np


TERRAIN_LAYERS = (
    "elevation",
    "slope",
    "roughness",
    "step_height",
    "traversability",
)


def _fill_small_holes(elevation, valid, allowed, iterations):
    """Only interpolate cells surrounded by measured terrain."""

    filled = elevation.copy()
    known = valid.copy()
    for _ in range(max(0, int(iterations))):
        total = np.zeros_like(filled, dtype=np.float64)
        count = np.zeros_like(filled, dtype=np.uint8)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                src_y = slice(max(0, -dy), filled.shape[0] - max(0, dy))
                src_x = slice(max(0, -dx), filled.shape[1] - max(0, dx))
                dst_y = slice(max(0, dy), filled.shape[0] - max(0, -dy))
                dst_x = slice(max(0, dx), filled.shape[1] - max(0, -dx))
                neighbor_valid = known[src_y, src_x]
                total[dst_y, dst_x] += np.where(
                    neighbor_valid, filled[src_y, src_x], 0.0
                )
                count[dst_y, dst_x] += neighbor_valid.astype(np.uint8)
        update = (~known) & allowed & (count >= 3)
        if not np.any(update):
            break
        filled[update] = (total[update] / count[update]).astype(np.float32)
        known[update] = True
    return filled, known


def _neighbor_metrics(elevation, valid, resolution):
    step = np.zeros_like(elevation, dtype=np.float32)
    gradient = np.zeros_like(elevation, dtype=np.float32)
    neighbors = np.zeros_like(elevation, dtype=np.uint8)

    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
        src_y = slice(max(0, -dy), elevation.shape[0] - max(0, dy))
        src_x = slice(max(0, -dx), elevation.shape[1] - max(0, dx))
        dst_y = slice(max(0, dy), elevation.shape[0] - max(0, -dy))
        dst_x = slice(max(0, dx), elevation.shape[1] - max(0, -dx))
        pair_valid = valid[src_y, src_x] & valid[dst_y, dst_x]
        difference = np.zeros_like(elevation[src_y, src_x], dtype=np.float32)
        np.subtract(
            elevation[src_y, src_x],
            elevation[dst_y, dst_x],
            out=difference,
            where=pair_valid,
        )
        np.abs(difference, out=difference)
        distance = resolution * math.hypot(dx, dy)
        pair_step = np.where(pair_valid, difference, 0.0)
        pair_gradient = pair_step / distance

        np.maximum(step[src_y, src_x], pair_step, out=step[src_y, src_x])
        np.maximum(step[dst_y, dst_x], pair_step, out=step[dst_y, dst_x])
        np.maximum(
            gradient[src_y, src_x], pair_gradient, out=gradient[src_y, src_x]
        )
        np.maximum(
            gradient[dst_y, dst_x], pair_gradient, out=gradient[dst_y, dst_x]
        )
        neighbors[src_y, src_x] += pair_valid.astype(np.uint8)
        neighbors[dst_y, dst_x] += pair_valid.astype(np.uint8)

    slope = np.degrees(np.arctan(gradient)).astype(np.float32)
    metrics_valid = valid & (neighbors > 0)
    return slope, step, metrics_valid


def analyze_terrain(
    points,
    *,
    width,
    height,
    resolution,
    origin_x,
    origin_y,
    origin_yaw=0.0,
    static_occupancy=None,
    min_points_per_cell=1,
    ground_band=0.12,
    hole_fill_iterations=2,
    max_slope_deg=15.0,
    max_roughness=0.05,
    max_step_height=0.10,
):
    """Convert map-frame XYZ samples into five 2.5D layers and Nav2 costs."""

    width = int(width)
    height = int(height)
    resolution = float(resolution)
    if width <= 0 or height <= 0 or resolution <= 0.0:
        raise ValueError("invalid terrain grid geometry")
    points = np.asarray(points, dtype=np.float32)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points must be an Nx3 array")

    allowed = np.ones((height, width), dtype=bool)
    if static_occupancy is not None:
        static = np.asarray(static_occupancy).reshape(height, width)
        allowed = static == 0

    finite = np.all(np.isfinite(points), axis=1)
    points = points[finite]
    if len(points) == 0:
        unknown = np.full((height, width), np.nan, dtype=np.float32)
        return {name: unknown.copy() for name in TERRAIN_LAYERS}, np.full(
            (height, width), -1, dtype=np.int8
        )

    dx = points[:, 0] - float(origin_x)
    dy = points[:, 1] - float(origin_y)
    cosine = math.cos(float(origin_yaw))
    sine = math.sin(float(origin_yaw))
    local_x = cosine * dx + sine * dy
    local_y = -sine * dx + cosine * dy
    gx = np.floor(local_x / resolution).astype(np.int64)
    gy = np.floor(local_y / resolution).astype(np.int64)
    inside = (gx >= 0) & (gx < width) & (gy >= 0) & (gy < height)
    points = points[inside]
    gx = gx[inside]
    gy = gy[inside]
    if len(points) == 0:
        unknown = np.full((height, width), np.nan, dtype=np.float32)
        return {name: unknown.copy() for name in TERRAIN_LAYERS}, np.full(
            (height, width), -1, dtype=np.int8
        )

    flat = gy * width + gx
    cells = width * height
    minimum = np.full(cells, np.inf, dtype=np.float32)
    np.minimum.at(minimum, flat, points[:, 2])

    near_ground = points[:, 2] <= minimum[flat] + float(ground_band)
    ground_flat = flat[near_ground]
    ground_z = points[near_ground, 2].astype(np.float64)
    count = np.bincount(ground_flat, minlength=cells)
    total = np.bincount(ground_flat, weights=ground_z, minlength=cells)
    squared = np.bincount(
        ground_flat, weights=ground_z * ground_z, minlength=cells
    )

    measured = (count >= int(min_points_per_cell)).reshape(height, width)
    measured &= allowed
    elevation = minimum.reshape(height, width)
    elevation, terrain_valid = _fill_small_holes(
        elevation, measured, allowed, hole_fill_iterations
    )

    roughness = np.zeros(cells, dtype=np.float32)
    populated = count > 0
    mean = np.zeros(cells, dtype=np.float64)
    mean[populated] = total[populated] / count[populated]
    variance = np.zeros(cells, dtype=np.float64)
    variance[populated] = (
        squared[populated] / count[populated] - mean[populated] ** 2
    )
    roughness[populated] = np.sqrt(np.maximum(variance[populated], 0.0))
    roughness = roughness.reshape(height, width)

    slope, step_height, metrics_valid = _neighbor_metrics(
        elevation, terrain_valid, resolution
    )
    valid = terrain_valid & metrics_valid & allowed

    slope_ratio = slope / max(float(max_slope_deg), 1e-6)
    roughness_ratio = roughness / max(float(max_roughness), 1e-6)
    step_ratio = step_height / max(float(max_step_height), 1e-6)
    risk = np.maximum.reduce((slope_ratio, roughness_ratio, step_ratio))
    traversability = np.clip(1.0 - risk, 0.0, 1.0).astype(np.float32)
    lethal = (
        (slope > float(max_slope_deg))
        | (roughness > float(max_roughness))
        | (step_height > float(max_step_height))
    )

    cost = np.full((height, width), -1, dtype=np.int8)
    cost[valid] = np.rint(np.clip(risk[valid], 0.0, 1.0) * 99.0).astype(
        np.int8
    )
    cost[valid & lethal] = 100

    layers = {
        "elevation": elevation.astype(np.float32, copy=True),
        "slope": slope,
        "roughness": roughness.astype(np.float32, copy=True),
        "step_height": step_height,
        "traversability": traversability,
    }
    for layer in layers.values():
        layer[~valid] = np.nan
    return layers, cost
