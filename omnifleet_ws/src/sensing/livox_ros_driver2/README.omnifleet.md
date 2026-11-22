# livox_ros_driver2｜OmniFleet 工作区介绍

The ROS device driver for Livox 3D LiDARs, for ROS2

- 功能域：`sensing`；源码：`/home/iecme/omnifleet_ws/src/sensing/livox_ros_driver2`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下未发现同名目录；按源代码/备用组件登记，不能称为已部署运行。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。现有项：`msg_AVIA2_launch.py`、`msg_HAP_launch.py`、`msg_MID360_launch.py`、`msg_MID360l_launch.py`、`msg_MID360s_launch.py`、`rviz_AVIA2_launch.py`、`rviz_HAP_launch.py`、`rviz_MID360_launch.py`、`rviz_MID360l_launch.py`、`rviz_MID360s_launch.py` 等。
- [config/](config)：业务/算法运行配置。现有项：`AVIA2_config.json`、`HAP_config.json`、`MID360_config.json`、`MID360l_config.json`、`MID360s_config.json`、`display_point_cloud_ROS1.rviz`、`display_point_cloud_ROS2.rviz`、`mixed_HAP_MID360_config.json`。
- [msg/](msg)：消息定义。现有项：`CustomMsg.msg`、`CustomPoint.msg`。

## 工作区内声明依赖

- [livox_sdk2](../../common/Livox-SDK2/README.omnifleet.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
