# omnifleet_waypoint_ui｜OmniFleet 工作区介绍

航点管理及本机导航 UI 桥接，区分添加航点与实际执行任务。

- 功能域：`visualization`；源码：`/home/iecme/omnifleet_ws/src/visualization/omnifleet_waypoint_ui`。
- colcon 类型：`(ros.ament_python)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [setup.py](setup.py)：Python包安装与console_scripts入口。
- [launch/](launch)：ROS启动入口。现有项：`waypoint_ui.launch.py`、`waypoint_ui_with_panel.launch.py`。
- [test/](test)：测试。现有项：`test_continuous_route.py`、`test_error_bridge_integration.py`、`test_navigation_error_dictionary.py`、`test_waypoint_ui_core.py`。

Python可执行入口（读取setup.py，未启动节点）：

- `waypoint_ui_bridge = omnifleet_waypoint_ui.waypoint_ui_bridge:main`
- `semantic_waypoint_panel = omnifleet_waypoint_ui.semantic_waypoint_panel:main`

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。

## 地图与路径显示层偏移

ros2 run omnifleet_waypoint_ui foxglove_layer_offset：承接原实验包中的可视化辅助工具，把地图/代价地图/路径复制到/foxglove/...并增加显示z偏移，不改变实际定位/地图/导航话题。此工具为Apache-2.0许可，默认不由生产管线启动。

## Foxglove 3D 拖拽已有航点

在原生 3D 面板的地图坐标系中，左键拖动航点中心的绿色圆环，松手保存；Esc 或窗口失焦取消。拖动空白处仍平移地图。仅修改平面 x/y，保留名称、顺序、高度、朝向、途经/停靠类型和等待时间；保存后刷新航点显示及路线预览。预览仍受地图和规划器可通行性限制。

导航执行中或导航状态超过 2 秒未更新时禁止拖动。该操作不会启动导航。后端沿用 `/omnifleet_t2/waypoints/update`（`std_msgs/msg/String`），请求中增加 `position`、`previous_position`、`frame_id`、`name` 和原有的 1 起始 `index`；原坐标与名称用于拒绝过期编辑，保存仍使用当前路线文件。

回归测试：本包 `test/test_waypoint_drag.py`；前端 `ThreeDeeRender/waypoint-drag.test.cjs` 可使用 Electron 的 `ELECTRON_RUN_AS_NODE=1` 模式运行。

## 地图生命周期与当前航点（2026-10-16）

面板重启导航栈和清空地图前，调用 `/omnifleet_t2/waypoints/invalidate_map`（Trigger），等待当前航点持久文件、Marker DELETEALL、空路线预览和空目录的清除确认；失败则阻止后续地图操作。地图加载成功时，旧航点被新地图配套航点替换；没有配套文件则清空。保存的地图、配套航点快照与历史备份保留。

航点桥接同时监测建图进程会话、地图变空、地图加载时间和坐标系变化；会话发生变化则作废旧路线。运行中的航点导航会收到取消请求。当前路线旁的 `.map-session.json` 记录所属会话及未完成的清除意图，避免重启航点服务后重新加载旧点。首次绑定时，若路线文件保存时间早于当前建图进程启动，也会将其作废。

正常地图消息更新、栅格增量变化、地图扩展及定位跳动计数不触发清除。地图加载期间禁止添加、拖拽及启动旧航点。加载已保存地图会恢复该地图配套航点，不会把保存的快照当作应删除的运行路线。

回归：`test/test_map_lifecycle.py`、`test/test_map_bundle.py`、`test/test_waypoint_drag.py` 位于航点包；两台共用代码各通过 40 项测试。真实 ROS 接口验收使用 localhost-only 的独立域 212 和临时路线、模拟地图后端，没有重置现场地图。113 原生面板读回当前 0 点；104 当前地图未变，保留 3 点。
