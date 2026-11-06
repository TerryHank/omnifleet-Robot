# mola_lidar_odometry｜OmniFleet 工作区介绍

LIDAR odometry system based on MOLA and MRPT components

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mola_lidar_odometry`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [config/](config)：业务/算法运行配置。当前项：`diagnostics_aggregator.yaml`。
- [scripts/](scripts)：可执行脚本。当前项：`README.md`、`lib`、`mola-lo-cli-botanicgarden`、`mola-lo-cli-citrusfarm`、`mola-lo-cli-conslam`、`mola-lo-cli-grandtour`、`mola-lo-cli-kitti`、`mola-lo-cli-kitti360`、`mola-lo-cli-mulran`、`mola-lo-cli-oxford-spires`、`mola-lo-cli-paris-luco`、`mola-lo-cli-rawlog`、`mola-lo-cli-rosbag1`、`mola-lo-cli-rosbag2`、`mola-lo-cli-tiers-livox-avia`、`mola-lo-cli-tiers-livox-horizon`、`mola-lo-cli-tiers-ouster-os0`、`mola-lo-cli-tiers-ouster-os1`、`mola-lo-cli-tiers-velodyne`、`mola-lo-gui-botanicgarden`、`mola-lo-gui-citrusfarm`、`mola-lo-gui-conslam`、`mola-lo-gui-grandtour`、`mola-lo-gui-kitti`、`mola-lo-gui-kitti360`、`mola-lo-gui-mulran`、`mola-lo-gui-ouster`、`mola-lo-gui-oxford-spires`、`mola-lo-gui-paris-luco`、`mola-lo-gui-rawlog`、`mola-lo-gui-rosbag1`、`mola-lo-gui-rosbag2`、`mola-lo-gui-tiers-livox-avia`、`mola-lo-gui-tiers-livox-horizon`、`mola-lo-gui-tiers-ouster-os0`、`mola-lo-gui-tiers-ouster-os1`、`mola-lo-gui-tiers-velodyne`。
- [test/](test)：测试。当前项：`CMakeLists.txt`、`kitti_00_fragment_gt.tum`、`mulran_KAIST01_fragment_gt.tum`、`rslidar_fragment_gt.tum`、`test_gravity_map_aligner.cpp`、`test_icp_budget_recovery.cpp`、`test_imu_scan_sync.cpp`、`test_keyframe_decider.cpp`、`test_lidar_odometry_rawlog.cpp`、`test_lidar_odometry_rosbag2.cpp`、`test_map_frame_relevel.cpp`、`test_single_deskew.cpp`、`test_worker_optimizations.cpp`。

## 工作区内声明依赖

- [mola_bridge_ros2](../mola_state_estimation_smoother/official_runtime/mola_bridge_ros2/README.omnifleet.md)
- [mola_common](../mola_common/README.omnifleet.md)
- [mola_imu_preintegration](../mola_imu_preintegration/README.omnifleet.md)
- [mola_input_kitti360_dataset](../mola_input_kitti360_dataset/README.omnifleet.md)
- [mola_input_kitti_dataset](../mola_input_kitti_dataset/README.omnifleet.md)
- [mola_input_mulran_dataset](../mola_input_mulran_dataset/README.omnifleet.md)
- [mola_input_paris_luco_dataset](../mola_input_paris_luco_dataset/README.omnifleet.md)
- [mola_input_rawlog](../mola_input_rawlog/README.omnifleet.md)
- [mola_input_rosbag2](../mola_input_rosbag2/README.omnifleet.md)
- [mola_kernel](../mola_kernel/README.omnifleet.md)
- [mola_launcher](../mola_launcher/README.omnifleet.md)
- [mola_metric_maps](../mola_metric_maps/README.omnifleet.md)
- [mola_pose_list](../mola_pose_list/README.omnifleet.md)
- [mola_state_estimation_simple](../mola_state_estimation_simple/README.omnifleet.md)
- [mola_state_estimation_smoother](../mola_state_estimation_smoother/official_runtime/mola_state_estimation_smoother/README.md)
- [mola_test_datasets](../mola_test_datasets/README.omnifleet.md)
- [mola_viz](../mola_viz/README.omnifleet.md)
- [mola_viz_imgui](../mola_viz_imgui/README.omnifleet.md)
- [mola_yaml](../mola_yaml/README.omnifleet.md)
- [mp2p_icp](../mp2p_icp/README.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
