<!-- OMNIFLEET_WORKSPACE_DOC_LINK -->
本工作区职责、入口及104约定见 [README.omnifleet.md](README.omnifleet.md)。

# omnifleet_bringup（OmniFleet T2）

本包是 113 履带车的生产启动入口。STM32 底盘只通过
`/dev/omnifleet_t2_stm32` 打开；左右履带差速、电机方向、PWM 补偿和编码器
PID 由履带固件负责，上位机发布标准 `/cmd_vel`。

## 常驻服务

```bash
systemctl status omnifleet-t2-chassis.service
systemctl status omnifleet-t2-airy.service
journalctl -u omnifleet-t2-chassis.service -f
```

底盘发布 `/odom`、`odom -> base_link`、`/voltage`、`/voltage/display`、
`/firmware/version`、`/vel_raw`、`/wheel/odometry`、`/imu/data_raw`、
`/imu/mag` 和 `/motor_command_sent`。Airy 服务发布 `/rslidar_points` 与
`/rslidar_imu_data`。

`omnifleet-t2-navigation.service` 固定保持 disabled，导航由操作员手动启动。

## 手动启动 MOLA + Nav2

```bash
source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_ws/hardware_drivers_ws/install/setup.bash
source /home/iecme/omnifleet_ws/mola_3_2_ws/install/setup.bash
cd /home/iecme/omnifleet_ws/omnifleet_t2_ws
source install/setup.bash
export ROS_DOMAIN_ID=0

ros2 launch omnifleet_bringup production.launch.py \
  backend:=mola \
  map_id:=active \
  map_dir:=/home/iecme/omnifleet_data/maps \
  start_description:=false
```

生产默认使用 MOLA、SmacPlanner2D 和 DWB。底盘驱动永远由
`omnifleet-t2-chassis.service` 通过 `systemctl` 管理；任何 MOLA、Nav2 或
上层 `robot.launch.py` 入口都不再接受或启动底盘节点。Airy 和车体描述同样
由各自常驻服务管理，生产导航入口只连接它们。

## 只读健康检查

```bash
ros2 run omnifleet_bringup robot_doctor --scope base
ros2 run omnifleet_bringup robot_doctor --scope nav
ros2 run omnifleet_bringup vehicle_status
```

## 104 当前总启动管线

整车跨域编排位于system/omnifleet_bringup，不依赖omnifleet_t2_mola_experiments。
- launch/mola_nav2_unified.launch.py：MOLA主定位、雷达IMU、原生轮式vx/wz Smoother、导航栅格、Nav2与就绪检查的统一入口。
- launch/mola_localization.launch.py：定位侧子管线，实际调用sensing、map及MOLA专用包。
- launch/navigation.launch.py：Nav2子管线，读取planning/omnifleet_planner/config/nav2_t2.yaml的最新永久参数。
当前由omnifleet-t2-mola与omnifleet-t2-pure-lio-nav2两个服务分别持有子管线；使用systemctl启动/重启。服务活动时统一手动launch会拒绝重复启动。底盘、Airy、描述节点仍由已有服务独立管理。
雷达IMU标定归sensing/omnifleet_sensor_processing/config/airy_imu_calibration.yaml。轮式仅vx/wz，最终/state_estimation/pose，无车端车辆前缀，去畸变关闭。目录迁移不改变融合算法和运动授权。

## RTAB-Map备用后端

launch/rtabmap_lidar_grid.launch.py承接原RTAB-Map包装包的原生ICP里程计和栅格节点编排，直接依赖rtabmap_odom、rtabmap_slam。默认输入/rslidar_points、base_link、/tf和/tf_static，输出隔离到rtabmap_trial，不发布生产TF。数据库位于/home/iecme/omnifleet_data/maps/rtabmap/trial.db，启动不删除数据库。本次没有启用该备用后端，当前仍为MOLA。
