# omnifleet_bringup：104 启动编排

当前环境由 `/home/iecme/omnifleet_ws/env.bash` 加载，ROS_DOMAIN_ID=104，RMW_IMPLEMENTATION=rmw_zenoh_cpp。

## 当前服务入口

- `omnifleet-t2-mola.service` → `mola_localization.launch.py profile:=integrated` → `mola_integrated_localization.launch.py`。
- integrated读取 `src/localization/omnifleet_mola/mola_state_estimation_simple/config/tracked-integrated-live-runtime.json` 和 `tracked-integrated-live-system.yaml`；状态估计器为StateEstimationSimple。配置文件名robot113-simple.yaml是现有路径，不能仅据文件名改为104或替换参数。
- `omnifleet-t2-pure-lio-nav2.service` → `navigation.launch.py`；Nav2永久配置在 `src/planning/omnifleet_planner/config/nav2_t2.yaml`，install入口软链接解析至该源码文件。
- `omnifleet-local-navigation.service`为安全速度出口。速度链为 `/navigation/nav_cmd_vel` → local_navigation → `/navigation/cmd_vel_safe` → 底盘；`/cmd_vel`为人工输入。
- 底盘、Airy、车体描述由各自systemd服务管理。MOLA及Nav2服务已启用；旧 `omnifleet-t2-navigation.service` 为disabled。

当前 integrated 配置使用 StateEstimationSimple；lidar3d-gicp.yaml 的 observations_deskew_pass 执行一次 Linear 去畸变，ICP 与地图插入共用该结果。依据 MOLA_OPTIMIZE_TWIST=false 和 LidarOdometry_ProcessScan.cpp 的 use_deskew 分支；话题 /navigation/deskewed_points 保持兼容名称。配置与源码核对不等于实车去畸变效果验收。

Nav2配置包含多个规划器和控制器，不能概括为固定SmacPlanner2D+DWB；实际选择由任务请求和当前nav2_t2.yaml决定。统一手动launch与常驻服务的重复启动检查以启动脚本为准。

## 只读检查

```bash
source /home/iecme/omnifleet_ws/env.bash
systemctl status omnifleet-t2-mola omnifleet-t2-pure-lio-nav2 omnifleet-local-navigation --no-pager
ros2 run omnifleet_bringup robot_doctor --scope base
ros2 run omnifleet_bringup robot_doctor --scope nav
```

当前文件及依赖清单见 [README.omnifleet.md](README.omnifleet.md)。`rtabmap_lidar_grid.launch.py`为备用入口，源码存在不表示生产服务已切换。本次为文档核对，未执行运动测试。
