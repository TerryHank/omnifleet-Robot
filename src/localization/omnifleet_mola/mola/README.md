# mola｜OmniFleet 工作区介绍

Metapackage with all core open-sourced MOLA packages.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mola`。
- colcon 类型：`(ros.cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。

## 工作区内声明依赖

- [mola_bridge_ros2](../mola_state_estimation_smoother/official_runtime/mola_bridge_ros2/README.omnifleet.md)
- [mola_demos](../mola_demos/README.omnifleet.md)
- [mola_input_rawlog](../mola_input_rawlog/README.omnifleet.md)
- [mola_input_rosbag2](../mola_input_rosbag2/README.omnifleet.md)
- [mola_input_video](../mola_input_video/README.omnifleet.md)
- [mola_kernel](../mola_kernel/README.omnifleet.md)
- [mola_launcher](../mola_launcher/README.omnifleet.md)
- [mola_metric_maps](../mola_metric_maps/README.omnifleet.md)
- [mola_pose_list](../mola_pose_list/README.omnifleet.md)
- [mola_relocalization](../mola_relocalization/README.omnifleet.md)
- [mola_traj_tools](../mola_traj_tools/README.omnifleet.md)
- [mola_viz](../mola_viz/README.omnifleet.md)
- [mola_yaml](../mola_yaml/README.omnifleet.md)

## 原有资料

- [README.rst](README.rst)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
