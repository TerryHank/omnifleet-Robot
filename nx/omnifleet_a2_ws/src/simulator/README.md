# simulator 功能域

车辆运动学和 Gazebo 仿真；源码存在不代表仿真依赖或场景已验收。

路径：`/home/iecme/omnifleet_ws/src/simulator`。本目录是功能域容器，不按它的名字推断整个域均已构建或正在运行。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [omnifleet_kinematic_sim](omnifleet_kinematic_sim/README.md) | 与 ROS 话题契约相匹配的无串口车辆运动学仿真。 |
| [omnifleet_multi_robot_sim](omnifleet_multi_robot_sim/README.md) | Gazebo Classic 多机器人仿真和验证示例。 |
| [omnifleet_simulator](omnifleet_simulator/README.omnifleet.md) | Gazebo Harmonic 仿真配置。 |

业务配置位于对应包 `config/`；长期数据位于 `/home/iecme/omnifleet_data`。完整规则见 [工作区AGENTS.md](../../AGENTS.md)。
