# OmniFleet T2 113 改名与 Foxglove 修复报告

日期：2026-09-01  
目标：`iecme@192.168.3.113`

## 结论

- 原空白画面不是底盘或 Airy 无数据。
- Foxglove Bridge 使用全量 `topic_whitelist: [".*"]`。
- 原布局仍订阅112旧电压、IMU、GLIM里程计话题，并固定在导航关闭时不存在的 `map` 坐标系。
- 已切换到 `/voltage`、`/imu/data_raw`、`/odom`、`/rslidar_points`，固定参考系改为 `odom`。
- 113专属活动命名已统一为 `omnifleet_t2`；标准ROS话题和共享第三方/平台包名保持标准。

## 当前主线

- 工作区：`/home/iecme/omnifleet_ws/omnifleet_t2_ws`
- 环境：`/etc/omnifleet_t2`
- 状态：`/var/lib/omnifleet_t2`
- systemd：`omnifleet-t2-*.service`
- ROS节点：`/omnifleet_t2_driver`、`/omnifleet_t2_robot_state_publisher`、`/omnifleet_t2_foxglove_bridge`、`/omnifleet_t2_waypoint_ui`
- 自定义话题：`/omnifleet_t2/waypoints/*`
- Nav2/MOLA服务保持 `disabled`，由用户手动启动。

## 验证

- 11个ROS包完整构建成功。
- T2生产专项：19 passed。
- 全量测试：221项结果中唯一实际失败来自旧工作区同样缺失的可选红绿灯launch，已复现为基线问题。
- 五个常驻T2服务：active，`NRestarts=0`。
- Airy点云约5至9Hz，`/odom`约10Hz。
- STM32反馈帧持续增长，校验错0、接收错0、最终速度精确零。
- T2 Nav2临时启动验证：controller、planner、behavior、BT全部active；`/map`、全局和局部代价地图均发布；未发送导航目标，验收后已停止。
- Foxglove可视验证：Airy点云、车模、电压、IMU、`/odom`、地图和代价地图可显示。
- 113活动布局已按112活动布局对齐为相同五面板树和相同分割比例；仅保留履带控制、T2车模/尺寸、T2话题及`odom`常驻参考系差异。
- T2底盘驱动同时发布原始`/voltage`和人类可读`/voltage/display`；Foxglove显示为一位小数和`V`单位。
- 旧活动节点、旧自定义话题、旧systemd单元、旧顶层工作区、旧`/etc`均已从生产路径移除。

## 哈希

- 默认布局：`28ff3e2ad95c53974b5a5b2a3e35a9bb4fc2bbddf6afa13c7d47fb3babd1c89a`
- 源码清单：`f4108b79a10b77f464920e2f4901a505f54bf538f30b57b47b8a7a0d1aff1049`
- Foxglove T2扩展0.4.0：`52d5375b9fd56fd69941e79b474f1bd422e4532a128ef2b3716c2e26943d8d16`

## 回滚

完整旧工作区和旧配置保存在：

```text
/home/iecme/omnifleet_migration_backups/20260901_212317_pre_omnifleet_t2
```

历史备份保持原名，不参与生产命名扫描。

## 手动导航

```bash
source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_ws/hardware_drivers_ws/install/setup.bash
cd /home/iecme/omnifleet_ws/omnifleet_t2_ws
source install/setup.bash
export ROS_DOMAIN_ID=0
sudo systemctl start omnifleet-t2-navigation.service
```

停止：

```bash
sudo systemctl stop omnifleet-t2-navigation.service
```
