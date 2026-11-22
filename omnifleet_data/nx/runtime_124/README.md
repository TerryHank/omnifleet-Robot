# 124 号车运行快照与恢复

采集自 124 的 Jetson Ubuntu 22.04 ARM64、ROS 2 Humble 环境。这里的 `files/` 按实机绝对路径组织，包含运行时加载的 MOLA 迁移包、RPP 控制器覆盖层、车端与网页资源、传感器驱动安装结果、调度运行文件和 systemd 单元。服务使用的完整路径见 [capture.json](capture.json)，基础包版本和启用状态见 [host-packages.tsv](host-packages.tsv) 与 [unit-files.tsv](unit-files.tsv)。

## 转向和导航

| 参数 | 实机值 | 配置 |
| --- | --- | --- |
| J4 舵机指令上限 | ±40° | [steering_limit.json](../omnifleet_a2_ws/deploy/chassis-111/steering_limit.json) |
| Hybrid A* 最小转弯半径 | 1.15 m | [nav2_glim.yaml](../../../omnifleet_ws/src/omnifleet_a2_planner/config/nav2_glim.yaml) |
| RPP 最小转弯半径 | 1.15 m | [controller_rpp.yaml](../../../omnifleet_ws/src/omnifleet_a2_planner/config/controller_rpp.yaml) |
| 备用 MPPI 最小转弯半径 | 1.15 m | [controller_mppi.yaml](../../../omnifleet_ws/src/omnifleet_a2_planner/config/controller_mppi.yaml) |

J4 指令角度与前轮等效转角之间有转向机构传动比。半径按 124 的标定取值，使该半径在左右转向时均落在 ±40° 指令范围内。2026-11-21 已回读实机参数，WSL 仿真的直线、绕柱、直角弯与倒车入位均到点且无碰撞。实车路线待复测。

## 恢复

在已装好匹配 JetPack、Ubuntu、ROS 2 Humble 的 ARM64 车端，以 `iecme` 用户克隆。若恢复到另一台车，按其硬件和网络检查 `/etc/omnifleet_a2/robot.env`、DDS 配置、设备规则、底盘及传感器外参。车端路径固定为 `/home/iecme`，保留原路径有助于解析 ROS 覆盖层的绝对链接。

```sh
git clone --single-branch --branch A2 https://github.com/TerryHank/omnifleet-Robot.git
cd omnifleet-Robot
sudo bash omnifleet_data/nx/runtime_124/restore-files.sh --dry-run /
sudo bash omnifleet_data/nx/runtime_124/restore-files.sh /
sudo systemctl daemon-reload
systemctl cat omnifleet-a2-chassis.service omnifleet-a2-mola.service omnifleet-a2-navigation.service
```

恢复脚本会复制工作区源码和原路径运行文件。根据 [unit-files.tsv](unit-files.tsv) 核对服务，再按底盘、传感器、MOLA、Nav2、网页和调度的顺序恢复启动。编译时请以 `package.xml`、工作区中的构建入口和实机选用的覆盖层为准，工作区包含并行保留的旧版包。若更换了 ROS 或 JetPack 版本，请用对应环境重新构建相关包。

公开快照包含项目源码和可分发的运行依赖。现场地图、录包、凭据、第三方相机 SDK 安装包和部分模型权重需在部署现场补齐。124 的控制板固件版本应在刷写前读取核对。[`omnifleet_data/stm32/`](../../stm32) 保留 121 归档，124 工作区的 `firmware/` 提供板端参考。
