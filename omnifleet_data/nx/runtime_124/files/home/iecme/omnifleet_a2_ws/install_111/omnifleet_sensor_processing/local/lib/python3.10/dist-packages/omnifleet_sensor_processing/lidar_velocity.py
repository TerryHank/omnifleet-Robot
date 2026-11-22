#!/usr/bin/env python3
"""Nav2 velocity feedback from LiDAR poses only; never uses wheel/IMU data."""
import math
from collections import deque
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry

class LidarVelocity(Node):
    def __init__(self):
        super().__init__('lidar_velocity');self.history=deque()
        self.pub=self.create_publisher(Odometry,'lidar_odometry/nav_odom',10)
        self.create_subscription(Odometry,'lidar_odometry/pose',self.pose,qos_profile_sensor_data)
        self.create_subscription(PoseWithCovarianceStamped,'initialpose',lambda _:self.history.clear(),10)
    def pose(self,msg):
        stamp=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        p=msg.pose.pose.position;q=msg.pose.pose.orientation
        yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
        if self.history and (stamp<=self.history[-1][0] or stamp-self.history[-1][0]>1.):self.history.clear()
        while len(self.history)>1 and stamp-self.history[1][0]>=.25:self.history.popleft()
        msg.twist.twist.linear.x=msg.twist.twist.linear.y=msg.twist.twist.linear.z=0.
        msg.twist.twist.angular.x=msg.twist.twist.angular.y=msg.twist.twist.angular.z=0.
        if self.history:
            t,x,y,a=self.history[0];dt=stamp-t
            vx,vy=(p.x-x)/dt,(p.y-y)/dt
            msg.twist.twist.linear.x=math.cos(yaw)*vx+math.sin(yaw)*vy
            msg.twist.twist.linear.y=-math.sin(yaw)*vx+math.cos(yaw)*vy
            msg.twist.twist.angular.z=math.atan2(math.sin(yaw-a),math.cos(yaw-a))/dt
        self.history.append((stamp,p.x,p.y,yaw));self.pub.publish(msg)

def main():
    rclpy.init();node=LidarVelocity()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:node.destroy_node();rclpy.try_shutdown()
if __name__=='__main__':main()
