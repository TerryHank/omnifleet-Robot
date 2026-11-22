# mola_msgs｜OmniFleet 工作区介绍

ROS message, services, and actions used in other MOLA packages.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mola_msgs`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [srv/](srv)：服务定义。现有项：`MapLoad.srv`、`MapSave.srv`、`MolaRuntimeParamGet.srv`、`MolaRuntimeParamSet.srv`、`RelocalizeFromStateEstimator.srv`、`RelocalizeNearPose.srv`。

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
