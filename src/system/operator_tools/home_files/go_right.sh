#!/bin/bash
source ~/wpb_mani_ws/install/setup.bash
timeout 0.5 ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {y: -0.15}}" -r 20 2>/dev/null
echo "右移 ~5cm 完成"
