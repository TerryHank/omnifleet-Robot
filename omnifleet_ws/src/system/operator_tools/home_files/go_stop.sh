#!/bin/bash
source ~/wpb_mani_ws/install/setup.bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{}" -1 2>/dev/null
echo "停止"
