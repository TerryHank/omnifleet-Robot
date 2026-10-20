#!/usr/bin/env bash
set -eo pipefail

ROOT=$(cat /tmp/current_smoke_root.txt)
echo "Smoke root is: $ROOT"
date --iso-8601=ns > "$ROOT/logs/record_start.txt"
echo "Record start: $(cat $ROOT/logs/record_start.txt)"

export GICP_BAG_DIR="$ROOT/bag"
/home/iecme/omnifleet_ws/src/system/operator_tools/home_files/record_gicp_mapping_bag.sh --duration 60

date --iso-8601=ns > "$ROOT/logs/record_end.txt"
echo "Record end: $(cat $ROOT/logs/record_end.txt)"

BAG_SUBDIR=$(find "$ROOT/bag" -maxdepth 1 -mindepth 1 -type d | head -n 1)
echo "Recorded Bag Subdir: $BAG_SUBDIR"
if [ -n "$BAG_SUBDIR" ]; then
  ros2 bag info "$BAG_SUBDIR" > "$ROOT/results/bag_info.txt" 2>&1
  cat "$ROOT/results/bag_info.txt"
fi

