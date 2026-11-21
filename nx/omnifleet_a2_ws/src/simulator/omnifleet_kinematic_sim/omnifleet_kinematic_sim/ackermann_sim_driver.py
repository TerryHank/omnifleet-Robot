#!/usr/bin/env python3
import math
import time
from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Float32, String
from tf2_ros import TransformBroadcaster


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


@dataclass(frozen=True)
class AckermannSolution:
    velocity: float
    yaw_rate: float
    center_steering: float
    left_steering: float
    right_steering: float
    front_left_speed: float
    front_right_speed: float
    rear_left_speed: float
    rear_right_speed: float


def solve_ackermann(
    velocity,
    requested_yaw_rate,
    wheel_base,
    front_track,
    rear_track,
    max_steering,
    stationary_steering=None,
):
    """Solve body Twist into wheel speed and steering targets.

    The real robot sends body velocity and yaw rate to STM32, where this inverse
    kinematics is owned.  This function is the simulation-only equivalent.
    """
    if abs(velocity) < 1e-9:
        steering = clamp(stationary_steering or 0.0, -max_steering, max_steering)
        return AckermannSolution(
            0.0, 0.0, steering, steering, steering, 0.0, 0.0, 0.0, 0.0
        )

    center = math.atan(wheel_base * requested_yaw_rate / velocity)
    center = clamp(center, -max_steering, max_steering)
    actual_yaw_rate = velocity * math.tan(center) / wheel_base

    if abs(actual_yaw_rate) < 1e-9:
        left_steering = right_steering = 0.0
    else:
        radius = velocity / actual_yaw_rate
        left_steering = math.atan(wheel_base / (radius - front_track / 2.0))
        right_steering = math.atan(wheel_base / (radius + front_track / 2.0))
        left_steering = clamp(left_steering, -max_steering, max_steering)
        right_steering = clamp(right_steering, -max_steering, max_steering)

    rear_left = velocity - actual_yaw_rate * rear_track / 2.0
    rear_right = velocity + actual_yaw_rate * rear_track / 2.0
    direction = math.copysign(1.0, velocity)
    front_left = direction * math.hypot(
        velocity - actual_yaw_rate * front_track / 2.0,
        actual_yaw_rate * wheel_base,
    )
    front_right = direction * math.hypot(
        velocity + actual_yaw_rate * front_track / 2.0,
        actual_yaw_rate * wheel_base,
    )
    return AckermannSolution(
        velocity,
        actual_yaw_rate,
        center,
        left_steering,
        right_steering,
        front_left,
        front_right,
        rear_left,
        rear_right,
    )


class AckermannSimDriver(Node):
    JOINT_NAMES = [
        "front_left_steering_joint",
        "front_right_steering_joint",
        "front_left_wheel_joint",
        "front_right_wheel_joint",
        "rear_left_wheel_joint",
        "rear_right_wheel_joint",
    ]

    def __init__(self):
        super().__init__("ackermann_sim_driver")
        self.declare_parameter("wheel_base", 0.362295943)
        self.declare_parameter("front_track", 0.264956799)
        self.declare_parameter("rear_track", 0.245400019)
        self.declare_parameter("wheel_radius", 0.058528263)
        self.declare_parameter("max_speed", 0.40)
        self.declare_parameter("max_yaw_rate", 0.30)
        self.declare_parameter("max_steering_angle", 0.523599)
        self.declare_parameter("stationary_steering_angle", 0.523599)
        self.declare_parameter("cmd_vel_timeout", 0.35)
        self.declare_parameter("update_rate", 50.0)
        self.declare_parameter("odom_frame", "odom")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("publish_tf", True)
        self.declare_parameter("simulated_voltage", 12.0)
        self.declare_parameter("initial_x", 0.0)
        self.declare_parameter("initial_y", 0.0)
        self.declare_parameter("initial_yaw", 0.0)

        self.wheel_base = float(self.get_parameter("wheel_base").value)
        self.front_track = float(self.get_parameter("front_track").value)
        self.rear_track = float(self.get_parameter("rear_track").value)
        self.wheel_radius = float(self.get_parameter("wheel_radius").value)
        self.max_speed = float(self.get_parameter("max_speed").value)
        self.max_yaw_rate = float(self.get_parameter("max_yaw_rate").value)
        self.max_steering = float(self.get_parameter("max_steering_angle").value)
        self.stationary_steering = float(
            self.get_parameter("stationary_steering_angle").value
        )
        self.timeout = float(self.get_parameter("cmd_vel_timeout").value)
        self.odom_frame = str(self.get_parameter("odom_frame").value)
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.publish_tf = bool(self.get_parameter("publish_tf").value)
        self.simulated_voltage = float(self.get_parameter("simulated_voltage").value)
        update_rate = max(1.0, float(self.get_parameter("update_rate").value))

        self.command = Twist()
        self.last_command_time = None
        self.zero_lock = False
        self.x = float(self.get_parameter("initial_x").value)
        self.y = float(self.get_parameter("initial_y").value)
        self.yaw = normalize_angle(float(self.get_parameter("initial_yaw").value))
        self.wheel_positions = [0.0, 0.0, 0.0, 0.0]
        self.last_update = time.monotonic()

        self.create_subscription(Twist, "/cmd_vel", self._command_callback, 10)
        self.create_subscription(Bool, "/rrc_safety/zero_lock", self._lock_callback, 10)
        self.odom_publisher = self.create_publisher(Odometry, "/odom", 20)
        self.wheel_odom_publisher = self.create_publisher(
            Odometry, "/wheel/odometry", 20
        )
        self.joint_publisher = self.create_publisher(JointState, "/joint_states", 20)
        self.velocity_publisher = self.create_publisher(Twist, "/vel_raw", 20)
        self.motor_publisher = self.create_publisher(
            Twist, "/motor_command_sent", 20
        )
        self.voltage_publisher = self.create_publisher(Float32, "/voltage", 5)
        self.mode_publisher = self.create_publisher(String, "/driver/mode", 1)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.create_timer(1.0 / update_rate, self._update)

        self.mode_publisher.publish(String(data="simulation"))
        self.get_logger().info(
            "Serial-free Ackermann simulation active: /cmd_vel -> /odom, /tf, "
            "/joint_states, /vel_raw"
        )

    def _command_callback(self, message):
        self.command = message
        self.last_command_time = time.monotonic()

    def _lock_callback(self, message):
        self.zero_lock = bool(message.data)
        if self.zero_lock:
            self.command = Twist()
            self.last_command_time = None

    def _current_solution(self, now):
        expired = (
            self.last_command_time is None
            or now - self.last_command_time > self.timeout
            or self.zero_lock
        )
        if expired:
            return solve_ackermann(
                0.0,
                0.0,
                self.wheel_base,
                self.front_track,
                self.rear_track,
                self.max_steering,
            )

        velocity = clamp(self.command.linear.x, -self.max_speed, self.max_speed)
        requested_yaw_rate = clamp(
            self.command.angular.z, -self.max_yaw_rate, self.max_yaw_rate
        )
        stationary = None
        if abs(velocity) < 1e-9:
            if abs(self.command.linear.y) > 1e-9:
                # Match the real driver's manual stationary steering contract:
                # cmd_vel.linear.y is degrees only while the wheels are stopped.
                stationary = math.radians(self.command.linear.y)
            elif abs(requested_yaw_rate) > 1e-9:
                stationary = math.copysign(
                    self.stationary_steering, requested_yaw_rate
                )
        return solve_ackermann(
            velocity,
            requested_yaw_rate,
            self.wheel_base,
            self.front_track,
            self.rear_track,
            self.max_steering,
            stationary,
        )

    def _update(self):
        now = time.monotonic()
        dt = clamp(now - self.last_update, 0.0, 0.10)
        self.last_update = now
        solution = self._current_solution(now)

        if abs(solution.yaw_rate) < 1e-9:
            self.x += solution.velocity * math.cos(self.yaw) * dt
            self.y += solution.velocity * math.sin(self.yaw) * dt
        else:
            next_yaw = self.yaw + solution.yaw_rate * dt
            radius = solution.velocity / solution.yaw_rate
            self.x += radius * (math.sin(next_yaw) - math.sin(self.yaw))
            self.y -= radius * (math.cos(next_yaw) - math.cos(self.yaw))
            self.yaw = normalize_angle(next_yaw)

        wheel_linear = [
            solution.front_left_speed,
            solution.front_right_speed,
            solution.rear_left_speed,
            solution.rear_right_speed,
        ]
        wheel_angular = [speed / self.wheel_radius for speed in wheel_linear]
        self.wheel_positions = [
            normalize_angle(position + velocity * dt)
            for position, velocity in zip(self.wheel_positions, wheel_angular)
        ]
        self._publish(solution, wheel_angular)

    def _publish(self, solution, wheel_angular):
        stamp = self.get_clock().now().to_msg()
        half_yaw = self.yaw / 2.0
        qz = math.sin(half_yaw)
        qw = math.cos(half_yaw)

        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = solution.velocity
        odom.twist.twist.angular.z = solution.yaw_rate
        self.odom_publisher.publish(odom)
        self.wheel_odom_publisher.publish(odom)

        if self.publish_tf:
            transform = TransformStamped()
            transform.header.stamp = stamp
            transform.header.frame_id = self.odom_frame
            transform.child_frame_id = self.base_frame
            transform.transform.translation.x = self.x
            transform.transform.translation.y = self.y
            transform.transform.rotation.z = qz
            transform.transform.rotation.w = qw
            self.tf_broadcaster.sendTransform(transform)

        joints = JointState()
        joints.header.stamp = stamp
        joints.name = list(self.JOINT_NAMES)
        joints.position = [
            solution.left_steering,
            solution.right_steering,
            self.wheel_positions[0],
            self.wheel_positions[1],
            self.wheel_positions[2],
            self.wheel_positions[3],
        ]
        joints.velocity = [0.0, 0.0] + wheel_angular
        self.joint_publisher.publish(joints)

        feedback = Twist()
        feedback.linear.x = solution.velocity
        feedback.linear.y = math.degrees(solution.center_steering)
        feedback.angular.z = solution.yaw_rate
        self.velocity_publisher.publish(feedback)

        motor = Twist()
        motor.linear.x = solution.velocity
        motor.angular.z = solution.yaw_rate
        if solution.velocity == 0.0:
            motor.linear.y = math.degrees(solution.center_steering)
        self.motor_publisher.publish(motor)
        self.voltage_publisher.publish(Float32(data=self.simulated_voltage))


def main(args=None):
    rclpy.init(args=args)
    node = AckermannSimDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
