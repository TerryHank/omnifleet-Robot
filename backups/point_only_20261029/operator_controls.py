"""Route map clicks and operator teleoperation through the current assignments."""
import math
import copy
import time
import uuid
import json

from geometry_msgs.msg import PoseStamped, Twist, Point
from std_msgs.msg import Bool
from visualization_msgs.msg import Marker, MarkerArray
from .map_hub import compose, inverse


class OperatorControls:
    def __init__(self, owner):
        self.owner=owner;self.subscriptions=[];self.receipt=None
        self.stop_path=owner.data/'operator-stop.json'
        self.stopped=json.loads(self.stop_path.read_text()).get('stopped',False) is True if self.stop_path.exists() else False
        self.stop_state=owner.create_publisher(Bool,'/rrc_safety/emergency_stop_state',1)
        owner.create_subscription(Bool,'/rrc_safety/emergency_stop',self.pause,1)
        owner.create_timer(.2,lambda:self.stop_state.publish(Bool(data=self.stopped)))
        self.markers=owner.create_publisher(MarkerArray,'/fleet/waypoints',1)
        owner.create_timer(.5,self.publish_waypoints)
        self.bind()

    def bind(self):
        for subscription in self.subscriptions:self.owner.destroy_subscription(subscription)
        self.subscriptions=[]
        base='/fleet/formation/ui/r'+str(self.owner.identities.revision)
        self.subscriptions.extend([
            self.owner.create_subscription(PoseStamped,base+'/goal',lambda msg:self.waypoint(None,msg,single=True,formation=True),1),
            self.owner.create_subscription(PoseStamped,base+'/waypoint',lambda msg:self.waypoint(None,msg,formation=True),1)])
        for mode in ('nearest','all'):
            base='/fleet/dispatch/'+mode+'/ui/r'+str(self.owner.identities.revision)
            self.subscriptions.append(self.owner.create_subscription(PoseStamped,base+'/goal',
                lambda msg,m=mode:self.waypoint(None,msg,single=True,dispatch=m),1))
        for robot,namespace in self.owner.maps.names.items():
            base=namespace+'/ui/r'+str(self.owner.identities.revision)
            self.subscriptions.extend([
                self.owner.create_subscription(PoseStamped,base+'/goal',lambda msg,r=robot:self.waypoint(r,msg,single=True),1),
                self.owner.create_subscription(PoseStamped,base+'/waypoint',lambda msg,r=robot:self.waypoint(r,msg),1),
                self.owner.create_subscription(Twist,base+'/cmd_vel',lambda msg,r=robot:self.manual(r,msg),1)])

    def web_command(self,command,states):
        op=command['op'];robot=command.get('robot_id')
        if op=='web_stop':
            if type(command.get('stopped')) is not bool:raise ValueError('停止状态无效')
            self.pause(Bool(data=command['stopped']))
            return {'phase':'accepted','message':'已请求停止全部车辆' if self.stopped else '调度停止已释放；不会自动续跑任务'}
        formation=op=='web_goal' and command.get('target')=='formation'
        dispatch=command.get('mode','nearest') if op=='web_goal' and command.get('target')=='dispatch' else None
        if not formation and not dispatch and robot not in self.owner.maps.names:raise ValueError('请选择有效车辆')
        if op=='web_goal':
            pose=command.get('pose')
            if not isinstance(pose,list) or len(pose)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) for v in pose):raise ValueError('目标位姿无效')
            message=PoseStamped();message.header.frame_id='fleet_map'
            message.pose.position.x=float(pose[0]);message.pose.position.y=float(pose[1])
            message.pose.orientation.z=math.sin(pose[2]/2);message.pose.orientation.w=math.cos(pose[2]/2)
            self.waypoint(robot,message,single=not command.get('multi',False),formation=formation,dispatch=dispatch)
            if self.receipt['phase']=='rejected':raise ValueError(self.receipt['message'])
            return dict(self.receipt)
        if op=='web_manual':
            velocity=command.get('velocity')
            if not isinstance(velocity,list) or len(velocity)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in velocity) or abs(velocity[0])>.3 or abs(velocity[1])>1.5:raise ValueError('遥控速度无效')
            if any(velocity):
                if self.stopped:raise ValueError('调度已停止')
                if not self.owner.execution_permissions(states)[2].get(robot):raise ValueError('本车执行许可尚未同步')
                if self.owner.missions.formation.active and robot in self.owner.missions.formation.saved['order'] and robot!=self.owner.missions.formation.saved['leader']:raise ValueError('编队中仅可操控领车')
                if self.owner.missions.follow['active'] and robot!=self.owner.missions.follow['leader']:raise ValueError('跟随中只可遥控领车')
            message=Twist();message.linear.x=float(velocity[0]);message.angular.z=float(velocity[1]);self.manual(robot,message)
            return {'phase':'accepted','message':'遥控请求已发送；以本车速度反馈为准'}
        if op=='web_estimate':
            if robot not in self.owner.maps.valid_robots:raise ValueError('共享地图变换尚未有效')
            pose=command.get('pose')
            if not isinstance(pose,list) or len(pose)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) for v in pose):raise ValueError('定位位姿无效')
            if self.owner.missions.nav(states.get(robot,{})).get('navigation_active'):raise ValueError('请先停止本车导航再设置定位')
            command={**command,'pose':compose(inverse(self.owner.maps.alignment[robot]),pose)}
        if not self.owner.send_command(op,command['id'],robot_id=robot,**{k:v for k,v in command.items() if k not in ('op','id','robot_id','identity_revision')}):raise ValueError('车辆接口不可用')
        return {'phase':'forwarding','message':'已发往本车接口，等待回执'}

    def waypoint(self, robot, message, single=False, formation=False, dispatch=None):
        request='map-'+uuid.uuid4().hex
        try:
            states=self.owner.snapshots()
            if not formation and not dispatch and robot not in self.owner.maps.valid_robots:raise ValueError(
                getattr(self.owner.maps,'validation_reasons',{}).get(robot,'当前车辆的共享地图变换尚未有效'))
            if message.header.frame_id!='fleet_map':raise ValueError('请在 fleet_map 中选择航点')
            p,q=message.pose.position,message.pose.orientation
            values=[p.x,p.y,p.z,q.x,q.y,q.z,q.w]
            if not all(math.isfinite(v) for v in values) or abs(sum(v*v for v in values[3:])-1.)>.01:
                raise ValueError('航点位置或朝向无效')
            yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
            if dispatch:
                if self.stopped:raise ValueError('调度操控处于停止状态')
                result=self.owner.missions.command({'op':'dispatch_goal','id':request,'mode':dispatch,
                    'point':{'name':'调度目标','pose':[p.x,p.y,yaw]}},states)
                self.receipt={'id':request,**result,'target':'dispatch','robot_id':'dispatch'}
                return
            if formation:
                group=self.owner.missions.formation
                if single and self.stopped:raise ValueError('调度操控处于停止状态')
                count=len(group.route['points'])
                result=self.owner.missions.command({'op':'single_goal' if single else 'route_add','id':request,'target':'formation',
                    'point':{'name':'队形目标' if single else '队形航点'+str(count+1),'pose':[p.x,p.y,yaw]}},states)
                self.receipt={'id':request,'phase':result['phase'],'target':'formation','robot_id':'formation','count':1 if single else count+1,'message':result['message']}
                return
            pose=compose(inverse(self.owner.maps.alignment[robot]),[p.x,p.y,yaw])
            if single:
                if self.stopped:raise ValueError('调度操控处于停止状态')
                if not self.owner.execution_permissions(states)[2].get(robot):raise ValueError('调度许可尚未同步到该车')
            saved=self.owner.missions.saved['routes'].get(robot)
            epoch=self.owner.missions.nav(states.get(robot,{})).get('localization_epoch')
            count=len(saved['points']) if saved and saved['epoch']==epoch else 0
            result=self.owner.missions.command({'op':'single_goal' if single else 'route_add','id':request,'robot_id':robot,
                'point':{'name':'单点目标' if single else '航点'+str(count+1),'pose':pose}},states)
            self.receipt={'id':request,'phase':result.get('phase','accepted'),'robot_id':robot,'count':1 if single else count+1,'mode':'single' if single else 'multi','message':result['message']}
        except (ValueError,KeyError,TypeError) as error:
            self.receipt={'id':request,'phase':'rejected','robot_id':robot,'message':str(error)}

    def manual(self, robot, message):
        velocity=[message.linear.x,message.angular.z]
        if not all(math.isfinite(v) for v in velocity) or abs(velocity[0])>.3 or abs(velocity[1])>1.5:return
        if any(v!=0. for v in (message.linear.y,message.linear.z,message.angular.x,message.angular.y)):return
        states=self.owner.snapshots()
        if any(velocity):
            if self.stopped:return
            if not self.owner.execution_permissions(states)[2].get(robot):return
            formation=self.owner.missions.formation
            if formation.active and robot in formation.saved['order'] and robot!=formation.saved['leader']:return
            follow=self.owner.missions.follow
            if follow['active'] and robot!=follow['leader']:return
            takeover=getattr(self.owner.missions,'pending_cooperative',None)
            if takeover and robot in takeover['requests']:return
            job=self.owner.missions.jobs.get(robot)
            if job and job['phase'] not in ('STOPPING','STOPPED','COMPLETED','FAILED','INVALIDATED'):return
            if job:job.pop('replacement',None)
        self.owner.send_command('manual','teleop-'+str(time.time_ns()),robot_id=robot,velocity=velocity)

    def update_waypoint(self,command,states):
        if command.get('target')=='formation':return self.owner.missions.command(command,states)
        robot=command.get('robot_id');route=self.owner.missions.saved['routes'].get(robot)
        if not route or not route['points']:raise ValueError('该车尚未安排航点')
        if robot not in self.owner.maps.valid_robots:raise ValueError('当前共享地图变换尚未有效')
        if self.owner.missions.nav(states.get(robot,{})).get('navigation_active'):raise ValueError('导航执行中，请先停止该车再修改航点')
        if command.get('localization_epoch')!=route['epoch'] or route['epoch']!=self.owner.missions.nav(states.get(robot,{})).get('localization_epoch'):
            raise ValueError('定位会话已变化，请重新检查航点')
        if type(command.get('route_revision')) is not int or command['route_revision']!=route.get('revision',0):raise ValueError('航点队列已变化，请重新拖动')
        transform=self.owner.maps.alignment[robot]
        if command.get('map_transform')!=transform:raise ValueError('共享地图变换已变化，请重新拖动')
        index,position=command.get('index'),command.get('position')
        if type(index) is not int or not 1<=index<=len(route['points']):raise ValueError('航点编号无效')
        if not isinstance(position,list) or len(position)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in position):raise ValueError('航点坐标无效')
        points=copy.deepcopy(route['points']);old=points[index-1]
        local=compose(inverse(transform),[*position,0.])
        old['pose']=[local[0],local[1],old['pose'][2]]
        result=self.owner.missions.command({'op':'route_save','id':command['id'],'robot_id':robot,'points':points},states)
        self.owner.missions.preview_paths[robot]=[compose(transform,p['pose']) for p in points]
        self.receipt={'id':command['id'],'phase':'saved','robot_id':robot,'count':len(points),'message':'航点位置已保存，航向和队列顺序保持不变'}
        return {**result,'robot_id':robot,'revision':self.owner.missions.saved['routes'][robot]['revision'],'message':self.receipt['message']}

    def start_routes(self,command,states):
        if self.stopped:raise ValueError('调度操控处于停止状态，请先释放操控面板的停止按钮')
        formation=self.owner.missions.formation
        if formation.active:
            return self.owner.missions.command({'op':'route_start','id':command['id'],'target':'formation'},states)
        if self.owner.missions.follow['active']:raise ValueError('请先停止跟随，再开始各车独立航点导航')
        enabled=self.owner.execution_permissions(states)[2];results={}
        for robot in self.owner.maps.names:
            route=self.owner.missions.saved['routes'].get(robot)
            if not route or not route['points']:
                results[robot]={'phase':'skipped','message':'未安排航点'};continue
            try:
                if not enabled.get(robot):raise ValueError('调度许可尚未同步到该车')
                self.owner.missions.command({'op':'route_start','id':command['id']+'-'+robot,'robot_id':robot},states)
                results[robot]={'phase':'accepted','message':'已加入规划执行队列'}
            except ValueError as error:results[robot]={'phase':'rejected','message':str(error)}
        counts={phase:sum(r['phase']==phase or (phase=='accepted' and r['phase']=='queued') for r in results.values()) for phase in ('accepted','skipped','rejected')}
        return {'phase':'accepted' if counts['accepted'] else 'rejected' if counts['rejected'] else 'skipped',
                'vehicles':results,'message':f"已启动 {counts['accepted']} 台；未安排跳过 {counts['skipped']} 台；未启动 {counts['rejected']} 台"}

    def pause(self,message):
        self.stopped=message.data
        temporary=self.stop_path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'stopped':self.stopped}));temporary.replace(self.stop_path)
        if not self.stopped:return
        if getattr(self.owner.missions, 'rmf_dispatch', None):self.owner.missions.rmf_dispatch.cancel_pending()
        self.owner.missions.goal_dispatch.stop('操作者按下调度停止')
        self.owner.missions.command({'op':'follow_stop'},self.owner.snapshots())
        for robot in self.owner.maps.names:
            self.owner.missions.stop(robot,'操作者按下调度停止')
            self.owner.send_command('operator_stop','operator-stop',robot_id=robot)

    def publish_waypoints(self):
        markers=[Marker(action=Marker.DELETEALL)]
        states=self.owner.snapshots()
        entries=[(r,route,'multi') for r,route in self.owner.missions.saved['routes'].items()]
        entries.extend((r,{'epoch':j['epoch'],'points':j['points']},'single') for r,j in self.owner.missions.jobs.items()
            if j['source'] in ('single','dispatch') and j['phase'] not in ('STOPPING','STOPPED','FAILED','INVALIDATED','CANCEL_UNCONFIRMED') and not j.get('hide_target'))
        formation=self.owner.missions.formation
        group_points=list(formation.route['points'])
        if formation.active and formation.goal:group_points=group_points+[{'name':'当前队形目标','pose':formation.goal}]
        dispatch=self.owner.missions.goal_dispatch.state
        if dispatch.get('goal'):
            goal=dispatch['goal']
            for kind in (Marker.ARROW,Marker.TEXT_VIEW_FACING):
                marker=Marker();marker.header.frame_id='fleet_map';marker.ns='dispatch_goal';marker.id=int(kind);marker.type=kind
                marker.pose.position.x=float(goal[0]);marker.pose.position.y=float(goal[1]);marker.pose.position.z=.2
                marker.pose.orientation.z=math.sin(goal[2]/2);marker.pose.orientation.w=math.cos(goal[2]/2)
                marker.scale.x=.35;marker.scale.y=.05;marker.scale.z=.07;marker.color.r=.6;marker.color.b=1.;marker.color.a=1.
                if kind==Marker.TEXT_VIEW_FACING:marker.text='调度目标';marker.scale.z=.18;marker.pose.position.z=.6
                markers.append(marker)
        for i,point in enumerate(group_points):
            x,y,yaw=point['pose']
            for kind in (Marker.ARROW,Marker.TEXT_VIEW_FACING):
                marker=Marker();marker.header.frame_id='fleet_map';marker.ns='formation_center';marker.id=i*2+(kind==Marker.TEXT_VIEW_FACING);marker.type=kind
                marker.pose.position.x=float(x);marker.pose.position.y=float(y);marker.pose.position.z=.15
                marker.pose.orientation.z=math.sin(yaw/2);marker.pose.orientation.w=math.cos(yaw/2)
                marker.scale.x=.35;marker.scale.y=.05;marker.scale.z=.07;marker.color.r=1.;marker.color.b=1.;marker.color.a=1.
                if kind==Marker.TEXT_VIEW_FACING:marker.text='队形中心 / '+point['name'];marker.scale.z=.18;marker.pose.position.z=.5
                markers.append(marker)
        for index,(robot,route,mode) in enumerate(entries):
            if robot not in self.owner.maps.valid_robots or route['epoch']!=self.owner.missions.nav(states.get(robot,{})).get('localization_epoch'):continue
            name=self.owner.config['central']['assignments'][robot]['robot_name']
            for i,point in enumerate(route['points']):
                x,y,yaw=compose(self.owner.maps.alignment[robot],point['pose'])
                for kind in (Marker.ARROW,Marker.TEXT_VIEW_FACING):
                    marker=Marker();marker.header.frame_id='fleet_map';marker.ns=name+('/single' if mode=='single' else '');marker.id=i*2+(kind==Marker.TEXT_VIEW_FACING);marker.type=kind
                    marker.pose.position.x=x;marker.pose.position.y=y;marker.pose.position.z=.12
                    marker.pose.orientation.z=math.sin(yaw/2);marker.pose.orientation.w=math.cos(yaw/2)
                    marker.color.r=1. if index%2 else 0.;marker.color.g=1.;marker.color.b=0. if index%2 else 1.;marker.color.a=1.
                    marker.scale.x=.25;marker.scale.y=.04;marker.scale.z=.05
                    if kind==Marker.TEXT_VIEW_FACING:
                        marker.text=name+' / '+('单点目标' if mode=='single' else point['name']);marker.scale.z=.18;marker.pose.position.z=.4
                    markers.append(marker)
        for index,zone in enumerate(getattr(getattr(self.owner.missions,'traffic',None),'zones',[])):
            marker=Marker();marker.header.frame_id='fleet_map';marker.ns='traffic_corridors';marker.id=index*4;marker.type=Marker.LINE_STRIP
            marker.pose.orientation.w=1.;marker.scale.x=float(zone['width']);marker.color.a=.3
            marker.color.r=1. if zone['state']!='FREE' else .1;marker.color.g=.7 if zone['state']!='BLOCKED' else .1
            marker.points=[Point(x=float(p[0]),y=float(p[1]),z=.04) for p in (zone['a'],zone['b'])]
            markers.append(marker)
            for offset,key in enumerate(('wait_a','wait_b')):
                wait=Marker();wait.header.frame_id='fleet_map';wait.ns='traffic_corridors';wait.id=index*4+offset+1;wait.type=Marker.CYLINDER
                wait.pose.position.x,wait.pose.position.y=zone[key][:2];wait.pose.orientation.w=1.
                wait.scale.x=wait.scale.y=.3;wait.scale.z=.04;wait.color.r=.2;wait.color.g=.8;wait.color.b=1.;wait.color.a=.7;markers.append(wait)
            label=Marker();label.header.frame_id='fleet_map';label.ns='traffic_corridors';label.id=index*4+3;label.type=Marker.TEXT_VIEW_FACING
            label.pose.position.x,label.pose.position.y=map(float,zone['a']);label.pose.position.z=.7;label.pose.orientation.w=1.;label.scale.z=.2;label.color.a=1.;label.color.r=label.color.g=label.color.b=1.
            owner=zone['owner'];name=self.owner.config['central']['assignments'].get(owner,{}).get('robot_name',owner)
            label.text=zone['id']+' / '+(name or zone['state']);markers.append(label)
        self.markers.publish(MarkerArray(markers=markers))
