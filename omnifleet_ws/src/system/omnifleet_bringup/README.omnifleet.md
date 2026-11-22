# omnifleet_bringup｜OmniFleet 工作区介绍

历史启动/可执行兼容入口及整体启动集成；实际底盘、遥控等实现已拆分。

- 功能域：`system`；源码：`/home/iecme/omnifleet_ws/src/system/omnifleet_bringup`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。现有项：`chassis_core.launch.py`、`mola_nav2_rep105.launch.py`、`mola_nav2_unified.launch.py`、`omnifleet_t2_mola_unified.launch.py`、`production.launch.py`、`production_mola.launch.py`、`production_nav2.launch.py`、`robot.launch.py`、`usb_camera.launch.py`。
- [config/](config)：业务/算法运行配置。现有项：`rslidar_airy.yaml`。
- [scripts/](scripts)：可执行脚本。现有项：`cleanup_unified_application_nodes.py`、`nav2_readiness_gate.py`、`omnifleet-t2-raw-pwm`、`pointcloud_radius_filter`、`robot_doctor`、`t2_driver`、`usb_camera_publisher`、`vr_protocol_adapter`。
- [test/](test)：测试。现有项：`test_t2_production_contract.py`、`test_t2_production_contract.py.orig`、`test_t2_sensor_contract.py`。

## 工作区内声明依赖

- [omnifleet_behaviors](../../control/omnifleet_behaviors/README.omnifleet.md)
- [omnifleet_chassis_driver](../../vehicle/omnifleet_chassis_driver/README.omnifleet.md)
- [omnifleet_description](../../vehicle/omnifleet_description/README.omnifleet.md)
- [omnifleet_interfaces](../../common/omnifleet_interfaces/README.omnifleet.md)
- [omnifleet_localization](../../localization/omnifleet_localization/README.omnifleet.md)
- [omnifleet_planner](../../planning/omnifleet_planner/README.omnifleet.md)
- [omnifleet_sensor_processing](../../sensing/omnifleet_sensor_processing/README.omnifleet.md)
- [omnifleet_teleop](../../control/omnifleet_teleop/README.omnifleet.md)
- [rslidar_sdk](../../sensing/rslidar_sdk/README.omnifleet.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。

104当前总启动编排及服务职责见[README.md](README.md#104-当前总启动管线)，原实验包已退役。
