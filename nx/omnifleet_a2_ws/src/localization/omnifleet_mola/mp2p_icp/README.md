# mp2p_icp｜OmniFleet 工作区介绍

Metapackage for mp2p_icp: depends on mp2p_icp_core (headless libraries and CLI applications) and mp2p_icp_viz (GUI applications).

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mp2p_icp`。
- colcon 类型：`(ros.cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。

## 工作区内声明依赖

- [mp2p_icp_core](../mp2p_icp_core/README.md)
- [mp2p_icp_viz](../mp2p_icp_viz/README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
