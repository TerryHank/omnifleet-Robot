#!/usr/bin/env bash
set -e
source /opt/ros/humble/setup.bash
source /home/iecme/文档/omnifleet_preserved_projects/ros2humble_ws/install/setup.bash
exec ros2 run rrc_glim_bridge cloud_filter --ros-args \
  -r __node:=lidar_visualization_filter \
  -p input_topic:=/rslidar_points \
  -p output_topic:=/lidar/visualization \
  -p output_frame:=base_link \
  -p translation:='[-0.041,0.0,0.15]' \
  -p rotation_rpy:='[0.0,0.0,0.167]' \
  -p range_min:=0.18 \
  -p range_max:=8.0 \
  -p z_min:=-1.0 \
  -p z_max:=3.0 \
  -p voxel_size:=0.12 \
  -p max_rate:=1.5 \
  -p remove_self:=true \
  -p self_min:='[-0.30,-0.25,-0.10]' \
  -p self_max:='[0.30,0.25,0.55]'
