"""Web UI operations using the existing per-domain client and vehicle interfaces."""
import base64,json,math,re,time
from pathlib import Path
from rclpy.qos import qos_profile_sensor_data,QoSProfile,DurabilityPolicy
from rosidl_runtime_py.utilities import get_message
from rosidl_runtime_py.convert import message_to_ordereddict
from std_msgs.msg import String
from std_srvs.srv import Trigger
from nav2_msgs.srv import ClearEntireCostmap
from geometry_msgs.msg import PoseWithCovarianceStamped
from mola_msgs.srv import MapLoad,MapSave

SERVICES={'clear_local':('/local_costmap/clear_entirely_local_costmap',ClearEntireCostmap),
          'clear_global':('/global_costmap/clear_entirely_global_costmap',ClearEntireCostmap),
          'reset_map':('/omnifleet_t2/nav2/reset_map',Trigger),
          'start_bag':('/omnifleet_t2/nav2/start_bag_record',Trigger),
          'stop_bag':('/omnifleet_t2/nav2/stop_bag_record',Trigger),
          'save_map':('/omnifleet_t2/waypoints/map_save',MapSave),
          'load_map':('/omnifleet_t2/waypoints/map_load',MapLoad)}

class WebClient:
    def __init__(self,node):
        self.node=node;self.watches={};self.pending={};self.last_write={};self.replies={}
        self.clients={name:node.create_client(cls,path) for name,(path,cls) in SERVICES.items()}
        self.root=node.cache/'web';self.root.mkdir(exist_ok=True)
        self.diagnostic=node.create_publisher(String,'/omnifleet_t2/diagnostics/question',10)
        self.initial=node.create_publisher(PoseWithCovarianceStamped,'/initialpose',1)
        node.create_subscription(String,'/omnifleet_t2/diagnostics/answer',self.answer,10)
        node.create_subscription(String,'/omnifleet_t2/diagnostics/models',lambda m:self.store('/omnifleet_t2/diagnostics/models',m),QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
        node.create_timer(.1,self.tick)

    def store(self,topic,message,force=False):
        now=time.monotonic()
        if not force and now-self.last_write.get(topic,0)<.18:return
        self.last_write[topic]=now
        if message.__class__.__name__=='PointCloud2':
            import struct
            fields={f.name:f for f in message.fields};points=[]
            if all(k in fields and fields[k].datatype in (7,8) for k in ('x','y','z')) and message.point_step:
                count=message.width*message.height;stride=max(1,math.ceil(count/2000));data=bytes(message.data)
                for index in range(0,count,stride):
                    base=(index//message.width)*message.row_step+(index%message.width)*message.point_step
                    p=[struct.unpack_from(('>' if message.is_bigendian else '<')+('f' if fields[k].datatype==7 else 'd'),data,base+fields[k].offset)[0] for k in ('x','y','z')]
                    if all(math.isfinite(v) for v in p):points.append(p)
            value={'frame_id':message.header.frame_id,'points':points,'original_points':message.width*message.height}
        elif message.__class__.__name__=='CompressedImage':
            kind='png' if 'png' in message.format.lower() else 'jpeg'
            value={'frame_id':message.header.frame_id,'image':'data:image/'+kind+';base64,'+base64.b64encode(bytes(message.data)).decode()}
        else:
            value=message_to_ordereddict(message)
            if len(json.dumps(value))>90000:value={'summary':'消息超过原始查看上限','type':message.__class__.__name__}
        path=self.root/(topic.strip('/').replace('/','__')+'.json');tmp=path.with_suffix('.tmp')
        epoch=getattr(self.node,'samples',{}).get('navigation',(0,{}))[1].get('localization_epoch')
        tmp.write_text(json.dumps({'topic':topic,'sample_monotonic':now,'localization_epoch':epoch,'value':value},allow_nan=False,default=lambda _:None));tmp.replace(path)

    def answer(self,message):
        self.store('/omnifleet_t2/diagnostics/answer',message,force=True)
        try:
            value=json.loads(message.data);identifier=value.get('request_id',value.get('id'))
            if not isinstance(identifier,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,160}',identifier) or identifier not in self.replies:return
            path=self.root/('diagnostic-'+identifier+'.json');temporary=path.with_suffix('.tmp')
            temporary.write_text(json.dumps(value));temporary.replace(path)
            status=value.get('status')
            self.reply({'request_id':identifier,'phase':'completed' if status=='complete' else 'failed' if status=='error' else 'forwarding',
                        'message':value.get('answer','诊断结果已返回')[:2000] if status=='error' else '诊断结果已返回' if status=='complete' else '正在诊断'})
        except ValueError:pass

    def reply(self,value):
        self.replies[value['request_id']]=value
        while len(self.replies)>16:
            done=next((key for key,value in self.replies.items() if value['phase']!='forwarding'),None)
            if done is None:break
            self.replies.pop(done)
        self.node.record('web_replies',dict(self.replies))

    def request(self,packet):
        identifier=packet['id'];op=packet['op'];reply={'request_id':identifier,'phase':'completed'}
        try:
            if op=='web_watch':
                topics=packet.get('topics',[])
                if not isinstance(topics,list) or len(topics)>12:raise ValueError('最多同时订阅12个话题')
                available=dict(self.node.get_topic_names_and_types())
                for topic in topics:
                    if not isinstance(topic,str) or topic not in available:raise ValueError('话题尚未发布：'+str(topic))
                    if topic in self.watches:self.watches[topic]['until']=time.monotonic()+8.;continue
                    cls=get_message(available[topic][0])
                    subscription=self.node.create_subscription(cls,topic,lambda m,t=topic:self.store(t,m),qos_profile_sensor_data)
                    self.watches[topic]={'subscription':subscription,'until':time.monotonic()+8.}
                reply['message']='可视化订阅已更新'
            elif op=='web_diagnostic':
                question=packet.get('question','')
                if not isinstance(question,str) or not 1<=len(question)<=4000:raise ValueError('请输入诊断问题')
                self.diagnostic.publish(String(data=json.dumps({'request_id':identifier,'question':question,'engine':packet.get('engine','dsh'),'model':packet.get('model','MiniMax-M3')})))
                reply.update(phase='forwarding',message='问题已发送，等待本车诊断结果')
            elif op=='web_estimate':
                pose=packet.get('pose')
                if not isinstance(pose,list) or len(pose)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) for v in pose):raise ValueError('初始位姿无效')
                msg=PoseWithCovarianceStamped();msg.header.frame_id='map';msg.header.stamp=self.node.get_clock().now().to_msg()
                msg.pose.pose.position.x=float(pose[0]);msg.pose.pose.position.y=float(pose[1]);msg.pose.pose.orientation.z=math.sin(pose[2]/2);msg.pose.pose.orientation.w=math.cos(pose[2]/2)
                msg.pose.covariance[0]=msg.pose.covariance[7]=.25;msg.pose.covariance[35]=.06854
                self.initial.publish(msg);reply['message']='初始位姿已发布；是否接受以本车定位反馈为准'
            elif op=='web_service':
                name=packet.get('service')
                if name not in SERVICES:raise ValueError('该服务不属于面板操作')
                path,cls=SERVICES[name];client=self.clients[name]
                if not client.service_is_ready():raise ValueError('本车服务暂不可用：'+path)
                request=cls.Request()
                if name in ('save_map','load_map'):
                    path=packet.get('map_path')
                    if not isinstance(path,str) or not 1<=len(path)<=2048:raise ValueError('请输入本车地图文件路径')
                    request.map_path=path
                self.pending[identifier]={'client':client,'future':client.call_async(request),'until':time.monotonic()+60.}
                reply.update(phase='forwarding',message='等待本车服务回执')
            else:raise ValueError('未知可视化操作')
        except (ValueError,TypeError,ImportError,AttributeError) as error:reply.update(phase='failed',message=str(error))
        self.reply(reply)

    def tick(self):
        now=time.monotonic()
        for topic,watch in list(self.watches.items()):
            if now>watch['until']:self.node.destroy_subscription(watch['subscription']);self.watches.pop(topic)
        for identifier,pending in list(self.pending.items()):
            if not pending['future'].done() and now<pending['until']:continue
            reply={'request_id':identifier,'phase':'completed','message':'本车服务执行完成'}
            try:
                if not pending['future'].done():pending['client'].remove_pending_request(pending['future']);raise ValueError('本车服务超时，结果未确认')
                result=pending['future'].result()
                if hasattr(result,'success') and not result.success:raise ValueError(getattr(result,'message',getattr(result,'error_message','本车拒绝了服务请求')))
                if hasattr(result,'message'):reply['message']=result.message
            except Exception as error:reply.update(phase='failed',message=str(error))
            self.pending.pop(identifier);self.reply(reply)
