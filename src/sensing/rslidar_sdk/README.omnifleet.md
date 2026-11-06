> 2026-11-06清理说明：本文提及的 `/home/iecme/robot_backups/` 历史副本已从104删除，不能作为当前可用回退路径；原日期的验证结论仅代表当时状态。

# rslidar_sdk｜OmniFleet 工作区介绍

RoboSense Airy 雷达驱动，发布原始点云和 IMU。

- 功能域：`sensing`；源码：`/home/iecme/omnifleet_ws/src/sensing/rslidar_sdk`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。当前项：`elequent_start.py`、`humble_start.py`、`start.launch`、`start.py`。
- [config/](config)：业务/算法运行配置。当前项：`config.10hz-full.yaml`、`config.20hz-half.yaml`、`config.yaml`。

## 工作区内声明依赖

- [rslidar_msg](../rslidar_msg/ros2/package.xml)

## 原有资料

- [README_CN.md](README_CN.md)
- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。




## 104 发布频率切换

当前默认10 Hz完整圈，配置为config/config.yaml中的split_frame_mode=1、split_angle=0。config/config.10hz-full.yaml和config/config.20hz-half.yaml保留两种配置；20 Hz为官方自定义块分帧模式3、900块/帧，每帧约半圈，完整圈仍为10 Hz。

```bash
/home/iecme/omnifleet_ws/src/sensing/rslidar_sdk/scripts/set_airy_rate.sh 20
/home/iecme/omnifleet_ws/src/sensing/rslidar_sdk/scripts/set_airy_rate.sh 10
```

切换前自动检查编码器静止且无活动导航任务；切换重启Airy、MOLA与Nav2，避免传感器停流间隔跨越Smoother窗口。停止后备份当前地图与配置到robot_backups。切换只改变分帧字段，保留其他硬件配置。当前启动入口采用重新建图；已有地图文件会保留，但重启后活动地图坐标原点重新建立。

## 104 Airy IMU 驱动滤波与零偏（2026-10-14）

驱动在ROS2发布前运行六轴独立随机游走Kalman滤波，原始话题`/rslidar_imu_data_raw`保留诊断，原有`/rslidar_imu_data`为滤波输出，后续适配器完成轴变换、g到m/s²比例换算及固定陀螺零偏扣除。没有使用底盘IMU。

`config/config.yaml`及10/20Hz两份配置中：`imu_kalman_enabled`为开关；R/Q各6项依次是gyro xyz、accel xyz；原生单位rad/s和g。R来自104连续60秒静止数据；Q为每秒方差，取R×180，在200Hz时稳态增益约0.6。独立测试阶跃95%响应<=20ms；这是软件测试，未做实车运动验收。滤波不会积分姿态/位置或扣除重力，输出orientation标为未知。

30秒实测六轴方差相对原始分别为0.704、0.624、0.388、0.353、0.409、0.302；不是所有轴都降低相同比例。采样断流>100ms重置滤波，重复/倒退时间戳与非有限数不进入滤波输出。原始话题保持采集时间，滤波不修改时间戳。

零偏活动文件：`../omnifleet_sensor_processing/config/airy_imu_calibration.yaml`，值是旋转到rslidar坐标后的三轴gyro均值，仅在适配器扣除一次；不可再在驱动或Smoother重复扣除。此次不是加速度六面标定或Allan标定。

官方Airy手册没有公开可配置的IMU Kalman开关；不能由此断言芯片内部完全没有滤波。本机六轴滤波属于自定义驱动发布层实现。

原始标定数据：/home/iecme/omnifleet_data/calibration/airy_imu_20261014_172859
回退源代码/配置与验证：/home/iecme/robot_backups/airy_imu_kalman_20261014_172939
