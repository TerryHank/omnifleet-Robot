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
target=${1%/}

rsync "${options[@]}" -- "$runtime_dir/../omnifleet_a2_ws/" "$target/home/iecme/omnifleet_a2_ws/"
rsync "${options[@]}" -- "$runtime_dir/../sensor_drivers_ws/" "$target/home/iecme/sensor_drivers_ws/"
rsync "${options[@]}" -- "$runtime_dir/files/" "$target/"
