#!/usr/bin/env bash
set -eo pipefail

source /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash

# Foxglove uses the public local navigation action directly.
# Keep the fleet-wide backend/cmd_vel remaps for other processes.
export OMNIFLEET_FOXGLOVE_DIRECT_ACTIONS=1

runtime_dir="/run/user/$(id -u)/omnifleet_t2"
rendered_config="${runtime_dir}/foxglove-${OMNIFLEET_ROBOT_ID}.yaml"
mkdir -p "${runtime_dir}"

python3 /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/render_foxglove_config.py \
  --source /etc/omnifleet_t2/foxglove.yaml \
  --output "${rendered_config}"

# Keep subscription destruction off Zenoh callbacks; scope this RMW backport to Foxglove.
# Match the Orbbec message definitions to the running SDK 2.10.6 camera.
orbbec_prefix="/home/iecme/orbbec345lg-v2.10.6/root/opt/ros/humble"
if [[ -f "${orbbec_prefix}/share/orbbec_camera_msgs/msg/DeviceStatus.msg" ]]; then
  export AMENT_PREFIX_PATH="${orbbec_prefix}:${AMENT_PREFIX_PATH:-}"
  export LD_LIBRARY_PATH="${orbbec_prefix}/lib:${LD_LIBRARY_PATH:-}"
fi
export LD_LIBRARY_PATH="/home/iecme/omnifleet_ws/install/foxglove_zenoh_compat/lib:${LD_LIBRARY_PATH:-}"
exec python3 /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/run.py run foxglove_bridge foxglove_bridge \
  --ros-args \
  -r __node:=omnifleet_t2_foxglove_bridge \
  --params-file "${rendered_config}" \
  -p address:="${OMNIFLEET_T2_FOXGLOVE_ADDRESS}" \
  -p port:="${OMNIFLEET_T2_FOXGLOVE_PORT}"
