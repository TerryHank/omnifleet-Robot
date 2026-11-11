#!/usr/bin/env bash
set -Eeuo pipefail
MODE=${1:-status}
BASE=/home/iecme/omnifleet_ws/src/system/omnifleet_fleet
ENV=/etc/omnifleet_t2/robot.env
BASHRC=/home/iecme/.bashrc
BACKUP_ROOT=/home/iecme/transport_backups
LOCK=/run/lock/omnifleet-transport.lock
UNITS=(omnifleet-msc-coordinator omnifleet-msc-agent omnifleet-t2-chassis omnifleet-t2-airy omnifleet-t2-description omnifleet-t2-orbbec-camera omnifleet-t2-foxglove omnifleet-t2-waypoints omnifleet-t2-nav2-parameters omnifleet-t2-dsh-diagnostics)
MODE_NAMES=(fastdds cyclonedds zenoh)
PRESENT=()
for u in "${UNITS[@]}"; do
  systemctl cat "$u.service" >/dev/null 2>&1 && PRESENT+=("$u.service")
done
source_ros(){ set +u; source /opt/ros/humble/setup.bash; set -u; }

usage(){ echo "Usage: sudo $0 {status|fastdds|cyclonedds|zenoh}"; }
read_mode(){ awk -F= '/^RMW_IMPLEMENTATION=/{print $2; exit}' "$ENV" 2>/dev/null || true; }
backup(){ local ts; ts=$(date +%Y%m%d_%H%M%S); local dir="$BACKUP_ROOT/$ts"; sudo mkdir -p "$dir"; sudo cp -a "$ENV" "$BASHRC" "$dir/"; sudo systemctl list-units --type=service --state=running --no-legend > "$dir/services.before.txt"; for f in /etc/systemd/system/*/90-fleet.conf; do [ -f "$f" ] && { sudo cp -a "$f" "$dir/$(echo "$f" | tr / _).bak"; }; done; echo "$dir"; }
set_kv(){ local key=$1 value=$2 file=$3; sudo awk -v k="$key" -v v="$value" 'BEGIN{done=0} $0 ~ "^" k "=" {if(v!=""){print k "=" v}; done=1; next} {print} END{if(!done && v!="") print k "=" v}' "$file" | sudo tee "$file.tmp" >/dev/null; sudo mv "$file.tmp" "$file"; }
clear_mode_keys(){ for k in RMW_IMPLEMENTATION FASTRTPS_DEFAULT_PROFILES_FILE FASTDDS_BUILTIN_TRANSPORTS CYCLONEDDS_URI ZENOH_SESSION_CONFIG_URI ZENOH_ROUTER_CHECK_ATTEMPTS ZENOH_CONFIG_OVERRIDE; do set_kv "$k" "" "$ENV"; done; }
set_bashrc_mode(){
  local mode=$1 rmw extra=""
  case "$mode" in fastdds) rmw=rmw_fastrtps_cpp; extra='export FASTRTPS_DEFAULT_PROFILES_FILE=/home/iecme/.config/fastdds/udp_only.xml';; cyclonedds) rmw=rmw_cyclonedds_cpp; extra='export CYCLONEDDS_URI=/etc/omnifleet_t2/cyclonedds.xml';; zenoh) rmw=rmw_zenoh_cpp; extra=$'export ZENOH_SESSION_CONFIG_URI=/etc/omnifleet_t2/zenoh-session.json5\nexport ZENOH_ROUTER_CHECK_ATTEMPTS=-1';; esac
  sudo sed -i '/^# BEGIN OMNIFLEET TRANSPORT$/,/^# END OMNIFLEET TRANSPORT$/d' "$BASHRC"
  {
    echo '# BEGIN OMNIFLEET TRANSPORT'
    echo 'export ROS_DOMAIN_ID=0'
    echo "export OMNIFLEET_TRANSPORT_MODE=$mode"
    echo "export RMW_IMPLEMENTATION=$rmw"
    printf '%s\n' "$extra"
    echo '# END OMNIFLEET TRANSPORT'
  } | sudo tee -a "$BASHRC" >/dev/null
}
check_pkg(){ local pkg=$1; source_ros; ros2 pkg prefix "$pkg" >/dev/null 2>&1 || { echo "missing package: $pkg" >&2; exit 3; }; }
status(){ echo "mode=$(read_mode)"; systemctl is-active omnifleet-t2-zenoh-router.service 2>/dev/null || true; for u in "${PRESENT[@]}"; do s=$(systemctl is-active "$u" 2>/dev/null || true); [ "$s" = active ] && echo "$u=$s"; done; pgrep -af 'rmw_zenohd|zenohd' || true; }
case "$MODE" in
 status) status; exit 0;;
 fastdds) RMW=rmw_fastrtps_cpp; PKG=rmw_fastrtps_cpp;;
 cyclonedds) RMW=rmw_cyclonedds_cpp; PKG=rmw_cyclonedds_cpp;;
 zenoh) RMW=rmw_zenoh_cpp; PKG=rmw_zenoh_cpp;;
 *) usage; exit 2;;
esac
sudo -v
exec 9>"$LOCK"; flock -n 9 || { echo 'another transport switch is running' >&2; exit 4; }
check_pkg "$PKG"
# Never interrupt an operator's manually launched nav stack.
if (pgrep -af 'mola-cli|nav2_bringup' | grep -v pgrep >/dev/null) || (ps -eo args= | grep -E '/ros2 launch ' | grep -vE 'grep|scoped.launch.py|omnifleet_transport|bash -c' >/dev/null); then echo 'manual ROS launch detected; stop it before switching' >&2; exit 5; fi
backup_dir=$(backup); echo "backup=$backup_dir"
# Stop only the registered fleet services and router. No broad pkill.
source_ros
old=$(read_mode); [ -n "$old" ] && RMW_IMPLEMENTATION="$old" ROS_DOMAIN_ID=0 ros2 daemon stop >/dev/null 2>&1 || true
sudo systemctl stop "${PRESENT[@]}" omnifleet-t2-zenoh-router.service || true
clear_mode_keys
set_kv ROS_DOMAIN_ID 0 "$ENV"
set_kv RMW_IMPLEMENTATION "$RMW" "$ENV"
if [ "$MODE" = zenoh ]; then
  set_kv ZENOH_SESSION_CONFIG_URI /etc/omnifleet_t2/zenoh-session.json5 "$ENV"
  set_kv ZENOH_ROUTER_CHECK_ATTEMPTS -1 "$ENV"
elif [ "$MODE" = fastdds ]; then
  set_kv FASTRTPS_DEFAULT_PROFILES_FILE /home/iecme/.config/fastdds/udp_only.xml "$ENV"
else
  set_kv CYCLONEDDS_URI /etc/omnifleet_t2/cyclonedds.xml "$ENV"
fi
set_bashrc_mode "$MODE"
sudo systemctl daemon-reload
if [ "$MODE" = zenoh ]; then sudo systemctl enable --now omnifleet-t2-zenoh-router.service; else sudo systemctl disable --now omnifleet-t2-zenoh-router.service || true; fi
sudo systemctl start "${PRESENT[@]}"
# Give systemd a short bounded settle period, then prove mode isolation.
sleep 12
actual=$(systemctl show omnifleet-msc-agent.service -p MainPID --value 2>/dev/null || true)
[ -n "$actual" ] && [ "$actual" != 0 ] || { echo 'msc agent did not start' >&2; exit 6; }
value=$(tr '\0' '\n' < "/proc/$actual/environ" | awk -F= '$1=="RMW_IMPLEMENTATION"{print $2}')
[ "$value" = "$RMW" ] || { echo "RMW mismatch: $value" >&2; exit 7; }
if [ "$MODE" = zenoh ]; then systemctl is-active --quiet omnifleet-t2-zenoh-router.service || { echo 'zenoh router inactive' >&2; exit 8; }; else ! systemctl is-active --quiet omnifleet-t2-zenoh-router.service || { echo 'zenoh router still active' >&2; exit 9; }; ! pgrep -x rmw_zenohd >/dev/null || { echo 'rmw_zenohd remains' >&2; exit 10; }; fi
echo "selected=$MODE rmw=$RMW backup=$backup_dir"
status
