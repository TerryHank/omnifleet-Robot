# OmniFleet R4 · Ranger Mini 3.0 四驱四转

## Windows OTG 镜像下载

[百度网盘 · OmniFleet-Windows-OTG](https://pan.baidu.com/s/14TIGdgtB91Ytbr5oRPV0Mg?pwd=2baf)，提取码 `2baf`。

该分享文件夹包含 T2、A2 和 R4 三种车型的 Windows OTG 镜像。按底盘型号选择对应镜像。

| 分支 | 底盘 |
| --- | --- |
| [T2](https://github.com/TerryHank/omnifleet-Robot/tree/T2) | 履带 |
| [A2](https://github.com/TerryHank/omnifleet-Robot/tree/A2) | 阿克曼 |
| [R4](https://github.com/TerryHank/omnifleet-Robot/tree/R4) | Ranger Mini 3.0 四驱四转 |

车端 ROS 2 Humble 使用 Fast DDS，见 [Fast DDS 配置](README.workspace.md#fast-dds)。

## 源码

ROS 2 工作区和车端配置采自 2026-11-20 的 Ranger 3.0 Windows OTG 镜像。

- [`omnifleet_ws/src/vehicle/ranger_can/`](../omnifleet_ws/src/vehicle/ranger_can) 包含 CAN 配置和 `ranger3.launch.py`。CAN 速率为 500 kbit/s。
- [`omnifleet_ws/src/vehicle/ranger_ros2/`](../omnifleet_ws/src/vehicle/ranger_ros2) 和 [`omnifleet_ws/src/vehicle/ugv_sdk/`](../omnifleet_ws/src/vehicle/ugv_sdk) 包含 Ranger V3 ROS 2 和 CAN SDK 源码。
- [底盘服务配置](system/etc/systemd/system/omnifleet-t2-chassis.service.d/zzzzzz-ranger3.conf) 提供实际启动入口。[工作区说明](README.workspace.md) 说明控制链、里程计和车型配置。
- SDK 随附的 PDF 手册见 [AgileX SDK 上游文档](https://github.com/agilexrobotics/ugv_sdk/tree/f2704eacdc90357078cd93ec60aae08bb4baab35/docs)。

[源码索引](../omnifleet_ws/src/README.md) 按功能域列出各包。[env.bash](env.bash) 是车端环境脚本，恢复时仍安装到 `/home/iecme/omnifleet_ws/env.bash`。快照清单沿用原采集路径。
