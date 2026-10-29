"""Common-clock, finite-acceleration trajectories for an elastic virtual formation."""
import bisect,copy,json,math,subprocess
import numpy as np

def wrap(a):return math.atan2(math.sin(a),math.cos(a))
def transform(frame,point):
    c,s=math.cos(frame[2]),math.sin(frame[2])
    return [frame[0]+c*point[0]-s*point[1],frame[1]+s*point[0]+c*point[1],wrap(frame[2]+point[2])]

def estimate_frame(poses,offsets,fallback):
    p=np.asarray(poses,dtype=float);r=np.asarray(offsets,dtype=float)
    pc=p[:,:2].mean(axis=0);rc=r[:,:2].mean(axis=0);a=r[:,:2]-rc;b=p[:,:2]-pc
    dot=float(np.sum(a*b));cross=float(np.sum(a[:,0]*b[:,1]-a[:,1]*b[:,0]))
    theta=math.atan2(cross,dot) if math.hypot(dot,cross)>1e-8 else fallback
    c,s=math.cos(theta),math.sin(theta)
    return [float(pc[0]-c*rc[0]+s*rc[1]),float(pc[1]-s*rc[0]-c*rc[1]),theta]

def convex_hull(points):
    values=sorted(set(tuple(map(float,p)) for p in points))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    sides=[]
    for seq in [values,values[::-1]]:
        side=[]
        for p in seq:
            while len(side)>1 and cross(side[-2],side[-1],p)<=0:side.pop()
            side.append(p)
        sides.append(side[:-1])
    return [list(p) for p in sides[0]+sides[1]]

def model(robot,profile,start,goal):
    footprint=profile['footprint'];padding=float(profile['padding'])
    if len(footprint)<3:
        radius=float(profile['robot_radius'])
        footprint=[[radius*math.cos(k*math.pi/16),radius*math.sin(k*math.pi/16)] for k in range(32)]
    footprint=convex_hull([[x+math.copysign(padding,x) if x else 0.,y+math.copysign(padding,y) if y else 0.] for x,y in footprint])
    limits=profile['limits'];body_radius=max(math.hypot(x,y) for x,y in footprint)
    return {'id':robot,'start':[*start[:2],wrap(start[2])],'goal':[*goal[:2],wrap(goal[2])],'footprint':footprint,'limits':dict(limits),
            'turn_radius':max(.10,body_radius*.5),'reversible':limits['reverse']>0,
            'can_spin':profile.get('motion_model')=='DiffDrive'}

def phase_poses(phase,fraction):
    result=[]
    if phase['kind']=='orbit':
        frame=list(phase['frame']);frame[2]+=phase['angle']*fraction
        for initial,offset in zip(phase['start'],phase['offsets']):
            p=transform(frame,offset);p[2]=wrap(initial[2]+phase['angle']*fraction);result.append(p)
    else:
        for p,(distance,angle) in zip(phase['start'],phase['delta']):
            x,y,yaw=p;turn=angle*fraction
            if abs(angle)>1e-9:
                x+=distance/angle*(math.sin(yaw+turn)-math.sin(yaw));y-=distance/angle*(math.cos(yaw+turn)-math.cos(yaw))
            else:x+=distance*fraction*math.cos(yaw);y+=distance*fraction*math.sin(yaw)
            result.append([x,y,wrap(yaw+turn)])
    return result

def timed(phases,models):
    output=[]
    for phase in phases:
        duration=0.
        for (distance,angle),robot in zip(phase['delta'],models):
            lim=robot['limits'];speed=lim['forward'] if distance>=0 else lim['reverse']
            if abs(distance)>1e-8 and speed<=0:raise ValueError('车辆永久参数不允许此倒车轨迹')
            duration=max(duration,math.pi*abs(distance)/(2*max(speed,1e-9)),
                math.pi*abs(angle)/(2*lim['angular']),
                math.pi*math.sqrt(abs(distance)/(2*min(lim['accel'],lim['decel']))),
                math.pi*math.sqrt(abs(angle)/(2*lim['angular_accel'])))
        if duration>1e-5:output.append({**phase,'duration':duration})
    return output

def nominal(starts,offsets,frame,goal,models,rotate_first=False):
    poses=copy.deepcopy(starts);phases=[];current_frame=list(frame)
    def twist(deltas):
        nonlocal poses
        if max(abs(v) for pair in deltas for v in pair)<1e-7:return
        phase={'kind':'twist','start':copy.deepcopy(poses),'delta':deltas};phases.append(phase);poses=phase_poses(phase,1.)
    def align(headings):twist([[0.,wrap(a-p[2])] for a,p in zip(headings,poses)])
    def lines(targets):
        headings=[];distances=[]
        for p,q,m in zip(poses,targets,models):
            distance=math.dist(p[:2],q[:2]);angle=math.atan2(q[1]-p[1],q[0]-p[0]) if distance>1e-7 else p[2]
            if distance<=.01:
                headings.append(p[2]);distances.append(0.);continue
            # Prefer the feasible direction requiring less body rotation. A
            # large turn followed by a short sprint is poor for close formation
            # tracking even if the nominal maximum-speed time looks shorter.
            forward=abs(wrap(angle-p[2]))
            reverse=abs(wrap(angle+math.pi-p[2])) if m['limits']['reverse']>0 else float('inf')
            if reverse<forward:angle=wrap(angle+math.pi);distance=-distance
            headings.append(angle);distances.append(distance)
        align(headings);twist([[d,0.] for d in distances])
    # Recover the saved shape from the current, possibly temporarily deformed configuration.
    lines([transform(current_frame,r) for r in offsets])
    def translate():
        nonlocal current_frame
        next_frame=[goal[0],goal[1],current_frame[2]]
        lines([transform(next_frame,r) for r in offsets]);current_frame=next_frame
    def rotate():
        nonlocal poses,current_frame
        angle=wrap(goal[2]-current_frame[2])
        if abs(angle)<=.01:return
        direction=1 if angle>0 else -1
        headings=[current_frame[2]+math.atan2(r[1],r[0])+direction*math.pi/2 if math.hypot(r[0],r[1])>1e-8 else p[2] for r,p in zip(offsets,poses)]
        align(headings)
        phase={'kind':'orbit','start':copy.deepcopy(poses),'frame':list(current_frame),'offsets':offsets,'angle':angle,
               'delta':[[math.hypot(r[0],r[1])*abs(angle),angle] for r in offsets]}
        phases.append(phase);poses=phase_poses(phase,1.);current_frame[2]=goal[2]
    if rotate_first:rotate();translate()
    else:translate();rotate()
    align([goal[2]+r[2] for r in offsets])
    return timed(phases,models)

def path_samples(phases,step=.02):
    values=[]
    for phase in phases:
        extent=max(abs(d)+.5*abs(a) for d,a in phase['delta']);n=max(1,math.ceil(extent/step))
        values.extend(phase_poses(phase,k/n) for k in range(n+1))
    return values

class JointTrajectory:
    def __init__(self,phases,models,planner):
        self.phases=phases;self.models=models;self.planner=planner;self.ends=[];total=0.
        for p in phases:total+=p['duration'];self.ends.append(total)
        self.duration=total
    def sample(self,elapsed):
        if not self.phases:return [m['goal'] for m in self.models],[[0.,0.] for _ in self.models]
        i=min(bisect.bisect_right(self.ends,elapsed),len(self.phases)-1);phase=self.phases[i]
        before=self.ends[i-1] if i else 0.;u=min(1.,max(0.,(elapsed-before)/phase['duration']))
        fraction=.5-.5*math.cos(math.pi*u);rate=math.pi/(2*phase['duration'])*math.sin(math.pi*u)
        return phase_poses(phase,fraction),[[d*rate,a*rate] for d,a in phase['delta']]
    def payload(self):return {'phases':self.phases,'models':self.models,'planner':self.planner,'duration':self.duration}

def call_worker(binary,request,seconds=5.):
    try:process=subprocess.run([str(binary)],input=json.dumps(request,allow_nan=False),text=True,capture_output=True,timeout=seconds)
    except subprocess.TimeoutExpired:raise ValueError('队形联合规划超时')
    try:result=json.loads(process.stdout)
    except ValueError:raise ValueError('队形规划器未返回有效结果：'+process.stderr[-200:])
    return result

def plan_joint(binary,map_data,starts,offsets,frame,goal,profiles,order,terminal_tolerance=.08):
    goals=[transform(goal,r) for r in offsets]
    models=[model(r,p,a,b) for r,p,a,b in zip(order,profiles,starts,goals)]
    request={'map':map_data,'robots':models,'seconds':max(p.get('planning_seconds',3.) for p in profiles)}
    if all(math.dist(a[:2],b[:2])<=.01 and abs(wrap(a[2]-b[2]))<=.01 for a,b in zip(starts,goals)):
        if call_worker(binary,{**request,'operation':'validate','path':[starts,goals]})['valid']:
            return JointTrajectory([],models,'joint_virtual_structure')
    if all(m['can_spin'] for m in models):
        candidates=[nominal(starts,offsets,frame,goal,models,mode) for mode in [False,True]]
        for phases in sorted(candidates,key=lambda p:sum(x['duration'] for x in p)):
            samples=path_samples(phases) or [starts]
            if call_worker(binary,{**request,'operation':'validate','path':samples})['valid']:
                return JointTrajectory(phases,models,'joint_virtual_structure')
    result=call_worker(binary,request,request['seconds']+3.)
    if not result.get('success') and result.get('reason')=='goal_collision' and terminal_tolerance>0.:
        # Use the same existing 8cm arrival tolerance for the whole formation.
        # Keep relative offsets/yaw and every obstacle; only a common translation is sampled.
        step=map_data['resolution']*.2
        count=math.ceil(terminal_tolerance/step)
        candidates=sorted(((x*step,y*step) for x in range(-count,count+1) for y in range(-count,count+1)
                           if 0.<math.hypot(x*step,y*step)<=terminal_tolerance),key=lambda p:math.hypot(*p))
        for dx,dy in candidates:
            candidate=[goal[0]+dx,goal[1]+dy,goal[2]]
            ends=[transform(candidate,r) for r in offsets]
            if call_worker(binary,{**request,'operation':'validate','path':[ends]})['valid']:
                return plan_joint(binary,map_data,starts,offsets,frame,candidate,profiles,order,terminal_tolerance=0.)
    if not result.get('success'):
        reasons={'start_collision':'当前成员轮廓与障碍或队友重叠','goal_collision':'队形终点有成员轮廓被占用','joint_path_not_found':'未找到全队可通行的弹性路径'}
        raise ValueError(reasons.get(result.get('reason'),result.get('reason','队形规划失败')))
    phases=timed(result['phases'],models)
    if not call_worker(binary,{**request,'operation':'validate','path':path_samples(phases) or [starts]})['valid']:
        raise ValueError('队形轨迹连续碰撞复核未通过')
    return JointTrajectory(phases,models,'joint_elastic_ompl')
