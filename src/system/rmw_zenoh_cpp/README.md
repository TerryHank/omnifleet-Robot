# rmw_zenoh_cpp｜OmniFleet 工作区介绍

ROS 2 的 Zenoh RMW 与路由器；域号和机器人命名空间是两个不同概念。

- 功能域：`system`；源码：`/home/iecme/omnifleet_ws/src/system/rmw_zenoh_cpp`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [config/](config)：业务/算法运行配置。当前项：`DEFAULT_RMW_ZENOH_ROUTER_CONFIG.json5`、`DEFAULT_RMW_ZENOH_SESSION_CONFIG.json5`。

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
