# 功能域与包索引

按功能域查阅源码和包说明。当前运行入口见 [工作区说明](../README.workspace.md)。

## common

公共消息/服务/Action、车队协议与共享基础库。业务控制逻辑不应堆放在接口包中。

- [livox_sdk2](common/Livox-SDK2/README.omnifleet.md)
- [mrpt_libros_bridge](common/mrpt_ros_bridge/ros2bridge/README.md)
- [omnifleet_interfaces](common/omnifleet_interfaces/README.omnifleet.md)
- [omnifleet_navigation_interfaces](common/omnifleet_navigation_interfaces/README.md)
- [rosbag2rawlog](common/mrpt_ros_bridge/rosbag2rawlog/README.md)
- [vikit_common](common/rpg_vikit/vikit_common/README.md)
- [vikit_ros](common/rpg_vikit/vikit_ros/README.md)

## control

本机导航任务执行、控制权仲裁、安全速度出口、车队执行和遥控协议。

- [omnifleet_behaviors](control/omnifleet_behaviors/README.omnifleet.md)
- [omnifleet_dwb_hot](control/omnifleet_dwb_hot/README.md)
- [omnifleet_local_navigation](control/omnifleet_local_navigation/README.md)
- [omnifleet_teleop](control/omnifleet_teleop/README.omnifleet.md)
- [omnifleet_vr_bridge](control/omnifleet_vr_bridge/README.md)

## localization

MOLA 定位/建图及其他定位后端、实验启动入口和重定位支持。

- [fast_livo](localization/fast_livo2_ros2/README.omnifleet.md)
- [kitti_metrics_eval](localization/omnifleet_mola/kitti_metrics_eval/README.omnifleet.md)
- [mola](localization/omnifleet_mola/mola/README.md)
- [mola_academic_datasets](localization/omnifleet_mola/mola_academic_datasets/README.md)
- [mola_bridge_ros2](localization/omnifleet_mola/mola_bridge_ros2/README.omnifleet.md)
- [mola_common](localization/omnifleet_mola/mola_common/README.omnifleet.md)
- [mola_demos](localization/omnifleet_mola/mola_demos/README.omnifleet.md)
- [mola_georeferencing](localization/omnifleet_mola/mola_georeferencing/README.omnifleet.md)
- [mola_gtsam_factors](localization/omnifleet_mola/mola_gtsam_factors/README.omnifleet.md)
- [mola_imu_preintegration](localization/omnifleet_mola/mola_imu_preintegration/README.omnifleet.md)
- [mola_input_euroc_dataset](localization/omnifleet_mola/mola_input_euroc_dataset/README.omnifleet.md)
- [mola_input_kitti360_dataset](localization/omnifleet_mola/mola_input_kitti360_dataset/README.omnifleet.md)
- [mola_input_kitti_dataset](localization/omnifleet_mola/mola_input_kitti_dataset/README.omnifleet.md)
- [mola_input_lidar_bin_dataset](localization/omnifleet_mola/mola_input_lidar_bin_dataset/README.omnifleet.md)
- [mola_input_mulran_dataset](localization/omnifleet_mola/mola_input_mulran_dataset/README.omnifleet.md)
- [mola_input_paris_luco_dataset](localization/omnifleet_mola/mola_input_paris_luco_dataset/README.omnifleet.md)
- [mola_input_rawlog](localization/omnifleet_mola/mola_input_rawlog/README.omnifleet.md)
- [mola_input_rosbag2](localization/omnifleet_mola/mola_input_rosbag2/README.omnifleet.md)
- [mola_input_video](localization/omnifleet_mola/mola_input_video/README.omnifleet.md)
- [mola_kernel](localization/omnifleet_mola/mola_kernel/README.omnifleet.md)
- [mola_launcher](localization/omnifleet_mola/mola_launcher/README.omnifleet.md)
- [mola_lidar_odometry](localization/omnifleet_mola/mola_lidar_odometry/README.omnifleet.md)
- [mola_metric_maps](localization/omnifleet_mola/mola_metric_maps/README.omnifleet.md)
- [mola_msgs](localization/omnifleet_mola/mola_msgs/README.md)
- [mola_pose_list](localization/omnifleet_mola/mola_pose_list/README.omnifleet.md)
- [mola_relocalization](localization/omnifleet_mola/mola_relocalization/README.omnifleet.md)
- [mola_sm_loop_closure](localization/omnifleet_mola/mola_sm_loop_closure/README.omnifleet.md)
- [mola_state_estimation](localization/omnifleet_mola/mola_state_estimation/README.md)
- [mola_state_estimation_simple](localization/omnifleet_mola/mola_state_estimation_simple/README.omnifleet.md)
- [mola_state_estimation_smoother](localization/omnifleet_mola/mola_state_estimation_smoother/README.omnifleet.md)
- [mola_test_datasets](localization/omnifleet_mola/mola_test_datasets/README.omnifleet.md)
- [mola_traj_tools](localization/omnifleet_mola/mola_traj_tools/README.omnifleet.md)
- [mola_viz](localization/omnifleet_mola/mola_viz/README.omnifleet.md)
- [mola_viz_imgui](localization/omnifleet_mola/mola_viz_imgui/README.omnifleet.md)
- [mola_yaml](localization/omnifleet_mola/mola_yaml/README.omnifleet.md)
- [mp2p_icp](localization/omnifleet_mola/mp2p_icp/README.md)
- [mp2p_icp_core](localization/omnifleet_mola/mp2p_icp_core/README.md)
- [mp2p_icp_viz](localization/omnifleet_mola/mp2p_icp_viz/README.md)
- [omnifleet_backend_adapters](localization/omnifleet_backend_adapters/README.md)
- [omnifleet_localization](localization/omnifleet_localization/README.omnifleet.md)
- [rtabmap_conversions](localization/rtabmap_ros/rtabmap_conversions/README.md)
- [rtabmap_costmap_plugins](localization/rtabmap_ros/rtabmap_costmap_plugins/README.md)
- [rtabmap_demos](localization/rtabmap_ros/rtabmap_demos/README.omnifleet.md)
- [rtabmap_examples](localization/rtabmap_ros/rtabmap_examples/README.md)
- [rtabmap_launch](localization/rtabmap_ros/rtabmap_launch/README.omnifleet.md)
- [rtabmap_msgs](localization/rtabmap_ros/rtabmap_msgs/README.md)
- [rtabmap_odom](localization/rtabmap_ros/rtabmap_odom/README.md)
- [rtabmap_python](localization/rtabmap_ros/rtabmap_python/README.md)
- [rtabmap_ros](localization/rtabmap_ros/rtabmap_ros/README.md)
- [rtabmap_rviz_plugins](localization/rtabmap_ros/rtabmap_rviz_plugins/README.md)
- [rtabmap_slam](localization/rtabmap_ros/rtabmap_slam/README.md)
- [rtabmap_sync](localization/rtabmap_ros/rtabmap_sync/README.md)
- [rtabmap_util](localization/rtabmap_ros/rtabmap_util/README.md)
- [rtabmap_viz](localization/rtabmap_ros/rtabmap_viz/README.md)

## map

点云到栅格/体素地图、地图坐标变换与地图导出。

- [omnifleet_cloud_grid_export](map/omnifleet_cloud_grid_export/README.omnifleet.md)
- [omnifleet_map_tf_generator](map/omnifleet_map_tf_generator/README.omnifleet.md)
- [omnifleet_mola_grid](map/omnifleet_mola_grid/README.md)

## perception

视觉、地形/深度处理及操作者使用的感知与导航示例。

- [omnifleet_terrain_analysis](perception/omnifleet_terrain_analysis/README.omnifleet.md)
- [omnifleet_tutorials](perception/omnifleet_tutorials/README.omnifleet.md)
- [omnifleet_vision](perception/omnifleet_vision/README.omnifleet.md)

## planning

Nav2 启动与规划/控制器配置、代价地图扩展和车队规划。

- [nav2_costmap_2d](planning/nav2_costmap_2d/README.omnifleet.md)
- [omnifleet_planner](planning/omnifleet_planner/README.omnifleet.md)

## sensing

雷达/相机驱动、传感器消息与点云/IMU 预处理。

- [livox_ros_driver2](sensing/livox_ros_driver2/README.omnifleet.md)
- [omnifleet_sensor_processing](sensing/omnifleet_sensor_processing/README.omnifleet.md)
- [orbbec_camera](sensing/orbbec_camera/README.md)
- [orbbec_camera_msgs](sensing/orbbec_camera_msgs/README.md)
- [orbbec_description](sensing/orbbec_description/README.md)
- [rslidar_msg](sensing/rslidar_msg/README.omnifleet.md)
- [rslidar_sdk](sensing/rslidar_sdk/README.omnifleet.md)

## simulator

车辆运动学和 Gazebo 仿真；源码存在不代表仿真依赖或场景已验收。

- [omnifleet_kinematic_sim](simulator/omnifleet_kinematic_sim/README.md)
- [omnifleet_multi_robot_sim](simulator/omnifleet_multi_robot_sim/README.md)
- [omnifleet_simulator](simulator/omnifleet_simulator/README.omnifleet.md)

## system

机器人启动、通信与运维。

- [omnifleet_bringup](system/omnifleet_bringup/README.omnifleet.md)
- [rmw_zenoh_cpp](system/rmw_zenoh_cpp/README.md)

## vehicle

底盘驱动、车辆模型/标定关系、控制器接口与舵机工具。

- [huaner_driver](vehicle/huaner_driver/package.xml)
- [omnifleet_chassis_driver](vehicle/omnifleet_chassis_driver/README.omnifleet.md)
- [omnifleet_description](vehicle/omnifleet_description/README.omnifleet.md)
- [omnifleet_servo_rqt](vehicle/omnifleet_servo_rqt/README.md)
- [ros_robot_controller](vehicle/ros_robot_controller/README.md)
- [ros_robot_controller_msgs](vehicle/ros_robot_controller_msgs/README.md)
- [rrc_tank_bridge](vehicle/rrc_tank_bridge/README.md)
- [rrc_tank_description](vehicle/rrc_tank_description/README.md)

## visualization

Foxglove、导航/协同面板、航点 UI、显示模型和录制辅助。

- [omnifleet_waypoint_ui](visualization/omnifleet_waypoint_ui/README.md)
