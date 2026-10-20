#!/usr/bin/env python3
"""
动态TF标定脚本 — 覆盖 rslidar 帧的 Roll 角
原理: 在 /tf 上发布 base_link→rslidar 的修正TF，动态TF优先于 /tf_static

用法:
  python3 calibrate_roll.py 1.5    # Roll=1.5度
  python3 calibrate_roll.py -2.0   # Roll=-2.0度
  python3 calibrate_roll.py 0      # 清零，恢复原始

验证标定是否正确：
  1. 运行此脚本（如 roll=1.5）
  2. 开遥控，让小车原地转弯/跑圈
  3. 观察 /map 话题更新的 pgm 是否还有黑点
  4. 逐渐调整 roll 直到转弯时黑点消失
"""
import sys
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class RollCalibrator(Node):
    def __init__(self, roll_deg=0.0, pitch_deg=0.0):
        super().__init__('roll_calibrator')
        self.broadcaster = TransformBroadcaster(self)
        self.roll = math.radians(roll_deg)
        self.pitch = math.radians(pitch_deg)

        self.tf = TransformStamped()
        self.tf.header.frame_id = 'base_link'
        self.tf.child_frame_id = 'rslidar'  # 直接覆盖原始帧

        # 从当前 tf_static 读取的默认值
        self.base_x = -0.041
        self.base_y = 0.0
        self.base_z = 0.15

        self.update_transform()
        # 高频发布 (> glim 的查询频率)
        self.timer = self.create_timer(0.02, self.publish_tf)  # 50Hz
        self.get_logger().info(f'标定TF发布中: roll={roll_deg}° pitch={pitch_deg}°')
        self.get_logger().info(f'帧: base_link -> rslidar @ 50Hz')

    def update_transform(self):
        self.tf.transform.translation.x = self.base_x
        self.tf.transform.translation.y = self.base_y
        self.tf.transform.translation.z = self.base_z

        # Roll (绕X轴) + Pitch (绕Y轴)
        cr = math.cos(self.roll / 2)
        sr = math.sin(self.roll / 2)
        cp = math.cos(self.pitch / 2)
        sp = math.sin(self.pitch / 2)

        # 四元数: roll(pitch(0))
        self.tf.transform.rotation.x = sr * cp
        self.tf.transform.rotation.y = cr * sp
        self.tf.transform.rotation.z = -sr * sp
        self.tf.transform.rotation.w = cr * cp

    def publish_tf(self):
        self.tf.header.stamp = self.get_clock().now().to_msg()
        self.broadcaster.sendTransform(self.tf)


def main():
    rclpy.init()
    roll = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    pitch = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    node = RollCalibrator(roll, pitch)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
