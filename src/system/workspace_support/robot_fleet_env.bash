#!/usr/bin/env bash
set -e

source /home/iecme/omnifleet_ws/src/system/workspace_support/mola_latest_20260917_ws/latest_env.bash
source /home/iecme/omnifleet_ws/install/local_setup.bash

set -a
source /etc/omnifleet_t2/robot.env
source /etc/omnifleet_t2/architecture.env
set +a

export PYTHONPATH="/home/iecme/omnifleet_ws/src/system/omnifleet_fleet:${PYTHONPATH:-}"
unset ZENOH_CONFIG_OVERRIDE
if [[ "${OMNIFLEET_ZENOH_CORE:-0}" == 1 ]]; then
  export ZENOH_SESSION_CONFIG_URI=/etc/omnifleet_t2/zenoh-core-session.json5
elif [[ "${OMNIFLEET_ZENOH_OBSERVER:-0}" == 1 ]]; then
  export ZENOH_SESSION_CONFIG_URI=/etc/omnifleet_t2/zenoh-observer-session.json5
fi
export LD_LIBRARY_PATH="/home/iecme/omnifleet_ws/install/mrpt/lib:/home/iecme/omnifleet_ws/install/mrpt_libros_bridge/lib:/home/iecme/omnifleet_ws/src/system/omnifleet_fleet/zenoh-patched-v2/lib:${LD_LIBRARY_PATH:-}"
export LD_PRELOAD=/home/iecme/omnifleet_ws/src/system/omnifleet_fleet/zenoh-patched-v2/lib/libzenohc.so
