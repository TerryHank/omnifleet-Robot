#!/usr/bin/env bash
set -e
source /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash
exec python3 /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/run.py "$@"
