# omnifleet_mola_grid｜OmniFleet 工作区介绍

MP2P 体素切片及 MRPT/ROS 地图桥接，供外部已配准点云使用。

- 功能域：`map`；源码：`/home/iecme/omnifleet_ws/src/map/omnifleet_mola_grid`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [test/](test)：测试。现有项：`test_grid.cpp`。

## 工作区内声明依赖

- [mp2p_icp_core](../../localization/omnifleet_mola/mp2p_icp_core/README.md)
- [mrpt_libros_bridge](../../common/mrpt_ros_bridge/ros2bridge/README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
