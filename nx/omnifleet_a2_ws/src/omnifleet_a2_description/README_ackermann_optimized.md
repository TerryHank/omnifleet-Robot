# Lunshi Ackermann Optimized URDF

本包在原始 SolidWorks STL 视觉模型基础上重构为 ROS2 常见阿克曼结构：

- `front_left_steering_joint`: position command/state
- `front_right_steering_joint`: position command/state
- `rear_left_wheel_joint`: velocity command/state
- `rear_right_wheel_joint`: velocity command/state
- `front_left_wheel_joint`: passive/state-only
- `front_right_wheel_joint`: passive/state-only

新增传感器：

- Hikrobot / 海康机器人 `MV-DT01SDU` ToF RGB-D camera placeholder, size `91 x 26 x 31.2 mm`.
- SLAMTEC `RPLIDAR S3` placeholder, size `55.6 x 55.6 x 41.3 mm`.

## 文件

- `urdf/lunshi_ackermann_optimized.urdf`：保留原始 200 个底盘 STL visual，加入阿克曼关节和传感器。
- `urdf/lunshi_ackermann_lite.urdf`：轻量版，底盘/轮子/传感器均用几何体，适合 RViz、Nav2、仿真调试。
- `../omnifleet_a2_bringup/config/ackermann_steering_controller.yaml`：按 ROS2 `ackermann_steering_controller` 命名准备的控制器参数。
- `config/sensor_frames.yaml`：摄像头和雷达安装位姿说明。

## 推荐使用

```bash
cd ~/omnifleet_a2_ws
colcon build --symlink-install
source install/setup.bash

# 轻量版，推荐日常调试
ros2 launch omnifleet_a2_description display_ackermann.launch.py

# 保留原始 SolidWorks STL 外观的版本
ros2 launch omnifleet_a2_description display_ackermann.launch.py model:=lunshi_ackermann_optimized.urdf
```

## 几何参数

- wheelbase: `0.362295943 m`
- steering_track_width: `0.264956799 m`
- traction_track_width: `0.245400019 m`
- wheel radius: `0.058528263 m`

## 传感器位姿

坐标遵循 ROS 习惯：`x` 前、`y` 左、`z` 上。

- `rplidar_s3_link`: `xyz = 0.020 0 0.13465`
- `laser_frame`: 相对 `rplidar_s3_link` 上移 `0.00990 m`
- `hik_camera_link`: `xyz = 0.240 0 0.125`, pitch down `8 deg`
- `camera_color_optical_frame` / `camera_depth_optical_frame`: 位于相机前表面中心，采用 ROS optical frame 方向。

## 注意

这里没有把真实舵机拉杆闭链做成 URDF 机械闭环。URDF/ros2_control 常见做法是用两个虚拟前轮转向 joint 表达运动学，真实硬件层把两个虚拟转角合成为一个舵机 PWM。
