# OmniFleet 126 工作区

| 项目 | 本机配置 |
| --- | --- |
| 主机与工作区 | `iecme@192.168.3.126`，`/home/iecme/omnifleet_ws` |
| ROS | Humble，`robot_101`，`ROS_DOMAIN_ID=101`，`rmw_zenoh_cpp` |
| 底盘 | 亚博履带 STM32，`omnifleet_chassis_driver t2_driver` |
| 环境与数据 | [env.bash](env.bash)，持久数据在 `/home/iecme/omnifleet_data` |

亚博底盘左 M2、右 M1，串口别名 `/dev/omnifleet_t2_stm32`。STM32 回传 SBUS，ROS 负责摇杆优先级和 CH5 三挡。

## 车端主链

- Airy 点云和 IMU 进入 MOLA。`integrated` 使用 [StateEstimationSimple 配置](src/localization/omnifleet_mola/mola_state_estimation_simple/config/tracked-integrated-live-system.yaml)，其 [LiDAR 流水线](src/localization/omnifleet_mola/mola_lidar_odometry/pipelines/lidar3d-gicp.yaml) 配置了 `Linear` 去畸变。导航点云接口为 `/navigation/deskewed_points`。
- Nav2 服务入口是 `omnifleet-t2-pure-lio-nav2.service`。速度经 `/navigation/nav_cmd_vel` → `local_navigation` → `/navigation/cmd_vel_safe` 交给底盘。
- 触屏点位走 `/navigation/goal_point`，使用 `point_goal_checker`。近障脱困读取当前导航控制器限速。
- 车队接口由本机导航按现有许可、定位 epoch 和租约处理。实车协同状态以对应验收记录为准。

## 配置与界面

| 项目 | 入口 |
| --- | --- |
| Nav2 永久参数 | [nav2_t2.yaml](src/planning/omnifleet_planner/config/nav2_t2.yaml)，参数保存和 [navigation.launch.py](src/system/omnifleet_bringup/launch/navigation.launch.py) 使用同一份源码配置 |
| 本机导航 | [local-navigation.json](src/control/omnifleet_local_navigation/config/local-navigation.json)，由 `omnifleet-local-navigation.service` 加载 |
| 车端环境和桥接 | `/etc/omnifleet_t2/robot.env`、`/etc/omnifleet_t2/foxglove.yaml` |
| Foxglove | 网页 `8780`，WebSocket `8765` |
| RGB-D | `omnifleet-t2-rgbd-camera.service`，启动脚本在 `/home/iecme/orbbec345lg-v2.10.6/` |

- 遥控导航 App 固定使用 `ws://192.168.144.108:8765/`。接收机 LAN 使用同一地址的 `/24`，机器人配网走 `https://192.168.144.108:8766`（`omnifleet-wifi.service`）。

源码分域见 [src/README.md](src/README.md)。`build/`、`install/`、`log/` 是构建产物和日志。
