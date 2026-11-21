"""Prediction-first observation points and directional scans, adapted from TROS.

All legs are public Nav2 goals; this module never publishes velocity.
"""
import math
import numpy as np


def nearest_free(point, grid, radius=2.):
    if grid is None:
        return np.asarray(point[:2], float)
    info = grid.info
    q = info.origin.orientation
    yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
    rotation = np.array([[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]])
    origin = np.array([info.origin.position.x, info.origin.position.y])
    center = (np.asarray(point[:2])-origin) @ rotation / info.resolution
    extent = int(math.ceil(radius/info.resolution))
    x1, y1 = np.maximum(np.floor(center).astype(int)-extent, 0)
    x2, y2 = np.minimum(np.floor(center).astype(int)+extent+1, [info.width, info.height])
    if x2 <= x1 or y2 <= y1:
        return None
    costs = np.asarray(grid.data, dtype=np.int8).reshape(info.height, info.width)[y1:y2, x1:x2]
    y, x = np.nonzero((costs >= 0) & (costs < 50))
    if not len(x):
        return None
    cells = np.c_[x+x1+.5, y+y1+.5]
    distances = np.sum((cells-center)**2, axis=1)
    index = int(np.argmin(distances))
    if distances[index] > (radius/info.resolution)**2:
        return None
    return cells[index] * info.resolution @ rotation.T + origin


class SearchRecovery:
    def __init__(self, timeout=30., max_rounds=2):
        self.timeout, self.max_rounds = timeout, max_rounds
        self.episode = 0
        self.reset()

    def reset(self):
        self.phase, self.goal = 'OFF', None
        self.leg, self.round = 0, 0
        self.points = []

    @property
    def token(self):
        return ('search', self.episode, self.leg)

    def start(self, history, predicted, robot, grid, now, direction=1.):
        self.reset()
        self.episode += 1
        self.started, self.direction = now, direction
        last = np.asarray(history[-1][1][:2], float) if history else None
        self.center = last
        candidates = []
        if predicted is not None:
            candidates.append(('NAV_PREDICTED', predicted))
        candidates.extend(('NAV_LAST_KNOWN' if i == 0 else 'NAV_HISTORY', value)
                          for i, (_, value) in enumerate(reversed(history)))
        for phase, point in candidates:
            free = nearest_free(point, grid)
            if free is not None and all(np.linalg.norm(free-old[1]) > .5 for old in self.points):
                self.points.append((phase, free))
                if len(self.points) >= self.max_rounds:
                    break
        self._next_point(robot)

    def _next_point(self, robot):
        if self.points:
            self.phase, point = self.points.pop(0)
            self.round += 1
            target = self.center if self.center is not None else point
            delta = point-target if self.phase == 'NAV_PREDICTED' else target-point
            if np.linalg.norm(delta) < .05:
                delta = point-np.asarray(robot[:2])
            self.goal = [float(point[0]), float(point[1]), math.atan2(delta[1], delta[0])]
            self.leg += 1
        elif self.round == 0:
            self.round = 1
            self._scan(robot)
        else:
            self.phase, self.goal = 'EXHAUSTED', None

    def _scan(self, robot):
        self.phase = 'SCAN'
        self.scan_origin = list(robot)
        self.scan_step = 1
        self._scan_goal()

    def _scan_goal(self):
        self.goal = self.scan_origin[:2] + [self.scan_origin[2]+self.direction*self.scan_step*math.pi/2]
        self.leg += 1

    def update(self, robot, now, completed=False, failed=False):
        if self.phase in ('OFF', 'EXHAUSTED'):
            return self.goal
        if now-self.started >= self.timeout:
            self.phase, self.goal = 'EXHAUSTED', None
            return None
        distance = np.linalg.norm(np.asarray(robot[:2])-self.goal[:2])
        angle = abs(math.atan2(math.sin(robot[2]-self.goal[2]), math.cos(robot[2]-self.goal[2])))
        reached = distance <= .08 and angle <= .25
        if completed or failed or reached:
            if self.phase != 'SCAN':
                self._scan(robot)
            elif failed:
                self._next_point(robot)
            elif self.scan_step < 4:
                self.scan_step += 1
                self._scan_goal()
            else:
                self._next_point(robot)
        return self.goal
