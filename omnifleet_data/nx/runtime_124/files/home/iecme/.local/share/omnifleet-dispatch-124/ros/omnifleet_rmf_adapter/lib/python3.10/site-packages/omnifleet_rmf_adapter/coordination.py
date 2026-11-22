"""Grid and timing utilities shared by navigation preflight and regression tests."""
from datetime import datetime
import heapq
import math

import numpy as np
from scipy.ndimage import distance_transform_edt
from rmf_adapter import geometry, graph, plan, vehicletraits

from .map_hub import compose, inverse


def grid_path(grid, start, goal, radius=.39):
    cells = np.asarray(grid.data, dtype=np.int8).reshape(grid.info.height, grid.info.width)
    free = distance_transform_edt((cells >= 0) & (cells < 65)) * grid.info.resolution > radius
    p, q = grid.info.origin.position, grid.info.origin.orientation
    origin = [p.x, p.y, math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))]
    def cell(pose):
        x, y, _ = compose(inverse(origin), pose)
        return math.floor(x/grid.info.resolution), math.floor(y/grid.info.resolution)
    def valid(c):
        return 0 <= c[0] < grid.info.width and 0 <= c[1] < grid.info.height and free[c[1], c[0]]
    a, b = cell(start), cell(goal)
    if not valid(a) or not valid(b):
        raise ValueError('Navigation endpoint or current body footprint intersects unknown/occupied space')
    pending, cost, previous = [(0., a)], {a: 0.}, {}
    while pending and len(cost) < 100000:
        _, current = heapq.heappop(pending)
        if current == b:
            route = [current]
            while route[-1] != a:
                route.append(previous[route[-1]])
            route.reverse()
            points = [compose(origin, [(x+.5)*grid.info.resolution, (y+.5)*grid.info.resolution, 0.]) for x, y in route]
            points[0], points[-1] = list(start), list(goal)
            return points
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nxt = current[0]+dx, current[1]+dy
            if not valid(nxt) or not valid((current[0]+dx,current[1])) or not valid((current[0],current[1]+dy)):
                continue
            candidate = cost[current] + math.hypot(dx, dy)
            if candidate < cost.get(nxt, float('inf')):
                cost[nxt] = candidate
                previous[nxt] = current
                heapq.heappush(pending, (candidate+math.dist(nxt,b), nxt))
    raise ValueError('No collision-free route in the current vehicle map')


def rmf_timing(points, now):
    g = graph.Graph()
    locations = [points[0]]
    for point in points[1:]:
        if math.dist(point[:2],locations[-1][:2]) > 1e-6: locations.append(point)
    for point in locations:
        g.add_waypoint('fleet_map', point[:2])
    for i in range(len(locations)-1):
        g.add_bidir_lane(i, i+1)
    profile = vehicletraits.Profile(geometry.make_final_convex_circle(.39), geometry.make_final_convex_circle(.49))
    traits = vehicletraits.VehicleTraits(vehicletraits.Limits(.08,.1), vehicletraits.Limits(.2,.2), profile)
    traits.differential.reversible = True
    planner = plan.Planner(plan.Configuration(g, traits))
    result = planner.get_plan_waypoints(plan.Start(now, 0, points[0][2]), plan.Goal(len(locations)-1,float(points[-1][2])))
    if not result:
        raise ValueError('Open-RMF could not time the checked formation route')
    return [{'pose': [float(v) for v in w.position], 'time': w.time.isoformat()} for w in result]


def timed_separation(first, second):
    def samples(path):
        return [(datetime.fromisoformat(w['time']).timestamp(),w['pose']) for w in path]
    a,b = samples(first),samples(second)
    def at(path, stamp):
        if stamp <= path[0][0]: return path[0][1]
        for (ta,pa),(tb,pb) in zip(path,path[1:]):
            if stamp <= tb:
                f=(stamp-ta)/(tb-ta) if tb>ta else 1.
                return [pa[i]+f*(pb[i]-pa[i]) for i in range(2)]
        return path[-1][1]
    start,stop=min(a[0][0],b[0][0]),max(a[-1][0],b[-1][0])
    return min(math.dist(at(a,t)[:2],at(b,t)[:2]) for t in np.linspace(start,stop,max(2,math.ceil((stop-start)/.2))))
