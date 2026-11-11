#!/usr/bin/env bash
set -e

source /home/iecme/omnifleet_a2_ws/src/system/workspace_support/mola_latest_20260917_ws/latest_env.bash
source /home/iecme/omnifleet_a2_ws/install/local_setup.bash
source /home/iecme/omnifleet_a2_ws/install_111/local_setup.bash

set -a
source /home/iecme/omnifleet_a2_ws/deploy/111-standard/config/robot.env
source /home/iecme/omnifleet_a2_ws/deploy/111-standard/config/architecture.env
set +a

export PYTHONPATH="/home/iecme/omnifleet_a2_ws/src/system/omnifleet_fleet:${PYTHONPATH:-}"
unset ZENOH_CONFIG_OVERRIDE
unset FASTRTPS_DEFAULT_PROFILES_FILE CYCLONEDDS_URI
if [[ "${OMNIFLEET_ZENOH_CORE:-0}" == 1 ]]; then
  export ZENOH_SESSION_CONFIG_URI=/home/iecme/omnifleet_a2_ws/deploy/111-standard/config/zenoh-core-session.json5
elif [[ "${OMNIFLEET_ZENOH_OBSERVER:-0}" == 1 ]]; then
  export ZENOH_SESSION_CONFIG_URI=/home/iecme/omnifleet_a2_ws/deploy/111-standard/config/zenoh-observer-session.json5
fi
export LD_LIBRARY_PATH="/home/iecme/omnifleet_a2_ws/install_111/mrpt/lib:/home/iecme/omnifleet_a2_ws/install_111/mrpt_libros_bridge/lib:/home/iecme/omnifleet_a2_ws/src/system/omnifleet_fleet/zenoh-patched-v2/lib:${LD_LIBRARY_PATH:-}"
export LD_PRELOAD=/home/iecme/omnifleet_a2_ws/src/system/omnifleet_fleet/zenoh-patched-v2/lib/libzenohc.so
