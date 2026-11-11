#!/usr/bin/env bash
set -u
TARGET_ROOT="${CPU_AFFINITY_ROOT:-/home/iecme/cpu_affinity_production_runtime}"
REPORT_DIR="$TARGET_ROOT/after"
mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/affinity_rollback_runtime.txt"
: > "$REPORT"
is_target() {
  local cmd="$1"
  case "$cmd" in
    *mola-cli*|*mola_lidar_odometry*|*nav_cloud_deskew*|*mola_realtime_nav_grid*|*lidar_velocity*|*controller_server*|*planner_server*|*behavior_server*|*bt_navigator*|*local_navigation*|*msc_agent*|*msc_coordinator*|*omnifleet_t2_driver*|*gateway_local*|*gateway_network*|*diagnostic_node*|*rmw_zenohd*|*foxglove*|*rosbridge*|*rosapi*|*waypoint_ui*|*waypoint*)
      return 0
      ;;
  esac
  return 1
}
found=0
failed=0
for d in /proc/[0-9]*; do
  pid="${d##*/}"
  [ -r "$d/cmdline" ] || continue
  cmd=$(tr '\0' ' ' < "$d/cmdline" 2>/dev/null || true)
  [ -n "$cmd" ] || continue
  is_target "$cmd" || continue
  found=$((found+1))
  if ! taskset -apc 0-7 "$pid" >/dev/null 2>&1; then
    echo "SET_FAIL pid=$pid cmd=$cmd" >> "$REPORT"
    failed=$((failed+1))
    continue
  fi
  bad_tid=0
  for td in "$d"/task/[0-9]*; do
    [ -d "$td" ] || continue
    tid="${td##*/}"
    affinity=$(taskset -pc "$tid" 2>/dev/null | sed -E 's/.*[:：] *//')
    if [ "$affinity" != "0-7" ]; then
      echo "VERIFY_FAIL pid=$pid tid=$tid affinity=$affinity cmd=$cmd" >> "$REPORT"
      bad_tid=1
    fi
  done
  if [ "$bad_tid" -ne 0 ]; then failed=$((failed+1)); else echo "OK pid=$pid cmd=$cmd" >> "$REPORT"; fi
done
if [ "$found" -eq 0 ]; then echo "NO_TARGETS" >> "$REPORT"; exit 1; fi
printf 'found=%s failed=%s\n' "$found" "$failed" >> "$REPORT"
[ "$failed" -eq 0 ]
