#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_ws/install/setup.bash
exec ros2 launch orbbec_camera ob_camera.launch.py \
  color_width:=640 color_height:=480 color_fps:=30 color_format:=MJPG \
  depth_width:=640 depth_height:=400 depth_fps:=30 depth_format:=Y12 \
  ir_width:=640 ir_height:=400 ir_fps:=30 ir_format:=Y10 \
  enable_color:=true enable_depth:=true enable_ir:=true \
  depth_registration:=true \
  enable_point_cloud:=true enable_colored_point_cloud:=true \
  enable_publish_extrinsic:=true
