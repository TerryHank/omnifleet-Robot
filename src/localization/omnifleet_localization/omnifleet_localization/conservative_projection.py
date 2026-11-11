"""ROS-independent conservative ray selection for a 3D-to-2D map."""

import math
from collections import defaultdict

import numpy as np

from .occupancy_evidence import bresenham_free_cells


def point_cells(points, resolution):
    """Return integer XY cells for an Nx3 point array."""
    points = np.asarray(points)
    if len(points) == 0:
        return np.empty((0, 2), dtype=np.int64)
    return np.floor(points[:, :2] / float(resolution)).astype(np.int64)


def mask_for_cells(points, resolution, cells):
    """Select points whose XY cell belongs to ``cells``."""
    selected = set(cells)
    if not selected or len(points) == 0:
        return np.zeros(len(points), dtype=bool)
    indices = point_cells(points, resolution)
    return np.fromiter(
        ((int(x), int(y)) in selected for x, y in indices),
        dtype=bool,
        count=len(indices),
    )


def obstacle_support_cells(
    xyz,
    obstacle_mask,
    relative_heights,
    intensities,
    resolution,
    neighborhood_radius=1,
    vertical_span_min=0.20,
    quality_intensity_min=1.0,
    structural_min_points=3,
):
    """Classify obstacle cells by local structure and return quality.

    A cell is structural when points in its small XY neighborhood span a
    meaningful vertical surface.  A non-structural cell is quality-supported
    only when the median return intensity in the same neighborhood is high
    enough.  Neither classification draws or inflates an obstacle by itself.
    """
    xyz = np.asarray(xyz)
    obstacle_mask = np.asarray(obstacle_mask, dtype=bool)
    relative_heights = np.asarray(relative_heights, dtype=np.float64)
    intensities = np.asarray(intensities, dtype=np.float64)
    useful = np.flatnonzero(obstacle_mask)
    if len(useful) == 0:
        return set(), set()

    grouped = defaultdict(list)
    cells = point_cells(xyz[useful], resolution)
    for index, cell in zip(useful, cells):
        grouped[(int(cell[0]), int(cell[1]))].append(
            (float(relative_heights[index]), float(intensities[index]))
        )

    radius = max(0, int(neighborhood_radius))
    strong = set()
    quality = set()
    for cell in grouped:
        values = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                values.extend(grouped.get((cell[0] + dx, cell[1] + dy), ()))
        if not values:
            continue
        heights = np.fromiter((value[0] for value in values), dtype=np.float64)
        returns = np.fromiter((value[1] for value in values), dtype=np.float64)
        if (
            len(values) >= max(1, int(structural_min_points))
            and float(np.ptp(heights)) >= float(vertical_span_min)
        ):
            strong.add(cell)
        if float(np.median(returns)) >= float(quality_intensity_min):
            quality.add(cell)
    return strong, quality


def bridge_small_obstacle_gaps(cells, max_gap_cells=2):
    """Fill only short gaps between observed obstacle endpoints.

    This is line closing, not dilation: no cell is added outside the segment
    joining two already occupied endpoints.
    """
    occupied = set(cells)
    gap = max(0, int(max_gap_cells))
    if gap < 2 or len(occupied) < 2:
        return occupied
    result = set(occupied)
    offsets = [
        (dx, dy)
        for dy in range(-gap, gap + 1)
        for dx in range(-gap, gap + 1)
        if (dx > 0 or (dx == 0 and dy > 0))
        and 1 < dx * dx + dy * dy <= gap * gap
    ]
    for cell in occupied:
        for dx, dy in offsets:
            target = (cell[0] + dx, cell[1] + dy)
            if target not in occupied:
                continue
            result.update(bresenham_free_cells(cell, target))
            result.add(target)
    return result


def expand_cells(cells, radius):
    """Expand cells for ray blocking only; callers must not render this set."""
    radius = max(0, int(radius))
    expanded = set()
    for x, y in cells:
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    expanded.add((x + dx, y + dy))
    return expanded


def clip_ray_at_guards(ray, guards, origin_cell):
    """Stop before the first protected wall cell without marking it free."""
    clipped = []
    for cell in ray:
        if cell != origin_cell and cell in guards:
            break
        clipped.append(cell)
    return clipped


def conservative_scan_segments(
    xyz,
    ground_mask,
    obstacle_mask,
    origin,
    resolution,
    angular_resolution_rad,
    range_min,
    range_max,
    wall_stop_margin,
):
    """Return occupied cells and de-duplicable free-ray grid segments."""
    useful = np.flatnonzero(ground_mask | obstacle_mask)
    if len(useful) == 0:
        return set(), []

    points = xyz[useful]
    delta = points[:, :2] - np.asarray(origin[:2], dtype=np.float32)
    ranges = np.linalg.norm(delta, axis=1)
    valid = (ranges >= range_min) & (ranges <= range_max)
    useful = useful[valid]
    delta = delta[valid]
    ranges = ranges[valid]
    if len(useful) == 0:
        return set(), []

    bins = np.floor(
        (np.arctan2(delta[:, 1], delta[:, 0]) + math.pi)
        / angular_resolution_rad
    ).astype(np.int32)
    grouped = defaultdict(list)
    for index, angle_bin, distance in zip(useful, bins, ranges):
        grouped[int(angle_bin)].append((int(index), float(distance)))

    origin_xy = np.asarray(origin[:2], dtype=np.float64)
    origin_cell = tuple(np.floor(origin_xy / resolution).astype(np.int64))
    occupied = set()
    segments = set()
    margin = max(0.0, float(wall_stop_margin))

    for values in grouped.values():
        obstacles = [value for value in values if obstacle_mask[value[0]]]
        if obstacles:
            index, distance = min(obstacles, key=lambda value: value[1])
            endpoint_xy = xyz[index, :2].astype(np.float64)
            endpoint_cell = tuple(np.floor(endpoint_xy / resolution).astype(np.int64))
            occupied.add(endpoint_cell)
            free_distance = max(0.0, distance - margin)
            if distance > 0.0 and free_distance >= range_min:
                free_xy = origin_xy + (endpoint_xy - origin_xy) * (
                    free_distance / distance
                )
                free_cell = tuple(np.floor(free_xy / resolution).astype(np.int64))
                if free_cell != endpoint_cell:
                    segments.add((origin_cell, free_cell))
            continue

        grounds = [value for value in values if ground_mask[value[0]]]
        if not grounds:
            continue
        index, _ = max(grounds, key=lambda value: value[1])
        endpoint_xy = xyz[index, :2].astype(np.float64)
        endpoint_cell = tuple(np.floor(endpoint_xy / resolution).astype(np.int64))
        segments.add((origin_cell, endpoint_cell))

    return occupied, segments


def rasterize_segment(segment):
    """Rasterize a free segment including its non-obstacle endpoint."""
    origin_cell, endpoint_cell = segment
    cells = bresenham_free_cells(origin_cell, endpoint_cell)
    cells.append(endpoint_cell)
    return cells
