#!/usr/bin/env bash
source /home/iecme/omnifleet_ws/src/system/workspace_support/robot_fleet_env.bash

export PATH="/home/iecme/.local/bin:$PATH"

# Show visual course windows on the user's desktop when started over SSH.
# Preserve an explicitly configured DISPLAY (including SSH X11 forwarding).
if [ -z "${DISPLAY:-}" ]; then
    while IFS='=' read -r _omnifleet_display_key _omnifleet_display_value; do
        case "$_omnifleet_display_key" in
            DISPLAY) export DISPLAY="$_omnifleet_display_value" ;;
            XAUTHORITY)
                if [ -z "${XAUTHORITY:-}" ]; then
                    export XAUTHORITY="$_omnifleet_display_value"
                fi
                ;;
        esac
    done < <(systemctl --user show-environment 2>/dev/null || true)
    unset _omnifleet_display_key _omnifleet_display_value
fi
