# vehicle 功能域

底盘驱动、车辆模型/标定关系、控制器接口与舵机工具。

路径：`/home/iecme/omnifleet_ws/src/vehicle`。本目录是功能域容器，不按它的名字推断整个域均已构建或正在运行。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [omnifleet_chassis_driver](omnifleet_chassis_driver/README.omnifleet.md) | STM32 履带底盘传输、原始 PWM 与轮滑检测实现。 |
| [omnifleet_description](omnifleet_description/README.omnifleet.md) | 履带差速车辆 URDF、Airy/IMU 安装关系和固定 TF。 |
| [omnifleet_servo_rqt](omnifleet_servo_rqt/README.md) | 舵机配置与运动工具；打开工具不等于允许执行舵机运动。 |
| [ros_robot_controller](ros_robot_controller/README.md) | TODO: Package description |
| [ros_robot_controller_msgs](ros_robot_controller_msgs/README.md) | TODO: Package description |
| [rrc_tank_bridge](rrc_tank_bridge/README.md) | Safe cmd_vel to Hiwonder tracked motor bridge. |
| [rrc_tank_description](rrc_tank_description/README.md) | Simple tracked chassis model for Foxglove and ROS 2 TF. |

业务配置位于对应包 `config/`；长期数据位于 `/home/iecme/omnifleet_data`。完整规则见 [工作区AGENTS.md](../../AGENTS.md)。
