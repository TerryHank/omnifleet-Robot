# omnifleet_localization｜OmniFleet 工作区介绍

定位域集成与兼容接口；传感器处理、栅格等实现已拆到对应新包。

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_localization`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。当前项：`airy_gateway.launch.py`、`backends`、`includes`。
- [config/](config)：业务/算法运行配置。当前项：`airy`、`cartographer_3d`、`modes.yaml`、`mola`。
- [scripts/](scripts)：可执行脚本。当前项：`airy_imu_adapter_node`、`cartographer_odom_adapter`、`depth_dropoff_detector`、`terrain_mapper`、`wheel_slip_detector`。
- [test/](test)：测试。当前项：`airy`、`mapping`、`test_cartographer_3d_contract.py`、`test_mode_configs.py`、`test_mola_backend_contract.py`。

## 工作区内声明依赖

- [omnifleet_chassis_driver](../../vehicle/omnifleet_chassis_driver/README.omnifleet.md)
- [omnifleet_description](../../vehicle/omnifleet_description/README.omnifleet.md)
- [omnifleet_interfaces](../../common/omnifleet_interfaces/README.omnifleet.md)
- [omnifleet_sensor_processing](../../sensing/omnifleet_sensor_processing/README.omnifleet.md)
- [omnifleet_terrain_analysis](../../perception/omnifleet_terrain_analysis/README.omnifleet.md)
- [rslidar_sdk](../../sensing/rslidar_sdk/README.omnifleet.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
