#!/usr/bin/env bash
set -eo pipefail

ROOT=/home/iecme/mola_latest_20260917_ws/reports/gicp_static_smoke_20260917_110134
source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_ws/install/setup.bash
export LD_LIBRARY_PATH="/home/iecme/omnifleet_ws/install/mrpt/lib:/home/iecme/omnifleet_ws/install/mola_imu_preintegration/lib:${LD_LIBRARY_PATH:-}"

/home/iecme/mola_latest_20260917_ws/reports/offline_latest_build/bin/verify_gicp_localization \
  "$ROOT/map/native_gicp_static_test.mm" \
  "$ROOT/config/lidar3d-gicp.yaml" \
  /home/iecme/omnifleet_ws/install/mola_metric_maps/lib/libmola_metric_maps.so \
  "$ROOT/results/gicp_static_frame_results.csv" \
  "$ROOT/results/gicp_static_summary.json" \
  "$ROOT"/bag/holdout_frames/frame_*.bin

