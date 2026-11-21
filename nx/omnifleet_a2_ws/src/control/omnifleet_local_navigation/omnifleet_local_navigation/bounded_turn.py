"""Retain a Nav2 turn while checking the full body at bounded low speed."""
import math
import numpy as np
from .clearance_recovery import signed_clearance


def body_velocity(history,source,now):
    if not source:return [0.,0.],False
    m=source[1];stamp=m.header.stamp.sec+m.header.stamp.nanosec/1e9
    p=m.pose.pose.position;q=m.pose.pose.orientation
    yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
    if history and stamp<history[-1][0]-.001:return [0.,0.],False
    if not history or stamp>history[-1][0]:history.append((stamp,p.x,p.y,yaw))
    history[:]=[row for row in history if stamp-row[0]<=.4]
    first,last=history[0],history[-1];dt=last[0]-first[0]
    if dt<.15:return [0.,0.],False
    return [math.hypot(last[1]-first[1],last[2]-first[2])/dt,
            math.atan2(math.sin(last[3]-first[3]),math.cos(last[3]-first[3]))/dt],now-source[0]<.3


class BoundedTurn:
    def __init__(self,pose,config,resolution,now,epoch):
        self.start=list(pose);self.length=config['length'];self.width=config['width']
        self.resolution=resolution;self.started=now;self.epoch=epoch;self.blocked_since=None
        self.angle=0.;self.last_yaw=pose[2];self.diagnostic={}

    def command(self,now,pose,requested,obstacles,unknown,velocity,fresh,epoch):
        if epoch!=self.epoch or now-self.started>90. or pose is None:return None
        self.angle+=abs(math.atan2(math.sin(pose[2]-self.last_yaw),math.cos(pose[2]-self.last_yaw)))
        self.last_yaw=pose[2]
        if self.angle>7. or math.dist(pose[:2],self.start[:2])>.15:return None
        if not fresh or abs(velocity[0])>.07 or abs(velocity[1])>.15:
            return self.hold(now,'等待新鲜低速机身反馈')
        points=np.concatenate((np.asarray(obstacles).reshape((-1,2)),np.asarray(unknown).reshape((-1,2))))
        if not len(points):return None
        radius=math.hypot(self.length/2,self.width/2)
        def forecast(command):
            v,w=command;minimum=float('inf');last_clearance=None
            required=self.resolution*.71+.005+.6*abs(velocity[0])+.01*(abs(v)+radius*abs(w))
            for t in np.linspace(0.,.6,31):
                yaw=pose[2]+w*t
                p=[pose[0]+(v/w*(math.sin(yaw)-math.sin(pose[2])) if abs(w)>1e-6 else v*t*math.cos(pose[2])),
                   pose[1]+(-v/w*(math.cos(yaw)-math.cos(pose[2])) if abs(w)>1e-6 else v*t*math.sin(pose[2])),yaw]
                last_clearance=float(signed_clearance(p,points,self.length,self.width).min())
                minimum=min(minimum,last_clearance-required)
                if minimum<0:return False,last_clearance
            return True,last_clearance
        if not forecast([0.,velocity[1]])[0]:return self.hold(now,'机身惯性预测净空不足')
        omega=max(-.08,min(.08,requested[1]));choices=[]
        preferred=max(-.01,min(.01,requested[0]))
        candidates=(preferred,0.) if abs(preferred)>1e-6 else (0.,-.01,.01)
        for v in candidates:
            safe,clearance=forecast([v,omega])
            if safe:
                if v==preferred:
                    self.blocked_since=None;return [v,omega]
                choices.append((clearance,[v,omega]))
        if choices:
            self.blocked_since=None;return max(choices,key=lambda row:row[0])[1]
        return self.hold(now,'低速转向及微调候选均无足够净空')

    def hold(self,now,reason):
        self.diagnostic={'reason':reason}
        if self.blocked_since is None:self.blocked_since=now
        return [0.,0.] if now-self.blocked_since<=1. else None
