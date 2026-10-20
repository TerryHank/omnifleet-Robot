#!/usr/bin/env bash
set -e

source /opt/ros/humble/setup.bash
source /home/iecme/文档/omnifleet_preserved_projects/slam_overlays/glim_cuda_ws/install/setup.bash
source /home/iecme/omnifleet_ws/install/setup.bash
source /home/iecme/文档/omnifleet_preserved_projects/ros2humble_ws/install/setup.bash

if pgrep -f \
  'ros2 launch rrc_slam_bringup glim_cuda.launch.py.*navigation_profile:=local_perception_nav' \
  >/dev/null; then
  echo "Nav2 导航测试模式已经在运行，不要重复启动；现在可以直接在 Foxglove 发布航点。"
  exit 0
fi

exec ros2 launch rrc_slam_bringup glim_cuda.launch.py \
  operation:=slam_navigation \
  navigation_profile:=local_perception_nav \
  map_id:=active
