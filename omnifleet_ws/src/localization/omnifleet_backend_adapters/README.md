# omnifleet_backend_adapters｜OmniFleet 工作区介绍

FAST-LIVO2 与 RTAB-Map 的隔离 Airy 启动配置。当前主定位链仍为 MOLA。

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_backend_adapters`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下未发现同名目录；按源代码/备用组件登记，不能称为已部署运行。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。现有项：`fast_livo2_airy.launch.py`、`rtabmap_airy.launch.py`。
- [config/](config)：业务/算法运行配置。现有项：`airy_imu_correction.yaml`、`fast_livo2_airy_lio.yaml`。
- [test/](test)：测试。现有项：`test_backend_contract.py`。

## 工作区内声明依赖

- [fast_livo](../fast_livo2_ros2/README.omnifleet.md)
- [omnifleet_mola_grid](../../map/omnifleet_mola_grid/README.md)
- [RTAB-Map启动编排](../../system/omnifleet_bringup/launch/rtabmap_lidar_grid.launch.py)：直接使用上游rtabmap_odom、rtabmap_slam；旧自定义包装包已归档。
- [omnifleet_sensor_processing](../../sensing/omnifleet_sensor_processing/README.omnifleet.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
