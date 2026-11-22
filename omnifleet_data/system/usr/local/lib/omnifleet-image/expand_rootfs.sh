#!/usr/bin/env bash
set -euo pipefail
root_device=$(readlink -f "$(findmnt -n -o SOURCE /)")
parent=$(lsblk -n -o PKNAME "$root_device")
partition=$(cat "/sys/class/block/$(basename "$root_device")/partition")
disk="/dev/$parent"
sgdisk -e "$disk"
printf ',+\n' | sfdisk --no-reread --force -N "$partition" "$disk"
partx --update --nr "$partition" "$disk"
resize2fs "$root_device"
mkdir -p /var/lib/omnifleet-image
touch /var/lib/omnifleet-image/expanded
