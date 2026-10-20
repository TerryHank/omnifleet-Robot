import math
from pathlib import Path

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist
from ros_robot_controller_msgs.msg import MotorState, MotorsState
from std_msgs.msg import Bool


class TankBridge(Node):
 def __init__(self):
  super().__init__('rrc_tank_bridge')
  for n,v in [('input_topic','/cmd_vel'),('enabled',True),('wheel_diameter_m',0.054),('track_width_m',0.1528),('max_rps',0.35),('command_timeout_s',0.35),('left_motor_id',1),('right_motor_id',2),('left_sign',1.0),('right_sign',-1.0),('emergency_stop_topic','/rrc_safety/emergency_stop'),('emergency_stop_state_topic','/rrc_safety/emergency_stop_state'),('emergency_stop_latch_file','~/.local/state/rrc_tank_bridge/emergency_stop')]: self.declare_parameter(n,v)
  self.enabled=bool(self.get_parameter('enabled').value); self.diameter=float(self.get_parameter('wheel_diameter_m').value); self.track=float(self.get_parameter('track_width_m').value); self.max_rps=float(self.get_parameter('max_rps').value); self.timeout=float(self.get_parameter('command_timeout_s').value); self.left_id=int(self.get_parameter('left_motor_id').value); self.right_id=int(self.get_parameter('right_motor_id').value); self.left_sign=float(self.get_parameter('left_sign').value); self.right_sign=float(self.get_parameter('right_sign').value); self.last=None
  self.estop_latch_file=Path(str(self.get_parameter('emergency_stop_latch_file').value)).expanduser()
  self.emergency_stopped=self.estop_latch_file.exists()
  state_qos=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
  self.pub=self.create_publisher(MotorsState,'/ros_robot_controller/set_motor',10)
  self.estop_state_pub=self.create_publisher(Bool,str(self.get_parameter('emergency_stop_state_topic').value),state_qos)
  self.sub=self.create_subscription(Twist,str(self.get_parameter('input_topic').value),self.on_cmd,10)
  self.estop_sub=self.create_subscription(Bool,str(self.get_parameter('emergency_stop_topic').value),self.on_emergency_stop,10)
  self.timer=self.create_timer(0.05,self.watchdog)
  self.state_timer=self.create_timer(1.0,self.publish_emergency_stop_state)
  self.publish_rps(0,0); self.publish_emergency_stop_state()
  self.get_logger().info('tank bridge %s, input=%s, M%d/M%d, emergency_stop=%s' % ('enabled' if self.enabled else 'disabled',self.get_parameter('input_topic').value,self.left_id,self.right_id,'active' if self.emergency_stopped else 'released'))
 def publish_rps(self,left,right):
  msg=MotorsState(); a=MotorState(); a.id=self.left_id; a.rps=float(max(-self.max_rps,min(self.max_rps,left*self.left_sign))); b=MotorState(); b.id=self.right_id; b.rps=float(max(-self.max_rps,min(self.max_rps,right*self.right_sign))); msg.data=[a,b]; self.pub.publish(msg)
 def on_cmd(self,msg):
  if not self.enabled or self.emergency_stopped:return
  c=math.pi*self.diameter; self.publish_rps((msg.linear.x+msg.angular.z*self.track/2)/c,(msg.linear.x-msg.angular.z*self.track/2)/c); self.last=self.get_clock().now()
 def publish_emergency_stop_state(self):
  msg=Bool(); msg.data=self.emergency_stopped; self.estop_state_pub.publish(msg)
 def persist_emergency_stop(self, stopped):
  try:
   if stopped:
    self.estop_latch_file.parent.mkdir(parents=True,exist_ok=True); self.estop_latch_file.write_text('locked\n',encoding='utf-8')
   else:
    self.estop_latch_file.unlink(missing_ok=True)
   return True
  except OSError as error:
   self.get_logger().error('cannot update emergency-stop latch file %s: %s' % (self.estop_latch_file,error)); return False
 def on_emergency_stop(self,msg):
  requested=bool(msg.data)
  if requested:
   self.emergency_stopped=True; self.last=None; self.publish_rps(0,0); self.persist_emergency_stop(True)
  elif self.persist_emergency_stop(False):
   self.emergency_stopped=False; self.last=None; self.publish_rps(0,0)
  self.publish_emergency_stop_state()
  self.get_logger().warning('emergency stop %s' % ('ACTIVE' if self.emergency_stopped else 'released'))
 def watchdog(self):
  if self.emergency_stopped:self.publish_rps(0,0); self.last=None
  elif self.last and (self.get_clock().now()-self.last).nanoseconds/1e9>self.timeout:self.publish_rps(0,0); self.last=None
 def destroy_node(self): self.publish_rps(0,0); super().destroy_node()
def main():
 rclpy.init(); n=TankBridge()
 try:rclpy.spin(n)
 except KeyboardInterrupt:pass
 finally:n.destroy_node(); rclpy.shutdown()

if __name__ == '__main__':
 main()
