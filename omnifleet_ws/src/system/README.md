# system 功能域

机器人启动、通信与运维。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [omnifleet_bringup](omnifleet_bringup/README.omnifleet.md) | 整车跨域总启动、MOLA/Nav2子管线及就绪检查；专用算法与驱动归各自功能包。 |
| [Fast DDS](../../../omnifleet_data/README.workspace.md#fast-dds) | ROS 2 Humble 使用 `rmw_fastrtps_cpp`。域号与机器人命名空间分别配置。 |
| [omnifleet_rmf_adapter](omnifleet_rmf_adapter/README.md) | 调度、车辆广播发现及 DDS Router 会话。 |

## 非独立ROS包的运行/支持目录

- [omnifleet_fleet/](omnifleet_fleet)：旧兼容运行入口、作用域 remap、env/start/run 脚本。许多旧文件是指向新功能包的软链接，不另建一套实现。
- [omnifleet_transport/](omnifleet_transport)：通信脚本和旧网关资料；独立于 ROS 包打包。
- [workspace_support/](workspace_support)：工作区环境、历史迁移/构建支持与验收资料；历史记录保留原日期。
- [operator_tools/](operator_tools)：操作者工具入口。执行会启动硬件或任务的脚本前，先检查其参数和实际服务关系。
- [tools/](tools) 收录独立工具，如 AgenticROS 和 PhyAgentOS。
