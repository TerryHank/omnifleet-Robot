"""Validate the 3D registration and its separate planar navigation projection."""
import math

import numpy as np
from scipy.spatial import cKDTree, ConvexHull, QhullError

from .cloud_quality import registration_valid


def metrics(moved, target):
    distance = cKDTree(target).query(moved)[0]
    reverse = cKDTree(moved).query(target)[0]
    keep = distance < .15
    result = {'fitness': float(np.mean(keep)), 'reverse_fitness': float(np.mean(reverse < .15)),
              'inlier_rmse_m': float(np.sqrt(np.mean(distance[keep]**2))) if keep.any() else 999.}
    result['score'] = min(result['fitness'], result['reverse_fitness']) - result['inlier_rmse_m']
    return result


def overlap_region_metrics(moved, target):
    """Evaluate shared spatial support, including all unmatched points inside it.

    Hulls depend on map extent, not on nearest-neighbour inliers. This prevents
    unobserved rooms outside a contained map from lowering reverse coverage.
    """
    def inside(points, support):
        hull = ConvexHull(support)
        return np.all(points @ hull.equations[:, :-1].T + hull.equations[:, -1] <= 1e-8, axis=1)
    try:
        source_mask, target_mask = inside(moved, target), inside(target, moved)
    except (QhullError, ValueError):
        return None
    if not source_mask.any() or not target_mask.any():
        return None
    return {**metrics(moved[source_mask], target[target_mask]),
            'source_points': int(source_mask.sum()), 'target_points': int(target_mask.sum()),
            'source_fraction': float(source_mask.mean()), 'target_fraction': float(target_mask.mean())}


def overlap_grid_margin(fits):
    """Keep whole-source completeness when comparing contained-grid candidates."""
    def score(fit):
        region=fit.get('overlap_region')
        return min(fit['source_overlap'],region['fitness'],region['reverse_fitness'])-fit['rms_m'] if region else -math.inf
    best=score(fits[0])
    return best-max((score(f) for f in fits[1:]),default=best-1.) if math.isfinite(best) else None


def validate_projection(source, target, fits):
    candidates = []
    for fit in fits:
        matrix = np.asarray(fit['full_transform'])
        moved = source @ matrix[:3, :3].T + matrix[:3, 3]
        full = metrics(moved, target)
        full['overlap_region'] = overlap_region_metrics(moved, target)
        x, y, yaw = fit['transform']
        rotation = np.array([[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]])
        planar_moved = source[:, :2] @ rotation.T + [x, y]
        planar = metrics(planar_moved, target[:, :2])
        planar['overlap_region'] = overlap_region_metrics(planar_moved, target[:, :2])
        candidates.append({**fit, **full, 'planar_xy': planar})
    candidates.sort(key=lambda f: -f['score'])
    best = candidates[0]
    margin = best['score'] - max((f['score'] for f in candidates[1:]), default=best['score'] - 1.)
    validated = registration_valid(best, margin) and registration_valid(best['planar_xy'], margin)
    return best, margin, bool(validated)


def independently_corroborated(best, margin, map_result):
    """Accept partial-map containment only when two registration methods agree."""
    if not map_result.get('best'):
        return False
    cloud=np.asarray(best.get('transform',[]),dtype=float)
    grid=np.asarray(map_result['best'].get('transform',[]),dtype=float)
    if cloud.shape!=(3,) or grid.shape!=(3,) or not np.isfinite(cloud).all() or not np.isfinite(grid).all():
        return False
    xy=best.get('planar_xy',{})
    xy_region = xy.get('overlap_region')
    grid_region = map_result['best'].get('overlap_region')
    grid_region_margin = map_result['best'].get('overlap_region_margin',map_result.get('distinct_candidate_margin',0.))
    # Navigation support is planar. A 3D convex hull also contains historically
    # observed surfaces occluded in the smaller map; its reverse coverage is
    # diagnostic. Full-cloud coverage and residual checks remain below.
    region_valid = bool(xy_region and grid_region
                        and registration_valid(xy_region, margin)
                        and type(grid_region_margin) in (int,float)
                        and registration_valid(grid_region, grid_region_margin))
    map_reverse = max(map_result['best'].get('target_overlap', 0.), grid_region['reverse_fitness']) if region_valid else map_result['best'].get('target_overlap')
    map_margin = max(map_result.get('distinct_candidate_margin',0.),grid_region_margin) if region_valid else map_result.get('distinct_candidate_margin')
    yaw_error=abs(math.atan2(math.sin(cloud[2]-grid[2]),math.cos(cloud[2]-grid[2])))
    values=(best.get('fitness'),best.get('reverse_fitness'),best.get('inlier_rmse_m'),
            xy.get('fitness'),xy.get('reverse_fitness'),xy.get('inlier_rmse_m'),margin,
            map_result['best'].get('source_overlap'),map_reverse,
            map_result['best'].get('rms_m'),map_margin)
    return bool(all(type(value) in (int,float) and np.isfinite(value) for value in values) and (
        np.linalg.norm(cloud[:2]-grid[:2])<=.10 and yaw_error<=.04
        and best['fitness']>=.80 and best['reverse_fitness']>=.35 and best['inlier_rmse_m']<.08
        and xy['fitness']>=.90 and xy['reverse_fitness']>=.50 and xy['inlier_rmse_m']<.06
        and margin>.12 and map_result['best']['source_overlap']>=.50
        and map_reverse>=.49 and map_result['best']['rms_m']<.115
        and map_margin>.10))
