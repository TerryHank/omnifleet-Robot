#!/usr/bin/env python
# encoding: utf-8

#public lib
import sys
import math
import signal
import threading
import time
from time import sleep
from .Rosmaster_Lib import Rosmaster

#ros lib
import rclpy
from rclpy.node import Node
from std_msgs.msg import String,Float32,Int32,Bool,Int64MultiArray
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from omnifleet_interfaces.srv import ServoCommand
from tf2_ros import TransformBroadcaster
from sensor_msgs.msg import Imu,MagneticField, JointState
from rclpy.clock import Clock

#from dynamic_reconfigure.server import Server
IMU_RAW_SCALE = 1000.0

class yahboomcar_driver(Node):
	def __init__(self, name):
		super().__init__(name)
		self.declare_parameter('serial_port', '/dev/myserial')
		self.serial_port = self.get_parameter('serial_port').get_parameter_value().string_value
		self.car = Rosmaster(com=self.serial_port)
		self.car.set_car_type(5)
		self.servo_service = self.create_service(
			ServoCommand, "/t2/servo_command", self.servo_command_callback)
		self.steering_center_service = self.create_service(
			ServoCommand, "/omnifleet_a2/chassis/steering_center", self.steering_center_callback)
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
		self.declare_parameter('angular_limit', 1.0)
		self.angular_limit = self.get_parameter('angular_limit').get_parameter_value().double_value
		print (self.angular_limit)
		self.declare_parameter('stationary_steering_angle_deg', 25.0)
		self.stationary_steering_angle_deg = max(
			1.0,
			min(
				45.0,
				self.get_parameter(
					'stationary_steering_angle_deg'
				).get_parameter_value().double_value,
			),
		)
		print (self.stationary_steering_angle_deg)
		self.declare_parameter('motion_command_rate', 20.0)
		self.motion_command_rate = self.get_parameter('motion_command_rate').get_parameter_value().double_value
		if self.motion_command_rate < 1.0:
			self.motion_command_rate = 1.0
		print (self.motion_command_rate)
		self.declare_parameter('cmd_vel_timeout', 0.35)
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
		self._last_feedback_log_time = 0.0
		self._last_lateral_warning_time = 0.0
		self._motion_cmd_lock = threading.Lock()
		self._motion_cmd = (0.0, 0.0, 0.0)
		self._stationary_steering_deg = None
		self._last_motion_cmd_time = time.monotonic()
		self._motion_cmd_received = False
		self._watchdog_reported = False
		self._serial_error_reported = False
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
		self.motorCommandPublisher = self.create_publisher(Twist,"/motor_command_sent",20)
		self.encoderPublisher = self.create_publisher(
			Int64MultiArray,"/stm32/encoder_counts",20
		)

		self.odomPublisher = self.create_publisher(Odometry, "/odom", 50)
		self.odomTfBroadcaster = TransformBroadcaster(self)
		self._odom_x = self._odom_y = self._odom_yaw = 0.0
		self._last_odom_stamp_ns = None

		#create timer
		self.timer = self.create_timer(0.1, self.pub_data)

		#create and init variable
		self.edition = Float32()
		self.edition.data = 1.0
		self.car.create_receive_threading()
		self.send_motion_period = 1.0 / self.motion_command_rate
		self.motion_timer = self.create_timer(self.send_motion_period, self.send_motion_command)
	#callback function
	def servo_command_callback(self, request, response):
		try:
			status, response.value0, response.value1, response.value2 = self.car.ftservo_command(
				request.operation, request.id, request.arg0, request.arg1, request.arg2)
			response.success = status == 0
			response.message = 'ok' if response.success else f'FTServo status {status}'
		except (ValueError, TimeoutError, OSError) as error:
			response.message = str(error)
		return response

	def steering_center_callback(self, request, response):
		# The web server polls for the serial reply without delaying the motion timer.
		try:
			if request.operation == 2:
				angle = self.car.steering_center_angle
				if angle is not None:
					response.value0 = angle
					response.success = True
				return response
			if request.operation == 1 and 0 <= request.arg0 <= 180:
				self.car.save_steering_center(request.arg0)
			elif request.operation != 0:
				response.message = "Invalid steering center operation or angle"
				return response
			self.car.request_steering_center()
			response.success = True
		except OSError as error:
			response.message = str(error)
		return response

	def cmd_vel_callback(self,msg):
		# 小车运动控制，订阅者回调函数
		# Car motion control, subscriber callback function
		if not isinstance(msg, Twist): return
		vx = max(-self.xlinear_limit, min(self.xlinear_limit, msg.linear.x*1.0))
		angular = max(-self.angular_limit, min(self.angular_limit, msg.angular.z*1.0))
		# Preserve an exact-zero teleop steering command, but never amplify a
		# nonzero command that the hardware cannot execute.  Collision Monitor
		# remains authoritative because its reduced output is never raised here.
		deadbanded_motion = 1e-6 < abs(vx) < self.minimum_linear_speed
		if abs(vx) <= 1e-6 or deadbanded_motion:
			vx = 0.0
		if deadbanded_motion:
			angular = 0.0

		stationary_steering_deg = None
		if vx == 0.0 and not deadbanded_motion:
			if abs(msg.linear.y) > 1e-6:
				# Foxglove sends an explicit manual steering angle in linear.y.
				stationary_steering_deg = max(
					-self.stationary_steering_angle_deg,
					min(self.stationary_steering_angle_deg, msg.linear.y),
				)
			elif abs(angular) > 1e-6:
				# teleop_twist_keyboard j/l sends zero speed and +/- yaw rate.
				stationary_steering_deg = math.copysign(
					self.stationary_steering_angle_deg,
					angular,
				)

		# During actual vehicle motion, STM32 remains the sole owner of Ackermann
		# inverse kinematics. NX only converts SI units to firmware units.
		motion_cmd = (vx * 1000.0, 0.0, angular * 1000.0)
		with self._motion_cmd_lock:
			# The subscriber only updates the target. All serial writes are owned by
			# the fixed-rate motion timer below.
			self._motion_cmd = motion_cmd
			self._stationary_steering_deg = stationary_steering_deg
			self._last_motion_cmd_time = time.monotonic()
			self._motion_cmd_received = True
			self._watchdog_reported = False

		now = Clock().now().nanoseconds / 1e9
		if (
			vx != 0.0
			and abs(msg.linear.y) > 1e-6
			and now - self._last_lateral_warning_time > 2.0
		):
			self._last_lateral_warning_time = now
			self.get_logger().warning(
				'cmd_vel.linear.y=%.3f is ignored while driving; '
				'STM32 accepts only body v and yaw rate'
				% msg.linear.y
			)
		if stationary_steering_deg is not None:
			if now - self._last_cmd_log_time > 0.5:
				self._last_cmd_log_time = now
				self.get_logger().info(
					'STM32 tx stationary steering: wheels=stopped angle=%.1f deg'
					% stationary_steering_deg
				)
		elif now - self._last_cmd_log_time > 0.5:
			self._last_cmd_log_time = now
			self.get_logger().info(
				'STM32 tx FUNC_MOTION: Vx=%d mm/s Vy=0 Vz=%d mrad/s '
				'(Twist v=%.3f m/s wz=%.3f rad/s; kinematics_owner=stm32)'
				% (motion_cmd[0], motion_cmd[2], vx, angular)
			)

	def send_motion_command(self):
		with self._motion_cmd_lock:
			command_expired = (
				not self._motion_cmd_received
				or time.monotonic() - self._last_motion_cmd_time > self.cmd_vel_timeout
			)
			force_zero = command_expired
			if force_zero:
				vx, vy, vz = (0.0, 0.0, 0.0)
				stationary_steering_deg = None
				self._stationary_steering_deg = None
				should_report = (
					command_expired
					and self._motion_cmd_received
					and not self._watchdog_reported
				)
				if command_expired:
					self._watchdog_reported = True
			else:
				vx, vy, vz = self._motion_cmd
				stationary_steering_deg = self._stationary_steering_deg
				should_report = False

		try:
			if force_zero:
				# Keep sending both motor zero and centered steering every 50 ms.
				self.car.set_motion(0.0, 0.0, 0.0)
				self.car.set_ackermann_steering(0.0)
			elif stationary_steering_deg is None:
				self.car.set_motion(vx, vy, vz)
			else:
				# 0xff holds the cached steering target while braking the wheels.
				self.car.set_motion(0.0, 255.0, 0.0)
				self.car.set_ackermann_steering(stationary_steering_deg)
			self._serial_error_reported = False
			motor_command = Twist()
			motor_command.linear.x = vx / 1000.0
			motor_command.angular.z = vz / 1000.0
			if stationary_steering_deg is not None:
				motor_command.linear.y = stationary_steering_deg
			self.motorCommandPublisher.publish(motor_command)
		except Exception as error:
			if not self._serial_error_reported:
				self.get_logger().error(
					'serial motion write failed; attempting zero motion: %s' % error
				)
				self._serial_error_reported = True
			try:
				self.car.set_motion(0.0, 0.0, 0.0)
				self.car.set_ackermann_steering(0.0)
			except Exception:
				pass
		if should_report:
			self.get_logger().warning(
				'cmd_vel timeout after %.3f s; forcing zero motion and centered steering'
				% self.cmd_vel_timeout
			)

	def stop_and_close(self):
		if self._closed:
			return
		self._closed = True
		with self._motion_cmd_lock:
			self._motion_cmd = (0.0, 0.0, 0.0)
			self._stationary_steering_deg = None
			self._motion_cmd_received = False
		for _ in range(3):
			try:
				self.car.set_motion(0.0, 0.0, 0.0)
				self.car.set_ackermann_steering(0.0)
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

	@staticmethod
	def _integrate_planar_pose(x, y, yaw, vx, wz, dt):
		"""Integrate encoder-derived body velocity in the REP-103 frame."""
		x += vx * math.cos(yaw) * dt
		y += vx * math.sin(yaw) * dt
		yaw += wz * dt
		yaw = math.atan2(math.sin(yaw), math.cos(yaw))
		return x, y, yaw

	def publish_odometry(self, time_stamp, vx, wz):
		stamp_ns = time_stamp.nanoseconds
		if self._last_odom_stamp_ns is not None:
			dt = (stamp_ns - self._last_odom_stamp_ns) / 1e9
			if dt > 0.0:
				self._odom_x, self._odom_y, self._odom_yaw = self._integrate_planar_pose(
					self._odom_x, self._odom_y, self._odom_yaw, vx, wz, dt
				)
		self._last_odom_stamp_ns = stamp_ns

		half_yaw = 0.5 * self._odom_yaw
		qz = math.sin(half_yaw)
		qw = math.cos(half_yaw)

		odom = Odometry()
		odom.header.stamp = time_stamp.to_msg()
		odom.header.frame_id = "odom"
		odom.child_frame_id = "base_link"
		odom.pose.pose.position.x = self._odom_x
		odom.pose.pose.position.y = self._odom_y
		odom.pose.pose.orientation.z = qz
		odom.pose.pose.orientation.w = qw
		odom.twist.twist.linear.x = vx
		odom.twist.twist.angular.z = wz
		odom.pose.covariance[0] = 0.001
		odom.pose.covariance[7] = 0.001
		odom.pose.covariance[14] = 1.0e6
		odom.pose.covariance[21] = 1.0e6
		odom.pose.covariance[28] = 1.0e6
		odom.pose.covariance[35] = 0.001
		odom.twist.covariance[0] = 0.0001
		odom.twist.covariance[7] = 1.0e6
		odom.twist.covariance[14] = 1.0e6
		odom.twist.covariance[21] = 1.0e6
		odom.twist.covariance[28] = 1.0e6
		odom.twist.covariance[35] = 0.0001
		self.odomPublisher.publish(odom)

		transform = TransformStamped()
		transform.header = odom.header
		transform.child_frame_id = "base_link"
		transform.transform.translation.x = self._odom_x
		transform.transform.translation.y = self._odom_y
		transform.transform.rotation.z = qz
		transform.transform.rotation.w = qw
		self.odomTfBroadcaster.sendTransform(transform)

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
		firmware_version = self.car.get_version()
		edition.data = float(firmware_version) if firmware_version else 0.0
		firmware.data = firmware_version or 'unknown'
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
		vx, steering_deg, angular = self.car.get_motion_data()
		encoder_counts = Int64MultiArray()
		encoder_counts.data = list(self.car.get_encoder_counts())

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
		# Legacy feedback contract: linear.y carries the measured steering angle
		# in degrees; linear.x and angular.z are standard SI body velocities.
		twist.linear.y = steering_deg
		twist.angular.z = angular*1.0
		self.velPublisher.publish(twist)
		self.publish_odometry(time_stamp, vx, angular)
		self.encoderPublisher.publish(encoder_counts)
		now = time.monotonic()
		if now - self._last_feedback_log_time > 2.0:
			self._last_feedback_log_time = now
			frames, checksum_errors, receive_errors, frame_age = self.car.get_transport_diagnostics()
			with self._motion_cmd_lock:
				tx_vx, _, tx_vz = self._motion_cmd
			self.get_logger().info(
				'STM32 rx FUNC_REPORT_SPEED: vx=%.3f m/s steer=%.1f deg '
				'wz=%.3f rad/s voltage=%.1f V frames=%d age=%.3f s '
				'errors(checksum=%d,receive=%d); last_tx=(%d,0,%d)'
				% (
					vx, steering_deg, angular, battery.data, frames, frame_age,
					checksum_errors, receive_errors, tx_vx, tx_vz,
				)
			)
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
		steer_radis = steering_deg*3.1416/180.0
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
