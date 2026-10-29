#!/usr/bin/env bash
set -e
source /opt/ros/humble/setup.bash
exec /opt/ros/humble/lib/rmw_zenoh_cpp/rmw_zenohd
