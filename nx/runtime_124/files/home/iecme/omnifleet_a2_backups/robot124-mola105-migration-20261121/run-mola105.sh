#!/bin/bash
set -e
cd /home/iecme/omnifleet_a2_ws
source src/system/workspace_support/robot_fleet_env.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp ROS_DOMAIN_ID=42
stage="/home/iecme/omnifleet_a2_backups/robot124-mola105-migration-20261121"
args=()
if [ -e "$stage/restore-next-start" ]; then args+=(restore_snapshot:=true); fi
exec ros2 launch "$stage/release105/mola105-localization.launch.py" "${args[@]}"
