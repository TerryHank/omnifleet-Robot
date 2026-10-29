"""One RMF reservation for one jointly planned formation, avoiding self-dependencies."""
from datetime import timedelta
import math
import rmf_adapter as rmf
from rmf_adapter import geometry,vehicletraits
from .elastic_trajectory import path_samples

class FormationTraffic:
    def __init__(self,traffic,trajectory,order,number,states):
        self.traffic=traffic;self.order=list(order);self.number=number;self.handle=None
        self.submitted=False;self.admitted=False;self.paused=False;self.index=0
        self.finished=False;self.position_arrived=False;self.last_instruction=None
        samples=path_samples(trajectory.phases,.08) or [[m['start'] for m in trajectory.models]]
        centers=[[sum(p[k] for p in sample)/len(sample) for k in (0,1)]+[0.] for sample in samples]
        body=[max(math.hypot(x,y) for x,y in m['footprint']) for m in trajectory.models]
        self.radius=max(math.dist(p[:2],center[:2])+r for sample,center in zip(samples,centers) for p,r in zip(sample,body))
        # This envelope is for traffic reservations only. Environment planning
        # and onboard avoidance continue to use each car's actual footprint.
        profile=vehicletraits.Profile(geometry.make_final_convex_circle(self.radius),geometry.make_final_convex_circle(self.radius+.1))
        traits=vehicletraits.VehicleTraits(vehicletraits.Limits(.5,.5),vehicletraits.Limits(.8,.8),profile)
        traits.differential.reversible=True
        from .rmf_traffic import simplify_formation_path
        unique=[centers[0]]
        for p in centers[1:]:
            if math.dist(p[:2],unique[-1][:2])>=.01:unique.append(p)
        if len(unique)>1:unique[-1]=centers[-1]
        self.path=simplify_formation_path(unique)
        for i,p in enumerate(self.path[:-1]):p[2]=math.atan2(self.path[i+1][1]-p[1],self.path[i+1][0]-p[0])
        if len(self.path)>1:self.path[-1][2]=self.path[-2][2]
        # Empty paths explicitly clear the old individual itineraries in Humble.
        for robot in order:
            member=traffic.members.get(robot,{})
            if member.get('handle'):member['handle'].follow_new_path([])
            traffic.routes.pop(robot,None)
        traffic.adapter.add_easy_traffic_light(lambda h:setattr(self,'handle',h),
            'omnifleet_formation','formation_'+str(number),traits,lambda:None,lambda:None,lambda _:None)

    def center(self,states):
        poses=[self.traffic.pose(r,states) for r in self.order]
        if any(p is None for p in poses):return None
        return [sum(p[k] for p in poses)/len(poses) for k in (0,1)]+[self.path[min(self.index,len(self.path)-1)][2]]

    def admit(self,states):
        if self.handle is None:return False
        if not self.submitted:
            if len(self.path)<2:
                center=self.center(states)
                if center is not None:self.handle.update_idle_location('fleet_map',center)
                self.admitted=True
            else:self.handle.follow_new_path([rmf.Waypoint('fleet_map',p,timedelta(seconds=0),True) for p in self.path])
            self.submitted=True;return self.admitted
        if not self.admitted:
            self.admitted=self.traffic.instruction(self.handle.waiting_at,0)==rmf.easy_traffic_light.WaitingInstruction.Resume
        return self.admitted

    def tick(self,states):
        if not self.admitted or not self.handle or len(self.path)<2 or self.finished:return
        traffic=self.traffic;jobs=traffic.owner.missions.jobs
        if any(jobs.get(r,{}).get('phase')!='EXECUTING' for r in self.order):return
        if any(jobs[r].get('traffic_command_pending') is not None for r in self.order):return
        center=self.center(states)
        if center is None:return
        if self.paused:
            if not all(traffic.waiting_stopped(r,states) for r in self.order):return
            if traffic.instruction(self.handle.waiting_after,self.index,center)!=rmf.easy_traffic_light.WaitingInstruction.Resume:return
            for r in self.order:traffic.set_paused(r,False,'Open-RMF 整队已放行')
            self.paused=False;traffic.group_wait=None;return
        if traffic.owner.missions.formation.phase=='HOLDING':
            # Reaching the center briefly does not mean every member arrived.
            # Report completion only after the formation's actual pose checks.
            self.handle.update_idle_location('fleet_map',center);self.finished=True;return
        if self.position_arrived or (self.index>=len(self.path)-2 and math.dist(center[:2],self.path[-1][:2])<.1):
            # WaitAtNextCheckpoint at the final checkpoint means hold position,
            # not cancel final orientation alignment and report moving again.
            self.position_arrived=True
            traffic.instruction(self.handle.waiting_at,len(self.path)-1);return
        while self.index<len(self.path)-2:
            a,b=self.path[self.index:self.index+2]
            if sum((center[k]-b[k])*(b[k]-a[k]) for k in (0,1))<0:break
            self.index+=1
        speed=max(abs(traffic.owner.missions.control(states[r]).get('velocity',[0.,0.])[0]) for r in self.order)
        stopping=.03+.5*speed+speed*speed
        checkpoint=self.index
        while checkpoint<len(self.path)-2 and math.dist(center[:2],self.path[checkpoint+1][:2])<=stopping:checkpoint+=1
        instruction=traffic.instruction(self.handle.moving_from,checkpoint,center)
        if str(instruction)!=self.last_instruction:
            self.last_instruction=str(instruction)
            traffic.record('formation_instruction',self.order[0],instruction=str(instruction),checkpoint=checkpoint,pose=center)
        # The final checkpoint is already a stop target of every member's
        # trajectory. Canceling before it would create a stop/resume loop.
        wait_between=(instruction==rmf.easy_traffic_light.MovingInstruction.WaitAtNextCheckpoint
            and checkpoint+1<len(self.path)-1 and math.dist(center[:2],self.path[checkpoint+1][:2])<=stopping)
        if instruction==rmf.easy_traffic_light.MovingInstruction.PauseImmediately or wait_between:
            self.paused=True;traffic.group_wait=('formation',self.order[0],self.order)
            for r in self.order:traffic.set_paused(r,True,'Open-RMF 整队交通等待')

    def clear(self):
        if self.handle:self.handle.follow_new_path([])

