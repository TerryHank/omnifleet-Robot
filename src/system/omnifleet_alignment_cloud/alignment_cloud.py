"""Read-only onboard scan selection; export compact geometry for map registration."""
import json
import time

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import String

from cloud_quality import cloud_xyz
from map_snapshot import MapSnapshot
from rclpy.executors import MultiThreadedExecutor


class AlignmentCloud(Node):
    def __init__(self):
        super().__init__('omnifleet_alignment_cloud')
        self.map_snapshot=MapSnapshot(self)
        self.output=self.create_publisher(PointCloud2,'/fleet/alignment_points',qos_profile_sensor_data)
        self.status=self.create_publisher(String,'/fleet/alignment_cloud_status',1)
        self.input=self.create_subscription(PointCloud2,'/rslidar_points',self.receive,qos_profile_sensor_data)
        self.best=None;self.frames=0;self.stamp=None;self.started=time.monotonic();self.last_input=self.started
        self.create_timer(5.,self.watchdog)

    def receive(self,message):
        self.last_input=time.monotonic()
        stamp=(message.header.stamp.sec,message.header.stamp.nanosec)
        if stamp==self.stamp:return
        self.stamp=stamp
        xyz=cloud_xyz(message)
        if not len(xyz):return
        self.frames+=1
        if self.best is None or len(xyz)>len(self.best[1]):self.best=(message.header,xyz,len(message.data))
        if self.frames<12:return
        header,xyz,input_bytes=self.best
        _,inverse=np.unique(np.floor(xyz/.08).astype(int),axis=0,return_inverse=True)
        counts=np.bincount(inverse)
        compact=np.column_stack([np.bincount(inverse,weights=xyz[:,i])/counts for i in range(3)]).astype('<f4')
        result=PointCloud2(header=header,height=1,width=len(compact),
            fields=[PointField(name=name,offset=i*4,datatype=PointField.FLOAT32,count=1) for i,name in enumerate(('x','y','z'))],
            is_bigendian=False,point_step=12,row_step=len(compact)*12,data=compact.tobytes(),is_dense=True)
        self.output.publish(result)
        self.status.publish(String(data=json.dumps({'input_scans':self.frames,'selected_filtered_points':len(xyz),
            'output_points':len(compact),'input_bytes':input_bytes,'output_bytes':len(result.data),
            'window_seconds':time.monotonic()-self.started,'frame_id':header.frame_id})))
        self.best=None;self.frames=0;self.started=time.monotonic()

    def watchdog(self):
        age=time.monotonic()-self.last_input
        if age>15.:
            raise RuntimeError('alignment cloud lost live LiDAR input for %.1f seconds'%age)


if __name__=='__main__':
    rclpy.init();node=AlignmentCloud();executor=MultiThreadedExecutor(num_threads=3);executor.add_node(node)
    try:executor.spin()
    finally:executor.shutdown();node.destroy_node();rclpy.try_shutdown()
