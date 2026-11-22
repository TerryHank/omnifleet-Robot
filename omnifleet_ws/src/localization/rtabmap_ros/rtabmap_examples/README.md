# rtabmap_examples｜OmniFleet 工作区介绍

RTAB-Map's example launch files.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/rtabmap_ros/rtabmap_examples`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下未发现同名目录；按源代码/备用组件登记，不能称为已部署运行。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。现有项：`depthai.launch.py`、`depthai_color.launch.py`、`depthai_stereo.launch.py`、`euroc_datasets.launch.py`、`k4a.launch.py`、`kinect_xbox_360.launch.py`、`lidar3d.launch.py`、`lidar3d_assemble.launch.py`、`lidar3d_assemble_x2.launch.py`、`multi_rgbd_inertial_dataset.launch.py` 等。
- [config/](config)：业务/算法运行配置。现有项：`euroc_left.yaml`、`euroc_right.yaml`、`multi_rgbd_inertial_dataset.ini`、`multi_rgbd_inertial_dataset_front.yaml`、`multi_rgbd_inertial_dataset_left.yaml`、`multi_rgbd_inertial_dataset_rear.yaml`、`multi_rgbd_inertial_dataset_right.yaml`、`slam_D405x2_config.rviz`、`slam_D405x3_config.rviz`。

## 工作区内声明依赖

- [rtabmap_odom](../rtabmap_odom/README.md)
- [rtabmap_rviz_plugins](../rtabmap_rviz_plugins/README.md)
- [rtabmap_slam](../rtabmap_slam/README.md)
- [rtabmap_util](../rtabmap_util/README.md)
- [rtabmap_viz](../rtabmap_viz/README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
