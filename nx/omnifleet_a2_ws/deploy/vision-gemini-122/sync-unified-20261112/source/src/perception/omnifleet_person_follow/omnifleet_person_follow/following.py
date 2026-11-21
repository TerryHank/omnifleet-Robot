"""A fixed standoff goal, with measured-target smoothing and hold hysteresis."""
import math
import numpy as np


class ImageCentering:
    def __init__(self, start_angle=.12, stop_angle=.06):
        self.start_angle,self.stop_angle = start_angle,stop_angle
        self.token = 0
        self.reset()

    def reset(self):
        self.goal,self.spin_angle,self.error_rad = None,None,0.

    def update(self, robot, bbox, width, fx, completed=False):
        pixel = (bbox[0]+bbox[2])/2
        self.error_rad = math.atan2(width/2-pixel,fx)
        if abs(self.error_rad) <= self.stop_angle:
            self.goal,self.spin_angle = None,None
            return None
        if completed:
            self.goal,self.spin_angle = None,None
        if self.spin_angle is not None and self.error_rad*self.spin_angle <= 0:
            self.goal,self.spin_angle = None,None
        if self.goal is None and abs(self.error_rad) > self.start_angle:
            self.token += 1
            self.spin_angle = self.error_rad
            self.goal = [float(robot[0]),float(robot[1]),float(robot[2]+self.error_rad)]
        return self.goal


class VisualApproach:
    def __init__(self, step=.2):
        self.step,self.token = step,0
        self.reset()

    def reset(self):
        self.goal = None

    def update(self, robot, bearing, completed=False):
        if completed:
            self.goal = None
        if self.goal is None:
            self.token += 1
            yaw = robot[2]+bearing
            self.goal = [float(robot[0]+self.step*math.cos(yaw)),
                         float(robot[1]+self.step*math.sin(yaw)),float(yaw)]
        return self.goal


def free_candidates(points, grid):
    if grid is None:
        return np.ones(len(points), bool)
    info = grid.info
    q = info.origin.orientation
    yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
    rotation = np.array([[math.cos(yaw),-math.sin(yaw)],[math.sin(yaw),math.cos(yaw)]])
    origin = [info.origin.position.x,info.origin.position.y]
    cells = np.floor((np.asarray(points)-origin) @ rotation/info.resolution).astype(int)
    valid = (cells[:,0]>=0)&(cells[:,1]>=0)&(cells[:,0]<info.width)&(cells[:,1]<info.height)
    values = np.full(len(points),100,np.int16)
    costs = np.asarray(grid.data,dtype=np.int8).reshape(info.height,info.width)
    values[valid] = costs[cells[valid,1],cells[valid,0]]
    # Keep traversable inflation costs and leave unknown-space policy to Nav2.
    return valid&(values<99)


class StandoffGoal:
    def __init__(self, distance=1., tolerance=.05, hysteresis=.05, smoothing=.25, goal_step=.15):
        self.distance, self.tolerance, self.hysteresis = distance,tolerance,hysteresis
        self.smoothing, self.goal_step = smoothing,goal_step
        self.reset()

    def reset(self):
        self.mode, self.goal = 'HOLD',None
        self.filtered, self.anchor = None,None
        self.stamp, self.identity = None,None
        self.range_m, self.filtered_range_m = None,None
        self.blocked = False

    def update(self, robot, person, stamp, identity, grid=None):
        person = np.asarray(person[:2],float)
        robot = np.asarray(robot[:2],float)
        if self.identity != identity:
            self.reset()
            self.identity = identity
        if self.filtered is None:
            self.filtered,self.stamp = person.copy(),stamp
        elif stamp > self.stamp:
            alpha = 1-math.exp(-(stamp-self.stamp)/self.smoothing)
            self.filtered += alpha*(person-self.filtered)
            self.stamp = stamp
        self.range_m = float(np.linalg.norm(person-robot))
        self.filtered_range_m = float(np.linalg.norm(self.filtered-robot))
        lower, upper = self.distance-self.tolerance,self.distance+self.tolerance
        if self.range_m < lower-self.hysteresis and self.mode != 'BACKOFF':
            # A person walking toward us must not wait for the forward-goal EMA.
            self.filtered,self.filtered_range_m = person.copy(),self.range_m
        control_range = min(self.range_m,self.filtered_range_m)
        previous = self.mode
        if self.mode == 'FOLLOW' and control_range <= upper:
            self.mode = 'HOLD'
        elif self.mode == 'BACKOFF' and control_range >= lower:
            self.mode = 'HOLD'
        if self.mode == 'HOLD':
            if control_range > upper+self.hysteresis:
                self.mode = 'FOLLOW'
            elif control_range < lower-self.hysteresis:
                self.mode = 'BACKOFF'
        if self.mode == 'HOLD':
            self.goal,self.anchor,self.blocked = None,None,False
            return None
        moved = self.anchor is None or np.linalg.norm(self.filtered-self.anchor) >= self.goal_step
        obstructed = self.goal is not None and not free_candidates([self.goal[:2]],grid)[0]
        if self.goal is not None and previous == self.mode and not moved and not obstructed:
            return self.goal
        delta = self.filtered-robot
        length = float(np.linalg.norm(delta))
        angle = math.atan2(delta[1],delta[0]) if length > .001 else 0.
        offsets = np.r_[0.,np.arange(1,25)*math.pi/24,-np.arange(1,25)*math.pi/24]
        headings = angle+offsets
        points = self.filtered-self.distance*np.c_[np.cos(headings),np.sin(headings)]
        valid = free_candidates(points,grid)
        if self.mode == 'BACKOFF':
            # A blocked retreat must not turn into another approach to the person.
            valid &= (points-robot) @ delta < 0
        if not valid.any():
            self.goal,self.blocked = None,True
            return None
        score = np.abs(offsets)+.1*np.linalg.norm(points-robot,axis=1)
        score[~valid] = np.inf
        index = int(np.argmin(score))
        point = points[index]
        self.goal = [float(point[0]),float(point[1]),float(headings[index])]
        self.anchor,self.blocked = self.filtered.copy(),False
        return self.goal
