#!/usr/bin/env bash

# Isolated build/runtime environment for the latest MOLA workspace.
unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH CMAKE_PREFIX_PATH PYTHONPATH
unset MOLA_DIR mp2p_icp_DIR mola_DIR
unset MOLA_MODULES_LIB_PATH
# Rebuild the loader search path instead of inheriting an old MOLA overlay.
unset LD_LIBRARY_PATH PKG_CONFIG_PATH

source /opt/ros/humble/setup.bash

export CMAKE_PREFIX_PATH="/home/iecme/omnifleet_ws/install/mrpt:/home/iecme/omnifleet_ws/install/mrpt/share/mrpt:/home/iecme/omnifleet_ws/install/mrpt_libros_bridge:${CMAKE_PREFIX_PATH:-}"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/home/iecme/omnifleet_ws/install/mrpt/lib:/home/iecme/omnifleet_ws/install/mrpt_libros_bridge/lib:/lib/aarch64-linux-gnu:/usr/lib/aarch64-linux-gnu:/usr/local/cuda/lib64:/opt/MVS/lib/aarch64"
export PKG_CONFIG_PATH="/home/iecme/omnifleet_ws/install/mrpt/lib/pkgconfig:${PKG_CONFIG_PATH:-}"

export ROS_DOMAIN_ID=113
export RMW_IMPLEMENTATION=rmw_zenoh_cpp

# Load MOLA plugins only from the unified install prefix.
export MOLA_MODULES_LIB_PATH="/home/iecme/omnifleet_ws/install/kitti_metrics_eval/lib:/home/iecme/omnifleet_ws/install/mola/lib:/home/iecme/omnifleet_ws/install/mola_academic_datasets/lib:/home/iecme/omnifleet_ws/install/mola_bridge_ros2/lib:/home/iecme/omnifleet_ws/install/mola_common/lib:/home/iecme/omnifleet_ws/install/mola_demos/lib:/home/iecme/omnifleet_ws/install/mola_georeferencing/lib:/home/iecme/omnifleet_ws/install/mola_gtsam_factors/lib:/home/iecme/omnifleet_ws/install/mola_imu_preintegration/lib:/home/iecme/omnifleet_ws/install/mola_input_euroc_dataset/lib:/home/iecme/omnifleet_ws/install/mola_input_kitti360_dataset/lib:/home/iecme/omnifleet_ws/install/mola_input_kitti_dataset/lib:/home/iecme/omnifleet_ws/install/mola_input_lidar_bin_dataset/lib:/home/iecme/omnifleet_ws/install/mola_input_mulran_dataset/lib:/home/iecme/omnifleet_ws/install/mola_input_paris_luco_dataset/lib:/home/iecme/omnifleet_ws/install/mola_input_rawlog/lib:/home/iecme/omnifleet_ws/install/mola_input_rosbag2/lib:/home/iecme/omnifleet_ws/install/mola_input_video/lib:/home/iecme/omnifleet_ws/install/mola_kernel/lib:/home/iecme/omnifleet_ws/install/mola_launcher/lib:/home/iecme/omnifleet_ws/install/mola_lidar_odometry/lib:/home/iecme/omnifleet_ws/install/mola_metric_maps/lib:/home/iecme/omnifleet_ws/install/mola_msgs/lib:/home/iecme/omnifleet_ws/install/mola_pose_list/lib:/home/iecme/omnifleet_ws/install/mola_relocalization/lib:/home/iecme/omnifleet_ws/install/mola_sm_loop_closure/lib:/home/iecme/omnifleet_ws/install/mola_state_estimation/lib:/home/iecme/omnifleet_ws/install/mola_state_estimation_simple/lib:/home/iecme/omnifleet_ws/install/mola_state_estimation_smoother/lib:/home/iecme/omnifleet_ws/install/mola_test_datasets/lib:/home/iecme/omnifleet_ws/install/mola_traj_tools/lib:/home/iecme/omnifleet_ws/install/mola_viz/lib:/home/iecme/omnifleet_ws/install/mola_viz_imgui/lib:/home/iecme/omnifleet_ws/install/mola_yaml/lib:/home/iecme/omnifleet_ws/install/mp2p_icp/lib:/home/iecme/omnifleet_ws/install/mp2p_icp_core/lib:/home/iecme/omnifleet_ws/install/mp2p_icp_viz/lib"
