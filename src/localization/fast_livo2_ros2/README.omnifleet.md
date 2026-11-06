# fast_livo｜OmniFleet 工作区介绍

This is a modified version of LOAM which is original algorithm is described in the following paper: J. Zhang and S. Singh. LOAM: Lidar Odometry and Mapping in Real-time. Robotics: Science and Systems Conference (RSS). Berkeley, CA, July 2014.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/fast_livo2_ros2`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下未发现同名目录；按源代码/备用组件登记，不能称为已部署运行。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。当前项：`mapping_avia_marslvig.launch.py`、`mapping_aviz.launch.py`、`mapping_hesaixt32_hilti22.launch`、`mapping_ouster_ntu.launch.py`。
- [config/](config)：业务/算法运行配置。当前项：`HILTI22.yaml`、`MARS_LVIG.yaml`、`NTU_VIRAL.yaml`、`avia.yaml`、`camera_MARS_LVIG.yaml`、`camera_NTU_VIRAL.yaml`、`camera_fisheye_HILTI22.yaml`、`camera_pinhole.yaml`。
- [scripts/](scripts)：可执行脚本。当前项：`colmap_output.sh`、`mesh.py`。
- [test/](test)：测试。当前项：`test_airy_preprocess.cpp`。

## 工作区内声明依赖

- [livox_ros_driver2](../../sensing/livox_ros_driver2/README.omnifleet.md)
- [vikit_common](../../common/rpg_vikit/vikit_common/README.md)
- [vikit_ros](../../common/rpg_vikit/vikit_ros/README.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
