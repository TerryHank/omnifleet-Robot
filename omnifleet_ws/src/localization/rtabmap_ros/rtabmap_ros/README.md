# rtabmap_ros｜OmniFleet 工作区介绍

RTAB-Map Stack

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/rtabmap_ros/rtabmap_ros`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下未发现同名目录；按源代码/备用组件登记，不能称为已部署运行。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。

## 工作区内声明依赖

- [rtabmap_conversions](../rtabmap_conversions/README.md)
- [rtabmap_costmap_plugins](../rtabmap_costmap_plugins/README.md)
- [rtabmap_demos](../rtabmap_demos/README.omnifleet.md)
- [rtabmap_examples](../rtabmap_examples/README.md)
- [rtabmap_launch](../rtabmap_launch/README.omnifleet.md)
- [rtabmap_msgs](../rtabmap_msgs/README.md)
- [rtabmap_odom](../rtabmap_odom/README.md)
- [rtabmap_python](../rtabmap_python/README.md)
- [rtabmap_rviz_plugins](../rtabmap_rviz_plugins/README.md)
- [rtabmap_slam](../rtabmap_slam/README.md)
- [rtabmap_sync](../rtabmap_sync/README.md)
- [rtabmap_util](../rtabmap_util/README.md)
- [rtabmap_viz](../rtabmap_viz/README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
