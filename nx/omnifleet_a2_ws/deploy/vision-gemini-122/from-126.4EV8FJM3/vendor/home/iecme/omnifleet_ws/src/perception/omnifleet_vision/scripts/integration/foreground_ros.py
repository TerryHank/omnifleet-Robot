"""ROS calibration/depth cache for the shared foreground query."""
from collections import deque
import numpy as np
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from orbbec_camera_msgs.msg import Extrinsics
from omnifleet_hikrobot_rgbd.foreground_tracking import ForegroundQuery
from omnifleet_hikrobot_rgbd.official_projection import project_depth


class RosForeground(ForegroundQuery):
    def __init__(self,node,minimum=.2,maximum=3.5):
        super().__init__(minimum,maximum)
        self.projector=project_depth
        self.depths=deque(maxlen=16)
        self.color_info=self.depth_info=None
        self.skew_ms=None
        self.depth_received_at=None
        self.wake=None
        node.create_subscription(Image,'/camera/depth/image_raw',self.on_depth,QoSProfile(depth=1,reliability=ReliabilityPolicy.BEST_EFFORT))
        node.create_subscription(CameraInfo,'/camera/color/camera_info',self.on_color,qos_profile_sensor_data)
        node.create_subscription(CameraInfo,'/camera/depth/camera_info',self.on_depth_info,qos_profile_sensor_data)
        node.create_subscription(Extrinsics,'/camera/depth_to_color',self.on_extrinsics,
            QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL))

    def on_color(self,info):
        if info.k[0]>0 and info.k[4]>0:
            self.color_info=info;self.rgb_k=np.asarray(info.k).reshape(3,3)
            self.rgb_size=(info.width,info.height);self.distortion=info.d

    def on_depth_info(self,info):
        if info.k[0]>0 and info.k[4]>0:self.depth_info=info;self.depth_k=np.asarray(info.k).reshape(3,3)

    def on_extrinsics(self,message):
        self.transform=np.eye(4);self.transform[:3,:3]=np.asarray(message.rotation).reshape(3,3)
        self.transform[:3,3]=message.translation

    def on_depth(self,message):
        import time
        self.depths.append(message)
        self.depth_received_at=time.monotonic()
        if self.wake is not None:self.wake()

    @staticmethod
    def image_stamp(message):
        return message.header.stamp.sec+message.header.stamp.nanosec*1e-9

    def select_frame(self,frames,last_stamp,now):
        frames=[m for m in frames if self.image_stamp(m)>last_stamp]
        if not frames:return None
        depths=list(self.depths)
        if not depths or self.depth_received_at is None or now-self.depth_received_at>.2:
            # RGB tracking remains available when the depth stream is absent.
            return frames[-1]
        depth_stamps=[self.image_stamp(m) for m in depths]
        # Either side of the RGB timestamp is usable within the existing200ms
        # tolerance; do not wait a whole RGB period for a future depth frame.
        for best in sorted(frames,key=self.image_stamp,reverse=True):
            if min(abs(self.image_stamp(best)-when) for when in depth_stamps)<=.2+1e-9:
                return best
        return None

    def prepare(self,stamp,rgb_size):
        self.stamp=stamp;self.depth=None;self.depth_stamp=None
        self.depth_is_aligned=False
        self.skew_ms=None
        self.calls,self.elapsed_ms=0,0.
        if self.rgb_size!=tuple(rgb_size) or self.depth_info is None or not self.depths:return
        message=min(list(self.depths),key=lambda m:abs(m.header.stamp.sec+m.header.stamp.nanosec*1e-9-stamp))
        when=message.header.stamp.sec+message.header.stamp.nanosec*1e-9
        self.skew_ms=(when-stamp)*1000
        if abs(when-stamp)>.2+1e-9 or message.encoding!='16UC1':return
        if (message.width,message.height)!=(self.depth_info.width,self.depth_info.height):return
        self.depth=np.ndarray((message.height,message.width),dtype='>u2' if message.is_bigendian else '<u2',buffer=message.data,strides=(message.step,2))
        self.depth_is_aligned=self.color_info is not None and message.header.frame_id==self.color_info.header.frame_id
        self.depth_stamp=when
