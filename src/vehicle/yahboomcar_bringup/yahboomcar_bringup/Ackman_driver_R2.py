#!/usr/bin/env python
# encoding: utf-8

#public lib
import sys
import math
import signal
import threading
import time
from math import pi
from time import sleep
from .Rosmaster_Lib import Rosmaster

#ros lib
import rclpy
from rclpy.node import Node
from std_msgs.msg import String,Float32,Int32,Bool
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu,MagneticField, JointState
from rclpy.clock import Clock

#from dynamic_reconfigure.server import Server
IMU_RAW_SCALE = 1000.0

class yahboomcar_driver(Node):
	def __init__(self, name):
		super().__init__(name)
		self.RA2DE = 180 / pi
		self.declare_parameter('serial_port', '/dev/myserial')
		self.serial_port = self.get_parameter('serial_port').get_parameter_value().string_value
		self.car = Rosmaster(com=self.serial_port)
		self.car.set_car_type(5)
		#get parameter
		self.declare_parameter('car_type', 'R2')
		self.car_type = self.get_parameter('car_type').get_parameter_value().string_value
		print (self.car_type)
		self.declare_parameter('imu_link', 'imu_link')
		self.imu_link = self.get_parameter('imu_link').get_parameter_value().string_value
		print (self.imu_link)
		self.declare_parameter('Prefix', "")
		self.Prefix = self.get_parameter('Prefix').get_parameter_value().string_value
		print (self.Prefix)
		self.declare_parameter('xlinear_limit', 1.0)
		self.xlinear_limit = self.get_parameter('xlinear_limit').get_parameter_value().double_value
		print (self.xlinear_limit)
		self.declare_parameter('minimum_linear_speed', 0.0)
		self.minimum_linear_speed = max(
			0.0,
			min(
				self.xlinear_limit,
				self.get_parameter('minimum_linear_speed').get_parameter_value().double_value,
			),
		)
		print (self.minimum_linear_speed)
		self.declare_parameter('ylinear_limit', 1.0)
		self.ylinear_limit = self.get_parameter('ylinear_limit').get_parameter_value().double_value
		print (self.ylinear_limit)
		self.declare_parameter('angular_limit', 1.0)
		self.angular_limit = self.get_parameter('angular_limit').get_parameter_value().double_value
		print (self.angular_limit)
		self.declare_parameter('nav_use_rotvel', False)
		self.nav_use_rotvel = self.get_parameter('nav_use_rotvel').get_parameter_value().bool_value
		print (self.nav_use_rotvel)
		self.declare_parameter('cmd_angular_to_steering', True)
		self.cmd_angular_to_steering = self.get_parameter('cmd_angular_to_steering').get_parameter_value().bool_value
		print (self.cmd_angular_to_steering)
		self.declare_parameter('wheelbase', 0.362295943)
		self.wheelbase = self.get_parameter('wheelbase').get_parameter_value().double_value
		print (self.wheelbase)
		self.declare_parameter('steering_limit', 30.0)
		self.steering_limit = self.get_parameter('steering_limit').get_parameter_value().double_value
		print (self.steering_limit)
		self.declare_parameter('motion_command_rate', 20.0)
		self.motion_command_rate = self.get_parameter('motion_command_rate').get_parameter_value().double_value
		if self.motion_command_rate < 1.0:
			self.motion_command_rate = 1.0
		print (self.motion_command_rate)
		self.declare_parameter('cmd_vel_timeout', 0.5)
		self.cmd_vel_timeout = max(
			0.1,
			self.get_parameter('cmd_vel_timeout').get_parameter_value().double_value,
		)
		print (self.cmd_vel_timeout)
		self.declare_parameter('publish_magnetometer', True)
		self.publish_magnetometer = self.get_parameter('publish_magnetometer').value
		# Firmware transports gyro/accel in SI*1000 and magnetometer in uT*1000.
		self.declare_parameter('magnetic_field_tesla_per_raw_unit', 1.0e-9)
		self.magnetic_field_tesla_per_raw_unit = self.get_parameter(
			'magnetic_field_tesla_per_raw_unit'
		).value
		self.declare_parameter('angular_velocity_variance', 4.0e-4)
		self.angular_velocity_variance = self.get_parameter(
			'angular_velocity_variance'
		).value
		self.declare_parameter('linear_acceleration_variance', 4.0e-2)
		self.linear_acceleration_variance = self.get_parameter(
			'linear_acceleration_variance'
		).value
		self.declare_parameter('magnetic_field_variance', 2.5e-11)
		self.magnetic_field_variance = self.get_parameter(
			'magnetic_field_variance'
		).value
		self._last_cmd_log_time = 0.0
		self._motion_cmd_lock = threading.Lock()
		self._motion_cmd = (0.0, 0.0, 0.0)
		self._last_motion_cmd_time = time.monotonic()
		self._motion_cmd_received = False
		self._watchdog_reported = False
		self._closed = False

		#create subcriber
		self.sub_cmd_vel = self.create_subscription(Twist,"cmd_vel",self.cmd_vel_callback,1)
		self.sub_RGBLight = self.create_subscription(Int32,"RGBLight",self.RGBLightcallback,100)
		self.sub_BUzzer = self.create_subscription(Bool,"Buzzer",self.Buzzercallback,100)

		#create publisher
		self.EdiPublisher = self.create_publisher(Float32,"edition",100)
		self.firmwarePublisher = self.create_publisher(String,"/firmware/version",10)
		self.volPublisher = self.create_publisher(Float32,"voltage",100)
		self.staPublisher = self.create_publisher(JointState,"joint_states",100)
		self.velPublisher = self.create_publisher(Twist,"vel_raw",50)
		self.imuPublisher = self.create_publisher(Imu,"/imu/data_raw",100)
		self.magPublisher = self.create_publisher(MagneticField,"/imu/mag",100)

		#create timer
		self.timer = self.create_timer(0.1, self.pub_data)

		#create and init variable
		self.edition = Float32()
		self.edition.data = 1.0
		self.car.create_receive_threading()
		self.send_motion_period = 1.0 / self.motion_command_rate
		self.motion_timer = self.create_timer(self.send_motion_period, self.send_motion_command)
	#callback function
	def cmd_vel_callback(self,msg):
        # 小车运动控制，订阅者回调函数
        # Car motion control, subscriber callback function
		if not isinstance(msg, Twist): return
        # 下发线速度和角速度
		# Issue linear vel and angular vel
		vx = max(-self.xlinear_limit, min(self.xlinear_limit, msg.linear.x*1.0))
		# Keep an exact zero as stop. Any actual motion command must overcome the
		# chassis startup threshold in either direction.
		if abs(vx) <= 1e-6:
			vx = 0.0
		elif abs(vx) < self.minimum_linear_speed:
			vx = math.copysign(self.minimum_linear_speed, vx)
        # R2 odometry is based on the steering-angle feedback in vel_raw.linear.y.
        # Standard cmd_vel users publish yaw rate on angular.z, so convert that to
        # an Ackermann steering angle unless a native steering command is present.
		steer = msg.linear.y*1.0
		angular = max(-self.angular_limit, min(self.angular_limit, msg.angular.z*1.0))
		if (not self.nav_use_rotvel) and self.cmd_angular_to_steering and abs(steer) < 1e-6 and abs(angular) > 1e-6:
			if abs(vx) > 1e-3:
				steer = math.degrees(math.atan(self.wheelbase * angular / vx))
			else:
				steer = 0.0
		steer = max(-self.steering_limit, min(self.steering_limit, steer))
		if self.nav_use_rotvel:
			motion_cmd = (vx * 1000.0, 0.0, angular * 1000.0)
		else:
			motion_cmd = (vx * 1000.0, steer, 0.0)
		with self._motion_cmd_lock:
			self._motion_cmd = motion_cmd
			self._last_motion_cmd_time = time.monotonic()
			self._motion_cmd_received = True
			self._watchdog_reported = False
		now = Clock().now().nanoseconds / 1e9
		if now - self._last_cmd_log_time > 0.5:
			self._last_cmd_log_time = now
			self.get_logger().info("cmd_vel: in_vx=%.3f in_wz=%.3f -> vx=%.3f steer=%.2f nav_use_rotvel=%s" % (
				msg.linear.x, msg.angular.z, vx, steer, str(self.nav_use_rotvel)))
		# self.get_logger().info("cmd_vel_callback: vx = {}, steer = {}, angular = {},".format(vx, steer, angular))
        #print(self.nav_use_rotvel)

	def send_motion_command(self):
		with self._motion_cmd_lock:
			command_expired = (
				not self._motion_cmd_received
				or time.monotonic() - self._last_motion_cmd_time > self.cmd_vel_timeout
			)
			if command_expired:
				vx, vy, vz = (0.0, 0.0, 0.0)
				should_report = self._motion_cmd_received and not self._watchdog_reported
				self._watchdog_reported = True
			else:
				vx, vy, vz = self._motion_cmd
				should_report = False
		self.car.set_motion(vx, vy, vz)
		if should_report:
			self.get_logger().warning(
				'cmd_vel timeout after %.3f s; forcing zero motion' % self.cmd_vel_timeout
			)

	def stop_and_close(self):
		if self._closed:
			return
		self._closed = True
		with self._motion_cmd_lock:
			self._motion_cmd = (0.0, 0.0, 0.0)
			self._motion_cmd_received = False
		for _ in range(3):
			try:
				self.car.set_motion(0.0, 0.0, 0.0)
			except Exception as error:
				self.get_logger().error('failed to send shutdown zero motion: %s' % error)
				break
			sleep(0.02)
		try:
			self.car.close()
		except Exception as error:
			self.get_logger().error('failed to close chassis serial port: %s' % error)

	def RGBLightcallback(self,msg):
        # 流水灯控制，服务端回调函数 RGBLight control
		if not isinstance(msg, Int32): return
		# print ("RGBLight: ", msg.data)
		for i in range(3): self.car.set_colorful_effect(msg.data, 6, parm=1)
	def Buzzercallback(self,msg):
		if not isinstance(msg, Bool): return
		if msg.data:
			for i in range(3): self.car.set_beep(1)
		else:
			for i in range(3): self.car.set_beep(0)

	#pub data
	def pub_data(self):
		time_stamp = Clock().now()
		imu = Imu()
		twist = Twist()
		battery = Float32()
		edition = Float32()
		firmware = String()
		mag = MagneticField()
		state = JointState()
		state.header.stamp = time_stamp.to_msg()
		state.header.frame_id = "joint_states"
		if len(self.Prefix)==0:
			state.name = ["rear_right_wheel_joint", "rear_left_wheel_joint", "front_left_steering_joint", "front_left_wheel_joint",
							"front_right_steering_joint", "front_right_wheel_joint"]
		else:
			state.name = [self.Prefix+"rear_right_wheel_joint", self.Prefix+"rear_left_wheel_joint", self.Prefix+"front_left_steering_joint", self.Prefix+"front_left_wheel_joint",
							self.Prefix+"front_right_steering_joint", self.Prefix+"front_right_wheel_joint"]
		
		#print ("mag: ",self.car.get_magnetometer_data())		
		edition.data = self.car.get_version()*1.0
		firmware.data = (
			format(edition.data, '.1f') if edition.data > 0.0
			else 'unknown'
		)
		battery.data = self.car.get_battery_voltage()*1.0
		ax, ay, az = self.car.get_accelerometer_data()
		# self.get_logger().info("ax = {}, ay = {}, az = {} ".format(ax,ay,az))
		gx, gy, gz = self.car.get_gyroscope_data()
		# self.get_logger().info("gx = {}, gy = {}, gz = {} ".format(gx,gy,gz))
		mx, my, mz = self.car.get_magnetometer_data()
		# self.get_logger().info("mx = {}, my = {}, mz = {} ".format(mx,my,mz))
		mx = mx * 1.0
		my = my * 1.0
		mz = mz * 1.0
		vx, vy, angular = self.car.get_motion_data()
		# self.get_logger().info("get_motion_data: vx = {}, vy = {}, angular = {},".format(vx, vy, angular))
		
		# 发布陀螺仪的数据
		# Publish gyroscope data
		imu.header.stamp = time_stamp.to_msg()
		imu.header.frame_id = self.imu_link
		# This topic intentionally contains no orientation estimate.
		imu.orientation.x = 0.0
		imu.orientation.y = 0.0
		imu.orientation.z = 0.0
		imu.orientation.w = 0.0
		imu.orientation_covariance[0] = -1.0
		imu.linear_acceleration.x = ax / IMU_RAW_SCALE
		imu.linear_acceleration.y = ay / IMU_RAW_SCALE
		imu.linear_acceleration.z = az / IMU_RAW_SCALE
		imu.angular_velocity.x = gx / IMU_RAW_SCALE
		imu.angular_velocity.y = gy / IMU_RAW_SCALE
		imu.angular_velocity.z = gz / IMU_RAW_SCALE
		for index in (0, 4, 8):
			imu.angular_velocity_covariance[index] = self.angular_velocity_variance
			imu.linear_acceleration_covariance[index] = self.linear_acceleration_variance

		mag.header.stamp = time_stamp.to_msg()
		mag.header.frame_id = self.imu_link
		mag.magnetic_field.x = mx * self.magnetic_field_tesla_per_raw_unit
		mag.magnetic_field.y = my * self.magnetic_field_tesla_per_raw_unit
		mag.magnetic_field.z = mz * self.magnetic_field_tesla_per_raw_unit
		for index in (0, 4, 8):
			mag.magnetic_field_covariance[index] = self.magnetic_field_variance
		
		# 将小车当前的线速度和角速度发布出去
		# Publish the current linear vel and angular vel of the car
		twist.linear.x = vx*1.0    #velocity in axis
		twist.linear.y = vy*1000*1.0   #steer angle
		#twist.linear.y = vy   #steer angle
		#twist.angular.z = angular
		twist.angular.z = angular*1.0    #this is invalued
		self.velPublisher.publish(twist)
		# print("ax: %.5f, ay: %.5f, az: %.5f" % (ax, ay, az))
		# print("gx: %.5f, gy: %.5f, gz: %.5f" % (gx, gy, gz))
		# print("mx: %.5f, my: %.5f, mz: %.5f" % (mx, my, mz))
		# rospy.loginfo("battery: {}".format(battery))
		# rospy.loginfo("vx: {}, vy: {}, angular: {}".format(twist.linear.x, twist.linear.y, twist.angular.z))
		self.imuPublisher.publish(imu)
		if self.publish_magnetometer:
			self.magPublisher.publish(mag)
		self.volPublisher.publish(battery)
		self.EdiPublisher.publish(edition)
		self.firmwarePublisher.publish(firmware)
		
		#turn to radis
		steer_radis = vy*1000.0*3.1416/180.0
		state.position = [0.0, 0.0, steer_radis, 0.0, steer_radis, 0.0]
		self.staPublisher.publish(state)
			
def main():
	rclpy.init()
	driver = yahboomcar_driver('driver_node')
	try:
		rclpy.spin(driver)
	except KeyboardInterrupt:
		pass
	finally:
		# ros2 launch may forward SIGINT again while the child is already
		# unwinding.  Do not let that second signal interrupt the zero-motion
		# and serial-close sequence.
		signal.signal(signal.SIGINT, signal.SIG_IGN)
		driver.stop_and_close()
		driver.destroy_node()
		if rclpy.ok():
			rclpy.shutdown()

'''if __name__ == '__main__':
	main()'''

		
		
