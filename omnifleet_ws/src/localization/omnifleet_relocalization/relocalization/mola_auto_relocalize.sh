#!/usr/bin/env bash
set -euo pipefail
map_path="${1:-${OMNIFLEET_T2_MAP_DIR:-/home/iecme/omnifleet_data/maps}/saved/foxglove_map.mm}"
robot="${OMNIFLEET_ROBOT_ID:?OMNIFLEET_ROBOT_ID is required}"
root="/home/iecme/omnifleet_ws/src/system/omnifleet_fleet/relocalization"
run_dir="$root/runtime-${robot}"
mkdir -p "$run_dir"
cloud="$run_dir/current.pcd"
result="$run_dir/result.json"
log="$run_dir/last.log"
exec > >(tee "$log") 2>&1
echo "[mola-auto-relocalize] robot=$robot map=$map_path"
python3 "$root/capture_cloud.py" "/$robot/rslidar_points" "$cloud"
"$root/mola_auto_relocalize" "$map_path" "$cloud" "$result" 0.35 15
python3 "$root/mola_auto_activate.py" "$result"
echo "[mola-auto-relocalize] accepted"
