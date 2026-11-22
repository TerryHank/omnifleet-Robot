#!/usr/bin/env bash
set -e

source /home/iecme/omnifleet_ws/src/system/workspace_support/mola_latest_20260917_ws/latest_env.bash
source /home/iecme/omnifleet_ws/install/local_setup.bash

set -a
source /etc/omnifleet_t2/robot.env
source /etc/omnifleet_t2/architecture.env
set +a

export PYTHONPATH="/home/iecme/omnifleet_ws/src/system/omnifleet_fleet:${PYTHONPATH:-}"
unset ZENOH_CONFIG_OVERRIDE ZENOH_SESSION_CONFIG_URI ZENOH_ROUTER_CONFIG_URI LD_PRELOAD
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export FASTRTPS_DEFAULT_PROFILES_FILE=/etc/omnifleet_t2/fastdds-local.xml
export RMW_FASTRTPS_USE_QOS_FROM_XML=1
export LD_LIBRARY_PATH="/home/iecme/omnifleet_ws/install/mrpt/lib:/home/iecme/omnifleet_ws/install/mrpt_libros_bridge/lib:${LD_LIBRARY_PATH:-}"

if [[ -n ${OMNIFLEET_RCLPY_COMMAND_METADATA_OVERLAY:-} ]]; then
    source "${OMNIFLEET_RCLPY_COMMAND_METADATA_OVERLAY}/local_setup.bash"
fi
