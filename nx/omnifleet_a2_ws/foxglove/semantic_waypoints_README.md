# OmniFleet 单实车简易多点导航面板

这是独立于生产源码的“Foxglove 自定义面板 + ROS 2 后台包”，只服务一辆实车。

操作员不需要编辑 JSON：先在自定义面板输入下一个点的中文语义名称，再在 Foxglove
三维地图中使用“发布姿态”工具放置航点。名称留空时自动使用 `航点1`、`航点2`……，
已放置的点也可以重命名。确认路线后点击“开始整条路线”。后台仍复用生产工作区已有的
`omnifleet_a2_waypoint_bridge`，由它把 `/omnifleet_a2/nav/waypoint_poses` 转发给 Nav2
`navigate_through_poses`，不会绕过定位和 Nav2 生命周期门控。

## 面板功能

- 地图点选：`/omnifleet_a2/waypoints/add_pose`
- 下一点名称：`/omnifleet_a2/waypoints/next_name`
- 重命名现有点：`/omnifleet_a2/waypoints/rename`
- 中文语义目录：`/omnifleet_a2/waypoints/catalog`
- 路线预览：`/omnifleet_a2/waypoints/path`
- 编号标记：`/omnifleet_a2/waypoints/markers`
- 开始路线：`/omnifleet_a2/waypoints/start`
- 停止导航：`/omnifleet_a2/waypoints/stop`
- 撤销上一点：`/omnifleet_a2/waypoints/undo`
- 清空路线：`/omnifleet_a2/waypoints/clear`
- 中文状态：`/omnifleet_a2/waypoints/status`

只有 `/omnifleet_a2/system/localization_ready` 和
`/omnifleet_a2/system/lifecycle_ready` 同时为
`true` 时，“开始路线”才会向生产 `/omnifleet_a2/nav/waypoint_poses` 发布点位。

## 构建

```bash
cd /home/iecme/omnifleet_a2_waypoint_ui/ros2_ws
source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_a2_ws/install/setup.bash
colcon build --packages-select omnifleet_a2_waypoint_ui --symlink-install
source install/setup.bash
```

## 启动

先启动生产建图/导航栈，再启动本节点：

```bash
export ROS_DOMAIN_ID=42
ros2 launch omnifleet_a2_waypoint_ui waypoint_ui.launch.py
```

当前远端 Foxglove Studio CN `1.87.0-cn.6` 已内置右侧轻量语义控制窗，并修复 ROS 2
`std_msgs/String` 中文 UTF-8 发布。双击桌面图标后，在 Foxglove 顶栏点击语义导航图标：

```bash
DISPLAY=:0 /home/iecme/omnifleet_a2_waypoint_ui/scripts/start_semantic_waypoints.sh
```

控制窗需要时才覆盖在 Foxglove 右侧，关闭后不占布局、不收发话题；左侧地图仍可继续放点。

远端桌面还提供 `OmniFleet语义多点导航` 图标。双击它只启动 Foxglove 和语义操作层，
不会自动启动底盘、建图或 Nav2，也不会让实车自行运动。

Foxglove 连接 `ws://192.168.3.112:8765`，导入
`/home/iecme/omnifleet_a2_waypoint_ui/layouts/omnifleet_single_robot_simple.json`。

Foxglove 扩展源码位于 `foxglove_extension/omnifleet-semantic-waypoints`，安装包为
`terryhank.omnifleet-semantic-waypoints-0.2.0.foxe`。面板输入和持久化均使用 UTF-8，
支持中文名称。

## 停止

前台启动时按 `Ctrl-C`。正在导航时也可点击面板中的“停止导航”，它只取消
`navigate_through_poses` 目标，不会停止底盘、雷达或生产 Foxglove bridge。
