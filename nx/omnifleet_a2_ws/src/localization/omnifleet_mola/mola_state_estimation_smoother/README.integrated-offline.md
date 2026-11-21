# 104 官方一体化定位候选（离线）

单个 mola-cli 内只实例化 LidarOdometry、StateEstimationSmoother 和 BridgeROS2。
激光前端通过 NavStateFilter 查询主 Smoother 的运动预测，匹配结果直接调用 fuse_pose 更新同一估计器。
轮式 /odom 使用官方 RobotPose/SE(3) 相邻位姿增量路径，不再次融合其 Twist。
雷达 /rslidar_imu_data_corrected 以 radar_imu 标签进入主 Smoother，使用三轴陀螺约束。
绝对 IMU 姿态与重力约束关闭；无底盘 IMU、无车辆话题/TF 前缀。
激光前端 IMU 标签匹配为空集合，不再缓存 IMU、等待扫描末端 IMU 或单独添加重力约束。
点云仍为原始 10 Hz 整圈，去畸变关闭，20 Hz 备用驱动配置未修改。

## 入口与配置

- 系统入口：src/system/omnifleet_bringup/launch/mola_integrated_offline.launch.py。
- 本包 config/tracked-integrated-system.yaml：模块、订阅和唯一状态/TF 输出。
- 本包 config/tracked-integrated-smoother.yaml：官方 Smoother 参数。
- 本包 config/tracked-integrated-runtime.json：前端调优、IMU 职责、库隔离和时效保护。
- isolated runtime：install/mola_state_estimation_smoother/lib/integrated。

入口固定 ROS_DOMAIN_ID=214、ROS_LOCALHOST_ONLY=1，仅启动定位软件，不启动硬件或导航。
回放脚本只发布点云、校正雷达 IMU、轮式里程计和 /clock，不重放控制话题。
2026-10-15 用户追加授权实机测试后，正式104已切换到同一主Smoother框架。
实机入口为系统包 mola_integrated_localization.launch.py；离线入口继续隔离运行。

## 适配与限制

官方 Smoother/因子图算法未修改。当前 Kernel 的 LocalizationUpdate 只有位姿，
Bridge 通过官方 estimated_navstate 接口查询同一时间的速度及协方差，避免最终速度字段全零。
Bridge 从直接激光回调更新参考时间；激光超过 0.5 秒未更新时，停止对外状态/TF。

当前旧 IMU SDK 无 ImuAverager，官方 Smoother 使用每个周期保留一条读数的兼容分支，
并非对整段读数求均值。此限制可能导致振动混叠；驱动滤波和已有零偏标定仍保留。
补上输出时间戳单调保护后，完整回放最大姿态单步约2.12度，最长间隔0.604秒，回退0。
这段录包通过有限值、跳变、时效和唯一TF检查；不构成严格20Hz或实机运动验收。
无 IMU 对照姿态更平滑、但出现 0.776 秒输出间隔，未通过相同时效检查。
重力开启、同步后端及前端等待 IMU 的早期候选失败记录全部保留。

## 证据与回退

录包：omnifleet_data/tests/official_pose_forward03_20261014_205911/bag。
证据：omnifleet_ws/build/integrated_smoother_20261014。
Bridge 源码回退副本：该证据目录 BridgeROS2.before.cpp；精确差异 bridge.patch。
离线阶段原服务和配置未变；随后授权部署阶段更新了系统启动入口、重启MOLA/Nav2。
导航永久参数、IMU标定、驱动配置保持；旧启动入口在robot_backups/integrated_primary_20261015_001650。

## 实机测试结果

一次0.3m航点请求已接受，但激光位姿停更超过0.75秒，守护取消。编码器位移0，
安全速度和底盘命令全程0，未完成前进，实机运动验收未通过；没有追加运动目标。
录包/导航并行时激光源时间间隔最大1.20秒，融合最大1.322秒；当前待解决的是时效。
静止时15秒最大姿态单步约0.034度，时间戳回退0；Nav2节点active。
完整证据和所有文件准确行号见工作区build/integrated_smoother_20261014/REPORT.md。
