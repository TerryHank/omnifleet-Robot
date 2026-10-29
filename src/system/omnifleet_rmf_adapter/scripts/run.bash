#!/usr/bin/env bash
set -e
task_ws=/home/zhangwnag/workspaces/omnifleet_ws
source /opt/ros/humble/setup.bash
source "$task_ws/install/local_setup.bash"
mkdir -p "$task_ws/data/rmf"
cd "$task_ws/data/rmf"
exec python3 -m omnifleet_rmf_adapter.launch "$@" \
  --config "$task_ws/src/system/omnifleet_rmf_adapter/config/framework.json" \
  --data "$task_ws/data"
