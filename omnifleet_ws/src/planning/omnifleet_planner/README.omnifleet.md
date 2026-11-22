# omnifleet_planner

车端 Nav2 规划、控制、目标检查与代价地图插件。支持的插件见 [包声明](package.xml) 和 [CMakeLists.txt](CMakeLists.txt)。

- [nav2_t2.yaml](config/nav2_t2.yaml) 是启动与面板保存使用的永久配置。`nav2_t2_rep105.reference.yaml` 为历史参考。
- 车端服务使用 bringup 的 [navigation.launch.py](../../system/omnifleet_bringup/launch/navigation.launch.py)。运行选择决定实际使用的规划器和控制器。
- 导航速度为 `/navigation/nav_cmd_vel`，同伴地图为 `/navigation/peer_map`。触屏点目标使用 `point_goal_checker`。

[测试](test) · [原有包说明](README.md)
