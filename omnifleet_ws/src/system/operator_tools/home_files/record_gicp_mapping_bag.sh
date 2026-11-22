#!/usr/bin/env bash
# ==============================================================================
# Script: record_gicp_mapping_bag.sh
# Target: OmniFleet T2 robot_113
# Purpose: Record complete, un-decimated raw 3D LiDAR, IMU, and TF data for
#          building native MOLA GICP maps.
# ==============================================================================
set -eo pipefail

BAG_ROOT="${GICP_BAG_DIR:-/home/iecme/omnifleet_data/recordings/bags/gicp_mapping}"
CHECK_ONLY=false
DURATION_SEC=0

while [ $# -gt 0 ]; do
  case "$1" in
    --check-only|-c)
      CHECK_ONLY=true
      shift
      ;;
    --duration|-d)
      DURATION_SEC="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

echo "======================================================================"
echo "[GICP Record] Starting Pre-flight Verification on $(hostname)"
echo "======================================================================"

if [ -f "/home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash" ]; then
  source "/home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash"
elif [ -f "/opt/ros/humble/setup.bash" ]; then
  source "/opt/ros/humble/setup.bash"
fi

export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_zenoh_cpp}"
if [ -f "/etc/omnifleet_t2/zenoh-session.json5" ]; then
  export ZENOH_SESSION_CONFIG_URI="/etc/omnifleet_t2/zenoh-session.json5"
fi

echo "[Env] ROS_DISTRO: $ROS_DISTRO"
echo "[Env] RMW_IMPLEMENTATION: $RMW_IMPLEMENTATION"
echo "[Env] ROS_DOMAIN_ID: $ROS_DOMAIN_ID"

# Check disk space
mkdir -p "$BAG_ROOT"
AVAIL_KB=$(df -k "$BAG_ROOT" | awk 'NR==2 {print $4}')
AVAIL_GB=$(( AVAIL_KB / 1024 / 1024 ))
echo "[Disk] Available space in $BAG_ROOT: ${AVAIL_GB} GB"
if [ "$AVAIL_GB" -lt 5 ]; then
  echo "ERROR: Less than 5 GB disk space available in $BAG_ROOT!" >&2
  exit 2
fi

LIDAR_TOPIC="/rslidar_points"
RAW_IMU_TOPIC="/rslidar_imu_data"
CORR_IMU_TOPIC="/omnifleet_t2/experiments/rslidar_imu_corrected"
TF_TOPIC="/tf"
TF_STATIC_TOPIC="/tf_static"
ODOM_TOPIC="/odom"

echo "[Topics to Record]"
echo "  - LiDAR raw pointcloud: $LIDAR_TOPIC"
echo "  - Raw LiDAR IMU:        $RAW_IMU_TOPIC"
echo "  - Corrected IMU:        $CORR_IMU_TOPIC"
echo "  - Transform tree:       $TF_TOPIC (/tf)"
echo "  - Static transforms:    $TF_STATIC_TOPIC (/tf_static)"
echo "  - Chassis odometry:     $ODOM_TOPIC"

if [ "$CHECK_ONLY" = true ]; then
  echo "======================================================================"
  echo "[GICP Record] Pre-flight Check PASSED (Check-Only Mode, no recording)."
  echo "======================================================================"
  exit 0
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BAG_NAME="gicp_mapping_${TIMESTAMP}"
BAG_DIR="${BAG_ROOT}/${BAG_NAME}"

echo "======================================================================"
echo "[GICP Record] Starting rosbag2 recording to: $BAG_DIR"
echo "======================================================================"

START_TIME_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cleanup() {
  echo ""
  echo "======================================================================"
  echo "[GICP Record] Stopping recording and indexing metadata..."
  echo "======================================================================"
  END_TIME_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  sleep 3
  if [ -d "$BAG_DIR" ]; then
    echo "--- Rosbag2 Info ---"
    ros2 bag info "$BAG_DIR" || true
    echo "--- Computing SHA256 Checksums ---"
    find "$BAG_DIR" -type f \( -name "*.db3" -o -name "*.mcap" \) -exec sha256sum {} + | tee "$BAG_DIR/SHA256SUMS.txt"
    cat << META > "$BAG_DIR/recording_meta.json"
{
  "bag_name": "$BAG_NAME",
  "start_time_utc": "$START_TIME_UTC",
  "end_time_utc": "$END_TIME_UTC",
  "lidar_topic": "$LIDAR_TOPIC",
  "raw_imu_topic": "$RAW_IMU_TOPIC",
  "corrected_imu_topic": "$CORR_IMU_TOPIC",
  "target_pipeline": "mola_lidar_odometry/pipelines/lidar3d-gicp.yaml",
  "max_icp_iterations_candidate": 50
}
META
    echo "[GICP Record] Recording successfully archived in: $BAG_DIR"
  fi
  exit 0
}

trap cleanup SIGINT SIGTERM

QOS_PATH="/home/iecme/文档/omnifleet_home_files/mapping_qos.yaml"
CMD=(ros2 bag record -o "$BAG_DIR")
if [ -f "$QOS_PATH" ]; then
  CMD+=(--qos-profile-overrides-path "$QOS_PATH")
fi

CMD+=(
  "$LIDAR_TOPIC"
  "$RAW_IMU_TOPIC"
  "$CORR_IMU_TOPIC"
  "$TF_TOPIC"
  "/tf"
  "$TF_STATIC_TOPIC"
  "/tf_static"
  "$ODOM_TOPIC"
)

if [ "$DURATION_SEC" -gt 0 ]; then
  echo "[GICP Record] Timed recording: duration = ${DURATION_SEC} seconds"
  timeout --signal=SIGINT "${DURATION_SEC}" "${CMD[@]}" || true
  cleanup
else
  "${CMD[@]}"
fi

