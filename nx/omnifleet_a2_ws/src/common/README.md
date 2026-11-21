# common 功能域

公共消息/服务/Action、车队协议与共享基础库。业务控制逻辑不应堆放在接口包中。

路径：`/home/iecme/omnifleet_ws/src/common`。本目录是功能域容器，不按它的名字推断整个域均已构建或正在运行。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [livox_sdk2](Livox-SDK2/README.omnifleet.md) | 构建组件，详见包说明 |
| [mrpt_libros_bridge](mrpt_ros_bridge/ros2bridge/README.md) | Mobile Robot Programming Toolkit (MRPT) ros2bridge C++ library |
| [omnifleet_fleet_common](omnifleet_fleet_common/README.omnifleet.md) | 共享协议、持久化、指标与 robot_id/话题/TF 命名空间工具。 |
| [omnifleet_fleet_interfaces](omnifleet_fleet_interfaces/README.md) | 车队任务与状态接口；迁移后位于 common。 |
| [omnifleet_interfaces](omnifleet_interfaces/README.omnifleet.md) | 公共自定义消息和服务契约。 |
| [omnifleet_navigation_interfaces](omnifleet_navigation_interfaces/README.md) | 本机导航任务 Action 与航点消息，定义任务请求和反馈的类型。 |
| [rosbag2rawlog](mrpt_ros_bridge/rosbag2rawlog/README.md) | CLI tool to transform between rosbags and rawlogs. |
| [vikit_common](rpg_vikit/vikit_common/README.md) | The vikit_common package |
| [vikit_ros](rpg_vikit/vikit_ros/README.md) | The vikit_ros package |

业务配置位于对应包 `config/`；长期数据位于 `/home/iecme/omnifleet_data`。完整规则见 [工作区AGENTS.md](../../AGENTS.md)。
