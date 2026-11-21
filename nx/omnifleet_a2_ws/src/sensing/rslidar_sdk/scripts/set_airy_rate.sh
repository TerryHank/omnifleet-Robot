#!/bin/bash
set -e
source /home/iecme/omnifleet_a2_ws/src/system/workspace_support/robot_fleet_env.bash
exec python3 /home/iecme/omnifleet_a2_ws/src/sensing/rslidar_sdk/scripts/set_scan_rate.py "$@"
