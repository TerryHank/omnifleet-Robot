#!/usr/bin/env python
# encoding: utf-8

#public lib
import sys
import signal
import math
import threading
import time
from time import sleep
from .Rosmaster_Lib import Rosmaster

#ros lib
import rclpy
from rclpy.node import Node
from std_msgs.msg import String,Float32,Float32MultiArray,Int32,Bool
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu,MagneticField, JointState
from rclpy.clock import Clock
from rcl_interfaces.msg import SetParametersResult
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from omnifleet_a2_interfaces.msg import SteeringAngleCommand
from tf2_ros import TransformBroadcaster

#from dynamic_reconfigure.server import Server
IMU_RAW_SCALE = 1000.0

class omnifleet_ackermann_driver(Node):
	def __init__(self, name):
		super().__init__(name)
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
		self._deadzone_pwm_parameter_names = (
			'motor_deadzone_pwm_m1_forward',
			'motor_deadzone_pwm_m2_forward',
			'motor_deadzone_pwm_m1_reverse',
			'motor_deadzone_pwm_m2_reverse',
		)
		for parameter_name in self._deadzone_pwm_parameter_names:
			self.declare_parameter(parameter_name, 1600)
		self._deadzone_pwm_values = tuple(
			int(self.get_parameter(name).value)
			for name in self._deadzone_pwm_parameter_names
		)
		self._steering_config_parameter_names = (
			'max_steering_angle_deg',
			'steering_center_offset_deg',
		)
		self.declare_parameter('max_steering_angle_deg', 15)
		self.declare_parameter('steering_center_offset_deg', 0)
		self._steering_config_values = tuple(
			int(self.get_parameter(name).value)
			for name in self._steering_config_parameter_names
		)
		self.max_steering_angle_deg = self._steering_config_values[0]
		self.steering_center_offset_deg = self._steering_config_values[1]
		print (self._steering_config_values)
		self.declare_parameter('motion_watchdog_timeout_ms', 1000)
		self.declare_parameter('watchdog_heartbeat_rate_hz', 10.0)
		self.motion_watchdog_timeout_ms = int(
			self.get_parameter('motion_watchdog_timeout_ms').value
		)
		self.watchdog_heartbeat_rate_hz = float(
			self.get_parameter('watchdog_heartbeat_rate_hz').value
		)
		self._validate_watchdog_settings(
			self.motion_watchdog_timeout_ms,
			self.watchdog_heartbeat_rate_hz,
		)
		self.declare_parameter(
			'steering_angle_target_topic',
			'/omnifleet_a2/chassis/steering_angle_cmd',
		)
		self.steering_angle_target_topic = self.get_parameter(
			'steering_angle_target_topic'
		).value
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
		self._motion_cmd_lock = threading.Lock()
		self._motion_cmd = (0.0, 0.0, 0.0)
		self._steering_angle_target_rad = None
		self._serial_error_reported = False
		self._steering_stop_sent = False
		self._configuring_deadzone_pwm = False
		self._configuring_steering_config = False
		self._configuring_watchdog = False
		self._last_watchdog_trigger_count = None
		self._closed = False

		#create subcriber
		self.sub_cmd_vel = self.create_subscription(Twist,"cmd_vel",self.cmd_vel_callback,1)
		self.sub_steering_angle_target = self.create_subscription(
			SteeringAngleCommand,
			self.steering_angle_target_topic,
			self.steering_angle_target_callback,
			10,
		)
		self.sub_RGBLight = self.create_subscription(Int32,"/omnifleet_a2/chassis/rgb_light",self.RGBLightcallback,100)
		self.sub_BUzzer = self.create_subscription(Bool,"/omnifleet_a2/chassis/buzzer",self.Buzzercallback,100)

		#create publisher
		self.EdiPublisher = self.create_publisher(Float32,"/omnifleet_a2/chassis/edition",100)
		self.firmwarePublisher = self.create_publisher(String,"/omnifleet_a2/chassis/firmware_version",10)
		self.volPublisher = self.create_publisher(Float32,"/omnifleet_a2/chassis/voltage",100)
		self.staPublisher = self.create_publisher(JointState,"joint_states",100)
		self.velPublisher = self.create_publisher(Twist,"/omnifleet_a2/chassis/velocity_raw",50)
		self.odomPublisher = self.create_publisher(Odometry,"/odom",50)
		self.odomTfBroadcaster = TransformBroadcaster(self)
		self.imuPublisher = self.create_publisher(Imu,"/imu/data_raw",100)
		self.magPublisher = self.create_publisher(MagneticField,"/imu/mag",100)
		self.motorCommandPublisher = self.create_publisher(Twist,"/omnifleet_a2/chassis/motor_command_sent",20)
		self.motorStatePublisher = self.create_publisher(Float32MultiArray,"/omnifleet_a2/chassis/motor_state_raw",20)
		self.watchdogStatusPublisher = self.create_publisher(
			DiagnosticArray, "/omnifleet_a2/chassis/watchdog_status", 10
		)
		self._odom_x = 0.0
		self._odom_y = 0.0
		self._odom_yaw = 0.0
		self._last_odom_stamp_ns = None

		#create timer
		self.timer = self.create_timer(0.1, self.pub_data)

		#create and init variable
		self.edition = Float32()
		self.edition.data = 1.0
		self.car.create_receive_threading()
		self._apply_deadzone_pwm(self._deadzone_pwm_values, require_echo=True)
		self._apply_steering_config(self._steering_config_values, require_echo=True)
		self._apply_watchdog_config(self.motion_watchdog_timeout_ms, require_echo=True)
		self.add_on_set_parameters_callback(self._on_parameters_changed)
		self.watchdog_heartbeat_timer = self.create_timer(
			1.0 / self.watchdog_heartbeat_rate_hz,
			self.send_watchdog_heartbeat,
		)
		self.watchdog_status_timer = self.create_timer(
			1.0,
			self.request_watchdog_status,
		)
		self.send_watchdog_heartbeat()
		self.request_watchdog_status()

	@staticmethod
	def _validate_watchdog_settings(timeout_ms, heartbeat_rate_hz):
		if not 100 <= timeout_ms <= 5000:
			raise ValueError('motion watchdog timeout must be in [100, 5000] ms')
		if not 1.0 <= heartbeat_rate_hz <= 50.0:
			raise ValueError('watchdog heartbeat rate must be in [1.0, 50.0] Hz')
		minimum_timeout_ms = 3.0 * 1000.0 / heartbeat_rate_hz
		if timeout_ms < minimum_timeout_ms:
			raise ValueError(
				'motion watchdog timeout must cover at least 3 heartbeat periods'
			)

	def _apply_deadzone_pwm(self, values, require_echo):
		values = tuple(int(value) for value in values)
		if any(value < 0 or value > 3000 for value in values):
			raise ValueError('motor dead-zone PWM values must be in [0, 3000]')
		self._configuring_deadzone_pwm = True
		try:
			# Stop once, then leave the serial link free of 20 Hz motion traffic
			# until the firmware's configuration echo has been received.
			self.car.set_motion(0.0, 0.0, 0.0)
			time.sleep(0.08)
			for _ in range(5):
				self.car.set_ackermann_deadzone_pwm(*values)
				deadline = time.monotonic() + 0.25
				while time.monotonic() < deadline:
					if self.car.get_ackermann_deadzone_pwm() == values:
						self._deadzone_pwm_values = values
						self.get_logger().info(
							'STM32 Ackermann dead-zone PWM confirmed: '
							'm1_forward=%d m2_forward=%d m1_reverse=%d m2_reverse=%d'
							% values
						)
						return True
					time.sleep(0.01)
			if require_echo:
				raise RuntimeError('STM32 did not echo Ackermann dead-zone PWM parameters')
			return False
		finally:
			self._configuring_deadzone_pwm = False

	def _apply_steering_config(self, values, require_echo):
		values = tuple(int(value) for value in values)
		max_angle, center_offset = values
		if not 1 <= max_angle <= 25:
			raise ValueError('maximum steering angle must be in [1, 25] degrees')
		if not -40 <= center_offset <= 40:
			raise ValueError('steering centre offset must be in [-40, 40] degrees')
		self._configuring_steering_config = True
		try:
			self.car.set_motion(0.0, 0.0, 0.0)
			time.sleep(0.08)
			for _ in range(5):
				self.car.set_ackermann_steering_config(max_angle, center_offset)
				deadline = time.monotonic() + 0.25
				while time.monotonic() < deadline:
					if self.car.get_ackermann_steering_config() == values:
						self._steering_config_values = values
						self.max_steering_angle_deg = max_angle
						self.steering_center_offset_deg = center_offset
						self.get_logger().info(
							'STM32 Ackermann steering config confirmed: '
							'max_angle=%d deg center_offset=%d deg'
							% values
						)
						return True
					time.sleep(0.01)
			if require_echo:
				raise RuntimeError('STM32 did not echo Ackermann steering config')
			return False
		finally:
			self._configuring_steering_config = False

	def _apply_watchdog_config(self, timeout_ms, require_echo):
		timeout_ms = int(timeout_ms)
		self._configuring_watchdog = True
		try:
			for _ in range(5):
				self.car.set_motion_watchdog_timeout(timeout_ms)
				deadline = time.monotonic() + 0.25
				while time.monotonic() < deadline:
					status = self.car.get_motion_watchdog_status()
					if status is not None and status[0] == timeout_ms:
						self.motion_watchdog_timeout_ms = timeout_ms
						self.get_logger().info(
							'STM32 motion watchdog confirmed: timeout=%d ms'
							% timeout_ms
						)
						return True
					time.sleep(0.01)
			if require_echo:
				raise RuntimeError('STM32 did not echo motion watchdog configuration')
			return False
		finally:
			self._configuring_watchdog = False

	def _on_parameters_changed(self, parameters):
		deadzone_candidate = dict(zip(self._deadzone_pwm_parameter_names, self._deadzone_pwm_values))
		steering_candidate = dict(zip(self._steering_config_parameter_names, self._steering_config_values))
		deadzone_changed = False
		steering_changed = False
		watchdog_timeout_ms = self.motion_watchdog_timeout_ms
		watchdog_heartbeat_rate_hz = self.watchdog_heartbeat_rate_hz
		watchdog_timeout_changed = False
		watchdog_rate_changed = False
		for parameter in parameters:
			if parameter.name in deadzone_candidate:
				if not isinstance(parameter.value, int) or isinstance(parameter.value, bool):
					return SetParametersResult(
						successful=False,
						reason='%s must be an integer PWM count' % parameter.name,
					)
				deadzone_candidate[parameter.name] = parameter.value
				deadzone_changed = True
			elif parameter.name in steering_candidate:
				if not isinstance(parameter.value, int) or isinstance(parameter.value, bool):
					return SetParametersResult(
						successful=False,
						reason='%s must be an integer degree value' % parameter.name,
					)
				steering_candidate[parameter.name] = parameter.value
				steering_changed = True
			elif parameter.name == 'motion_watchdog_timeout_ms':
				if not isinstance(parameter.value, int) or isinstance(parameter.value, bool):
					return SetParametersResult(
						successful=False,
						reason='motion_watchdog_timeout_ms must be an integer',
					)
				watchdog_timeout_ms = parameter.value
				watchdog_timeout_changed = True
			elif parameter.name == 'watchdog_heartbeat_rate_hz':
				if not isinstance(parameter.value, (int, float)) or isinstance(parameter.value, bool):
					return SetParametersResult(
						successful=False,
						reason='watchdog_heartbeat_rate_hz must be numeric',
					)
				watchdog_heartbeat_rate_hz = float(parameter.value)
				watchdog_rate_changed = True
		if not (deadzone_changed or steering_changed or watchdog_timeout_changed or watchdog_rate_changed):
			return SetParametersResult(successful=True)
		deadzone_values = tuple(
			deadzone_candidate[name] for name in self._deadzone_pwm_parameter_names
		)
		steering_values = tuple(
			steering_candidate[name] for name in self._steering_config_parameter_names
		)
		if any(value < 0 or value > 3000 for value in deadzone_values):
			return SetParametersResult(
				successful=False,
				reason='motor dead-zone PWM values must be in [0, 3000]',
			)
		if not 1 <= steering_values[0] <= 25:
			return SetParametersResult(
				successful=False,
				reason='maximum steering angle must be in [1, 25] degrees',
			)
		if not -40 <= steering_values[1] <= 40:
			return SetParametersResult(
				successful=False,
				reason='steering centre offset must be in [-40, 40] degrees',
			)
		try:
			self._validate_watchdog_settings(
				watchdog_timeout_ms,
				watchdog_heartbeat_rate_hz,
			)
		except ValueError as error:
			return SetParametersResult(successful=False, reason=str(error))
		if deadzone_changed or steering_changed:
			with self._motion_cmd_lock:
				self._motion_cmd = (0.0, 0.0, 0.0)
				self._steering_angle_target_rad = None
		try:
			if steering_changed and not self._apply_steering_config(steering_values, require_echo=False):
				return SetParametersResult(successful=False, reason='STM32 did not acknowledge steering config')
			if deadzone_changed and not self._apply_deadzone_pwm(deadzone_values, require_echo=False):
				return SetParametersResult(successful=False, reason='STM32 did not acknowledge dead-zone PWM values')
			if watchdog_timeout_changed and not self._apply_watchdog_config(watchdog_timeout_ms, require_echo=False):
				return SetParametersResult(successful=False, reason='STM32 did not acknowledge watchdog timeout')
			if watchdog_rate_changed:
				self.watchdog_heartbeat_rate_hz = watchdog_heartbeat_rate_hz
				self.destroy_timer(self.watchdog_heartbeat_timer)
				self.watchdog_heartbeat_timer = self.create_timer(
					1.0 / self.watchdog_heartbeat_rate_hz,
					self.send_watchdog_heartbeat,
				)
		except Exception as error:
			return SetParametersResult(successful=False, reason=str(error))
		return SetParametersResult(successful=True)

	def send_watchdog_heartbeat(self):
		try:
			self.car.send_motion_watchdog_heartbeat()
		except Exception as error:
			if not self._serial_error_reported:
				self.get_logger().error('serial watchdog heartbeat failed: %s' % error)
				self._serial_error_reported = True

	def request_watchdog_status(self):
		try:
			self.car.request_motion_watchdog_status()
		except Exception as error:
			if not self._serial_error_reported:
				self.get_logger().error('serial watchdog status request failed: %s' % error)
				self._serial_error_reported = True

	def publish_watchdog_status(self, time_stamp):
		message = DiagnosticArray()
		message.header.stamp = time_stamp.to_msg()
		status_message = DiagnosticStatus()
		status_message.name = 'omnifleet_a2/stm32_motion_watchdog'
		status_message.hardware_id = 'stm32_chassis'
		status = self.car.get_motion_watchdog_status()
		status_age = self.car.get_motion_watchdog_status_age()
		if status is None or status_age > 2.5:
			status_message.level = DiagnosticStatus.ERROR
			status_message.message = 'STM32 watchdog status unavailable'
			values = (
				('nx_heartbeat_rate_hz', '%.3f' % self.watchdog_heartbeat_rate_hz),
				('status_age_sec', 'inf' if status is None else '%.3f' % status_age),
			)
		else:
			timeout_ms, elapsed_ms, armed, stopped, trigger_count = status
			if stopped:
				status_message.level = DiagnosticStatus.ERROR
				status_message.message = 'communication-loss watchdog stopped the motors'
			elif not armed:
				status_message.level = DiagnosticStatus.WARN
				status_message.message = 'waiting for first NX heartbeat'
			else:
				status_message.level = DiagnosticStatus.OK
				status_message.message = 'heartbeat active'
			if (
				self._last_watchdog_trigger_count is not None
				and trigger_count > self._last_watchdog_trigger_count
			):
				self.get_logger().error(
					'STM32 communication-loss watchdog triggered; count=%d'
					% trigger_count
				)
			self._last_watchdog_trigger_count = trigger_count
			values = (
				('timeout_ms', str(timeout_ms)),
				('elapsed_since_heartbeat_ms', str(elapsed_ms)),
				('armed', str(armed).lower()),
				('motors_stopped_by_watchdog', str(stopped).lower()),
				('trigger_count', str(trigger_count)),
				('nx_heartbeat_rate_hz', '%.3f' % self.watchdog_heartbeat_rate_hz),
				('status_age_sec', '%.3f' % status_age),
			)
		status_message.values = [KeyValue(key=key, value=value) for key, value in values]
		message.status = [status_message]
		self.watchdogStatusPublisher.publish(message)
	#callback function
	def cmd_vel_callback(self,msg):
		# 小车运动控制，订阅者回调函数
		# Car motion control, subscriber callback function
		if not isinstance(msg, Twist): return
		# Preserve the requested body speed. STM32 owns its physical speed limits
		# and per-wheel PWM dead-zone compensation.
		vx = msg.linear.x * 1.0
		if abs(vx) <= 1e-6:
			vx = 0.0
			angular = 0.0
		else:
			angular = msg.angular.z * 1.0

		# During actual vehicle motion, STM32 remains the sole owner of Ackermann
		# inverse kinematics. NX only converts SI units to firmware units.
		motion_cmd = (vx * 1000.0, 0.0, angular * 1000.0)
		with self._motion_cmd_lock:
			self._motion_cmd = motion_cmd
			self._steering_angle_target_rad = None
			self._steering_stop_sent = False
		# Forward this received command exactly once. The STM32 watchdog owns
		# communication-loss stopping; ROS must not keep an old command alive.
		self.send_motion_command()

		now = Clock().now().nanoseconds / 1e9
		if now - self._last_cmd_log_time > 0.5:
			self._last_cmd_log_time = now
			self.get_logger().info(
				'STM32 tx FUNC_MOTION: Vx=%d mm/s Vy=0 Vz=%d mrad/s '
				'(Twist v=%.3f m/s wz=%.3f rad/s; kinematics_owner=stm32)'
				% (motion_cmd[0], motion_cmd[2], vx, angular)
			)

	def steering_angle_target_callback(self, msg):
		"""Apply a finite steering target in radians; positive is left."""
		if not isinstance(msg, SteeringAngleCommand):
			return
		requested_rad = float(msg.steering_angle_rad)
		if not math.isfinite(requested_rad):
			self.get_logger().warning('ignored non-finite steering target')
			return
		with self._motion_cmd_lock:
			entering_explicit_steering = self._steering_angle_target_rad is None
			self._motion_cmd = (0.0, 0.0, 0.0)
			self._steering_angle_target_rad = requested_rad
			if entering_explicit_steering:
				self._steering_stop_sent = False
		self.send_motion_command()
		self.get_logger().info(
			'STM32 explicit steering target: %.4f rad (%.1f deg)'
			% (requested_rad, math.degrees(requested_rad))
		)

	def send_motion_command(self):
		if (
			getattr(self, '_configuring_deadzone_pwm', False)
			or getattr(self, '_configuring_steering_config', False)
		):
			return
		with self._motion_cmd_lock:
			vx, vy, vz = self._motion_cmd
			steering_angle_target_rad = self._steering_angle_target_rad

		try:
			if steering_angle_target_rad is None:
				self.car.set_motion(vx, vy, vz)
				self._steering_stop_sent = False
			else:
				# Entering explicit steering must stop the motors once. Re-sending
				# FUNC_MOTION(0,0,0) every cycle also commands steering centre in
				# firmware and fights the following manual steering packet.
				if not self._steering_stop_sent:
					self.car.set_motion(0.0, 0.0, 0.0)
					self._steering_stop_sent = True
				self.car.set_ackermann_steering(
					math.degrees(steering_angle_target_rad)
				)
			self._serial_error_reported = False
			motor_command = Twist()
			motor_command.linear.x = vx / 1000.0
			motor_command.angular.z = vz / 1000.0
			self.motorCommandPublisher.publish(motor_command)
		except Exception as error:
			if not self._serial_error_reported:
				self.get_logger().error(
					'serial command write failed; STM32 watchdog will stop motors: %s'
					% error
				)
				self._serial_error_reported = True
	def stop_and_close(self):
		if self._closed:
			return
		self._closed = True
		with self._motion_cmd_lock:
			self._motion_cmd = (0.0, 0.0, 0.0)
			self._steering_angle_target_rad = None
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
		self.publish_watchdog_status(time_stamp)
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
		motor_state = self.car.get_ackermann_motor_state()
		if motor_state is not None:
			motor_state_message = Float32MultiArray()
			motor_state_message.data = [float(value) for value in motor_state]
			self.motorStatePublisher.publish(motor_state_message)

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
		twist.angular.z = angular*1.0
		self.velPublisher.publish(twist)
		self.publish_odometry(time_stamp, vx, angular)
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
		# rospy.loginfo("vx: {}, angular: {}".format(twist.linear.x, twist.angular.z))
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
	driver = omnifleet_ackermann_driver('omnifleet_a2_driver')
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
