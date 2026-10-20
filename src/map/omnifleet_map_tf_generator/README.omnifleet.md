# omnifleet_map_tf_generator｜OmniFleet 工作区介绍

地图坐标变换、TF 构造与共享地图栅格编解码。

- 功能域：`map`；源码：`/home/iecme/omnifleet_ws/src/map/omnifleet_map_tf_generator`。
- colcon 类型：`(ros.ament_python)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [setup.py](setup.py)：Python包安装与console_scripts入口。

## 工作区内声明依赖

- [omnifleet_fleet_common](../../common/omnifleet_fleet_common/README.omnifleet.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
