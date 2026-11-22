# 功能域与包索引

2026-10-14：11个功能域，103个colcon可识别包/组件。以下是源代码清单，不是已构建/已运行清单。

## common

公共消息/服务/Action、车队协议与共享基础库。业务控制逻辑不应堆放在接口包中。

- [livox_sdk2](../omnifleet_ws/src/common/Livox-SDK2/README.omnifleet.md)
- [mrpt_libros_bridge](../omnifleet_ws/src/common/mrpt_ros_bridge/ros2bridge/README.md)
- [omnifleet_interfaces](../omnifleet_ws/src/common/omnifleet_interfaces/README.omnifleet.md)
- [omnifleet_navigation_interfaces](../omnifleet_ws/src/common/omnifleet_navigation_interfaces/README.md)
- [rosbag2rawlog](../omnifleet_ws/src/common/mrpt_ros_bridge/rosbag2rawlog/README.md)
- [vikit_common](../omnifleet_ws/src/common/rpg_vikit/vikit_common/README.md)
- [vikit_ros](../omnifleet_ws/src/common/rpg_vikit/vikit_ros/README.md)

## control

本机导航任务执行、控制权仲裁、安全速度出口、车队执行和遥控协议。

- [omnifleet_behaviors](../omnifleet_ws/src/control/omnifleet_behaviors/README.omnifleet.md)
- [omnifleet_dwb_hot](../omnifleet_ws/src/control/omnifleet_dwb_hot/README.md)
- [omnifleet_local_navigation](../omnifleet_ws/src/control/omnifleet_local_navigation/README.md)
- [omnifleet_teleop](../omnifleet_ws/src/control/omnifleet_teleop/README.omnifleet.md)
- [omnifleet_vr_bridge](../omnifleet_ws/src/control/omnifleet_vr_bridge/README.md)

## localization

MOLA 定位/建图及其他定位后端、实验启动入口和重定位支持。

- [fast_livo](../omnifleet_ws/src/localization/fast_livo2_ros2/README.omnifleet.md)
- [kitti_metrics_eval](../omnifleet_ws/src/localization/omnifleet_mola/kitti_metrics_eval/README.omnifleet.md)
- [mola](../omnifleet_ws/src/localization/omnifleet_mola/mola/README.md)
- [mola_academic_datasets](../omnifleet_ws/src/localization/omnifleet_mola/mola_academic_datasets/README.md)
- [mola_bridge_ros2](../omnifleet_ws/src/localization/omnifleet_mola/mola_bridge_ros2/README.omnifleet.md)
- [mola_common](../omnifleet_ws/src/localization/omnifleet_mola/mola_common/README.omnifleet.md)
- [mola_demos](../omnifleet_ws/src/localization/omnifleet_mola/mola_demos/README.omnifleet.md)
- [mola_georeferencing](../omnifleet_ws/src/localization/omnifleet_mola/mola_georeferencing/README.omnifleet.md)
- [mola_gtsam_factors](../omnifleet_ws/src/localization/omnifleet_mola/mola_gtsam_factors/README.omnifleet.md)
- [mola_imu_preintegration](../omnifleet_ws/src/localization/omnifleet_mola/mola_imu_preintegration/README.omnifleet.md)
- [mola_input_euroc_dataset](../omnifleet_ws/src/localization/omnifleet_mola/mola_input_euroc_dataset/README.omnifleet.md)
- [mola_input_kitti360_dataset](../omnifleet_ws/src/localization/omnifleet_mola/mola_input_kitti360_dataset/README.omnifleet.md)
- [mola_input_kitti_dataset](../omnifleet_ws/src/localization/omnifleet_mola/mola_input_kitti_dataset/README.omnifleet.md)
- [mola_input_lidar_bin_dataset](../omnifleet_ws/src/localization/omnifleet_mola/mola_input_lidar_bin_dataset/README.omnifleet.md)
- [mola_input_mulran_dataset](../omnifleet_ws/src/localization/omnifleet_mola/mola_input_mulran_dataset/README.omnifleet.md)
- [mola_input_paris_luco_dataset](../omnifleet_ws/src/localization/omnifleet_mola/mola_input_paris_luco_dataset/README.omnifleet.md)
- [mola_input_rawlog](../omnifleet_ws/src/localization/omnifleet_mola/mola_input_rawlog/README.omnifleet.md)
- [mola_input_rosbag2](../omnifleet_ws/src/localization/omnifleet_mola/mola_input_rosbag2/README.omnifleet.md)
- [mola_input_video](../omnifleet_ws/src/localization/omnifleet_mola/mola_input_video/README.omnifleet.md)
- [mola_kernel](../omnifleet_ws/src/localization/omnifleet_mola/mola_kernel/README.omnifleet.md)
- [mola_launcher](../omnifleet_ws/src/localization/omnifleet_mola/mola_launcher/README.omnifleet.md)
- [mola_lidar_odometry](../omnifleet_ws/src/localization/omnifleet_mola/mola_lidar_odometry/README.omnifleet.md)
- [mola_metric_maps](../omnifleet_ws/src/localization/omnifleet_mola/mola_metric_maps/README.omnifleet.md)
- [mola_msgs](../omnifleet_ws/src/localization/omnifleet_mola/mola_msgs/README.md)
- [mola_pose_list](../omnifleet_ws/src/localization/omnifleet_mola/mola_pose_list/README.omnifleet.md)
- [mola_relocalization](../omnifleet_ws/src/localization/omnifleet_mola/mola_relocalization/README.omnifleet.md)
- [mola_sm_loop_closure](../omnifleet_ws/src/localization/omnifleet_mola/mola_sm_loop_closure/README.omnifleet.md)
- [mola_state_estimation](../omnifleet_ws/src/localization/omnifleet_mola/mola_state_estimation/README.md)
- [mola_state_estimation_simple](../omnifleet_ws/src/localization/omnifleet_mola/mola_state_estimation_simple/README.omnifleet.md)
- [mola_state_estimation_smoother](../omnifleet_ws/src/localization/omnifleet_mola/mola_state_estimation_smoother/README.omnifleet.md)
- [mola_test_datasets](../omnifleet_ws/src/localization/omnifleet_mola/mola_test_datasets/README.omnifleet.md)
- [mola_traj_tools](../omnifleet_ws/src/localization/omnifleet_mola/mola_traj_tools/README.omnifleet.md)
- [mola_viz](../omnifleet_ws/src/localization/omnifleet_mola/mola_viz/README.omnifleet.md)
- [mola_viz_imgui](../omnifleet_ws/src/localization/omnifleet_mola/mola_viz_imgui/README.omnifleet.md)
- [mola_yaml](../omnifleet_ws/src/localization/omnifleet_mola/mola_yaml/README.omnifleet.md)
- [mp2p_icp](../omnifleet_ws/src/localization/omnifleet_mola/mp2p_icp/README.md)
- [mp2p_icp_core](../omnifleet_ws/src/localization/omnifleet_mola/mp2p_icp_core/README.md)
- [mp2p_icp_viz](../omnifleet_ws/src/localization/omnifleet_mola/mp2p_icp_viz/README.md)
- [omnifleet_backend_adapters](../omnifleet_ws/src/localization/omnifleet_backend_adapters/README.md)
- [omnifleet_localization](../omnifleet_ws/src/localization/omnifleet_localization/README.omnifleet.md)
- [rtabmap_conversions](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_conversions/README.md)
- [rtabmap_costmap_plugins](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_costmap_plugins/README.md)
- [rtabmap_demos](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_demos/README.omnifleet.md)
- [rtabmap_examples](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_examples/README.md)
- [rtabmap_launch](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_launch/README.omnifleet.md)
- [rtabmap_msgs](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_msgs/README.md)
- [rtabmap_odom](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_odom/README.md)
- [rtabmap_python](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_python/README.md)
- [rtabmap_ros](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_ros/README.md)
- [rtabmap_rviz_plugins](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_rviz_plugins/README.md)
- [rtabmap_slam](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_slam/README.md)
- [rtabmap_sync](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_sync/README.md)
- [rtabmap_util](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_util/README.md)
- [rtabmap_viz](../omnifleet_ws/src/localization/rtabmap_ros/rtabmap_viz/README.md)

## map

点云到栅格/体素地图、地图坐标变换与地图导出。

- [omnifleet_cloud_grid_export](../omnifleet_ws/src/map/omnifleet_cloud_grid_export/README.omnifleet.md)
- [omnifleet_map_tf_generator](../omnifleet_ws/src/map/omnifleet_map_tf_generator/README.omnifleet.md)
- [omnifleet_mola_grid](../omnifleet_ws/src/map/omnifleet_mola_grid/README.md)

## perception

视觉、地形/深度处理及操作者使用的感知与导航示例。

- [omnifleet_terrain_analysis](../omnifleet_ws/src/perception/omnifleet_terrain_analysis/README.omnifleet.md)
- [omnifleet_tutorials](../omnifleet_ws/src/perception/omnifleet_tutorials/README.omnifleet.md)
- [omnifleet_vision](../omnifleet_ws/src/perception/omnifleet_vision/README.omnifleet.md)

## planning

Nav2 启动与规划/控制器配置、代价地图扩展和车队规划。

- [nav2_costmap_2d](../omnifleet_ws/src/planning/nav2_costmap_2d/README.omnifleet.md)
- [omnifleet_planner](../omnifleet_ws/src/planning/omnifleet_planner/README.omnifleet.md)

## sensing

雷达/相机驱动、传感器消息与点云/IMU 预处理。

- [livox_ros_driver2](../omnifleet_ws/src/sensing/livox_ros_driver2/README.omnifleet.md)
- [omnifleet_sensor_processing](../omnifleet_ws/src/sensing/omnifleet_sensor_processing/README.omnifleet.md)
- [orbbec_camera](../omnifleet_ws/src/sensing/orbbec_camera/README.md)
- [orbbec_camera_msgs](../omnifleet_ws/src/sensing/orbbec_camera_msgs/README.md)
- [orbbec_description](../omnifleet_ws/src/sensing/orbbec_description/README.md)
- [rslidar_msg](../omnifleet_ws/src/sensing/rslidar_msg/README.omnifleet.md)
- [rslidar_sdk](../omnifleet_ws/src/sensing/rslidar_sdk/README.omnifleet.md)

## simulator

车辆运动学和 Gazebo 仿真；源码存在不代表仿真依赖或场景已验收。

- [omnifleet_kinematic_sim](../omnifleet_ws/src/simulator/omnifleet_kinematic_sim/README.md)
- [omnifleet_multi_robot_sim](../omnifleet_ws/src/simulator/omnifleet_multi_robot_sim/README.md)
- [omnifleet_simulator](../omnifleet_ws/src/simulator/omnifleet_simulator/README.omnifleet.md)

## system

机器人启动集成、协调器、MSC 入口、通信运行脚本和运维支持。

- [omnifleet_bringup](../omnifleet_ws/src/system/omnifleet_bringup/README.omnifleet.md)
- [rmw_zenoh_cpp](../omnifleet_ws/src/system/rmw_zenoh_cpp/README.md)

## vehicle

底盘驱动、车辆模型/标定关系、控制器接口与舵机工具。

- [omnifleet_chassis_driver](../omnifleet_ws/src/vehicle/omnifleet_chassis_driver/README.omnifleet.md)
- [omnifleet_description](../omnifleet_ws/src/vehicle/omnifleet_description/README.omnifleet.md)
- [omnifleet_servo_rqt](../omnifleet_ws/src/vehicle/omnifleet_servo_rqt/README.md)
- [ros_robot_controller](../omnifleet_ws/src/vehicle/ros_robot_controller/README.md)
- [ros_robot_controller_msgs](../omnifleet_ws/src/vehicle/ros_robot_controller_msgs/README.md)
- [rrc_tank_bridge](../omnifleet_ws/src/vehicle/rrc_tank_bridge/README.md)
- [rrc_tank_description](../omnifleet_ws/src/vehicle/rrc_tank_description/README.md)

## visualization

Foxglove、导航/协同面板、航点 UI、显示模型和录制辅助。

- [omnifleet_waypoint_ui](../omnifleet_ws/src/visualization/omnifleet_waypoint_ui/README.md)

2026-10-14：104 已移除旧 MSC 专用包，以上目录条目不再列出已退役包；回退资料仅位于 robot_backups。
