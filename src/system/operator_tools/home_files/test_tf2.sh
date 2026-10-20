#!/bin/bash
source /opt/ros/humble/setup.bash
python3 /home/iecme/omnifleet_ws/src/system/operator_tools/home_files/calibrate_roll.py 5.0 &
CALIB=$!
sleep 3

echo '=== tf2_echo (should see roll=5) ==='
timeout 2 bash -c 'source /opt/ros/humble/setup.bash && ros2 run tf2_ros tf2_echo base_link rslidar' 2>&1 | head -10

kill $CALIB 2>/dev/null
wait $CALIB 2>/dev/null
echo '=== DONE ==='
