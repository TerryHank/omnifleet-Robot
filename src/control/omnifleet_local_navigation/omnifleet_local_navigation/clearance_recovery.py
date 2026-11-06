"""Escape existing costmap overlap using the selected collision model."""
import math
import json
import numpy as np


def grid_start_blocked(grid,pose):
    if grid is None or pose is None:return False
    o=grid.info.origin
    a=math.atan2(2*(o.orientation.w*o.orientation.z+o.orientation.x*o.orientation.y),
                 1-2*(o.orientation.y**2+o.orientation.z**2))
    dx,dy=pose[0]-o.position.x,pose[1]-o.position.y
    x=math.floor((math.cos(a)*dx+math.sin(a)*dy)/grid.info.resolution)
    y=math.floor((-math.sin(a)*dx+math.cos(a)*dy)/grid.info.resolution)
    return 0<=x<grid.info.width and 0<=y<grid.info.height and grid.data[y*grid.info.width+x]>=99



def grid_body_blocked(grid, pose, config, values=None):
    if grid is None or pose is None:
        return False
    origin = grid.info.origin
    angle = math.atan2(2*(origin.orientation.w*origin.orientation.z+
                        origin.orientation.x*origin.orientation.y),
                       1-2*(origin.orientation.y**2+origin.orientation.z**2))
    c, sn = math.cos(angle), math.sin(angle)
    dx, dy = pose[0]-origin.position.x, pose[1]-origin.position.y
    resolution = grid.info.resolution
    cx, cy = math.floor((c*dx+sn*dy)/resolution), math.floor((-sn*dx+c*dy)/resolution)
    extent = math.ceil((math.hypot(config['length'],config['width'])/2+
                        float((values or {}).get('footprint_padding',config.get('padding',0.))))/resolution)+2
    x0, x1 = max(0,cx-extent), min(grid.info.width,cx+extent+1)
    y0, y1 = max(0,cy-extent), min(grid.info.height,cy+extent+1)
    cells = np.asarray(grid.data).reshape(grid.info.height,grid.info.width)
    ys, xs = np.nonzero(cells[y0:y1,x0:x1]>=100)
    x, y = (xs+x0+.5)*resolution, (ys+y0+.5)*resolution
    points = np.column_stack((origin.position.x+c*x-sn*y,origin.position.y+sn*x+c*y))
    return grid_start_blocked(grid,pose) or local_body_collision(pose,points,config,resolution,values,angle)


def recovery_heading(pose,goal,command):
    dx,dy=goal[0]-pose[0],goal[1]-pose[1]
    distance=math.hypot(dx,dy);bearing=math.atan2(dy,dx)
    final_error=math.atan2(math.sin(goal[2]-pose[2]),math.cos(goal[2]-pose[2]))
    bearing_error=math.atan2(math.sin(bearing-pose[2]),math.cos(bearing-pose[2]))
    final_turn=(distance<.25 and abs(command[0])<.02 and command[1]*final_error>0. and command[1]*bearing_error<=0.)
    return goal[2] if distance<=.08 or final_turn else bearing


def recovery_config(config, values):
    result = dict(config)
    footprint = values.get('footprint')
    if footprint is not None and not json.loads(footprint):
        result['robot_radius'] = float(values['robot_radius'])+float(values.get('footprint_padding',0.))
    return result


def local_body_collision(pose, points, config, resolution, values=None, grid_yaw=0.):
    """Intersect lethal local-map cell squares with the complete selected body."""
    values = values or {}
    points = np.asarray(points, dtype=float).reshape((-1, 2))
    if not len(points):return False
    dx, dy = points[:, 0]-pose[0], points[:, 1]-pose[1]
    half = resolution/2
    radius = recovery_config(config, values).get('robot_radius')
    if radius is not None:
        c, s = math.cos(grid_yaw), math.sin(grid_yaw)
        x = np.maximum(np.abs(c*dx+s*dy)-half, 0.)
        y = np.maximum(np.abs(-s*dx+c*dy)-half, 0.)
        return bool(np.any(np.hypot(x, y) <= radius+1e-12))
    footprint = json.loads(values.get('footprint', '[]'))
    if footprint:
        corners = np.asarray(footprint, dtype=float)
        low, high = corners.min(axis=0), corners.max(axis=0)
        center = (low+high)/2
        hx, hy = (high-low)/2+float(values.get('footprint_padding', 0.))
    else:
        center = [0., 0.]; hx, hy = config['length']/2, config['width']/2
    c, s = math.cos(pose[2]), math.sin(pose[2])
    x, y = c*dx+s*dy-center[0], -s*dx+c*dy-center[1]
    c, s = math.cos(grid_yaw-pose[2]), math.sin(grid_yaw-pose[2])
    abs_c, abs_s = abs(c), abs(s)
    # Separating axes of both rectangles include interior cells and rotated corners.
    return bool(np.any((np.abs(x) <= hx+half*(abs_c+abs_s)+1e-12) &
                       (np.abs(y) <= hy+half*(abs_c+abs_s)+1e-12) &
                       (np.abs(c*x+s*y) <= half+hx*abs_c+hy*abs_s+1e-12) &
                       (np.abs(-s*x+c*y) <= half+hx*abs_s+hy*abs_c+1e-12)))


def signed_clearance(pose, points, length, width, radius=None):
    points = np.asarray(points, dtype=float).reshape((-1, 2))
    dx, dy = points[:, 0]-pose[0], points[:, 1]-pose[1]
    if radius is not None:
        return np.hypot(dx, dy)-radius
    c, s = math.cos(pose[2]), math.sin(pose[2])
    x, y = np.abs(c*dx+s*dy)-length/2, np.abs(-s*dx+c*dy)-width/2
    return np.hypot(np.maximum(x, 0), np.maximum(y, 0))+np.minimum(np.maximum(x, y), 0)


def arc_pose(start, distance, curvature):
    angle=start[2]+curvature*distance
    if abs(curvature)<1e-6:
        return [start[0]+distance*math.cos(start[2]),start[1]+distance*math.sin(start[2]),angle]
    return [start[0]+(math.sin(angle)-math.sin(start[2]))/curvature,
            start[1]-(math.cos(angle)-math.cos(start[2]))/curvature,angle]


def unknown_cells(grid, start):
    if grid is None or grid.header.frame_id != 'map':
        raise ValueError('脱困需要map坐标系的完整局部栅格')
    ys, xs = np.nonzero(np.asarray(grid.data).reshape((grid.info.height, grid.info.width)) < 0)
    o = grid.info.origin
    a = math.atan2(2*(o.orientation.w*o.orientation.z+o.orientation.x*o.orientation.y),
                   1-2*(o.orientation.y**2+o.orientation.z**2))
    x, y = (xs+.5)*grid.info.resolution, (ys+.5)*grid.info.resolution
    world = np.column_stack((o.position.x+math.cos(a)*x-math.sin(a)*y,
                             o.position.y+math.sin(a)*x+math.cos(a)*y))
    return world[np.linalg.norm(world-np.array(start[:2]), axis=1) < 1.4]


class ClearanceEscape:
    def __init__(self, pose, obstacles, unknown, config, resolution, now, epoch, turn_speed=.35, target_heading=None, start_blocked=None):
        self.speed_scale = float(config.get('recovery_speed_scale', 1.))
        if not math.isfinite(self.speed_scale) or self.speed_scale <= 0.:
            raise ValueError('recovery_speed_scale must be finite and positive')
        self.angular_speed = .30 * self.speed_scale
        self.start = list(pose)
        self.start_blocked = start_blocked
        self.length, self.width = config['length'], config['width']
        self.circle_radius = config.get('robot_radius')
        self.resolution = resolution
        self.physical = resolution*.71+.005
        padded_radius=math.hypot(self.length/2+config['padding'],self.width/2+config['padding'])
        self.exit_clearance = resolution*.71+config['padding']+.05*abs(turn_speed)*padded_radius+.005
        self.escape_clearance=self.physical+.02 if target_heading is not None else self.exit_clearance
        self.max_lateral=max(.02,config['padding'])
        self.radius = self.circle_radius if self.circle_radius is not None else math.hypot(self.length/2, self.width/2)
        if self.circle_radius is not None:
            self.exit_clearance = self.escape_clearance = self.physical
        occupied = np.asarray(obstacles, dtype=float).reshape((-1, 2))
        unknown = np.asarray(unknown, dtype=float).reshape((-1, 2))
        initial = self.distances(pose, occupied)
        if (not len(initial) and start_blocked is None) or (len(initial) and self.circle_radius is None and initial.min() < -resolution*.71):
            raise ValueError('车体内障碍超过栅格离散误差范围，不能自动脱困')
        if len(unknown) and self.distances(pose, unknown).min() < self.physical:
            raise ValueError('当前车体周围存在未知空间，不能自动脱困')
        # Hand orientation planning back to Nav2 at a free start with no lost body clearance.
        if start_blocked is not None and len(initial):
            self.escape_clearance=min(self.escape_clearance,max(self.physical,float(initial.min())))
        curve_speed=min(.30,max(.08,(initial.min(initial=math.inf)-self.physical)/.5))
        self.contacts = {self.key(p): float(d) for p, d in zip(occupied, initial) if d < self.physical}
        self.contact_surface = occupied[initial < self.exit_clearance].copy()
        blocked = np.concatenate((occupied, unknown))
        baseline = np.concatenate((np.minimum(initial, self.physical), np.full(len(unknown), self.physical)))
        self.distance = None
        self.turn_target=None
        error=0. if target_heading is None else math.atan2(math.sin(target_heading-pose[2]),math.cos(target_heading-pose[2]))
        turn_clearance=self.physical+(.002 if self.circle_radius is not None else .02)
        turn_safe=target_heading is not None and not (start_blocked and start_blocked(pose)) and all(self.distances([*pose[:2],pose[2]+a],blocked).min(initial=math.inf)>=turn_clearance
                    for a in np.linspace(0.,error,max(2,math.ceil(abs(error)/.02)+1)))
        if turn_safe:
            self.turn_target=target_heading;self.distance=0.;self.direction=1;self.curvature=0.;self.speed=0.
            self.path=np.asarray([pose]);self.epoch=epoch;self.started=now
            error=math.atan2(math.sin(target_heading-pose[2]),math.cos(target_heading-pose[2]))
            self.timeout=abs(error)/self.angular_speed+4.;self.state='moving';self.reason=''
            self.diagnostic={};self.replan_allowed=False
            return
        for direction in (1, -1):
            for curvature in (0.,-.6,.6,-.3,.3,-.15,.15,-1.2,1.2,-2.,2.):
                prior = baseline.copy(); path=[list(pose)]
                for step in range(1, 81):
                    p=arc_pose(pose,direction*step*.01,curvature)
                    d = self.distances(p, blocked)
                    if np.any(d < prior-1e-7):break
                    prior = np.maximum(prior, np.minimum(d, self.physical));path.append(p)
                    turn = math.inf if start_blocked is not None else np.linalg.norm(blocked-np.array(p[:2]), axis=1).min(initial=math.inf)-self.radius
                    if (d.min(initial=math.inf) >= self.escape_clearance and turn >= self.escape_clearance+(.01 if target_heading is None and self.circle_radius is None else 0.)
                            and not (start_blocked and start_blocked(p))):
                        speed=(.10 if abs(curvature)<1e-6 else min(curve_speed,.30/max(abs(curvature),1.))) * self.speed_scale
                        if step*.01/speed+4.>35.:break
                        score=step*.01+.05*abs(curvature)
                        if self.distance is None or score<best_score:
                            self.direction,self.distance,self.curvature=direction,step*.01,curvature
                            self.path=np.asarray(path);self.speed=speed;best_score=score
                        break
        if self.distance is None:
            raise ValueError('0.8米范围内未找到不加深现有重叠且不新增碰撞的退出轨迹')
        self.epoch, self.started = epoch, now
        self.timeout=self.distance/self.speed+4.
        self.state, self.reason = 'moving', ''
        self.progress = (now, 0.)
        self.blocked_since = None
        self.diagnostic = {}
        self.replan_allowed = False

    def key(self, point):
        return tuple(math.floor(v/self.resolution) for v in point[:2])

    def distances(self, pose, points):
        return signed_clearance(pose, points, self.length, self.width, self.circle_radius)

    def contact_floor(self, point):
        original=self.contacts.get(self.key(point))
        if original is not None:return original
        # Adjacent cells can represent the same stationary surface as returns
        # cross voxel boundaries. Association never grows beyond the start map.
        dx,dy=point[0]-self.start[0],point[1]-self.start[1]
        if self.circle_radius is not None:
            initial=math.hypot(dx,dy)-self.circle_radius
        else:
            c,s=math.cos(self.start[2]),math.sin(self.start[2])
            x,y=abs(c*dx+s*dy)-self.length/2,abs(-s*dx+c*dy)-self.width/2
            initial=math.hypot(max(x,0.),max(y,0.))+min(max(x,y),0.)
        minimum=-self.circle_radius if self.circle_radius is not None else -self.resolution*.71
        if (minimum<=initial<self.physical and len(self.contact_surface) and
                np.linalg.norm(self.contact_surface-np.asarray(point),axis=1).min()<=self.resolution*math.sqrt(2)+1e-6):
            return initial
        return self.physical

    def abort(self, reason, replan=False, timed_out=False):
        self.state, self.reason = 'failed', reason
        self.replan_allowed=replan or timed_out
        self.timed_out=timed_out

    def certified(self, pose, command, obstacles, unknown, margin=0.):
        occupied = np.asarray(obstacles, dtype=float).reshape((-1, 2))
        unknown = np.asarray(unknown, dtype=float).reshape((-1, 2))
        blocked = np.concatenate((occupied, unknown))
        floors = np.array([self.contact_floor(p) for p in occupied]
                          + [self.physical]*len(unknown))+margin
        swept_speed = abs(command[0]) + abs(command[1]) * self.radius
        samples = max(11, math.ceil(.5 * swept_speed / min(.01, self.resolution / 2.)) + 1)
        for t in np.linspace(0., .5, samples):
            v, w = command
            angle = pose[2]+w*t
            if abs(w) < 1e-6:
                p = [pose[0]+v*t*math.cos(pose[2]), pose[1]+v*t*math.sin(pose[2]), angle]
            else:
                p = [pose[0]+v/w*(math.sin(angle)-math.sin(pose[2])),
                     pose[1]-v/w*(math.cos(angle)-math.cos(pose[2])), angle]
            values=self.distances(p, blocked)
            bad=np.flatnonzero(values < floors-.001)
            if len(bad):
                i=int(bad[0]);self.diagnostic={'point':blocked[i].tolist(),'clearance':float(values[i]),
                    'required':float(floors[i]),'initial_contact':bool(i<len(occupied) and floors[i]<self.physical),
                    'prediction_seconds':float(t),'pose':list(pose),'command':list(command)}
                return False
        return True

    def command(self, now, pose, obstacles, unknown, velocity, fresh, epoch):
        if self.state != 'moving':
            return [0., 0.]
        if epoch != self.epoch:
            self.abort('脱困定位代次变化'); return [0., 0.]
        if now-self.started > self.timeout:
            self.abort('脱困超过轨迹限时',timed_out=True); return [0., 0.]
        if not fresh or pose is None:
            return [0., 0.]
        if self.turn_target is not None:
            error=math.atan2(math.sin(self.turn_target-pose[2]),math.cos(self.turn_target-pose[2]))
            if math.dist(pose[:2],self.start[:2])>.1:
                self.abort('脱困转向机身偏移超过边界',replan=True);return [0.,0.]
            if abs(error)<.04:
                self.state='stopping';return [0.,0.]
            command=[0.,max(-self.angular_speed,min(self.angular_speed,1.2*error*self.speed_scale))]
            if not self.certified(pose,command,obstacles,unknown,margin=.002+.5*abs(velocity[0])):
                self.abort('脱困转向预测净空不足',replan=True);return [0.,0.]
            return command
        index=int(np.argmin(np.linalg.norm(self.path[:,:2]-np.asarray(pose[:2]),axis=1)))
        reference=self.path[index];dx,dy=pose[0]-reference[0],pose[1]-reference[1]
        c,s=math.cos(reference[2]),math.sin(reference[2]);progress=index*.01
        lateral=-s*dx+c*dy
        angle = math.atan2(math.sin(reference[2]-pose[2]), math.cos(reference[2]-pose[2]))
        if abs(lateral) > self.max_lateral or abs(angle) > .25:
            self.diagnostic={'lateral_error':lateral,'heading_error':angle,'body_velocity':list(velocity),'pose':list(pose)}
            self.abort('脱困轨迹偏差超过边界，停止后重新规划',replan=True); return [0., 0.]
        blocked = np.concatenate((np.asarray(obstacles).reshape((-1, 2)), np.asarray(unknown).reshape((-1, 2))))
        turn = math.inf if self.start_blocked is not None else np.linalg.norm(blocked-np.array(pose[:2]), axis=1).min(initial=math.inf)-self.radius
        if (progress >= self.distance-.01 and turn >= self.escape_clearance and self.distances(pose, blocked).min(initial=math.inf) >= self.escape_clearance
                and not (self.start_blocked and self.start_blocked(pose))):
            self.state = 'stopping'; return [0., 0.]
        end=self.path[-1]
        overshoot=self.direction*(math.cos(end[2])*(pose[0]-end[0])+math.sin(end[2])*(pose[1]-end[1]))
        if index==len(self.path)-1 and overshoot>.05:
            self.abort('脱困终点环境已变化',replan=True); return [0., 0.]
        if now-self.progress[0] >= 4:
            if progress-self.progress[1] < .015:
                self.abort('脱困没有足够位姿进展'); return [0., 0.]
            self.progress = (now, progress)
        speed=self.speed*min(1.,self.speed/max(abs(velocity[0]),self.speed))
        angular=self.direction*speed*self.curvature+1.5*angle-self.direction*12.*lateral
        command = [self.direction*speed, max(-self.angular_speed, min(self.angular_speed, angular))]
        safe=self.certified(pose,command,obstacles,unknown)
        if not safe and command[1]!=0.:
            straight=[command[0],0.]
            if self.certified(pose,straight,obstacles,unknown):command=straight;safe=True
        if safe and any(abs(v)>1e-6 for v in velocity):
            safe=self.certified(pose,[self.direction*abs(velocity[0]),velocity[1]],obstacles,unknown)
        if not safe:
            if self.blocked_since is None:self.blocked_since=now
            self.reason='脱困暂停：预测净空不足，保持零速等待重新验证'
            if now-self.blocked_since>1.:
                self.abort('脱困预测净空持续不足，已停止恢复',replan=True)
            return [0., 0.]
        self.blocked_since=None;self.reason=''
        return command
