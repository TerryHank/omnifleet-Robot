#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_ws/install/setup.bash

# The tracked chassis uses opposite motor polarities for straight-ahead motion.
# 1.326 rps corresponds to approximately 0.30 m/s with 72 mm wheels.
exec ros2 topic pub --rate 10 \
  /ros_robot_controller/set_motor \
  ros_robot_controller_msgs/msg/MotorsState \
  "{data: [{id: 1, rps: 1.326}, {id: 2, rps: -1.326}]}"
