"""Export the current MOLA keyframe map without moving or reloading localization."""
import base64,json,math,subprocess,tempfile,threading,time
from pathlib import Path
import numpy as np
from rclpy.callback_groups import ReentrantCallbackGroup,MutuallyExclusiveCallbackGroup
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from rclpy.serialization import serialize_message
from mola_msgs.srv import MapSave
from nav_msgs.msg import OccupancyGrid
from std_srvs.srv import Trigger
from std_msgs.msg import String
from sensor_msgs.msg import PointCloud2,PointField


class MapSnapshot:
    def __init__(self,node):
        self.node=node;self.samples={}
        self.display_ground_z = 0.0
        self.client_group=ReentrantCallbackGroup();self.service_group=MutuallyExclusiveCallbackGroup()
        self.client=node.create_client(MapSave,'/map_save',callback_group=self.client_group)
        latched=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        live=QoSProfile(depth=10,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.VOLATILE)
        self.subscriptions=[
            node.create_subscription(OccupancyGrid,'/map',self.receive_map,latched,callback_group=self.client_group),
            node.create_subscription(String,'/navigation/status',lambda m:self.receive('nav',m),latched,callback_group=self.client_group),
            node.create_subscription(String,'/navigation/local_status',lambda m:self.receive('control',m),live,callback_group=self.client_group),
        ]
        node.create_service(Trigger,'/fleet/alignment_map_snapshot',self.capture,callback_group=self.service_group)
        node.create_service(Trigger,'/visualization/slam_dense_snapshot',
                            lambda request,response:self.capture(request,response,dense=True),
                            callback_group=self.service_group)

    def receive_map(self, message):
        if message.header.frame_id.lstrip('/') == 'map':
            self.display_ground_z = message.info.origin.position.z

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

    def densify_display_snapshot(self, workspace, folder, baseline, max_z):
        """Supplement the display with registered observations from the same MOLA snapshot."""
        tools = workspace / 'install/mp2p_icp_core/bin'
        try:
            subprocess.run(
                [str(tools / 'sm2mm'), '-i', 'current.simplemap', '-o', 'keyframes.mm',
                 '--no-progress-bar', '-v', 'WARN'],
                cwd=folder, check=True, timeout=20., capture_output=True)
            subprocess.run(
                [str(tools / 'mm2txt'), 'keyframes.mm', '--export-fields', 'x,y,z', '--layer', 'raw'],
                cwd=folder, check=True, timeout=20., capture_output=True)
            raw = np.loadtxt(folder / 'keyframes_raw.txt', dtype='<f4', skiprows=1, ndmin=2)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            self.node.get_logger().warning(f'Dense visualization keyframes unavailable: {error}')
            return baseline
        if not len(raw):
            return baseline
        raw = raw[np.isfinite(raw).all(axis=1) & (raw[:, 2] <= max_z)]
        merged = np.concatenate((baseline, raw))
        _, unique = np.unique(merged, axis=0, return_index=True)
        extra = unique[unique >= len(baseline)]
        count = min(len(extra), 9 * len(baseline))
        selected = extra[np.linspace(0, len(extra) - 1, count, dtype=np.int64)] if count else extra
        return np.concatenate((baseline, merged[selected]))

    def capture(self,request,response,dense=False):
        try:
            epoch=self.samples.get('nav',(0,{}))[1].get('localization_epoch')
            if not self.client.wait_for_service(timeout_sec=1.):raise ValueError('MOLA 地图保存服务不可用')
            ws=Path.home()/'omnifleet_ws';run=ws/'data/run';run.mkdir(parents=True,exist_ok=True)
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
                max_z = self.display_ground_z + 2.5
                if dense:xyz=xyz[xyz[:,2]<=max_z]
                if not len(xyz):raise ValueError('当前 MOLA 关键帧地图为空')
                _,inverse=np.unique(np.floor(xyz/.16).astype(np.int64),axis=0,return_inverse=True);counts=np.bincount(inverse)
                points=np.column_stack([np.bincount(inverse,weights=xyz[:,i])/counts for i in range(3)]).astype('<f4')
                if dense:
                    target=min(len(xyz),5*len(points))
                    points=xyz[np.linspace(0,len(xyz)-1,target,dtype=np.int64)]
                    points=self.densify_display_snapshot(ws,folder,points,max_z)
                cloud=PointCloud2(height=1,width=len(points),fields=[PointField(name=k,offset=i*4,datatype=7,count=1) for i,k in enumerate(('x','y','z'))],
                    is_bigendian=False,point_step=12,row_step=len(points)*12,data=points.tobytes(),is_dense=True)
                cloud.header.frame_id='map';cloud.header.stamp=self.node.get_clock().now().to_msg()
                response.message=json.dumps({'epoch':epoch,'kind':'current_mola_keyframes','points':len(points),'voxel_m':None if dense else .16,
                    'cloud_cdr_base64':base64.b64encode(serialize_message(cloud)).decode('ascii')})
                response.success=True
        except Exception as error:response.success=False;response.message=str(error)
        return response
