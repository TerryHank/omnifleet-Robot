#!/bin/bash
set -e
source /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash
exec /usr/bin/python3 /home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/nav2_permanent_panel/navigation_restart.py "$@"
