#!/bin/bash
source /opt/ros/humble/setup.bash
python3 /home/iecme/omnifleet_ws/src/system/operator_tools/home_files/calibrate_roll.py 3.0 &
CALIB=$!
sleep 3
echo '=== TF msgs with rslidar ==='
timeout 2 bash -c 'source /opt/ros/humble/setup.bash && ros2 topic echo /tf' 2>/dev/null | grep -A5 rslidar | head -20
kill $CALIB 2>/dev/null
wait $CALIB 2>/dev/null
echo '=== DONE ==='
