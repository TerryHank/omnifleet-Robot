#!/bin/bash
set -e
root=/home/iecme/.local/share/omnifleet-dispatch-124
cd /home/iecme/omnifleet_a2_ws
source deploy/chassis-111/chassis_env.bash
source "$root/ros/local_setup.bash"
exec /usr/bin/python3 "$root/dispatch_nav_124.py"
