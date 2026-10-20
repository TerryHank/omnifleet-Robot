# perception 功能域

视觉、地形/深度处理及操作者使用的感知与导航示例。

路径：`/home/iecme/omnifleet_ws/src/perception`。本目录是功能域容器，不按它的名字推断整个域均已构建或正在运行。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [omnifleet_terrain_analysis](omnifleet_terrain_analysis/README.omnifleet.md) | 地形层及深度落差/悬崖检测。 |
| [omnifleet_tutorials](omnifleet_tutorials/README.omnifleet.md) | 面向操作者的建图、导航和视觉示例，入口位于 perception。 |
| [omnifleet_vision](omnifleet_vision/README.omnifleet.md) | 视觉模型与推理集成；模型权重放 omnifleet_data/ml_models。 |

业务配置位于对应包 `config/`；长期数据位于 `/home/iecme/omnifleet_data`。完整规则见 [工作区AGENTS.md](../../AGENTS.md)。
