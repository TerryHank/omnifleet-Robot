#!/usr/bin/env bash
set -e
source /home/iecme/omnifleet_ws/env.bash
cd "$(dirname "${BASH_SOURCE[0]}")"
export PYTHONPATH="/home/iecme/orbbec345lg-v2.10.6:${PYTHONPATH:-}"
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp ROS_DOMAIN_ID=101
/usr/bin/python3 relay.py &
/opt/ros/humble/lib/foxglove_bridge/foxglove_bridge --ros-args --params-file bridge.yaml -p address:=192.168.3.124 -r __node:=dispatch_media_bridge &
wait -n
exit 1
