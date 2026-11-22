#!/usr/bin/env bash
set -euo pipefail

options=(-a --mkpath --itemize-changes)
if [[ ${1:-} == --dry-run ]]; then
  options+=(--dry-run)
  shift
fi
if [[ $# -ne 1 || $1 != /* ]]; then
  printf 'Usage: %s [--dry-run] /absolute/destination\n' "$0" >&2
  exit 2
fi

runtime_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_dir=$(cd -- "$runtime_dir/../../../omnifleet_ws/src" && pwd)
target=${1%/}
workspace_target="$target/home/iecme/omnifleet_a2_ws"
drivers_target="$target/home/iecme/sensor_drivers_ws"

rsync "${options[@]}" -- "$runtime_dir/../omnifleet_a2_ws/" "$workspace_target/"
rsync "${options[@]}" --exclude=/sensing/mvs_camera_driver/ -- "$source_dir/" "$workspace_target/src/"
rsync "${options[@]}" -- "$runtime_dir/../sensor_drivers_ws/" "$drivers_target/"
rsync "${options[@]}" -- "$source_dir/sensing/mvs_camera_driver/" "$drivers_target/src/mvs_camera_driver/"
rsync "${options[@]}" -- "$runtime_dir/files/" "$target/"
