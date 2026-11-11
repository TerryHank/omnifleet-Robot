# sensing 功能域

雷达/相机驱动、传感器消息与点云/IMU 预处理。

路径：`/home/iecme/omnifleet_ws/src/sensing`。本目录是功能域容器，不按它的名字推断整个域均已构建或正在运行。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [livox_ros_driver2](livox_ros_driver2/README.omnifleet.md) | The ROS device driver for Livox 3D LiDARs, for ROS2 |
| [omnifleet_sensor_processing](omnifleet_sensor_processing/README.omnifleet.md) | 相机、点云与 Airy IMU 处理实现；含可选去畸变代码，但104当前主链已旁路运动去畸变。 |
| [orbbec_camera](orbbec_camera/README.md) | Orbbec Camera package |
| [orbbec_camera_msgs](orbbec_camera_msgs/README.md) | A package containing orbbec camera messages definitions. |
| [orbbec_description](orbbec_description/README.md) | TODO: Package description |
| [rslidar_msg](rslidar_msg/README.omnifleet.md) | RoboSense 驱动使用的消息定义。 |
| [rslidar_sdk](rslidar_sdk/README.omnifleet.md) | RoboSense Airy 雷达驱动，发布原始点云和 IMU。 |

业务配置位于对应包 `config/`；长期数据位于 `/home/iecme/omnifleet_data`。完整规则见 [工作区AGENTS.md](../../AGENTS.md)。
