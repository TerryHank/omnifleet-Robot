# encoding: utf-8
"""
@File: motor_odom_node.py
@Brief: 编码器里程计 + 运动控制节点
依赖: ros_robot_controller (需先打 SDK 补丁)

功能:
  1. 从 STM32 读取编码器数据，发布 /odom
  2. 订阅 /cmd_vel，转发给底盘
  3. Action: MoveDistance(前进指定距离)
  4. Action: RotateAngle(旋转指定角度)

STM32 上报协议 (PACKET_FUNC_MOTOR=3, sub=0x02):
  [0x02] [motor_count:1B] [id:1B][rps:4B float][counter:4B int32] ... [crc8:1B]
  注意: 需要 STM32 固件启用 motor 上报。当前出厂固件已禁用，需刷修改版。
"""
import math
import struct
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, Quaternion, TransformStamped
from std_msgs.msg import Header
from tf2_ros import TransformBroadcaster
from ros_robot_controller_msgs.msg import MotorsState, MotorState

# ---- 机器人运动学参数 (小履带底盘12V) ----
WHEEL_RADIUS = 0.020        # 驱动轮半径 (m) = 4cm / 2
WHEEL_BASE = 0.285          # 履带中心距 (m) = 28.5cm
TICKS_PER_REV = 3960.0      # 编码器每转脉冲数 (JGB520 = 11*4*90)
GEAR_RATIO = 1.0            # 额外减速比 (直驱=1.0)
MOTOR_COUNT = 2             # 电机数量 (左右各1)

# ---- PID 参数 ----
PID_KP_LINEAR = 1.5
PID_KI_LINEAR = 0.2
PID_KD_LINEAR = 0.1
PID_KP_ANGULAR = 2.0
PID_KI_ANGULAR = 0.15
PID_KD_ANGULAR = 0.05
MAX_LINEAR_SPEED = 0.3      # m/s
MAX_ANGULAR_SPEED = 1.0     # rad/s


class MotorOdomNode(Node):
    def __init__(self):
        super().__init__("motor_odom_node")
        cb_group = ReentrantCallbackGroup()

        # ---- 底盘 SDK (需先导入打了补丁的 Board) ----
        from ros_robot_controller.ros_robot_controller_sdk import Board
        self.board = Board()
        self.board.enable_reception()
        self.get_logger().info("Board connected")

        # ---- 发布 ----
        self.odom_pub = self.create_publisher(Odometry, "/odom", 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # ---- 订阅 ----
        self.create_subscription(Twist, "/cmd_vel", self.on_cmd_vel, 10)

        # ---- 定时器 (100Hz) ----
        self.dt = 0.01
        self.create_timer(self.dt, self.update)

        # ---- 状态 ----
        self.x = 0.0; self.y = 0.0; self.yaw = 0.0
        self.linear_vel = 0.0; self.angular_vel = 0.0
        self.last_encoders = None
        self.last_time = time.monotonic()

        # ---- PID ----
        self.target_distance = 0.0
        self.target_yaw = 0.0
        self.distance_traveled = 0.0
        self.yaw_changed = 0.0
        self.pid_mode = None  # None, "distance", "yaw"
        self.pid_error_sum = 0.0
        self.pid_last_error = 0.0

        self.get_logger().info(
            f"Motor Odom Node started. Params: R={WHEEL_RADIUS}m, B={WHEEL_BASE}m, {MOTOR_COUNT} motors"
        )

    # ====================== 编码器读取 ======================
    def read_motor_state(self):
        """返回 [(motor_id, rps, counter), ...] 或 None"""
        raw = self.board.get_motor_state()
        if raw is None or len(raw) < 2:
            return None
        count = raw[0]
        motors = []
        offset = 1
        for _ in range(count):
            if offset + 9 > len(raw):
                break
            mid, rps, cnt = struct.unpack("<Bfi", raw[offset:offset+9])
            motors.append((mid, rps, cnt))
            offset += 9
        return motors

    # ====================== 里程计更新 ======================
    def update(self):
        motors = self.read_motor_state()
        now = time.monotonic()
        dt = now - self.last_time
        self.last_time = now

        if motors is None or len(motors) < 2:
            # 没收到编码器数据，用 cmd_vel 做开环估计
            self.x += self.linear_vel * math.cos(self.yaw) * dt
            self.y += self.linear_vel * math.sin(self.yaw) * dt
            self.yaw += self.angular_vel * dt
        else:
            # 左右各1电机: id 0 = 左履带, id 1 = 右履带
            left_motors = [m for m in motors if m[0] == 0]
            right_motors = [m for m in motors if m[0] == 1]
            left_rps = left_motors[0][1] if left_motors else 0.0
            right_rps = right_motors[0][1] if right_motors else 0.0

            # 轮速 → 车速
            wheel_circ = 2.0 * math.pi * WHEEL_RADIUS
            v_left = left_rps * wheel_circ / GEAR_RATIO
            v_right = right_rps * wheel_circ / GEAR_RATIO
            self.linear_vel = (v_left + v_right) / 2.0
            self.angular_vel = (v_right - v_left) / WHEEL_BASE

            # 积分
            self.x += self.linear_vel * math.cos(self.yaw) * dt
            self.y += self.linear_vel * math.sin(self.yaw) * dt
            self.yaw += self.angular_vel * dt

        self.publish_odom()

        # PID 控制
        self.update_pid(dt)

    def publish_odom(self):
        msg = Odometry()
        msg.header = Header(stamp=self.get_clock().now().to_msg(), frame_id="odom")
        msg.child_frame_id = "base_footprint"
        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y
        cy = math.cos(self.yaw / 2); sy = math.sin(self.yaw / 2)
        msg.pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=sy, w=cy)
        msg.twist.twist.linear.x = self.linear_vel
        msg.twist.twist.angular.z = self.angular_vel
        self.odom_pub.publish(msg)

        t = TransformStamped()
        t.header = msg.header
        t.child_frame_id = "base_footprint"
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.rotation = msg.pose.pose.orientation
        self.tf_broadcaster.sendTransform(t)

    # ====================== cmd_vel 转发 ======================
    def on_cmd_vel(self, msg: Twist):
        """将 /cmd_vel 转为电机 rps 指令下发"""
        wheel_circ = 2.0 * math.pi * WHEEL_RADIUS
        v_linear = max(-MAX_LINEAR_SPEED, min(MAX_LINEAR_SPEED, msg.linear.x))
        v_angular = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, msg.angular.z))

        v_right = v_linear + v_angular * WHEEL_BASE / 2.0
        v_left = v_linear - v_angular * WHEEL_BASE / 2.0

        rps_left = v_left / wheel_circ * GEAR_RATIO
        rps_right = v_right / wheel_circ * GEAR_RATIO

        speeds = [[0, rps_left], [1, rps_right]]
        self.board.set_motor_speed(speeds)

    # ====================== PID 定点移动 ======================
    def move_distance(self, distance_m):
        """前进 distance_m 米 (正=前, 负=后)"""
        self.target_distance = distance_m
        self.distance_traveled = 0.0
        self.pid_error_sum = 0.0
        self.pid_last_error = 0.0
        self.pid_mode = "distance"
        self.get_logger().info(f"Starting move: {distance_m:.3f}m")

    def rotate_angle(self, angle_rad):
        """旋转 angle_rad 弧度 (正=左转)"""
        self.target_yaw = angle_rad
        self.yaw_changed = 0.0
        self.pid_error_sum = 0.0
        self.pid_last_error = 0.0
        self.pid_mode = "yaw"
        self.get_logger().info(f"Starting rotate: {math.degrees(angle_rad):.1f}°")

    def update_pid(self, dt):
        if self.pid_mode == "distance":
            error = self.target_distance - self.distance_traveled
            if abs(error) < 0.01:
                self.board.set_motor_speed([[0, 0], [1, 0]])
                self.pid_mode = None
                self.get_logger().info("Move done")
                return

            self.pid_error_sum += error * dt
            d_error = (error - self.pid_last_error) / dt if dt > 0 else 0
            speed = PID_KP_LINEAR * error + PID_KI_LINEAR * self.pid_error_sum + PID_KD_LINEAR * d_error
            speed = max(-MAX_LINEAR_SPEED, min(MAX_LINEAR_SPEED, speed))
            self.pid_last_error = error

            wheel_circ = 2.0 * math.pi * WHEEL_RADIUS
            rps = speed / wheel_circ * GEAR_RATIO
            self.board.set_motor_speed([[0, rps], [1, rps]])
            self.distance_traveled += self.linear_vel * dt

        elif self.pid_mode == "yaw":
            remaining = self.target_yaw - self.yaw_changed
            if abs(remaining) < 0.02:
                self.board.set_motor_speed([[0, 0], [1, 0]])
                self.pid_mode = None
                self.get_logger().info("Rotate done")
                return

            self.pid_error_sum += remaining * dt
            d_error = (remaining - self.pid_last_error) / dt if dt > 0 else 0
            ang_speed = PID_KP_ANGULAR * remaining + PID_KI_ANGULAR * self.pid_error_sum + PID_KD_ANGULAR * d_error
            ang_speed = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, ang_speed))
            self.pid_last_error = remaining

            self.board.set_motor_speed([
                [0, -ang_speed * 0.5], [1,  ang_speed * 0.5]
            ])
            self.yaw_changed += self.angular_vel * dt

    # ====================== 测试入口 ======================
    def test_move(self, distance=0.5):
        """非阻塞测试: 前进 distance 米"""
        self.move_distance(distance)

    def test_rotate(self, angle_deg=90.0):
        """非阻塞测试: 旋转 angle_deg 度"""
        self.rotate_angle(math.radians(angle_deg))

    def get_pose(self):
        return self.x, self.y, self.yaw


def main():
    rclpy.init()
    node = MotorOdomNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    # ---- 简单测试序列: 前进0.5m, 转90°, 后退0.5m ----
    import threading
    def test_sequence():
        time.sleep(2)
        node.get_logger().info("===== 测试: 前进 0.5m =====")
        node.test_move(0.5)
        time.sleep(5)
        node.get_logger().info("===== 测试: 左转 90° =====")
        node.test_rotate(90.0)
        time.sleep(5)
        node.get_logger().info("===== 测试: 后退 0.5m =====")
        node.test_move(-0.5)
        time.sleep(5)
        node.get_logger().info("===== 测试完成 =====")
        x, y, yaw = node.get_pose()
        node.get_logger().info(f"最终位姿: x={x:.3f}m, y={y:.3f}m, yaw={math.degrees(yaw):.1f}°")

    threading.Thread(target=test_sequence, daemon=True).start()

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    node.board.set_motor_speed([[0, 0], [1, 0]])
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
