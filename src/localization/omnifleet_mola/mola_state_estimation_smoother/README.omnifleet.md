# mola_state_estimation_smoother｜OmniFleet 工作区介绍

SE(3) pose and twist path data fusion estimator

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mola_state_estimation_smoother`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [test/](test)：测试。当前项：`integration`。
- [tests/](tests)：测试。当前项：`CMakeLists.txt`、`mola-navstate-fg-params.yaml`、`test-lidar-imu-leveling.cpp`、`test-navstate-basic.cpp`、`test-navstate-odom-gnss-fusion.cpp`、`test-publish-map-to-odom.cpp`、`test-static-gnss-imu-orientation.cpp`、`test-twist-fusion.cpp`、`test-two-odometries.cpp`。

## 工作区内声明依赖

- [mola_bridge_ros2](official_runtime/mola_bridge_ros2/README.omnifleet.md)
- [mola_common](../mola_common/README.omnifleet.md)
- [mola_gtsam_factors](official_runtime/mola_gtsam_factors/README.md)
- [mola_imu_preintegration](../mola_imu_preintegration/README.omnifleet.md)
- [mola_kernel](../mola_kernel/README.omnifleet.md)
- [mola_launcher](../mola_launcher/README.omnifleet.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。

## 104 官方轮式位姿增量与激光位姿融合

固定上游提交074ec696e759bc013c1eb08da290bfbb0d0befe2，官方Smoother与因子源码位于official_runtime/。此目录COLCON_IGNORE用于避免和工作区旧SDK产生重复包注册；算法源码未改，CMake仅做本机MRPT目标名适配。
入口ros2-launchs/ros2-tracked-lidar-wheel-pose.launch.py，系统mola-cli-launchs/tracked_lidar_wheel_pose.yaml，参数params/tracked-lidar-wheel-pose.yaml；由system/omnifleet_bringup总编排。
BridgeROS2直接读取/lidar_odometry/pose与/odom，输出传感器标签map、wheel_odom，两路均按CObservationRobotPose送入官方fuse_pose。map为绝对位姿先验，wheel_odom首帧估计坐标系对齐，后续相邻SE(3)位姿增量进入官方因子图；不融合原始Twist，不走旧wheel_velocity分支。
轮式增量噪声sigma_lin=0.1m、sigma_ang=0.2rad，增长项0.1m/sqrt(m)、0.2rad/sqrt(rad)。这些权重作用三轴，轮式填零z/roll/pitch仍有有限权重，是待运动验收的保守配置，不是逐轴屏蔽或已标定最佳值。
配套新版Bridge/Smoother/GTSAM因子库安装在本包lib/official_pose，仅在融合进程隔离加载，并显式核对当前Kernel3.2 SDK。旧SDK与库保留用于其他模块及回退，不被该融合进程混用。
雷达IMU仅给现有主定位链；外部Smoother没有IMU订阅并拒绝全部IMU标签，不接底盘IMU。最终/state_estimation/pose与唯一map->base_link TF供导航使用，车端没有车辆前缀。
Bridge边界保留输入时效/帧/有限值检查、激光协方差下限以及激光停更0.5秒停止对外发布的保护；不改变官方因子数学。去畸变仍关闭，导航永久参数不改。
这是下游位姿融合，轮式约束最终导航状态；主定位前端仍使用原来的Simple运动预测/重力辅助，不声称本次已把轮式反馈接入激光配准预测。录包/静止验证不等于新的运动闭环验收。
