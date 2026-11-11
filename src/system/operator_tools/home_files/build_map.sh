#!/usr/bin/env bash
set -eo pipefail

ROOT=$(cat /tmp/current_smoke_root.txt)
BAG_DIR=$(find "$ROOT/bag" -maxdepth 1 -mindepth 1 -type d | head -n 1)

echo "Starting MOLA GICP mapping from: $BAG_DIR"
echo "Output map: $ROOT/map/native_gicp_static_test.mm"

source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_a2_ws/install_111/setup.bash

export LD_LIBRARY_PATH="/home/iecme/omnifleet_a2_ws/install_111/mrpt_libros_bridge/lib:/home/iecme/omnifleet_a2_ws/install_111/mrpt/lib:/home/iecme/omnifleet_a2_ws/install_111/mola_imu_preintegration/lib:${LD_LIBRARY_PATH:-}"

export MOLA_WITH_GUI=false
export MOLA_INPUT_ROSBAG2="$BAG_DIR"
export MOLA_ODOMETRY_PIPELINE_YAML="$ROOT/config/lidar3d-gicp.yaml"
export MOLA_LIDAR_TOPIC="/rslidar_points"
export MOLA_LIDAR_NAME="lidar"
export MOLA_IMU_TOPIC="/omnifleet_t2/experiments/rslidar_imu_corrected"
export MOLA_IMU_NAME="imu"
export MOLA_TF_TOPIC="/tf"
export MOLA_TF_STATIC_TOPIC="/tf_static"
export MOLA_TF_BASE_LINK="base_link"
export MOLA_QUIT_ON_DATASET_END=true
export MOLA_SAVE_MM="$ROOT/map/native_gicp_static_test.mm"
export MOLA_MAX_ICP_ITERATIONS=50
export LIDAR_POSE_X="-0.041"
export LIDAR_POSE_Y="0.0"
export LIDAR_POSE_Z="0.150"
export LIDAR_POSE_YAW="0.0"
export LIDAR_POSE_PITCH="0.0"
export LIDAR_POSE_ROLL="0.0"
export MOLA_USE_FIXED_LIDAR_POSE=true
export IMU_POSE_X="-0.041"
export IMU_POSE_Y="0.0"
export IMU_POSE_Z="0.150"
export IMU_POSE_YAW="0.0"
export IMU_POSE_PITCH="0.0"
export IMU_POSE_ROLL="0.0"
export MOLA_USE_FIXED_IMU_POSE=true
export MOLA_LOCALMAP_CLASS="mola::KeyframePointCloudMap"
export MOLA_MAPPING_ENABLED=true
export MOLA_TIME_WARP=2.0

mola-cli   /home/iecme/mola_latest_20260917_ws/src/mola_lidar_odometry/mola-cli-launchs/lidar_odometry_from_rosbag2.yaml   2>&1 | tee "$ROOT/logs/mola_mapping.log"

echo "MOLA exited. Checking generated map:"
ls -lh "$ROOT/map/native_gicp_static_test.mm"

