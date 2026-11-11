#!/bin/bash
source /opt/ros/humble/setup.bash

# Start calibrator in background
python3 /home/iecme/omnifleet_ws/src/system/operator_tools/home_files/calibrate_roll.py 3.0 &
CALIB_PID=$!
sleep 2

# Check TF
echo "=== rslidar TF (roll=3.0°) ==="
ros2 run tf2_ros tf2_echo base_link rslidar --once 2>&1 | head -15

# Kill calibrator
kill $CALIB_PID 2>/dev/null
wait $CALIB_PID 2>/dev/null

# Wait and check original TF again
sleep 1
echo ""
echo "=== rslidar TF (恢复) ==="
ros2 run tf2_ros tf2_echo base_link rslidar --once 2>&1 | head -15
