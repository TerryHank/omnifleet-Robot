# visualization 功能域

Foxglove、导航/协同面板、航点 UI、显示模型和录制辅助。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [omnifleet_waypoint_ui](omnifleet_waypoint_ui/README.md) | 航点管理及本机导航 UI 桥接，区分添加航点与实际执行任务。 |

## 非独立ROS包的运行/支持目录

- [foxglove_studio_source/](foxglove_studio_source)：Foxglove 中文客户端源代码，桌面分发二进制另行安装；源代码与布局不是完整桌面镜像。
- [omnifleet_t2_ws/](omnifleet_t2_ws)：Foxglove 导航参数、车队/诊断面板与扩展源文件的兼容容器。主要运行文件位于 foxglove 子目录。
