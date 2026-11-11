# omnifleet_bringup

`omnifleet_bringup`是整车驱动、安全命令链、统一启动入口和生产诊断包。
它持有STM32串口、命令仲裁和底盘安全限制，并负责装配定位、规划和行为包。
阿克曼逆解、转向限幅、左右轮目标速度和执行器控制只由STM32固件实现。

The core runtime owns `/dev/myserial` and publishes:

- `/voltage`
- `/imu/data_raw`
- `/imu/mag`
- `/vel_raw`
- `/wheel/odometry`（仅封装STM32速度反馈，不计算或积分位姿）
- `/joint_states`
- `/edition`

The hardware driver subscribes only to Collision Monitor output `/cmd_vel`.
Command producers must use:

- `/cmd_vel_teleop` for Foxglove control;
- `/cmd_vel_keyboard` for keyboard control;
- `/cmd_vel_nav_raw` for Nav2 controller/behavior output;
- `/cmd_vel_vision` for safety-gated visual following;
- `/cmd_vel_nav_smoothed` and `/cmd_vel_nav_adjusted` inside the navigation chain;
- `/cmd_vel_muxed` only as Collision Monitor input;
- `/rrc_safety/zero_cmd` for short, timeout-bounded SLAM transition stops.

The persistent `/rrc_safety/zero_lock` path is disabled. The mux applies source
timeouts and priorities before Collision Monitor. The
hardware driver enforces a 0.35 second watchdog and resends the last valid
command at 20 Hz; `/motor_command_sent` mirrors successful serial writes.
For vehicle motion it sends `FUNC_MOTION(Vx_mm_s, 0, Vz_mrad_s)`; it has no
wheelbase or `v,w -> steering` calculation. STM32 remains the sole owner of
Ackermann inverse kinematics and left/right drive-wheel targets. `/vel_raw`
reports the STM32
feedback as `linear.x` in m/s, `linear.y` as steering degrees for legacy
compatibility, and `angular.z` in rad/s. `stm32_feedback_adapter` only wraps
that measured body twist in `/wheel/odometry` for slip diagnostics and does not
derive angular velocity or integrate a pose.

## 零速手动舵机

遥控输入在 `linear.x=0` 时支持纯舵机操作，后轮保持停止：

- 键盘 `j`：左转 `+30°`
- 键盘 `l`：右转 `-30°`
- 键盘 `k`：回中 `0°`
- Foxglove 左右按钮：直接使用 `linear.y` 中的目标角度（当前布局为 `±15°`）
- Foxglove 松开按钮：发送零 Twist，舵机回中

这条分支只调用 STM32 固件已有的手动舵机命令，不在 NX 上计算车辆运动学。
键盘必须发布到命令仲裁输入，不要直接绕过仲裁发布 `/cmd_vel`：

```bash
source /opt/ros/humble/setup.bash
set -a; source /etc/rrc/robot.env; set +a
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
  -p speed:=0.20 -p turn:=0.20 -p repeat_rate:=0.0 \
  -p key_timeout:=0.25 -r cmd_vel:=/cmd_vel_keyboard

# 等价的本车快捷命令（自动使用上述安全重映射和速度）
ros2 run omnifleet_bringup keyboard_teleop
```

The systemd service is the normal production entry point:

```bash
sudo systemctl status ackermann-stm32-chassis.service
sudo systemctl restart ackermann-stm32-chassis.service
journalctl -u ackermann-stm32-chassis.service -f
```

Do not start another STM32 serial driver while this service is active because
the service exclusively owns the serial port.
