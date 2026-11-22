FIELDS = ('robot_id', 'local_pose', 'pose_stamp_ns', 'task_id', 'source', 'phase', 'navigation_active', 'local_ready', 'traffic_paused', 'traffic_suspended', 'readiness_reason', 'control_mode', 'manual_active', 'local_override', 'fleet_enabled', 'fleet_hold', 'estop', 'contact', 'safety_reason', 'control_gate_ready', 'tf_age_ms', 'localization_status', 'fleet_control_available', 'message', 'localization_epoch', 'fleet_lease_fresh', 'fleet_lease_sequence', 'fleet_lease_task_id', 'fleet_lease_revision', 'velocity', 'velocity_age', 'nav_active', 'stopped_seconds', 'navigation_parameter_source', 'selected_planner', 'selected_controller', 'follow_stream', 'formation_stream', 'manual_command_age', 'fleet_rx', 'last_fleet_failure')
import base64,json,zlib
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile,DurabilityPolicy
from rclpy.serialization import serialize_message
from std_msgs.msg import String
from nav_msgs.msg import OccupancyGrid
class FleetTransport(Node):
    def __init__(self):
        super().__init__('fastdds_fleet_transport_124')
        latched=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.control=None
        self.control_output=self.create_publisher(String,'/navigation/fleet_status',1)
        self.create_subscription(String,'/navigation/local_status',self.receive_control,1)
        self.maps={}
        self.pending={}
        for key,topic in [('map','/map'),('global_costmap','/global_costmap/costmap'),('local_costmap','/local_costmap/costmap')]:
            self.maps[key]=self.create_publisher(String,'/fleet/transport/'+key,latched)
            self.create_subscription(OccupancyGrid,topic,lambda message,k=key:self.receive_map(k,message),latched)
        self.create_timer(.1,self.publish_control)
        self.create_timer(.5,self.publish_maps)
    def receive_control(self,message):
        value=json.loads(message.data)
        self.control=String(data=json.dumps({k:value[k] for k in FIELDS if k in value},separators=(',',':')))
    def receive_map(self,key,message):
        self.pending[key]=String(data=base64.b64encode(zlib.compress(serialize_message(message),1)).decode())
    def publish_control(self):
        if self.control is not None:
            self.control_output.publish(self.control)
            self.control=None
    def publish_maps(self):
        for key,message in self.pending.items():self.maps[key].publish(message)
        self.pending.clear()
rclpy.init();node=FleetTransport()
try:rclpy.spin(node)
except KeyboardInterrupt:pass
finally:node.destroy_node();rclpy.shutdown()
