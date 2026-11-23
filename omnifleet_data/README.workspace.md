# OmniFleet Ranger Mini 3.0 四驱四转工作区

系统底包：124 的 2026-11-20 完整镜像，保留 MOLA、相机、模型、地图及烧录修复。
车型代码：可恢复的 104 Ranger 适配和 2026-11-11 单点导航修复，来源见 /usr/local/share/omnifleet-image/ranger3-source.json。

底盘采用 Ranger Mini 3.0 官方 ROS 2 SDK 及对应 V3 协议补丁，CAN 500 kbit/s，自动识别 gs_usb 适配器。
启动入口 omnifleet-t2-chassis.service 的最终覆盖配置 zzzzzz-ranger3.conf，启动 ranger3.launch.py。
控制链路 /navigation/nav_cmd_vel → local_navigation → /navigation/cmd_vel_safe → Ranger SDK。
唯一兼容里程计 /odom 由 CAN 反馈节点发布，SDK 独立输出 /ranger_sdk/odom。

车型轮廓 0.72 × 0.50 m；车体传感器 TF、MOLA 和接收机专用网络沿用 124 系统环境。
普通联网使用 DHCP。车辆编号由调度分配，初始身份按 DHCP 地址尾段生成；EasyTier 也使用自动地址和主机名。
允许横移、斜移和四轮转向，网页使用 Ranger 运动面板。
没有连接实车进行运动或烧录验收，软件验证记录随完整工具包交付。

## Fast DDS

车端 ROS 2 Humble 使用 `rmw_fastrtps_cpp`。快照中的 [robot.env](system/etc/omnifleet_t2/robot.env) 设置 `ROS_DOMAIN_ID=101`、`ROS_LOCALHOST_ONLY=0` 和 `RMW_FASTRTPS_USE_QOS_FROM_XML=1`，并加载 `/etc/omnifleet_t2/fastdds-local.xml`。[fastdds-local.xml](system/etc/omnifleet_t2/fastdds-local.xml) 显式启用回环 UDPv4 和共享内存（SHM）。即使 `ROS_LOCALHOST_ONLY=0`，这份 XML 的车端 UDP 仍绑定 `127.0.0.1`。

局域网调度通过 DDS Router 转发配置允许的 ROS 数据。仓库保留 [fastdds-router.yaml](system/etc/omnifleet_t2/fastdds-router.yaml)、[路由服务](system/etc/systemd/system/omnifleet-fastdds-router.service) 和 [广播发现与接入](../omnifleet_ws/src/system/omnifleet_rmf_adapter/BROADCAST_DISCOVERY.md)。车辆广播用于发布身份和路由端口，调度根据广播生成连接配置。Foxglove 远程客户端连接车端 Foxglove Bridge 的 WebSocket。

R4 镜像快照沿用了底包的域号和旧地址。装车后按本车有效的 `robot.env`、路由配置及广播报文核对 Domain 和地址。
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

