#!/bin/bash
set -e
root=/home/iecme/.local/share/omnifleet-dispatch-124
source /opt/ros/humble/setup.bash
source "$root/ros/local_setup.bash"
export OMNIFLEET_DISPATCHER_ID=robot_124
export PYTHONPATH="$root/omnifleet_rmf_adapter:$root/omnifleet-discovery:$root/omnifleet_formation_planner:$PYTHONPATH"
cd "$root/data/rmf"
exec /usr/bin/python3 -m omnifleet_rmf_adapter.launch "$@" --config "$root/omnifleet_rmf_adapter/config/framework.json" --data "$root/data"
