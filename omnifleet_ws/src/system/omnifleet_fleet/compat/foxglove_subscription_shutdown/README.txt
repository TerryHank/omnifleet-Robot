Foxglove-only RMW subscription shutdown backport.
Upstream: https://github.com/ros2/rmw_zenoh/pull/994
Retain an application-thread owner until shutdown finishes, and release the
subscription mutex before the blocking Zenoh undeclare.
Only foxglove_start.sh prepends install/foxglove_zenoh_compat/lib.
The shared install/rmw_zenoh_cpp library is not replaced.
Rebuild after building rmw_zenoh_cpp in the standard workspace layout:
source /home/iecme/omnifleet_ws/env.bash
python3 /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/compat/foxglove_subscription_shutdown/build.py
Output: /home/iecme/omnifleet_ws/build/foxglove_zenoh_compat/librmw_zenoh_cpp.so
Reproduction and validation evidence: /home/iecme/robot_backups/foxglove-deadlock-20261020
