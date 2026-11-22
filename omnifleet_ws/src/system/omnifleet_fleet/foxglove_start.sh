#!/usr/bin/env bash
set -eo pipefail

source /home/iecme/omnifleet_a2_ws/src/system/omnifleet_fleet/env.bash

# Foxglove uses the public local navigation action directly.
# Keep the fleet-wide backend/cmd_vel remaps for other processes.
export OMNIFLEET_FOXGLOVE_DIRECT_ACTIONS=1

runtime_dir="/run/user/$(id -u)/omnifleet_t2"
rendered_config="${runtime_dir}/foxglove-${OMNIFLEET_ROBOT_ID}.yaml"
mkdir -p "${runtime_dir}"

python3 /home/iecme/omnifleet_a2_ws/src/system/omnifleet_fleet/render_foxglove_config.py \
  --source /home/iecme/omnifleet_a2_ws/deploy/111-standard/config/foxglove.yaml \
  --output "${rendered_config}"

# Keep subscription destruction off Zenoh callbacks; scope this RMW backport to Foxglove.
export LD_LIBRARY_PATH="/home/iecme/omnifleet_a2_ws/install_111/foxglove_zenoh_compat/lib:${LD_LIBRARY_PATH:-}"
exec python3 /home/iecme/omnifleet_a2_ws/src/system/omnifleet_fleet/run.py run foxglove_bridge foxglove_bridge \
  --ros-args \
  -r __node:=omnifleet_t2_foxglove_bridge \
  -r /navigation/deskewed_points:=/visualization/deskewed_points \
  --params-file "${rendered_config}" \
  -p address:="${OMNIFLEET_T2_FOXGLOVE_ADDRESS}" \
  -p port:="${OMNIFLEET_T2_FOXGLOVE_PORT}"
