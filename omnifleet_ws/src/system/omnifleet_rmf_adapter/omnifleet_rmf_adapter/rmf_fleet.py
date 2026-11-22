"""Humble RobotCommandHandle integration following the official template API."""
from datetime import timedelta
import json,math,queue,time,uuid
import rmf_adapter as adpt
from rmf_adapter import battery,geometry,graph,plan,vehicletraits
from rmf_task_msgs.msg import TaskType
from .rmf_updates import TaskUpdates


class CommandHandle(adpt.RobotCommandHandle):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.inbox=queue.Queue();self.update=None
        self.path=[];self.index=0;self.arrival=None;self.finished=None;self.request=None;self.deadline=0.
        self.stopping=False;self.wait_until=None;self.path_calls=0;self.stop_calls=0

    def follow_new_path(self,waypoints,next_arrival_estimator,path_finished_callback):
        self.path_calls+=1
        self.inbox.put(('path',list(waypoints),next_arrival_estimator,path_finished_callback))

    def stop(self):self.stop_calls+=1;self.inbox.put(('stop',))

    def dock(self,name,callback):
        self.owner.error='Docking is not commissioned';self.stop()

    def tick(self,state):
        while not self.inbox.empty():
            item=self.inbox.get_nowait()
            self.owner.send('cancel','rmf-stop-'+uuid.uuid4().hex)
            self.stopping=True;self.request=None;self.wait_until=None
            if item[0]=='path':self.path,self.arrival,self.finished=item[1:];self.index=0
            else:self.path=[];self.arrival=None;self.finished=None
        if not self.update:return
        samples=state['samples'];pose=samples.get('pose',{}).get('value');control=samples.get('control',{}).get('value',{})
        if self.owner.localized(state):
            starts=plan.compute_plan_starts(self.owner.graph,self.owner.map_name,
                    [pose['x'],pose['y'],pose['yaw']],self.owner.adapter.now(),max_merge_waypoint_distance=.1,max_merge_lane_distance=.2)
            if starts:self.update.update_position(starts)
            else:self.update.update_lost_position(self.owner.map_name,[pose['x'],pose['y'],pose['yaw']],.1,.2)
        if not self.path:return
        if not self.owner.healthy(state):
            self.owner.error='Robot state/lease/map session invalid';self.path=[]
            self.owner.cancel('rmf-health-stop');self.owner.send('disarm','rmf-health-disarm');return
        if self.stopping:
            if control.get('nav_active') or control.get('stopped_seconds',0)<.3:return
            self.stopping=False
        if self.wait_until:
            if self.owner.adapter.now()<self.wait_until:
                if self.arrival:self.arrival(self.index,timedelta(seconds=0))
                return
            self.wait_until=None;self.index+=1
        if self.index>=len(self.path):
            callback=self.finished;self.path=[];self.finished=None;self.arrival=None
            if callback:callback()
            return
        waypoint=self.path[self.index];position=waypoint.position
        distance=math.hypot(pose['x']-position[0],pose['y']-position[1])
        angle=abs(math.atan2(math.sin(pose['yaw']-position[2]),math.cos(pose['yaw']-position[2])))
        if self.arrival:self.arrival(self.index,timedelta(seconds=distance/.08+angle/.2))
        if self.request is None:
            if distance<.02 and abs(math.atan2(math.sin(pose['yaw']-position[2]),math.cos(pose['yaw']-position[2])))<.05:
                self.wait_until=waypoint.time;return
            self.request='rmf-leg-'+uuid.uuid4().hex;self.deadline=time.monotonic()+30
            self.owner.send('navigate',self.request,pose=[float(v) for v in position])
        client=samples.get('fleet_client',{}).get('value',{})
        event=client.get('history',{}).get(self.request) or client.get('event') or {}
        if event.get('request_id')==self.request:
            if event['phase']=='completed' and not control.get('nav_active') and control.get('stopped_seconds',0)>=.3:
                self.request=None;self.wait_until=waypoint.time
            elif event['phase']=='failed':
                self.owner.error=event.get('message','navigation failed');self.path=[];self.owner.cancel('rmf-leg-failed')
        if self.request and time.monotonic()>self.deadline:
            self.owner.error='Navigation leg timed out';self.owner.cancel('rmf-leg-timeout');self.path=[];self.request=None


class LiveFleet:
    def __init__(self,node,adapter,send,robot_id='robot_104'):
        self.node=node;self.adapter=adapter;self.send=send;self.graph=None;self.command=None
        self.robot_id=robot_id
        self.epoch=None;self.map_name=robot_id+'_live_mapping';self.fleet=None;self.names=[]
        self.error='';self.task_id=None;self.requests={};self.pending_submission=None;self.cancel_pending=False
        self.updates=queue.Queue();self.task_states={};self.last_update_type=None

    def localized(self,state):
        nav=state['samples'].get('navigation',{}).get('value',{})
        pose=state['samples'].get('pose',{}).get('value') or {}
        return bool(state.get('online') and nav.get('local_ready') and nav.get('localization_epoch')==self.epoch
                    and pose.get('frame_id')=='map' and all(type(pose.get(k)) in (int,float) and math.isfinite(pose[k]) for k in ('x','y','yaw')))

    def healthy(self,state):
        nav=state['samples'].get('navigation',{}).get('value',{})
        control=state['samples'].get('control',{}).get('value',{})
        return bool(self.localized(state) and nav.get('fleet_enabled') and nav.get('fleet_lease_fresh')
                    and not nav.get('local_override') and control.get('control_gate_ready')
                    and not control.get('manual_active') and not control.get('estop'))

    def commission(self,state,path):
        if self.graph is not None:raise ValueError('Graph already registered; restart Adapter to commission a new SLAM session')
        nav=state['samples']['navigation']['value'];control=state['samples']['control']['value'];pose=state['samples']['pose']['value']
        if not state['online'] or not nav['local_ready'] or control.get('nav_active') or control.get('stopped_seconds',0)<.3:
            raise ValueError('Commissioning requires fresh localization and a stationary ready robot')
        self.epoch=nav['localization_epoch'];x,y,yaw=pose['x'],pose['y'],pose['yaw']
        points={'origin':[x,y,yaw],'back_030':[x-.3*math.cos(yaw),y-.3*math.sin(yaw),yaw]}
        g=graph.Graph()
        for name,position in points.items():
            waypoint=g.add_waypoint(self.map_name,position[:2]);waypoint.holding_point=True
            g.add_key(name,waypoint.index)
        g.add_bidir_lane(0,1);g.get_waypoint(0).charger=True
        profile=vehicletraits.Profile(geometry.make_final_convex_circle(.32),geometry.make_final_convex_circle(.42))
        traits=vehicletraits.VehicleTraits(vehicletraits.Limits(.08,.1),vehicletraits.Limits(.2,.2),profile)
        traits.differential.reversible=True
        fleet=self.adapter.add_fleet('omnifleet_'+self.robot_id,traits,g,TaskUpdates.uri)
        fleet.set_update_listener(self.updates.put)
        # Energy accounting is disabled; these unit models are not battery measurements.
        bs=battery.BatterySystem.make(1.,1.,1.);ms=battery.MechanicalSystem.make(1.,1.,.01);ps=battery.PowerSystem.make(.0001)
        assert fleet.set_task_planner_params(bs,battery.SimpleMotionPowerSink(bs,ms),battery.SimpleDevicePowerSink(bs,ps),battery.SimpleDevicePowerSink(bs,ps),.01,1.,False,'nothing')
        fleet.accept_task_requests(lambda request:request.description.task_type==TaskType.TYPE_LOOP)
        self.graph=g;self.fleet=fleet;self.names=list(points);self.command=CommandHandle(self)
        starts=[plan.Start(self.adapter.now(),0,yaw)]
        def registered(handle):
            self.command.update=handle;handle.enable_responsive_wait(False)
        fleet.add_robot(self.command,self.robot_id,profile,starts,registered)
        path.write_text(json.dumps({'scope':'live_mapping_test_graph','localization_epoch':self.epoch,'map_name':self.map_name,'places':points,'saved_map_loaded':False,'energy_accounting':False},indent=2)+'\n')

    def submit(self,state,destination,request_id):
        if not self.command or not self.command.update or not self.healthy(state):raise ValueError('Robot is not registered, armed and healthy')
        control=state['samples']['control']['value']
        if control.get('nav_active') or control.get('stopped_seconds',0)<.3:raise ValueError('Previous navigation must be canceled and physically stopped')
        if destination not in self.names:raise ValueError('Destination is not in the commissioned graph')
        if request_id in self.requests:return
        if self.task_id or self.pending_submission:raise ValueError('A task is already active or submitting')
        payload={'category':'patrol','description':{'places':[destination],'rounds':1},'unix_millis_earliest_start_time':int(time.time()*1000)}
        self.requests[request_id]={'phase':'submitting'}
        self.pending_submission=request_id
        def response(result):
            self.pending_submission=None
            self.requests[request_id]=result
            if result.get('success'):
                self.task_id=result.get('state',{}).get('booking',{}).get('id')
                if self.cancel_pending:self.cancel_pending=False;self.cancel('cancel-pending-submission')
            else:self.cancel_pending=False
        try:self.command.update.submit_direct_request(payload,request_id,response)
        except Exception:
            self.pending_submission=None;self.cancel_pending=False
            self.requests[request_id]={'phase':'submit_failed'}
            raise

    def cancel(self,request_id):
        if self.pending_submission:self.cancel_pending=True
        if not self.command or not self.command.update or not self.task_id:
            self.send('cancel',request_id);return
        task=self.task_id
        def canceled(ok):
            self.requests[request_id]={'phase':'cancel_issued' if ok else 'cancel_failed','task_id':task}
        self.command.update.cancel_task(task,['operator_cancel'],canceled)
        self.send('cancel',request_id)

    def tick(self,state):
        while not self.updates.empty():
            message=self.updates.get_nowait();self.last_update_type=message.get('type')
            if message.get('type')!='task_state_update':continue
            task=message['data'];identifier=task['booking']['id']
            self.task_states[identifier]=task
            while len(self.task_states)>64:self.task_states.pop(next(iter(self.task_states)))
        if self.task_states.get(self.task_id,{}).get('status') in ('completed','canceled','killed','failed'):
            self.task_id=None
        if self.command:self.command.tick(state)

    def snapshot(self):
        return {'registered':bool(self.command and self.command.update),'places':self.names,'task_id':self.task_id,'requests':self.requests,'error':self.error,'map_scope':'live_mapping_single_robot',
                'task_states':self.task_states,'last_update_type':self.last_update_type,
                'pending_submission':self.pending_submission,'path_calls':self.command.path_calls if self.command else 0,'path_length':len(self.command.path) if self.command else 0,
                'path_index':self.command.index if self.command else 0,'leg_request':self.command.request if self.command else None}
