#!/usr/bin/env bash
set -e
source /home/iecme/omnifleet_a2_ws/src/system/workspace_support/robot_fleet_env.bash
sudo -n systemctl start omnifleet-t2-airy.service omnifleet-t2-description.service omnifleet-t2-chassis.service omnifleet-t2-foxglove.service omnifleet-t2-waypoints.service omnifleet-t2-nav2-parameters.service
sudo -n systemctl start omnifleet-t2-mola.service omnifleet-t2-pure-lio-nav2.service
if ! pgrep -f '^/opt/Foxglove-Studio-CN/foxglove-studio-cn ' >/dev/null; then
  DISPLAY=:0 XAUTHORITY=/run/user/1000/gdm/Xauthority XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus nohup /opt/Foxglove-Studio-CN/foxglove-studio-cn --force-device-scale-factor=0.75 >/tmp/foxglove-desktop-start.log 2>&1 </dev/null &
fi
echo '启动完成。'
