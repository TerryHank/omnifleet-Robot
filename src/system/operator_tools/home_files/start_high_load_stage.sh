#!/usr/bin/env bash
set -eo pipefail

run_dir="/home/iecme/omnifleet_data/recordings/legacy_evidence/battery_tests/unattended_20260811_130548"
source /opt/ros/humble/setup.bash
source /home/iecme/文档/omnifleet_preserved_projects/slam_overlays/glim_cuda_ws/install/setup.bash
source /home/iecme/omnifleet_ws/install/setup.bash
source /home/iecme/文档/omnifleet_preserved_projects/ros2humble_ws/install/setup.bash
export ROS_DOMAIN_ID=0
export ROS2CLI_NO_DAEMON=1

if ! ps -p 23540 >/dev/null; then
  echo "Motor load process is not running" >&2
  exit 1
fi

echo "high_load_stage_requested=$(date --iso-8601=seconds)" >> "$run_dir/metadata.txt"
sync "$run_dir/metadata.txt"

sudo -n systemctl stop rrc-orbbec-camera.service
sudo -n systemctl stop rrc-orbbec-camera-heavy.service 2>/dev/null || true
sudo -n systemd-run \
  --unit=rrc-orbbec-camera-heavy.service \
  --uid=iecme --gid=iecme \
  --setenv=HOME=/home/iecme --setenv=ROS_DOMAIN_ID=0 \
  --property=Restart=on-failure --property=RestartSec=2 \
  /home/iecme/omnifleet_ws/src/system/operator_tools/home_files/start_orbbec_heavy.sh

for _ in $(seq 1 30); do
  if ros2 topic list | grep -q '/camera/depth/points'; then
    break
  fi
  sleep 1
done

nohup setsid bash -lc \
  'source /opt/ros/humble/setup.bash; source /home/iecme/文档/omnifleet_preserved_projects/slam_overlays/glim_cuda_ws/install/setup.bash; source /home/iecme/omnifleet_ws/install/setup.bash; source /home/iecme/文档/omnifleet_preserved_projects/ros2humble_ws/install/setup.bash; exec ros2 launch rrc_slam_bringup glim_cuda.launch.py operation:=slam_navigation navigation_profile:=full_3d map_id:=battery_full_load enable_map_projector:=true enable_nav2:=true enable_cloud_fuser:=false' \
  </dev/null > "$run_dir/glim_nav2_full_load.log" 2>&1 &
glim_pid=$!

# Force image transport plugins and point-cloud serialization to stay active.
nohup setsid bash -lc \
  'source /opt/ros/humble/setup.bash; source /home/iecme/omnifleet_ws/install/setup.bash; exec ros2 topic hz /camera/color/image_raw/compressed' \
  </dev/null > "$run_dir/color_compressed_load.log" 2>&1 &
color_load_pid=$!
nohup setsid bash -lc \
  'source /opt/ros/humble/setup.bash; source /home/iecme/omnifleet_ws/install/setup.bash; exec ros2 topic hz /camera/depth/image_raw/compressedDepth' \
  </dev/null > "$run_dir/depth_compressed_load.log" 2>&1 &
depth_load_pid=$!
nohup setsid bash -lc \
  'source /opt/ros/humble/setup.bash; source /home/iecme/omnifleet_ws/install/setup.bash; exec ros2 topic hz /camera/depth/points' \
  </dev/null > "$run_dir/camera_pointcloud_load.log" 2>&1 &
pointcloud_load_pid=$!

{
  echo "camera_heavy_start=$(date --iso-8601=seconds)"
  echo "glim_nav2_pid=$glim_pid"
  echo "color_compressed_load_pid=$color_load_pid"
  echo "depth_compressed_load_pid=$depth_load_pid"
  echo "camera_pointcloud_load_pid=$pointcloud_load_pid"
} >> "$run_dir/metadata.txt"
sync "$run_dir/metadata.txt"

echo "$glim_pid $color_load_pid $depth_load_pid $pointcloud_load_pid"
