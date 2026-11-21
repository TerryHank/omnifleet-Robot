# omnifleet_a2_bringup

`omnifleet_a2_bringup`是整车驱动、统一启动入口和生产诊断包。
它持有STM32串口，并负责装配定位、规划和行为包。
阿克曼逆解、转向限幅、左右轮目标速度和执行器控制只由STM32固件实现。

The core runtime owns `/dev/myserial` and publishes:

- `/omnifleet_a2/chassis/voltage`
- `/imu/data_raw`
- `/imu/mag`
- `/omnifleet_a2/chassis/velocity_raw`
- `/odom`（在现有底盘驱动中积分STM32编码器反馈，并发布`odom -> base_link`）
- `/omnifleet_a2/chassis/motor_state_raw`（M1/M2目标轮速、实际轮速、最终施加PWM和控制状态）
- `/joint_states`
- `/omnifleet_a2/chassis/edition`

The hardware driver subscribes directly to `/cmd_vel`. Nav2 publishes the same
standard topic without a steering adapter or command arbitration node.
There is no teleop repeater, command mux, zero-lock selector, velocity smoother,
or collision monitor in the minimal single-point navigation chain. The
hardware driver forwards each newly received command once and never keeps an
old nonzero command alive. The independent NX
heartbeat defaults to 10 Hz and the STM32 communication-loss timeout defaults
to 1000 ms; both are NX parameters and the timeout remains enforced by STM32 if
Linux or the serial transport fails. `/omnifleet_a2/chassis/motor_command_sent` mirrors successful
serial writes.
Stopped-vehicle steering is accepted only as an explicit radian target on
`/omnifleet_a2/chassis/steering_angle_cmd`; conversion to firmware degrees
happens only at the serial boundary and positive means left.
For vehicle motion it sends `FUNC_MOTION(Vx_mm_s, 0, Vz_mrad_s)`; it has no
wheelbase or `v,w -> steering` calculation. STM32 remains the sole owner of
Ackermann inverse kinematics and left/right drive-wheel targets. `/omnifleet_a2/chassis/velocity_raw`
reports the STM32
feedback as `linear.x` in m/s and `angular.z` in rad/s; `linear.y` is unused.
No second wheel-odometry adapter is started by the production launch. In the
MOLA production mode, the chassis driver is the sole owner of `/odom` and
`odom -> base_link`; the official MOLA bridge is the sole owner of
`map -> odom`.

`/omnifleet_a2/chassis/motor_state_raw.data` contains eight values in this order:
`target_m1_mm_s`, `target_m2_mm_s`, `actual_m1_mm_s`, `actual_m2_mm_s`,
`applied_pwm_m1`, `applied_pwm_m2`, `control_state_m1`, `control_state_m2`.
Control state 0 is exact zero and 1 is the OEM encoder PID with its configured
per-motor, per-direction PWM dead-zone offset. The four volatile offsets are
owned by the NX launch configuration and are sent to STM32 with echo
verification after every board boot; STM32 owns all compensation and actuator
control. The ground-tested R2 values are M1 forward `2050`, M2 forward `2250`,
M1 reverse `2000`, and M2 reverse `2200`.

The systemd service is the normal production entry point:

`omnifleet-a2-chassis.service` first runs
`omnifleet-a2-resolve-chassis-port`. Both attached CH340 devices use the same
VID/PID and expose no unique USB serial number, so the resolver passively reads
each free CH340 at 115200 baud, requires checksum-valid chassis feedback frames,
and only then creates `/dev/myserial`. It never writes to a probed serial port.

```bash
sudo systemctl status omnifleet-a2-chassis.service
sudo systemctl restart omnifleet-a2-chassis.service
journalctl -u omnifleet-a2-chassis.service -f
```

## 开机自检和问题闭环

```bash
ros2 run omnifleet_a2_bringup vehicle_status
ros2 run omnifleet_a2_bringup vehicle_task_log issues
journalctl -u omnifleet-boot-selfcheck.service -n 100 --no-pager
```

`omnifleet-boot-selfcheck.timer` 每次开机后只触发一次旁路观察，并以 Linux `boot_id` 拒绝同一次开机里的重复采样。它不参与任何整车服务的启动顺序，不阻止底盘、导航或其他任务，也不执行周期监测、补触发或手动重复自检。失败项只写为“待解决”；当前恢复不等于闭环，只有提供验证策略、修复引用、稳定窗口和证据后才可标记“已完善”。

`omnifleet-vehicle-status-publisher.service` 只把上述落盘报告和问题台账转换为标准 `/diagnostics`，供 Foxglove 的 Diagnostics Summary 清单显示。它不重新检查硬件，不发送控制命令，也不参与任何门控。

Do not start another STM32 serial driver while this service is active because
the service exclusively owns the serial port.

Watchdog parameters and monitoring:

```bash
ros2 param set /omnifleet_a2_driver motion_watchdog_timeout_ms 500
ros2 param set /omnifleet_a2_driver watchdog_heartbeat_rate_hz 10.0
ros2 topic echo /omnifleet_a2/chassis/watchdog_status
```

The timeout must cover at least three heartbeat periods. The status reports the
applied STM32 timeout, elapsed time since the last heartbeat, current stop flag,
and a cumulative trigger count. It is diagnostic output only and never gates
`/cmd_vel`.

## 生产导航与后端冷切换

生产服务固定使用MOLA，Nav2由官方`nav2_lifecycle_manager`以
`autostart=true`启动：

```bash
ros2 launch omnifleet_a2_bringup production.launch.py backend:=mola
```

GLIM和Cartographer只在停止生产导航服务后显式冷切换测试：

```bash
sudo systemctl stop omnifleet-a2-navigation.service
ros2 launch omnifleet_a2_bringup production.launch.py backend:=glim_cuda
# 或：backend:=cartographer_3d
```

MOLA原生地图使用其官方服务`/map_save`和`/map_load`。二维占据栅格使用
Nav2官方命令保存，不再经过项目自定义地图管理器：

```bash
ros2 service call /map_save mola_msgs/srv/MapSave \
  "{map_path: '/var/lib/omnifleet_a2/maps/mola/active/manual'}"
ros2 service call /map_load mola_msgs/srv/MapLoad \
  "{map_path: '/var/lib/omnifleet_a2/maps/mola/active/manual'}"
ros2 run nav2_map_server map_saver_cli -t /map -f /var/lib/omnifleet_a2/maps/map
```
