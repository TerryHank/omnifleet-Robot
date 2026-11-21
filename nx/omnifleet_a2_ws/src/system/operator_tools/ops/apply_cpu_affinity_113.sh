#!/usr/bin/env bash
set -u

ROOT_DIR="${CPU_AFFINITY_ROOT:-/home/iecme/cpu_affinity_production_runtime}"
mkdir -p "$ROOT_DIR/after"

declare -a seen=()
declare -a missing=()
declare -a rows=()
declare -a proc_pids=()
declare -a proc_cmds=()
declare -a proc_classes=()

classify_cmd() {
  local c="$1"
  case "$c" in
    *mola-cli*|*mola_lidar_odometry*) echo MOLA ;;
    *nav_cloud_deskew*|*mola_realtime_nav_grid*|*controller_server*|*planner_server*|*bt_navigator*|*behavior_server*|*local_navigation*|*msc_agent*|*msc_coordinator*|*t2_driver*|*omnifleet_t2_driver*|*zenohd*|*rmw_zenohd*) echo CRITICAL_NAV ;;
    *foxglove*|*gateway_local*|*gateway_network*|*diagnostic_node*|*rosbridge*|*rosapi*|*waypoint_ui*|*waypoint*) echo BACKGROUND ;;
    *) echo IGNORE ;;
  esac
}

target_for_class() {
  case "$1" in
    MOLA) echo 4-7 ;;
    CRITICAL_NAV) echo 1-4 ;;
    BACKGROUND) echo 0-3 ;;
    *) echo 0-7 ;;
  esac
}

write_row() {
  local pid="$1" cls="$2" target="$3" cmd="$4"
  local current
  current=$(taskset -pc "$pid" 2>/dev/null | sed 's/.*: //') || return 0
  printf '%s\t%s\t%s\t%s\t%s\n' "$pid" "$cmd" "$cls" "$current" "$target" >> "$ROOT_DIR/after/affinity_after.txt"
}

: > "$ROOT_DIR/after/affinity_after.txt"
printf 'PID\tCOMMAND\tCLASS\tCURRENT_AFFINITY\tTARGET_AFFINITY\n' >> "$ROOT_DIR/after/affinity_after.txt"

while IFS= read -r d; do
  pid="${d##*/}"
  [ -r "$d/cmdline" ] || continue
  cmd=$(tr '\0' ' ' < "$d/cmdline" 2>/dev/null | sed 's/[[:space:]]\+$//')
  [ -n "$cmd" ] || continue
  cls=$(classify_cmd "$cmd")
  [ "$cls" != IGNORE ] || continue
  case " ${seen[*]} " in *" $pid "*) continue ;; esac
  seen+=("$pid")
  proc_pids+=("$pid")
  proc_cmds+=("$cmd")
  proc_classes+=("$cls")
done < <(printf '%s\n' /proc/[0-9]*)

rm -f "$ROOT_DIR/after/missing_required.tsv"
required_patterns=(
  'mola-cli'
  'mola_realtime_nav_grid'
  'controller_server'
  'planner_server'
  'bt_navigator'
  'behavior_server'
  'local_navigation'
  'msc_agent'
  'msc_coordinator'
  'zenohd'
)
for pat in "${required_patterns[@]}"; do
  found=0
  for i in "${!proc_pids[@]}"; do
    [[ "${proc_cmds[$i]}" == *"$pat"* ]] && found=1 && break
  done
  if [ "$found" -eq 0 ]; then
    printf '%s\n' "$pat" >> "$ROOT_DIR/after/missing_required.tsv"
  fi
done

if [ -s "$ROOT_DIR/after/missing_required.tsv" ]; then
  exit 2
fi

rm -f "$ROOT_DIR/after/apply_failures.tsv"
for i in "${!proc_pids[@]}"; do
  pid="${proc_pids[$i]}"
  cls="${proc_classes[$i]}"
  cmd="${proc_cmds[$i]}"
  target=$(target_for_class "$cls")
  if ! taskset -apc "$target" "$pid" >/dev/null 2>&1; then
    printf 'FAILED\t%s\t%s\t%s\n' "$pid" "$cls" "$cmd" >> "$ROOT_DIR/after/apply_failures.tsv"
    continue
  fi
  write_row "$pid" "$cls" "$target" "$cmd"
done
if [ -s "$ROOT_DIR/after/apply_failures.tsv" ]; then exit 3; fi
exit 0
