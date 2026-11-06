# planning 功能域

Nav2 启动与规划/控制器配置、代价地图扩展和车队规划。

路径：`/home/iecme/omnifleet_ws/src/planning`。本目录是功能域容器，不按它的名字推断整个域均已构建或正在运行。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [nav2_costmap_2d](nav2_costmap_2d/README.omnifleet.md) | Nav2 代价地图工作区覆盖；本机使用其中的高度过滤修复库。 |
| [omnifleet_planner](omnifleet_planner/README.omnifleet.md) | Nav2 启动、规划与多控制器配置；包含本机导航永久参数和 Ordered MPPI 相关源码。 |

业务配置位于对应包 `config/`；长期数据位于 `/home/iecme/omnifleet_data`。完整规则见 [工作区AGENTS.md](../../AGENTS.md)。
