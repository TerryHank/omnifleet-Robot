#!/bin/bash
set -u

for _ in $(seq 1 60); do
    if [ "$(timedatectl show -p NTPSynchronized --value 2>/dev/null)" = "yes" ]; then
        exit 0
    fi
    sleep 1
done

echo "NTP clock did not synchronize within 60 seconds" >&2
exit 1
