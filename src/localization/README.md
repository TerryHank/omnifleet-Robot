# localization 功能域

MOLA 定位/建图及其他定位后端、实验启动入口和重定位支持。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [fast_livo](fast_livo2_ros2/README.omnifleet.md) | This is a modified version of LOAM which is original algorithm is described in the following paper: J. Zhang and S. Singh. LOAM: Lidar Odometry and Mapping in Real-time. Robotics: Science and Systems Conference (RSS). Berkeley, CA, July 2014. |
| [kitti_metrics_eval](omnifleet_mola/kitti_metrics_eval/README.omnifleet.md) | CLI tool to evaluate the KITTI odometry bechmark metrics to trajectory files |
| [mola](omnifleet_mola/mola/README.md) | Metapackage with all core open-sourced MOLA packages. |
| [mola_academic_datasets](omnifleet_mola/mola_academic_datasets/README.md) | Metapackage with all packages supporting reading academic datasets. |
| [mola_bridge_ros2](omnifleet_mola/mola_bridge_ros2/README.omnifleet.md) | Bidirectional bridge ROS2-MOLA |
| [mola_common](omnifleet_mola/mola_common/README.omnifleet.md) | Common CMake scripts to all MOLA modules |
| [mola_demos](omnifleet_mola/mola_demos/README.omnifleet.md) | Demo and example launch files for MOLA |
| [mola_georeferencing](omnifleet_mola/mola_georeferencing/README.omnifleet.md) | C++ library for georeferencing key-frame maps (simplemaps) and related CLI tools |
| [mola_gtsam_factors](omnifleet_mola/mola_gtsam_factors/README.omnifleet.md) | C++ library with reusable GTSAM Factors useful in georeferencing and state-estimation MOLA modules |
| [mola_imu_preintegration](omnifleet_mola/mola_imu_preintegration/README.omnifleet.md) | Integrator of IMU angular velocity readings |
| [mola_input_euroc_dataset](omnifleet_mola/mola_input_euroc_dataset/README.omnifleet.md) | Offline RawDataSource from EUROC SLAM datasets |
| [mola_input_kitti360_dataset](omnifleet_mola/mola_input_kitti360_dataset/README.omnifleet.md) | Offline RawDataSource from Kitti-360 datasets |
| [mola_input_kitti_dataset](omnifleet_mola/mola_input_kitti_dataset/README.omnifleet.md) | Offline RawDataSource from Kitti odometry/SLAM datasets |
| [mola_input_lidar_bin_dataset](omnifleet_mola/mola_input_lidar_bin_dataset/README.omnifleet.md) | Offline RawDataSource from LiDAR datasets stored as `.bin` files in the Kitti binary format |
| [mola_input_mulran_dataset](omnifleet_mola/mola_input_mulran_dataset/README.omnifleet.md) | Offline RawDataSource from MulRan datasets |
| [mola_input_paris_luco_dataset](omnifleet_mola/mola_input_paris_luco_dataset/README.omnifleet.md) | Offline RawDataSource from Paris LUCO (CT-ICP) odometry/SLAM datasets |
| [mola_input_rawlog](omnifleet_mola/mola_input_rawlog/README.omnifleet.md) | Offline RawDataSource from MRPT rawlog datasets |
| [mola_input_rosbag2](omnifleet_mola/mola_input_rosbag2/README.omnifleet.md) | Offline RawDataSource from rosbag2 datasets |
| [mola_input_video](omnifleet_mola/mola_input_video/README.omnifleet.md) | RawDataSource from live or offline video sources |
| [mola_kernel](omnifleet_mola/mola_kernel/README.omnifleet.md) | Fundamental C++ virtual interfaces and data types for the rest of MOLA modules |
| [mola_launcher](omnifleet_mola/mola_launcher/README.omnifleet.md) | Launcher app for MOLA systems |
| [mola_lidar_odometry](omnifleet_mola/mola_lidar_odometry/README.omnifleet.md) | LIDAR odometry system based on MOLA and MRPT components |
| [mola_metric_maps](omnifleet_mola/mola_metric_maps/README.omnifleet.md) | Advanced metric map classes, using the generic `mrpt::maps::CMetricMap` interface, for use in other MOLA odometry and SLAM modules. |
| [mola_msgs](omnifleet_mola/mola_msgs/README.md) | ROS message, services, and actions used in other MOLA packages. |
| [mola_pose_list](omnifleet_mola/mola_pose_list/README.omnifleet.md) | C++ library for searchable pose lists |
| [mola_relocalization](omnifleet_mola/mola_relocalization/README.omnifleet.md) | C++ library with algorithms for relocalization, global localization, or pose estimation given a large initial uncertainty |
| [mola_sm_loop_closure](omnifleet_mola/mola_sm_loop_closure/README.omnifleet.md) | Simplemap loop-closure postprocessing library and CLI tool |
| [mola_state_estimation](omnifleet_mola/mola_state_estimation/README.md) | Metapackage with all MOLA state estimation packages. |
| [mola_state_estimation_simple](omnifleet_mola/mola_state_estimation_simple/README.omnifleet.md) | SE(3) pose and twist path data fusion estimator |
| [mola_state_estimation_smoother](omnifleet_mola/mola_state_estimation_smoother/README.omnifleet.md) | SE(3) pose and twist path data fusion estimator |
| [mola_test_datasets](omnifleet_mola/mola_test_datasets/README.omnifleet.md) | Small SLAM dataset extracts used for demos or unit tests in the rest of MOLA packages |
| [mola_traj_tools](omnifleet_mola/mola_traj_tools/README.omnifleet.md) | CLI tools to manipulate trajectory files as a complement to the evo package |
| [mola_viz](omnifleet_mola/mola_viz/README.omnifleet.md) | GUI for MOLA |
| [mola_viz_imgui](omnifleet_mola/mola_viz_imgui/README.omnifleet.md) | Dear ImGui (docking branch) GUI backend for MOLA |
| [mola_yaml](omnifleet_mola/mola_yaml/README.omnifleet.md) | YAML helper library common to MOLA modules |
| [mp2p_icp](omnifleet_mola/mp2p_icp/README.md) | Metapackage for mp2p_icp: depends on mp2p_icp_core (headless libraries and CLI applications) and mp2p_icp_viz (GUI applications). |
| [mp2p_icp_core](omnifleet_mola/mp2p_icp_core/README.md) | C++ libraries for multi primitive-to-primitive (MP2P) ICP algorithms and point cloud processing pipelines, plus headless CLI applications. No GUI/display dependencies; see mp2p_icp_viz for the GUI apps. |
| [mp2p_icp_viz](omnifleet_mola/mp2p_icp_viz/README.md) | GUI applications for mp2p_icp: mm-viewer (interactive *.mm map viewer) and icp-log-viewer (ICP log inspector). Kept in a separate package from mp2p_icp_core so headless consumers don't need to pull in mrpt_libgui. |
| [omnifleet_backend_adapters](omnifleet_backend_adapters/README.md) | FAST-LIVO2 与 RTAB-Map 的隔离 Airy 启动配置。当前主定位链仍为 MOLA。 |
| [omnifleet_localization](omnifleet_localization/README.omnifleet.md) | 定位域集成与兼容接口；传感器处理、栅格等实现已拆到对应新包。 |
| [rtabmap_conversions](rtabmap_ros/rtabmap_conversions/README.md) | RTAB-Map's conversions package. This package can be used to convert rtabmap_msgs's msgs into RTAB-Map's library objects. |
| [rtabmap_costmap_plugins](rtabmap_ros/rtabmap_costmap_plugins/README.md) | RTAB-Map's costmap plugins. |
| [rtabmap_demos](rtabmap_ros/rtabmap_demos/README.omnifleet.md) | RTAB-Map's demo launch files. |
| [rtabmap_examples](rtabmap_ros/rtabmap_examples/README.md) | RTAB-Map's example launch files. |
| [rtabmap_launch](rtabmap_ros/rtabmap_launch/README.omnifleet.md) | RTAB-Map's main launch files. |
| [rtabmap_msgs](rtabmap_ros/rtabmap_msgs/README.md) | RTAB-Map's msgs package. |
| [rtabmap_odom](rtabmap_ros/rtabmap_odom/README.md) | RTAB-Map's odometry package. |
| [rtabmap_python](rtabmap_ros/rtabmap_python/README.md) | RTAB-Map's python package. |
| [rtabmap_ros](rtabmap_ros/rtabmap_ros/README.md) | RTAB-Map Stack |
| [rtabmap_rviz_plugins](rtabmap_ros/rtabmap_rviz_plugins/README.md) | RTAB-Map's rviz plugins. |
| [rtabmap_slam](rtabmap_ros/rtabmap_slam/README.md) | RTAB-Map's SLAM package. |
| [rtabmap_sync](rtabmap_ros/rtabmap_sync/README.md) | RTAB-Map's synchronization package. |
| [rtabmap_util](rtabmap_ros/rtabmap_util/README.md) | RTAB-Map's various useful nodes and nodelets. |
| [rtabmap_viz](rtabmap_ros/rtabmap_viz/README.md) | RTAB-Map's visualization package. |

## 非独立ROS包的运行/支持目录

- [omnifleet_relocalization/](omnifleet_relocalization)：MOLA 重定位、地图恢复和故障证据支持目录，保留旧兼容入口。
