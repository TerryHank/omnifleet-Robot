#!/usr/bin/env bash
set -e
task_ws=/home/zhangwnag/workspaces/omnifleet_ws
mkdir -p "$task_ws/data/run"
systemctl --user start omnifleet-rmf.target
exec flock -n "$task_ws/data/run/windows-keeper.lock" /bin/bash -c 'exec -a omnifleet_ws_keepalive sleep infinity'
