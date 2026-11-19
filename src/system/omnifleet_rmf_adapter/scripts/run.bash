#!/usr/bin/env bash
set -e
task_ws=/home/iecme/omnifleet_ws
task_data=/home/iecme/omnifleet_data/dispatch
source "$task_ws/src/system/workspace_support/robot_fleet_env.bash"
export OMNIFLEET_DISPATCHER_ID="$OMNIFLEET_ROBOT_ID"
mkdir -p "$task_data/rmf"
cd "$task_data/rmf"
exec python3 -m omnifleet_rmf_adapter.launch "$@" \
  --config "$task_ws/src/system/omnifleet_rmf_adapter/config/framework.json" \
  --data "$task_data"
