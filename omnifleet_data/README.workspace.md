# OmniFleet T2 · 124 工作区

| 项目 | 本机配置 |
| --- | --- |
| 主机与工作区 | `iecme@192.168.3.124`，`/home/iecme/omnifleet_ws` |
| ROS | Humble，`robot_101`，见 [Fast DDS](#fast-dds) |
| 底盘 | 亚博履带 STM32，`omnifleet_chassis_driver t2_driver` |
| 环境与数据 | [env.bash](env.bash)，恢复车端时将此脚本安装到 `/home/iecme/omnifleet_ws/env.bash`，供现有 systemd 服务加载。持久数据在 `/home/iecme/omnifleet_data` |

亚博底盘左 M2、右 M1，串口别名 `/dev/omnifleet_t2_stm32`。STM32 回传 SBUS，ROS 负责摇杆优先级和 CH5 三挡。

## Fast DDS

车端 ROS 2 Humble 使用 `rmw_fastrtps_cpp`。快照中的 [robot.env](system/etc/omnifleet_t2/robot.env) 设置 `ROS_DOMAIN_ID=101`、`ROS_LOCALHOST_ONLY=0` 和 `RMW_FASTRTPS_USE_QOS_FROM_XML=1`，并加载 `/etc/omnifleet_t2/fastdds-local.xml`。[fastdds-local.xml](system/etc/omnifleet_t2/fastdds-local.xml) 显式启用回环 UDPv4 和共享内存（SHM）。即使 `ROS_LOCALHOST_ONLY=0`，这份 XML 的车端 UDP 仍绑定 `127.0.0.1`。

局域网调度通过 DDS Router 转发配置允许的 ROS 数据。仓库保留 [fastdds-router.yaml](system/etc/omnifleet_t2/fastdds-router.yaml)、[路由服务](system/etc/systemd/system/omnifleet-fastdds-router.service) 和 [广播发现与接入](../omnifleet_ws/src/system/omnifleet_rmf_adapter/BROADCAST_DISCOVERY.md)。车辆广播用于发布身份和路由端口，调度根据广播生成连接配置。Foxglove 远程客户端连接车端 Foxglove Bridge 的 WebSocket。

在车端终端读取同一份环境后检查 ROS 图：

```bash
source /opt/ros/humble/setup.bash
set -a
source /etc/omnifleet_t2/robot.env
set +a
printenv RMW_IMPLEMENTATION ROS_DOMAIN_ID ROS_LOCALHOST_ONLY FASTRTPS_DEFAULT_PROFILES_FILE RMW_FASTRTPS_USE_QOS_FROM_XML
ros2 node list
ros2 topic list -t
```

从其他 RMW 切换后，如果 ROS 2 CLI 还在使用旧 daemon，先在该环境中运行 `ros2 daemon stop`，再重新列出节点。排查服务时用 `systemctl cat <服务名>` 查看 `EnvironmentFile` 和 `ExecStart`，以服务实际加载的环境为准。Fast DDS 的 XML 路径由 `FASTRTPS_DEFAULT_PROFILES_FILE` 指定。参见 [Fast DDS 环境变量](https://fast-dds.docs.eprosima.com/en/2.6.x/fastdds/env_vars/env_vars.html)。

## 车端主链

- Airy 点云和 IMU 进入 MOLA。`integrated` 使用 [StateEstimationSimple 配置](../omnifleet_ws/src/localization/omnifleet_mola/mola_state_estimation_simple/config/tracked-integrated-live-system.yaml)，其 [LiDAR 流水线](../omnifleet_ws/src/localization/omnifleet_mola/mola_lidar_odometry/pipelines/lidar3d-gicp.yaml) 配置了 `Linear` 去畸变。导航点云接口为 `/navigation/deskewed_points`。
- Nav2 服务入口是 `omnifleet-t2-pure-lio-nav2.service`。速度经 `/navigation/nav_cmd_vel` → `local_navigation` → `/navigation/cmd_vel_safe` 交给底盘。
- 触屏点位走 `/navigation/goal_point`，使用 `point_goal_checker`。近障脱困读取当前导航控制器限速。
- 车队接口由本机导航按现有许可、定位 epoch 和租约处理。实车协同状态以对应验收记录为准。

## 配置与界面

| 项目 | 入口 |
| --- | --- |
| Nav2 永久参数 | [nav2_t2.yaml](../omnifleet_ws/src/planning/omnifleet_planner/config/nav2_t2.yaml)，参数保存和 [navigation.launch.py](../omnifleet_ws/src/system/omnifleet_bringup/launch/navigation.launch.py) 使用同一份源码配置 |
| 本机导航 | [local-navigation.json](../omnifleet_ws/src/control/omnifleet_local_navigation/config/local-navigation.json)，由 `omnifleet-local-navigation.service` 加载 |
| 车端环境和桥接 | `/etc/omnifleet_t2/robot.env`、`/etc/omnifleet_t2/foxglove.yaml` |
| Foxglove | 网页 `8780`，WebSocket `8765` |
| RGB-D | `omnifleet-t2-rgbd-camera.service`，启动脚本在 `/home/iecme/orbbec345lg-v2.10.6/` |

- 遥控导航 App 固定使用 `ws://192.168.144.108:8765/`。接收机 LAN 使用同一地址的 `/24`，机器人配网走 `https://192.168.144.108:8766`（`omnifleet-wifi.service`）。

源码分域见 [源码索引](../omnifleet_ws/src/README.md)。`build/`、`install/`、`log/` 是构建产物和日志。
