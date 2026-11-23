# system 功能域

机器人启动集成、协调器、MSC 入口、通信运行脚本和运维支持。

路径：`/home/iecme/omnifleet_ws/src/system`。本目录是功能域容器，不按它的名字推断整个域均已构建或正在运行。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [omnifleet_bringup](omnifleet_bringup/README.omnifleet.md) | 整车跨域总启动、MOLA/Nav2子管线及就绪检查；专用算法与驱动归各自功能包。 |
| [Fast DDS](../../../omnifleet_data/nx/runtime_124/README.md#fast-dds) | ROS 2 Humble 使用 `rmw_fastrtps_cpp`。域号与机器人命名空间分别配置。 |

## 非独立ROS包的运行/支持目录

- [omnifleet_fleet/](omnifleet_fleet)：旧兼容运行入口、作用域 remap、env/start/run 脚本。许多旧文件是指向新功能包的软链接，不另建一套实现。
- [omnifleet_transport/](omnifleet_transport)：通信脚本和旧网关资料；独立于 ROS 包打包。
- [workspace_support/](workspace_support)：工作区环境、历史迁移/构建支持与验收资料；历史记录保留原日期。
- [operator_tools/](operator_tools)：操作者工具入口。执行会启动硬件或任务的脚本前，先检查其参数和实际服务关系。

业务配置位于对应包 `config/`；长期数据位于 `/home/iecme/omnifleet_data`。完整规则见 [工作区AGENTS.md](../AGENTS.md)。
