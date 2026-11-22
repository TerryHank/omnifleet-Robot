# Foxglove Nav2 永久参数（113）

面板按钮为“保存并应用”。永久文件保存成功和当前运行节点应用成功是两个独立结果。

实际启动入口通过 `omnifleet_planner` 的安装目录读取 `config/nav2_t2.yaml`。
该文件当前是源码 YAML 的软链接：
`/home/iecme/omnifleet_ws/src/planning/omnifleet_planner/config/nav2_t2.yaml`。
服务解析软链接后更新源码文件，因此下一次启动及正常重建会保留值。
临时的 `/tmp/launch_params_*` 不会被当成永久文件修改。

面板还提供全局规划器和局部控制器选择。全局规划器包括 Smac 2D、NavFn（可选 A* 或
Dijkstra）和 Theta*；局部控制器包括 Hot DWB、Regulated Pure Pursuit 和 MPPI。
这些插件会在 Nav2 启动时同时加载，面板通过 `/planner_selector` 和 `/controller_selector`
发布选择，因此切换算法不需要重启；算法下方的常用子参数也会随选择动态显示，保存后按当前
插件能力尝试热应用，不能热应用时面板会明确标注“下次启动读取新值”。

配置依据 Nav2 官方资料：多插件配置与选择见
`https://docs.nav2.org/jazzy/configuration_and_development/first_time_robot_setup_guide/navigation_plugins/setup_navigation_plugins/`；
selector 的输入话题要求 reliable + transient local QoS，见
`https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/bt_plugins/actions/PlannerSelector/`
和 `ControllerSelector/`；NavFn、RPP、MPPI 和 Theta* 的参数分别以 Nav2 Humble 官方文档为准。

面板保留局部和全局膨胀半径、代价衰减系数、footprint 安全边界、导航最大线速度、最大角速度，
以及 DWB 障碍物/路径权重、全局规划代价权重和未知区域开关。
线速度一项在一次原子文件替换中同步更新 `FollowPath.max_vel_x` 和
`FollowPath.max_speed_xy`，运行时也通过 SetParametersAtomically 同步应用。
速度是上限，不保证机器人实际达到该速度。

`nav2_parameter_store.py` 提供：

- `/omnifleet_t2/nav2/read_saved` (`std_srvs/srv/Trigger`)：JSON 格式的磁盘保存值。
- `/omnifleet_t2/nav2/save_parameters` (`rcl_interfaces/srv/SetParameters`)：请求名称是
  面板中的数值子参数，以及 `global_planner_algorithm` 和 `local_controller_algorithm`。
  服务只接受白名单内的有限数值、布尔值和算法字符串。`successful` 指文件写入并回读成功；`reason` 中的 JSON
  包含文件路径、备份、SHA256 及各节点运行时回读结果。

保存仅替换 YAML 数值标量，保留其他配置与注释，数值保留浮点类型。
有变化时先备份，再 fsync / 原子替换。备份位于
`/home/iecme/.local/share/omnifleet_t2/nav2-parameter-backups/`。
Nav2 未运行或实时参数请求失败时，永久保存仍可成功；面板明确显示当前实例未确认，
不会将其当作运行时已生效。保存不启动导航、不重启 Nav2、不发送运动指令。

永久服务随开机启动：

```bash
sudo systemctl restart omnifleet-t2-nav2-parameters.service
sudo systemctl restart omnifleet-t2-foxglove.service
```

Foxglove 使用 `Nav2PermanentPanel.js`。当前中文构建没有本地扩展 loader，
`deploy_panel.py` 将同一源函数注册到现有内置面板位置，并同步扩展源码包装入口。
运行包修改前留备份，运行包升级后需重新集成该面板。
本次未修改航点逻辑；地图航点绑定版本已从本地部署源恢复，12 项既有测试通过。

验证：`python3 -m pytest test_parameter_store.py -q`，覆盖全部 6 项数值类型、
双速度联动、软链接、备份、拒绝非法写入和未涉及参数不变。
从真实面板把线速度 0.4 改为 0.35 并获得永久保存及运行时回读确认，
独立 ROS 参数加载进程用安装 YAML 读到 [0.35, 0.35]，随后从面板恢复 0.4。
未为验证重启真实 Nav2 或移动小车。

当前 113 实验导航栈的手动启动命令（先正常停止已有 Nav2，避免重复节点）：

```bash
source /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash
export ROS_DOMAIN_ID=73 RMW_IMPLEMENTATION=rmw_fastrtps_cpp FASTDDS_BUILTIN_TRANSPORTS=LARGE_DATA
cd /home/iecme/omnifleet_ws
ros2 launch omnifleet_t2_mola_experiments nav2_direct.launch.py transform_tolerance:=0.8 odom_topic:=/odom obstacle_topic:=/rslidar_points obstacle_clearing:=true
```

这是本次读取的实际运行参数组合；MOLA/地图由原有进程负责。
永久参数服务停止命令：`sudo systemctl stop omnifleet-t2-nav2-parameters.service`。
Foxglove 可关闭窗口停止，或运行 `/home/iecme/.local/bin/start-foxglove-single.sh` 手动打开。

## 导航碰撞模型选择（2026-10-16）

“远离障碍 · 全局与局部共用”顶部新增“导航碰撞模型”：实际车体模型、近似点模型（半径 1 cm）。支持搜索“点模型”定位。

选择后永久保存，在手动点击“重启导航栈”后生效，不热切换、不自动重启导航。导航执行中、仍有运动指令或导航状态过期时拒绝切换。点模型会忽略真实车体宽度，车角与履带可能碰撞；模型选项旁持续显示该提示。

近似点模型统一设置全局/局部 `footprint: "[]"`、`robot_radius: 0.01`、`footprint_padding: 0.0`、`inflation_layer.inflation_radius: 0.01`，并关闭配置中 MPPI CostCritic/ObstaclesCritic 的 `consider_footprint`。切换前将本车原来的相关字段（含缺省键状态）保存到规划包 `config/nav2-collision-body.json`；切回实际车体时仅恢复这些字段，保留后来修改的速度、路径权重等参数。

沿用 `save_parameters` 服务，以单个字符串参数 `__collision_model` 提交 `body` 或 `point`。`read_saved` 增加 `collision_model` 状态，其 `mode` 表示已保存配置，不是运行时确认。首次部署保持原配置，不默认启用点模型。

回归：`python3 -m pytest -q test_collision_model.py`；前端 `ELECTRON_RUN_AS_NODE=1 /opt/Foxglove-Studio-CN/foxglove-studio-cn test_collision_model_panel.cjs`。实际原生面板在 113 验证显示和读回，104 部署时没有运行原生窗口。

## 地图生命周期与当前航点（2026-10-16）

面板重启导航栈和清空地图前，调用 `/omnifleet_t2/waypoints/invalidate_map`（Trigger），等待当前航点持久文件、Marker DELETEALL、空路线预览和空目录的清除确认；失败则阻止后续地图操作。地图加载成功时，旧航点被新地图配套航点替换；没有配套文件则清空。保存的地图、配套航点快照与历史备份保留。

航点桥接同时监测建图进程会话、地图变空、地图加载时间和坐标系变化；会话发生变化则作废旧路线。运行中的航点导航会收到取消请求。当前路线旁的 `.map-session.json` 记录所属会话及未完成的清除意图，避免重启航点服务后重新加载旧点。首次绑定时，若路线文件保存时间早于当前建图进程启动，也会将其作废。

正常地图消息更新、栅格增量变化、地图扩展及定位跳动计数不触发清除。地图加载期间禁止添加、拖拽及启动旧航点。加载已保存地图会恢复该地图配套航点，不会把保存的快照当作应删除的运行路线。

回归：`test/test_map_lifecycle.py`、`test/test_map_bundle.py`、`test/test_waypoint_drag.py` 位于航点包；两台共用代码各通过 40 项测试。真实 ROS 接口验收使用 localhost-only 的独立域 212 和临时路线、模拟地图后端，没有重置现场地图。113 原生面板读回当前 0 点；104 当前地图未变，保留 3 点。

## 碰撞模型详细参数（2026-10-16）

新增独立区域“碰撞模型详细参数 · 修改后重启生效”，共 9 个控件：全局与局部各自的 footprint、robot_radius、footprint_padding、inflation_layer.inflation_radius，以及 FollowPathMPPI.CostCritic.consider_footprint。文本、数值、布尔分别使用 ROS 字符串、浮点和布尔类型。支持参数名搜索、配置定位与官方资料链接。

这些详细参数只永久保存，手动重启导航栈后统一生效；导航执行中、状态过期或刚有运动指令时禁止编辑。footprint 填 [] 表示使用 robot_radius，非空时校验至少三个有限二维坐标点且轮廓不退化；圆形半径须至少 0.001 m。未显式配置的 robot_radius 显示本机默认 0.1，读取不会写回默认值，配置定位链接会说明其当前缺省。

保留车体/近似点快捷切换。手动修改导致参数不再匹配预设时显示“自定义模型”；首次修改前保留原车体几何备份，切回车体模型恢复它并保留速度、路径权重等无关参数。点模型或自定义模型下，共用的即时膨胀/余量快捷项仍锁定，但本次新增的 9 个详细控件可分别编辑，保存后重启生效。

参数链接在单次 catalog 请求内复用 YAML 解析结果，下次请求重新解析，避免新增字段放大读取耗时而又不使用跨请求旧缓存。部署后重连 Foxglove bridge，使其重新发现重启后的参数服务；没有重启 Nav2 或 MOLA。

验证：两台各通过 33 项几何参数与模型切换回归，前端 JSDOM 验证全部控件与保存类型。真实 read_saved 和同值 save_parameters 回读通过，YAML 字节不变；113 实际原生窗口已目视检查 9 个控件，104 部署时未运行原生窗口。测试进程均已退出。

## 碰撞模型与远离障碍布局合并（2026-10-16）

原“碰撞模型详细参数”和“远离障碍”已合并为“远离障碍与碰撞模型”。沿用原有模型下拉框和保存流程：近似点展示圆形半径，车体模式展示 footprint（为空时展示圆形半径），自定义模式展示全部形状字段。全局/局部膨胀半径、额外余量及 MPPI 完整车体检查位于同一区域；重复的共用半径/余量输入默认隐藏，搜索仍可定位。切换模型仍永久保存并在重启导航栈后生效。布局部署不修改已有参数，不自动重启服务或刷新用户正在使用的窗口。

回归：`test_collision_layout_panel.cjs` 覆盖合并区域、两种预设与自定义字段展示、模型切换保存协议、输入保存类型、状态保护及参数搜索。

## 合并区域内参数去重（2026-10-16）

全局与局部不再分别展示两份几何控件。车体轮廓、圆形半径、额外余量、障碍膨胀半径使用单个控件，修改时通过现有 save_parameters 服务在同一请求中提交两张地图的对应字段；数值不一致时显示空值及明确提示，未编辑不写入。保留 MPPI 完整车体检查和共用代价衰减系数。普通近似点/车体模式各显示 4 个几何控件，自定义模式显示 5 个。搜索列表同步去重。

`test_collision_dedup_panel.cjs` 覆盖显示数量、联动请求、不同值读取及导航/过期状态保护。布局部署本身不改变已保存配置，几何参数仍在重启导航栈后生效。

## 近似点模型膨胀半径即时应用（2026-10-16）

卡片顶部优先展示“障碍膨胀半径”和“膨胀代价衰减系数”。膨胀半径仍联动全局/局部，在停车且导航空闲时永久保存，并尝试即时应用到两张运行代价地图，参数回读匹配后明确报告成功；失败则保留未确认原因，不宣称生效。footprint、robot_radius、padding 与 MPPI 几何开关仍按原规则在重启后生效。

碰撞模型类型判定只按车体几何及对应 MPPI 检查配置，膨胀半径不再参与类型比较，因此调整膨胀范围不会把近似点或车体模型误标成自定义。切换预设时仍沿用原有预设与备份恢复行为。

113 停车实测：两张运行代价地图半径从 0.01 改为 0.25，回读均为 0.25，膨胀中间代价格数量明显增加，模型仍是 point；随后恢复原半径与原 YAML 文件字节。没有执行导航任务。回归见 `test_inflation.py`、`test_inflation_panel.cjs`。
