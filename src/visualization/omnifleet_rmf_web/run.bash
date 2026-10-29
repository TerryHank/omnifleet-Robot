#!/usr/bin/env bash
set -e
task_ws=/home/zhangwnag/workspaces/omnifleet_ws
runtime="$task_ws/install/rmf_web_runtime"
deployment="$task_ws/src/visualization/omnifleet_rmf_web"
source "$task_ws/env.bash"
export PATH="$runtime/node-v20.20.2-linux-x64/bin:$runtime/npm/node_modules/.bin:$PATH"
export TZ=Asia/Shanghai
case "$1" in
  api)
    mkdir -p "$task_ws/data/rmf_web/cache"
    export RMF_API_SERVER_CONFIG="$deployment/api_config.py"
    cd "$task_ws/data/rmf_web"
    exec "$runtime/venv/bin/python" "$deployment/read_only_api.py"
    ;;
  observer)
    exec "$runtime/venv/bin/python" "$deployment/web_robot_observer.py"
    ;;
  dashboard)
    exec serve -s "$task_ws/install/rmf_web_dashboard/zh-CN" -l tcp://127.0.0.1:3000 -l tcp://127.0.0.1:8080 --no-clipboard
    ;;
  trajectory)
    cd "$task_ws/data/rmf_web"
    exec /opt/ros/humble/lib/rmf_visualization_schedule/schedule_visualizer_node --ros-args -p use_sim_time:=false -p port:=8006
    ;;
esac
