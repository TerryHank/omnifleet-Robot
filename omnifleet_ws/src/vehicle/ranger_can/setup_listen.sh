#!/bin/bash
set -euo pipefail

modprobe gs_usb
udevadm settle --timeout=5

interfaces=()
for device in /sys/class/net/*; do
    driver=$(readlink "$device/device/driver" || true)
    if [[ ${driver##*/} == gs_usb ]]; then
        interfaces+=("${device##*/}")
    fi
done
if (( ${#interfaces[@]} != 1 )); then
    echo "Expected one gs_usb CAN adapter, found ${#interfaces[@]}" >&2
    exit 1
fi
device=${interfaces[0]}
ip link set dev "$device" down
ip link set dev "$device" type can bitrate 500000 listen-only "${1:-on}"
ip link set dev "$device" up
printf '%s\n' "$device" > /run/omnifleet-ranger-can/interface
