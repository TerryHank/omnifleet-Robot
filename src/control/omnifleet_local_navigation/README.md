# omnifleet_local_navigation

本机单点、多点导航任务与控制仲裁。Nav2 速度从 `/navigation/nav_cmd_vel` 进入，统一输出 `/navigation/cmd_vel_safe` 给底盘。

- 可执行入口 `local_navigation`，节点和任务入口见 [runtime.py](omnifleet_local_navigation/runtime.py)，速度仲裁见 [control.py](omnifleet_local_navigation/control.py)。
- `omnifleet-local-navigation.service` 读取 [local-navigation.json](config/local-navigation.json)。
- 触屏点位走 `/navigation/goal_point`，使用 `point_goal_checker`。近障脱困读取当前导航控制器限速。
- 车队接口管理许可与租约。任务接受条件包括现有就绪状态、定位 epoch 和租约匹配。

[包声明](package.xml) · [测试](test) · [本机运行入口](../../../README.workspace.md)
