"""Fuse registered occupancy grids in the fleet coordinate frame."""
from array import array
import copy
import math

import numpy as np
from scipy.ndimage import affine_transform


def merge_grids(maps, transforms):
    sources = []
    for robot, grid in maps.items():
        x, y, yaw = transforms[robot]
        p, q = grid.info.origin.position, grid.info.origin.orientation
        c, s = math.cos(yaw), math.sin(yaw)
        origin = (x+c*p.x-s*p.y, y+s*p.x+c*p.y)
        angle = yaw+math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
        sources.append((robot, grid, origin, angle))
    resolution = min(g.info.resolution for _, g, _, _ in sources)
    corners = []
    for _, grid, (x, y), angle in sources:
        c, s = math.cos(angle), math.sin(angle)
        for dx in (0., grid.info.width*grid.info.resolution):
            for dy in (0., grid.info.height*grid.info.resolution):
                corners.append((x+c*dx-s*dy, y+s*dx+c*dy))
    # Keep the reference grid's lattice instead of shifting it by a fraction of a cell.
    base_x, base_y = sources[0][2]
    left = math.floor((min(x for x, _ in corners)-base_x)/resolution+1e-9)
    bottom = math.floor((min(y for _, y in corners)-base_y)/resolution+1e-9)
    right = math.ceil((max(x for x, _ in corners)-base_x)/resolution-1e-9)
    top = math.ceil((max(y for _, y in corners)-base_y)/resolution-1e-9)
    min_x, min_y = base_x+left*resolution, base_y+bottom*resolution
    merged = np.full((top-bottom, right-left), -1, dtype=np.int16)
    added = {}
    for robot, grid, (x, y), angle in sources:
        c, s = math.cos(angle), math.sin(angle)
        scale = resolution/grid.info.resolution
        dx, dy = min_x+resolution*.5-x, min_y+resolution*.5-y
        sampled = affine_transform(
            np.asarray(grid.data, dtype=np.int16).reshape(grid.info.height, grid.info.width),
            [[c*scale, -s*scale], [s*scale, c*scale]],
            offset=[(-s*dx+c*dy)/grid.info.resolution-.5,
                    (c*dx+s*dy)/grid.info.resolution-.5],
            output_shape=merged.shape, order=0, mode='grid-constant', cval=-1, prefilter=False)
        added[robot] = int(np.count_nonzero((merged < 0) & (sampled >= 0)))
        np.maximum(merged, sampled, out=merged)
    result = copy.deepcopy(sources[0][1])
    result.header.frame_id = 'fleet_map'
    result.info.resolution = resolution
    result.info.height, result.info.width = merged.shape
    result.info.origin.position.x, result.info.origin.position.y = min_x, min_y
    result.info.origin.position.z = 0.
    q = result.info.origin.orientation
    q.x, q.y, q.z, q.w = 0., 0., 0., 1.
    result.data = array('b', merged.astype(np.int8).tobytes())
    return result, {'contributors': list(maps), 'added_known_cells': added,
                    'known_cells': int(np.count_nonzero(merged >= 0)),
                    'occupied_cells': int(np.count_nonzero(merged == 100)),
                    'width': result.info.width, 'height': result.info.height,
                    'resolution': resolution, 'origin': [min_x, min_y]}
