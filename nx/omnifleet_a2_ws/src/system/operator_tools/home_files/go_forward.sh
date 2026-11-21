#!/bin/bash
source ~/wpb_mani_ws/install/setup.bash
timeout 0.5 ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.15}}" -r 20 2>/dev/null
echo "前进 ~5cm 完成"
