"""Export the current MOLA keyframe map without moving or reloading localization."""
import base64,json,math,os,subprocess,tempfile,threading,time
from pathlib import Path
import numpy as np
from rclpy.callback_groups import ReentrantCallbackGroup,MutuallyExclusiveCallbackGroup
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from rclpy.serialization import serialize_message
from mola_msgs.srv import MapSave
from std_srvs.srv import Trigger
from std_msgs.msg import String
from sensor_msgs.msg import PointCloud2,PointField


class MapSnapshot:
    def __init__(self,node):
        self.node=node;self.samples={}
        self.client_group=ReentrantCallbackGroup();self.service_group=MutuallyExclusiveCallbackGroup()
        self.client=node.create_client(MapSave,'/map_save',callback_group=self.client_group)
        latched=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        live=QoSProfile(depth=10,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.VOLATILE)
        self.subscriptions=[
            node.create_subscription(String,'/navigation/status',lambda m:self.receive('nav',m),latched,callback_group=self.client_group),
            node.create_subscription(String,'/navigation/local_status',lambda m:self.receive('control',m),live,callback_group=self.client_group),
        ]
        node.create_service(Trigger,'/msc/alignment_map_snapshot',self.capture,callback_group=self.service_group)
        node.create_service(Trigger,'/fleet/alignment_map_snapshot',self.capture,callback_group=self.service_group)

    def receive(self,key,message):
        try:self.samples[key]=(time.monotonic(),json.loads(message.data))
        except (ValueError,TypeError):pass

    def epoch(self):
        now=time.monotonic();nav=self.samples.get('nav');control=self.samples.get('control')
        if not nav:raise ValueError('未收到导航状态')
        if not control:raise ValueError('未收到轮速状态')
        if now-nav[0]>2.:raise ValueError('导航状态超时 '+format(now-nav[0],'.2f')+' 秒')
        if now-control[0]>2.:raise ValueError('轮速状态超时 '+format(now-control[0],'.2f')+' 秒')
        n,c=nav[1],control[1];velocity=c.get('velocity',[])
        if n.get('navigation_active') or c.get('nav_active') or c.get('stopped_seconds',0)<.3 or len(velocity)!=2 or not all(math.isfinite(v) and abs(v)<.01 for v in velocity):
            raise ValueError('地图配准采样时车辆必须静止')
        epoch=n.get('localization_epoch')
        if not epoch:raise ValueError('定位会话尚未就绪')
        return epoch

    def capture(self,request,response):
        try:
            epoch=self.samples.get('nav',(0,{}))[1].get('localization_epoch')
            if not self.client.wait_for_service(timeout_sec=1.):raise ValueError('MOLA 地图保存服务不可用')
            ws=Path(os.environ['RRC_ROBOT_WS']);run=Path.home()/'omnifleet_a2_data/run';run.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='alignment-map-',dir=run) as temporary:
                folder=Path(temporary);future=self.client.call_async(MapSave.Request(map_path=str(folder/'current')))
                event=threading.Event();future.add_done_callback(lambda _:event.set())
                if not event.wait(15.):
                    self.client.remove_pending_request(future);raise TimeoutError('MOLA 当前地图导出超时')
                result=future.result()
                if not result.success:raise ValueError(result.error_message)
                command=[str(Path(__file__).parent/'export-keyframes'),str(ws/'install/mola_metric_maps/lib/libmola_metric_maps.so'),str(folder/'current.mm'),str(folder/'map')]
                subprocess.run(command,check=True,timeout=25.,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
                xyz=np.fromfile(folder/'map_localmap.xyz',dtype='<f4').reshape(-1,3)
                xyz=xyz[np.isfinite(xyz).all(axis=1)]
                if not len(xyz):raise ValueError('当前 MOLA 关键帧地图为空')
                _,inverse=np.unique(np.floor(xyz/.16).astype(np.int64),axis=0,return_inverse=True);counts=np.bincount(inverse)
                points=np.column_stack([np.bincount(inverse,weights=xyz[:,i])/counts for i in range(3)]).astype('<f4')
                cloud=PointCloud2(height=1,width=len(points),fields=[PointField(name=k,offset=i*4,datatype=7,count=1) for i,k in enumerate(('x','y','z'))],
                    is_bigendian=False,point_step=12,row_step=len(points)*12,data=points.tobytes(),is_dense=True)
                cloud.header.frame_id='map';cloud.header.stamp=self.node.get_clock().now().to_msg()
                response.message=json.dumps({'epoch':epoch,'kind':'current_mola_keyframes','points':len(points),'voxel_m':.16,
                    'cloud_cdr_base64':base64.b64encode(serialize_message(cloud)).decode('ascii')})
                response.success=True
        except Exception as error:response.success=False;response.message=str(error)
        return response
