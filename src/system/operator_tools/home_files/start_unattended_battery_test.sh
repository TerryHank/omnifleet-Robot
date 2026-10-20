#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_ws/install/setup.bash
set -u
export ROS_DOMAIN_ID=0
export ROS2CLI_NO_DAEMON=1

run_id="$(date +%Y%m%d_%H%M%S)"
run_dir="/home/iecme/omnifleet_data/recordings/legacy_evidence/battery_tests/unattended_${run_id}"
mkdir -p "$run_dir"
printf '%s\n' "$run_dir" > /home/iecme/omnifleet_data/recordings/legacy_evidence/battery_tests/current_run_path

{
  echo "test_start=$(date --iso-8601=seconds)"
  echo "host=$(hostname)"
  echo "purpose=all configured sensors plus both track motors at about 0.30 m/s"
  echo "heartbeat_interval_seconds=15"
  echo "motor_command=/home/iecme/omnifleet_ws/src/system/operator_tools/home_files/rrc-battery-test-drive.sh"
  echo "motor_setpoint=left 1.326 rps, right -1.326 rps"
} > "$run_dir/metadata.txt"

{
  date --iso-8601=seconds
  systemctl --no-pager --plain is-active \
    rrc-ros-robot-controller.service \
    rrc-tank-bridge.service \
    rrc-orbbec-camera.service \
    rrc-rslidar.service \
    rrc-foxglove-bridge.service \
    rrc-tank-description.service \
    lidar-watchdog.service \
    rrc-jetson-performance.service
  echo "--- nodes ---"
  ros2 node list
  echo "--- topics ---"
  ros2 topic list -t
} > "$run_dir/startup_snapshot.txt" 2>&1

nohup setsid bash -c \
  "while true; do date --iso-8601=seconds >> '$run_dir/heartbeat.log'; sync '$run_dir/heartbeat.log' 2>/dev/null || sync; sleep 15; done" \
  </dev/null > "$run_dir/heartbeat_runner.log" 2>&1 &
heartbeat_pid=$!

nohup setsid /home/iecme/omnifleet_ws/src/system/operator_tools/home_files/rrc-battery-test-drive.sh \
  </dev/null > "$run_dir/motor.log" 2>&1 &
motor_pid=$!

{
  echo "heartbeat_pid=$heartbeat_pid"
  echo "motor_pid=$motor_pid"
} >> "$run_dir/metadata.txt"

sleep 4
{
  echo "verification_time=$(date --iso-8601=seconds)"
  ps -p "$heartbeat_pid" -o pid=,stat=,cmd=
  ps -p "$motor_pid" -o pid=,stat=,cmd=
  timeout 5 ros2 topic echo --once /ros_robot_controller/set_motor
} > "$run_dir/verification.txt" 2>&1

echo "$run_dir"
echo "$heartbeat_pid"
echo "$motor_pid"
