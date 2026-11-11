#!/usr/bin/env python3
"""ROS 2 driver for the OmniFleet tracked chassis STM32 protocol."""

import math
import json
import os
import threading
import time
from pathlib import Path

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import DurabilityPolicy, QoSProfile
from sensor_msgs.msg import Imu, MagneticField
from std_msgs.msg import Bool, Float32, Int32, String
from std_srvs.srv import Trigger
from tf2_ros import TransformBroadcaster
from omnifleet_interfaces.srv import ServoCommand

from omnifleet_chassis_driver.Rosmaster_Lib import Rosmaster
from source_time_executor import SourceTimeExecutor, velocity_command_time, with_source_time


IMU_RAW_SCALE = 1000.0


def stm32_imu_to_rep103(x, y, z):
    """Undo the current ICM firmware Rx(pi) body mapping for ROS body axes."""
    return x, -y, -z


def sanitize_body_command(linear_x, linear_y, angular_z, max_angular):
    """Return a finite tracked-body command and lateral-input flag."""
    values = (linear_x, linear_y, angular_z)
    if not all(math.isfinite(float(value)) for value in values):
        return 0.0, 0.0, False
    vx = float(linear_x)
    wz = max(-max_angular, min(max_angular, float(angular_z)))
    if abs(vx) <= 1.0e-6:
        vx = 0.0
    if abs(wz) <= 1.0e-6:
        wz = 0.0
    return vx, wz, abs(float(linear_y)) > 1.0e-6


class OmnifleetT2Driver(Node):
    """Translate ROS body velocity into the STM32 tracked-motion command."""

    def __init__(self):
        super().__init__("omnifleet_t2_driver")
        self.declare_parameter("serial_port", "/dev/omnifleet_t2_stm32")
        self.declare_parameter("imu_link", "imu_link")
        self.declare_parameter("odom_frame", "odom")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("publish_odom_tf", True)
        self.declare_parameter("track_separation_m", 0.33)
        self.declare_parameter("motion_command_rate", 20.0)
        self.declare_parameter("cmd_vel_timeout", 0.35)
        self.declare_parameter("max_angular_speed_rps", 2.0)
        self.declare_parameter("publish_magnetometer", True)
        self.declare_parameter("magnetic_field_tesla_per_raw_unit", 1.0e-9)
        self.declare_parameter("angular_velocity_variance", 4.0e-4)
        self.declare_parameter("linear_acceleration_variance", 4.0e-2)
        self.declare_parameter("magnetic_field_variance", 2.5e-11)
        self.declare_parameter("pwm_compensation_m1", 900)
        self.declare_parameter("pwm_compensation_m2", 900)

        serial_port = str(self.get_parameter("serial_port").value)
        self.imu_link = str(self.get_parameter("imu_link").value)
        self.odom_frame = str(self.get_parameter("odom_frame").value)
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.track_separation_m = float(
            self.get_parameter("track_separation_m").value
        )
        if self.track_separation_m <= 0.0:
            raise ValueError("track_separation_m must be positive")
        command_rate = max(1.0, float(self.get_parameter("motion_command_rate").value))
        self.cmd_vel_timeout = max(0.10, float(self.get_parameter("cmd_vel_timeout").value))
        self.max_angular = max(0.01, float(self.get_parameter("max_angular_speed_rps").value))
        self.publish_magnetometer = bool(self.get_parameter("publish_magnetometer").value)
        self.mag_scale = float(self.get_parameter("magnetic_field_tesla_per_raw_unit").value)
        self.angular_variance = float(self.get_parameter("angular_velocity_variance").value)
        self.acceleration_variance = float(self.get_parameter("linear_acceleration_variance").value)
        self.magnetic_variance = float(self.get_parameter("magnetic_field_variance").value)

        self._lock = threading.Lock()
        self._target = (0.0, 0.0)
        self._joystick_target = (0.0, 0.0)
        self._joystick_until = 0.0
        self._stop_gear = None
        self._stop_gear_released_at = 0.0
        self._estop_input = False
        self._estop_latched = False
        self._estop_state = Path.home() / ".local/share/omnifleet_t2/local-navigation-state.json"
        self._estop_state_revision = None
        self.estop_active()
        self._last_command_time = time.monotonic()
        self._last_command_ros_ns = 0
        self._last_command_receive_time = self._last_command_time
        self._last_command_source_ros_ns = 0
        self._expired_command_count = 0
        self._command_received = False
        self._watchdog_reported = False
        self._serial_error_reported = False
        self._last_feedback_log_time = 0.0
        self._last_lateral_warning_time = 0.0
        self._closed = False
        self._odom_x = 0.0
        self._odom_y = 0.0
        self._odom_yaw = 0.0
        self._last_odometry_time = time.monotonic()

        self.car = Rosmaster(car_type=7, com=serial_port)
        self.car.create_receive_threading()
        self.servo_service = self.create_service(
            ServoCommand, "/t2/servo_command", self.servo_command_callback
        )
        for _ in range(3):
            self.car.set_motion(0, 0, 0)
            time.sleep(0.02)

        compensation = None
        for _ in range(3):
            try:
                compensation = self.car.get_tracked_pwm_compensation()
                break
            except Exception:
                time.sleep(0.1)
        if compensation is None:
            compensation = (
                int(self.get_parameter("pwm_compensation_m1").value),
                int(self.get_parameter("pwm_compensation_m2").value),
            )
            self.get_logger().warning(
                "STM32 未提供 PWM 补偿读回，保留参数默认值 %d/%d"
                % compensation
            )
        self.set_parameters([
            Parameter("pwm_compensation_m1", value=int(compensation[0])),
            Parameter("pwm_compensation_m2", value=int(compensation[1])),
        ])
        self.add_on_set_parameters_callback(self.set_runtime_parameters)

        self.create_subscription(Twist, os.environ.get("OMNIFLEET_CMD_VEL_INPUT", "/cmd_vel"), self.cmd_vel_callback, 1)
        self.create_subscription(Bool, "/navigation/estop", self.on_estop, 10)
        self.create_subscription(Bool, "/navigation/contact", self.on_contact, 10)
        self.create_subscription(Int32, "/RGBLight", self.rgb_light_callback, 10)
        self.create_subscription(Bool, "/Buzzer", self.buzzer_callback, 10)
        self.voltage_publisher = self.create_publisher(Float32, "/voltage", 20)
        self.voltage_display_publisher = self.create_publisher(
            String, "/voltage/display", 20
        )
        self.firmware_publisher = self.create_publisher(String, "/firmware/version", 10)
        self.edition_publisher = self.create_publisher(Float32, "/edition", 10)
        self.velocity_publisher = self.create_publisher(Twist, "/vel_raw", 50)
        self.odometry_publisher = self.create_publisher(Odometry, "/odom", 50)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.imu_publisher = self.create_publisher(Imu, "/imu/data_raw", 50)
        self.mag_publisher = self.create_publisher(MagneticField, "/imu/mag", 50)
        self.command_publisher = self.create_publisher(Twist, "/motor_command_sent", 20)
        self.command_timing_publisher = self.create_publisher(String, "/chassis/command_timing", 20)
        self.control_state_service = self.create_service(Trigger, "/chassis/control_state", self.control_state_callback)

        self.create_timer(1.0 / command_rate, self.send_motion_command)
        self.create_timer(0.1, self.publish_feedback)
        self.joystick = self.create_publisher(Twist, "/navigation/joystick_cmd_vel", 1)
        self.stop_gear_pub = self.create_publisher(
            Bool, "/navigation/joystick_stop_gear",
            QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL),
        )
        self.joystick_active = False
        self.create_timer(0.04, self.publish_joystick)
        self.get_logger().info(
            "履带底盘驱动已启动：串口=%s，M2=左履带，M1=右履带，履带中心距=%.3f m，PWM补偿=%d/%d"
            % (serial_port, self.track_separation_m, compensation[0], compensation[1])
        )

    def publish_joystick(self):
        try:
            state = self.car.poll_control_state()
        except OSError:
            state = None
        command = Twist()
        if state and state["failsafe"] == 0 and state["age_ms"] <= 100:
            def stick(channel):
                value = state["channels"][channel] - 1002
                return math.copysign(min(1.0, max(0, abs(value) - 60) / 660.0), value)

            gear = state["channels"][4]
            stop_gear = gear < 642
            if stop_gear != self._stop_gear:
                with self._lock:
                    if self._stop_gear and not stop_gear:
                        self._stop_gear_released_at = time.monotonic()
                    self._stop_gear = stop_gear
                    if stop_gear:
                        self._target = self._joystick_target = (0.0, 0.0)
                        self._command_received = False
                        self._joystick_until = 0.0
                self.stop_gear_pub.publish(Bool(data=stop_gear))
                if stop_gear:
                    self.send_motion_command()
            if not stop_gear:
                linear_limit, angular_limit = (0.70, 1.00) if gear < 1362 else (1.50, 1.80)
                command.linear.x = linear_limit * stick(2)
                command.angular.z = -angular_limit * stick(0)
        active = bool(command.linear.x or command.angular.z)
        if active or self.joystick_active:
            with self._lock:
                self._joystick_target = (command.linear.x, command.angular.z)
                self._joystick_until = time.monotonic() + self.cmd_vel_timeout
                if not active:
                    self._target = (0.0, 0.0)
                    self._command_received = False
            if active != self.joystick_active:
                self.get_logger().info("SBUS " + ("接管底盘" if active else "已回中或失联"))
            self.joystick.publish(command)
        self.joystick_active = active

    def on_estop(self, message):
        self._estop_input = bool(message.data)
        self._estop_latched |= self._estop_input

    def on_contact(self, message):
        self._estop_latched |= bool(message.data)

    def estop_active(self):
        try:
            revision = self._estop_state.stat().st_mtime_ns
            if revision != self._estop_state_revision:
                self._estop_latched = bool(json.loads(self._estop_state.read_text())["safety_latched"])
                self._estop_state_revision = revision
        except (OSError, ValueError, KeyError):
            pass
        return self._estop_input or self._estop_latched

    def set_runtime_parameters(self, parameters):
        names = {"pwm_compensation_m1", "pwm_compensation_m2"}
        updates = {parameter.name: parameter.value for parameter in parameters if parameter.name in names}
        if not updates:
            return SetParametersResult(successful=True)
        try:
            values = {
                name: int(self.get_parameter(name).value)
                for name in names
            }
            for name, value in updates.items():
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError("PWM 补偿必须是整数")
                values[name] = value
            with self._lock:
                moving_command = (
                    self._target != (0.0, 0.0)
                    and time.monotonic() - self._last_command_time <= self.cmd_vel_timeout
                )
            if moving_command:
                raise ValueError("底盘存在非零运动指令，请停车后再修改 PWM 补偿")
            self.get_logger().info(
                "正在写入 STM32 PWM 补偿：M1=%d M2=%d"
                % (values["pwm_compensation_m1"], values["pwm_compensation_m2"])
            )
            self.car.set_motion(0, 0, 0)
            actual = self.car.set_tracked_pwm_compensation(
                values["pwm_compensation_m1"],
                values["pwm_compensation_m2"],
            )
            self.get_logger().info(
                "STM32 PWM 补偿已回读确认：M1=%d M2=%d" % actual
            )
            return SetParametersResult(
                successful=True,
                reason="STM32 已永久保存并回读确认：M1=%d M2=%d" % actual,
            )
        except Exception as error:
            return SetParametersResult(successful=False, reason=str(error))

    @with_source_time
    def cmd_vel_callback(self, message, info):
        issued = velocity_command_time(message, info, self.cmd_vel_timeout)
        if issued is None:
            with self._lock:
                self._target = (0.0, 0.0)
                self._command_received = False
                self._expired_command_count += 1
            return
        vx, wz, lateral_ignored = sanitize_body_command(
            message.linear.x,
            message.linear.y,
            message.angular.z,
            self.max_angular,
        )
        with self._lock:
            if self._stop_gear or issued <= self._stop_gear_released_at:
                return
            self._target = (vx, wz)
            self._last_command_time = issued
            self._last_command_receive_time = time.monotonic()
            self._last_command_source_ros_ns = info.get('source_timestamp', 0) if isinstance(info, dict) else getattr(info, 'source_timestamp', 0)
            self._last_command_ros_ns = self.get_clock().now().nanoseconds
            self._command_received = True
            self._watchdog_reported = False
        now = time.monotonic()
        if lateral_ignored and now - self._last_lateral_warning_time > 2.0:
            self._last_lateral_warning_time = now
            self.get_logger().warning("履带底盘忽略 cmd_vel.linear.y，仅执行前进速度和转向角速度")

    def send_motion_command(self):
        with self._lock:
            expired = (
                not self._command_received
                or time.monotonic() - self._last_command_time > self.cmd_vel_timeout
            )
            vx, wz = (0.0, 0.0) if expired else self._target
            joystick_priority = time.monotonic() < self._joystick_until
            if self._stop_gear:
                vx, wz = 0.0, 0.0
            elif joystick_priority:
                vx, wz = self._joystick_target
            received_mono, received_ros = self._last_command_receive_time, self._last_command_ros_ns
            source_ros, expired_count = self._last_command_source_ros_ns, self._expired_command_count
            report_timeout = expired and self._command_received and not self._watchdog_reported
            if expired:
                self._watchdog_reported = True
        if self.estop_active():
            vx, wz = 0.0, 0.0
        send_mono = time.monotonic()
        send_ros = self.get_clock().now().nanoseconds
        write_ok = True
        try:
            # The tracked firmware closes the speed loop using the installed
            # channel map: M2 drives the left track and M1 drives the right track.
            # The selected front is opposite the MCU body X axis.
            self.car.set_motion(round(-vx * 1000.0), 0, round(wz * 1000.0))
            self._serial_error_reported = False
        except Exception as error:
            write_ok = False
            vx, wz = 0.0, 0.0
            if not self._serial_error_reported:
                self._serial_error_reported = True
                self.get_logger().error("底盘串口写入失败，已强制零速：%s" % error)
            try:
                self.car.set_motion(0, 0, 0)
            except Exception:
                pass
        sent = Twist()
        sent.linear.x = vx
        sent.angular.z = wz
        self.command_publisher.publish(sent)
        now_mono = time.monotonic()
        self.command_timing_publisher.publish(String(data=json.dumps({
            'input_receive_ros_ns':received_ros,'input_receive_monotonic':received_mono,
            'input_source_ros_ns':source_ros,'expired_command_count':expired_count,
            'serial_start_ros_ns':send_ros,'serial_start_monotonic':send_mono,
            'serial_end_ros_ns':self.get_clock().now().nanoseconds,'serial_end_monotonic':now_mono,
            'vx':vx,'wz':wz,'watchdog_expired':expired,'write_ok':write_ok,
            'joystick_priority':joystick_priority, 'joystick_stop_gear': self._stop_gear,
            'speed_feedback_age':now_mono-self.car.last_speed_frame_time if self.car.last_speed_frame_time is not None else None,
            'imu_feedback_age':now_mono-self.car.last_imu_frame_time if self.car.last_imu_frame_time is not None else None})))
        if report_timeout:
            self.get_logger().warning(
                "超过 %.2f 秒未收到 cmd_vel，已持续发送精确零速" % self.cmd_vel_timeout
            )

    def publish_feedback(self):
        stamp = self.get_clock().now().to_msg()
        voltage = Float32()
        voltage.data = float(self.car.get_battery_voltage())
        self.voltage_publisher.publish(voltage)
        voltage_display = String()
        voltage_display.data = f"{voltage.data:.1f} V"
        self.voltage_display_publisher.publish(voltage_display)

        firmware_value = self.car.get_version()
        firmware = String()
        firmware.data = firmware_value or "unknown"
        self.firmware_publisher.publish(firmware)
        edition = Float32()
        try:
            edition.data = float(firmware_value) if firmware_value else 0.0
        except ValueError:
            edition.data = 0.0
        self.edition_publisher.publish(edition)

        hardware_vx, _vy, wz = self.car.get_motion_data()
        vx = -hardware_vx
        velocity = Twist()
        velocity.linear.x = float(vx)
        velocity.linear.y = 0.0
        velocity.angular.z = float(wz)
        self.velocity_publisher.publish(velocity)

        odometry_time = time.monotonic()
        dt = odometry_time - self._last_odometry_time
        self._last_odometry_time = odometry_time
        if not 0.0 < dt <= 0.5:
            dt = 0.0
        midpoint_yaw = self._odom_yaw + 0.5 * float(wz) * dt
        self._odom_x += float(vx) * math.cos(midpoint_yaw) * dt
        self._odom_y += float(vx) * math.sin(midpoint_yaw) * dt
        self._odom_yaw = math.atan2(
            math.sin(self._odom_yaw + float(wz) * dt),
            math.cos(self._odom_yaw + float(wz) * dt),
        )
        quaternion_z = math.sin(0.5 * self._odom_yaw)
        quaternion_w = math.cos(0.5 * self._odom_yaw)

        odometry = Odometry()
        odometry.header.stamp = stamp
        odometry.header.frame_id = self.odom_frame
        odometry.child_frame_id = self.base_frame
        odometry.pose.pose.position.x = self._odom_x
        odometry.pose.pose.position.y = self._odom_y
        odometry.pose.pose.orientation.z = quaternion_z
        odometry.pose.pose.orientation.w = quaternion_w
        odometry.twist.twist.linear.x = float(vx)
        odometry.twist.twist.angular.z = float(wz)
        odometry.pose.covariance[0] = 0.02
        odometry.pose.covariance[7] = 0.02
        odometry.pose.covariance[14] = 1.0
        odometry.pose.covariance[21] = 0.01
        odometry.pose.covariance[28] = 0.01
        odometry.pose.covariance[35] = 0.05
        odometry.twist.covariance[0] = 0.01
        odometry.twist.covariance[7] = 0.04
        odometry.twist.covariance[14] = 1.0
        odometry.twist.covariance[21] = 0.01
        odometry.twist.covariance[28] = 0.01
        odometry.twist.covariance[35] = 0.04
        self.odometry_publisher.publish(odometry)

        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = self.odom_frame
        transform.child_frame_id = self.base_frame
        transform.transform.translation.x = self._odom_x
        transform.transform.translation.y = self._odom_y
        transform.transform.rotation.z = quaternion_z
        transform.transform.rotation.w = quaternion_w
        if bool(self.get_parameter("publish_odom_tf").value):
            self.tf_broadcaster.sendTransform(transform)

        ax, ay, az = stm32_imu_to_rep103(*self.car.get_accelerometer_data())
        gx, gy, gz = stm32_imu_to_rep103(*self.car.get_gyroscope_data())
        imu = Imu()
        imu.header.stamp = stamp
        imu.header.frame_id = self.imu_link
        imu.orientation_covariance[0] = -1.0
        imu.angular_velocity.x = gx / IMU_RAW_SCALE
        imu.angular_velocity.y = gy / IMU_RAW_SCALE
        imu.angular_velocity.z = gz / IMU_RAW_SCALE
        imu.linear_acceleration.x = ax / IMU_RAW_SCALE
        imu.linear_acceleration.y = ay / IMU_RAW_SCALE
        imu.linear_acceleration.z = az / IMU_RAW_SCALE
        for index in (0, 4, 8):
            imu.angular_velocity_covariance[index] = self.angular_variance
            imu.linear_acceleration_covariance[index] = self.acceleration_variance
        self.imu_publisher.publish(imu)

        if self.publish_magnetometer:
            mx, my, mz = stm32_imu_to_rep103(*self.car.get_magnetometer_data())
            mag = MagneticField()
            mag.header.stamp = stamp
            mag.header.frame_id = self.imu_link
            mag.magnetic_field.x = mx * self.mag_scale
            mag.magnetic_field.y = my * self.mag_scale
            mag.magnetic_field.z = mz * self.mag_scale
            for index in (0, 4, 8):
                mag.magnetic_field_covariance[index] = self.magnetic_variance
            self.mag_publisher.publish(mag)

        now = time.monotonic()
        if now - self._last_feedback_log_time > 5.0:
            self._last_feedback_log_time = now
            frames, checksum_errors, receive_errors, frame_age = self.car.get_transport_diagnostics()
            self.get_logger().info(
                "STM32反馈：vx=%.3f m/s wz=%.3f rad/s 帧=%d age=%.3fs 校验错=%d 接收错=%d"
                % (vx, wz, frames, frame_age, checksum_errors, receive_errors)
            )

    def control_state_callback(self, request, response):
        with self._lock:
            moving = self._target != (0.0,0.0) and time.monotonic()-self._last_command_time <= self.cmd_vel_timeout
        vx,_,wz = self.car.get_motion_data()
        moving = moving or abs(vx)>.01 or abs(wz)>.05
        if moving:
            response.success=False;response.message='Readback requires a stopped command target';return response
        try:
            state=self.car.get_control_state()
            response.success=True;response.message=json.dumps(state)
        except Exception as error:
            response.success=False;response.message=str(error)
        return response

    def rgb_light_callback(self, message):
        self.car.set_colorful_effect(message.data, 6, parm=1)

    def servo_command_callback(self, request, response):
        try:
            status, value0, value1, value2 = self.car.ftservo_command(
                request.operation, request.id, request.arg0, request.arg1, request.arg2
            )
            response.success = status == 0
            response.value0 = value0
            response.value1 = value1
            response.value2 = value2
            response.message = "ok" if response.success else "舵机返回错误状态 %d" % status
        except Exception as error:
            response.success = False
            response.message = str(error)
            self.get_logger().warning("FTServo命令失败：%s" % error)
        return response

    def buzzer_callback(self, message):
        self.car.set_beep(1 if message.data else 0)

    def stop_and_close(self):
        if self._closed:
            return
        self._closed = True
        with self._lock:
            self._target = (0.0, 0.0)
            self._command_received = False
        for _ in range(3):
            try:
                self.car.set_motion(0, 0, 0)
            except Exception as error:
                self.get_logger().error("关闭前发送零速失败：%s" % error)
                break
            time.sleep(0.02)
        try:
            self.car.close()
        except Exception as error:
            self.get_logger().error("关闭底盘串口失败：%s" % error)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = OmnifleetT2Driver()
        rclpy.spin(node, executor=SourceTimeExecutor())
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.stop_and_close()
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
