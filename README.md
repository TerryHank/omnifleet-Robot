# OmniFleet A2 · 124 号阿克曼

本分支收录 124 号车在 2026-11-21 的源码、部署配置及 ARM64 运行快照。包含阿克曼底盘、Nav2、MOLA SLAM、Foxglove 前端、局域网发现及 Open-RMF 调度。

| 内容 | 路径 |
| --- | --- |
| ROS 2 工作区、固件参考、前端和部署配置 | [nx/omnifleet_a2_ws](nx/omnifleet_a2_ws) |
| 雷达及相机驱动源码 | [nx/sensor_drivers_ws](nx/sensor_drivers_ws) |
| 124 运行文件、服务、依赖清单和恢复步骤 | [nx/runtime_124](nx/runtime_124) |
| 121 旧版车端快照 | [nx/runtime_121](nx/runtime_121/README-121-snapshot.md) |

124 当前设定为舵机指令上限 ±40°、全局 Hybrid A* 与局部 RPP 最小转弯半径 1.15 m、底盘最低可行驶速度 0.12 m/s。Nav2 配置为开机启动。用 [恢复说明](nx/runtime_124/README.md) 确认设备与依赖，再恢复文件。

## Windows OTG 镜像下载

[百度网盘 · OmniFleet-Windows-OTG](https://pan.baidu.com/s/14TIGdgtB91Ytbr5oRPV0Mg?pwd=2baf)，提取码 `2baf`。

| 分支 | 底盘 |
| --- | --- |
| [T2](https://github.com/TerryHank/omnifleet-Robot/tree/T2) | 履带 |
| [A2](https://github.com/TerryHank/omnifleet-Robot/tree/A2) | 阿克曼 |
| [R4](https://github.com/TerryHank/omnifleet-Robot/tree/R4) | Ranger Mini 3.0 四驱四转 |
