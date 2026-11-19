"""Publish losslessly compressed PointCloud2 CDR and JPEG-only display topics."""
from array import array
import ctypes
import math
import os
import struct
import time
import zlib
import io

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.serialization import serialize_message
from sensor_msgs.msg import CompressedImage, LaserScan, PointCloud2, PointField
from std_msgs.msg import UInt8MultiArray
from PIL import Image
from image_loan import Images, Callback


class SensorFeed:
    def __init__(self,node,prefix,sim_index=None):
        self.sim_index=sim_index
        self.last_cloud=0.
        self.cloud=node.create_publisher(UInt8MultiArray,prefix+'/points/compressed',qos_profile_sensor_data)
        self.jpeg=node.create_publisher(CompressedImage,prefix+'/color/compressed',qos_profile_sensor_data)
        if sim_index is None:
            node.create_subscription(PointCloud2,'/rslidar_points',self.publish_cloud,qos_profile_sensor_data)
            topic='omnifleet/camera/color/preview_jpeg'
        else:
            node.create_subscription(LaserScan,f'/t2_sim_{sim_index}/scan',self.scan,qos_profile_sensor_data)
            topic=f'omnifleet/sim/{sim_index}/rgb'
        self.images=Images(topic,False)
        self.callback=Callback(self.image)
        node.create_timer(.04,self.take)

    def take(self):
        self.images.take(self.callback)

    def image(self,address,size,stamp):
        if not self.jpeg.get_subscription_count():return
        view=(ctypes.c_uint8*size).from_address(address)
        if self.sim_index is None:
            payload=bytes(view)
        else:
            if size!=320*240*3:return
            output=io.BytesIO()
            Image.frombytes('RGB',(320,240),view).save(output,'JPEG',quality=78)
            payload=output.getvalue()
        msg=CompressedImage(format='jpeg',data=payload)
        msg.header.stamp.sec,msg.header.stamp.nanosec=divmod(stamp,1000000000)
        msg.header.frame_id='camera_color_optical_frame' if self.sim_index is None else 'base_link'
        self.jpeg.publish(msg)

    def wanted(self):
        return self.cloud.get_subscription_count() and time.monotonic()-self.last_cloud>=.4

    def scan(self,scan):
        if not self.wanted():return
        points=bytearray()
        for i,r in enumerate(scan.ranges):
            if math.isfinite(r) and scan.range_min<=r<=scan.range_max:
                angle=scan.angle_min+i*scan.angle_increment
                points.extend(struct.pack('<fff',r*math.cos(angle),r*math.sin(angle),0.))
        fields=[PointField(name=name,offset=i*4,datatype=PointField.FLOAT32,count=1) for i,name in enumerate('xyz')]
        self.publish_cloud(PointCloud2(header=scan.header,height=1,width=len(points)//12,fields=fields,
                                      point_step=12,row_step=len(points),data=bytes(points),is_dense=True))

    def publish_cloud(self,msg):
        if not self.wanted():return
        self.last_cloud=time.monotonic()
        raw=serialize_message(msg)
        self.cloud.publish(UInt8MultiArray(data=array('B',zlib.compress(raw,1))))


def main():
    rclpy.init()
    node=Node('dispatch_compressed_sensors')
    if os.environ.get('DISPATCH_MEDIA_SIM')=='1':
        feeds=[SensorFeed(node,f'/dispatch_media/sim_{i}',i) for i in range(3)]
    else:
        feeds=[SensorFeed(node,'/dispatch_media/robot124')]
    try:rclpy.spin(node)
    finally:
        for feed in feeds:feed.images.close()
        node.destroy_node()
        rclpy.try_shutdown()

if __name__=='__main__':
    main()
