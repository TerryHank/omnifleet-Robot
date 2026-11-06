# omnifleet_planner｜OmniFleet 工作区介绍

Nav2 启动、规划与多控制器配置；包含本机导航永久参数和 Ordered MPPI 相关源码。

- 功能域：`planning`；源码：`/home/iecme/omnifleet_ws/src/planning/omnifleet_planner`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。当前项：`navigation.launch.py`。
- [config/](config)：业务/算法运行配置。当前项：`lattice`、`nav2-collision-body.json`、`nav2_t2.yaml`、`nav2_t2.yaml.before-arrival-20261104-055112`、`nav2_t2.yaml.before-single-lateral-20261027`、`nav2_t2.yaml.before-tolerance-20261104-071255`、`nav2_t2_rep105.reference.yaml`。
- [test/](test)：测试。当前项：`data`、`test_follow_rpp.cpp`、`test_follow_velocity_critic.cpp`、`test_footprint_clearance_critic.cpp`、`test_footprint_safe_goal_checker_config.py`、`test_goal_footprint_cost.cpp`、`test_hot_rpp.cpp`、`test_native_progress.cpp`、`test_native_publisher.cpp`、`test_normalize_path.cpp`、`test_peer_layer.cpp`、`test_short_follow_plan.cpp`、`test_t2_nav2_stack.py`。

## 工作区内声明依赖

- [nav2_costmap_2d](../nav2_costmap_2d/README.omnifleet.md)
- [nav2_mppi_controller](../nav2_mppi_controller/README.md)
- [nav2_smac_planner](../nav2_smac_planner/README.md)

## 104 当前约定

104导航永久参数在本包 `config/nav2_t2.yaml`。保存服务与 `system/omnifleet_bringup/launch/navigation.launch.py` 均直接读它；部署时保留最新保存值，不用备份默认值覆盖。

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。

历史REP-105参数参考已归入config/nav2_t2_rep105.reference.yaml，移除旧车端frame/topic前缀；该文件不是当前活动参数，也没有针对104重新做运动验收。当前永久参数仍唯一使用config/nav2_t2.yaml，未覆盖。

## 当前导航话题命名（2026-10-24）

导航速度接口使用 `/navigation/nav_cmd_vel`；底盘仍经过原有本机仲裁。同伴占据地图接口统一为 `/navigation/peer_map`。此次只更新接口名称，保留各车型控制链、peer layer 插件/开关和已调参数。源码与安装资源同步更新；本次没有重启运行中的导航进程。
