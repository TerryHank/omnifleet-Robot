# OmniFleet T2 · 履带

## Windows OTG 镜像下载

[百度网盘 · OmniFleet-Windows-OTG](https://pan.baidu.com/s/14TIGdgtB91Ytbr5oRPV0Mg?pwd=2baf)，提取码 `2baf`。

该分享文件夹包含 T2、A2 和 R4 三种车型的 Windows OTG 镜像。按底盘型号选择对应镜像。

| 分支 | 底盘 |
| --- | --- |
| [T2](https://github.com/TerryHank/omnifleet-Robot/tree/T2) | 履带 |
| [A2](https://github.com/TerryHank/omnifleet-Robot/tree/A2) | 阿克曼 |
| [R4](https://github.com/TerryHank/omnifleet-Robot/tree/R4) | Ranger Mini 3.0 四驱四转 |

## 源码

ROS 2 工作区和车端配置采自 124 号车。车端入口见 [124 工作区说明](README.workspace.md)。

- [`src/`](src) 为车端工作区源码。
- [`firmware/robot-124-cascade/`](firmware/robot-124-cascade) 为 124 号车当天的 STM32 级联控制固件源码。
- [`follow-media/`](follow-media)、[`web/`](web) 分别包含跟随视频服务和车端网页。
- [`system/`](system) 包含车端服务和配置。采集范围见 [快照说明](BACKUP_INFO.json)。
