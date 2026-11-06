# rtabmap_util｜OmniFleet 工作区介绍

RTAB-Map's various useful nodes and nodelets.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/rtabmap_ros/rtabmap_util`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下未发现同名目录；按源代码/备用组件登记，不能称为已部署运行。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [scripts/](scripts)：可执行脚本。当前项：`assemble_local_grids.py`、`gazebo_ground_truth.py`、`netvlad_tf_ros.py`、`objects_to_tags.py`、`patrol.py`、`point_to_tf.py`、`republish_tf_static.py`、`transform_to_tf.py`、`yaml_to_camera_info.py`。

## 工作区内声明依赖

- [rtabmap_conversions](../../rtabmap/rtabmap_ros/rtabmap_conversions/package.xml)
- [rtabmap_msgs](../../rtabmap/rtabmap_ros/rtabmap_msgs/package.xml)
- [rtabmap_sync](../../rtabmap/rtabmap_ros/rtabmap_sync/package.xml)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
