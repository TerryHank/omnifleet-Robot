"""Bulk map serialization and publication, isolated from control/lease callbacks."""
import ctypes
import json
import os
from pathlib import Path
import signal
import time

import rclpy
from rclpy.clock import Clock,ClockType
from rclpy.node import Node
from rclpy.qos import QoSProfile,DurabilityPolicy,qos_profile_sensor_data
from std_msgs.msg import String
from nav_msgs.msg import OccupancyGrid
from tf2_msgs.msg import TFMessage
from .client import RobotObserver


class MapRelay(Node):
    # Preserve the existing transport, payload verification and cache format.
    transfer_maps=RobotObserver.transfer_maps
    cache_message=RobotObserver.cache_message
    flush_cache=RobotObserver.flush_cache

    def __init__(self):
        self.robot_id=os.environ['OMNIFLEET_ROBOT_ID']
        super().__init__('omnifleet_map_relay_'+self.robot_id)
        config=json.loads(Path(os.environ['OMNIFLEET_CONFIG']).read_text())
        profile=config['robots'][self.robot_id]
        runtime=os.environ.get('OMNIFLEET_DISCOVERY_PROFILE')
        if runtime:profile={**profile,**json.loads(Path(runtime).read_text())}
        prefix=profile['observed_namespace']
        self.cache=Path(os.environ['OMNIFLEET_DATA'])/'vehicle-cache'/self.robot_id
        self.cache.mkdir(parents=True,exist_ok=True)
        self.samples={};self.cache_pending={};self.local_grid=None
        self.transforms={'tf':{},'tf_static':{}}
        latched=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.peer_output=self.create_publisher(OccupancyGrid,'/navigation/peer_map',latched)
        self.shared_output=self.create_publisher(OccupancyGrid,'/fleet/map',latched)
        self.shared_status=self.create_publisher(String,'/fleet/shared_map_status',latched)
        self.fleet_tf=self.create_publisher(TFMessage,'/tf',10)
        self.create_subscription(String,prefix+'/navigation/status',self.navigation,qos_profile_sensor_data)
        self.create_subscription(TFMessage,prefix+'/tf',lambda message:self.cache_tf('tf',message),qos_profile_sensor_data)
        self.create_subscription(TFMessage,prefix+'/tf_static',lambda message:self.cache_tf('tf_static',message),latched)
        for key,topic in [('map','/map'),('global_costmap','/global_costmap/costmap'),('local_costmap','/local_costmap/costmap')]:
            self.create_subscription(OccupancyGrid,prefix+topic,lambda m,k=key:self.cache_message(k,m),latched)
        clock=Clock(clock_type=ClockType.STEADY_TIME)
        self.create_timer(.1,self.transfer_maps,clock=clock)
        self.create_timer(.1,self.flush_cache,clock=clock)

    def navigation(self,message):
        value=json.loads(message.data)
        if value.get('robot_id')==self.robot_id:self.samples['navigation']=(time.monotonic(),value)

    def cache_tf(self,key,message):
        for transform in message.transforms:
            if transform.header.frame_id!='fleet_map':self.transforms[key][transform.child_frame_id]=transform
        self.cache_pending[key]=TFMessage(transforms=list(self.transforms[key].values()))

    def record(self,key,value):
        self.samples[key]=(time.monotonic(),value)
        metadata={k:v for k,v in self.samples.items() if k!='navigation'}
        temporary=self.cache/'map_relay_state.tmp'
        temporary.write_text(json.dumps(metadata,allow_nan=False))
        temporary.replace(self.cache/'map_relay_state.json')


def main():
    # A force-killed discovery client must not leave an orphan map publisher.
    ctypes.CDLL(None).prctl(1,signal.SIGTERM)
    rclpy.init();node=MapRelay()
    try:rclpy.spin(node)
    except (KeyboardInterrupt,rclpy.executors.ExternalShutdownException):pass
    finally:node.destroy_node();rclpy.try_shutdown()


if __name__=='__main__':main()
