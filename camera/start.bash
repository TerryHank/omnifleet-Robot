#!/bin/bash
set -e
source /home/iecme/omnifleet_ws/env.bash
prefix=/home/iecme/orbbec345lg-v2.10.6/root/opt/ros/humble
export AMENT_PREFIX_PATH="$prefix:${AMENT_PREFIX_PATH:-}"
export LD_LIBRARY_PATH="$prefix/lib:${LD_LIBRARY_PATH:-}"
export PYTHONPATH="$prefix/local/lib/python3.10/dist-packages:$prefix/lib/python3.10/site-packages:${PYTHONPATH:-}"
export ZENOH_CONFIG_OVERRIDE="transport/shared_memory/enabled=false;transport/shared_memory/transport_optimization/enabled=false"
exec ros2 launch /home/iecme/orbbec345lg-v2.10.6/camera.launch.py
