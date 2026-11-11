"""Announce the local robot on each LAN interface; no ROS commands or fixed peer addresses."""
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import time


def robot_config():
    values = {}
    for line in Path('/home/iecme/omnifleet_a2_ws/deploy/111-standard/config/robot.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.removeprefix('export ').split('=', 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def settings():
    values = robot_config()
    # Read the actual middleware/domain from the running local navigation process.
    pid = subprocess.check_output(['systemctl','show','omnifleet-local-navigation.service','-p','MainPID','--value'], text=True).strip()
    process = Path('/proc') / pid / 'environ'
    if pid == '0' or not process.exists():
        raise RuntimeError('Local navigation is not running; do not announce an unverified domain')
    runtime = dict(item.split('=',1) for item in process.read_bytes().decode().split('\0') if '=' in item)
    if runtime.get('RMW_IMPLEMENTATION') != 'rmw_zenoh_cpp':
        raise RuntimeError('Local navigation does not use native Zenoh')
    domain = int(runtime['ROS_DOMAIN_ID'])
    if domain != int(values['ROS_DOMAIN_ID']):
        raise RuntimeError('Configured and running ROS domains disagree')
    simple = False
    for command_file in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            command = command_file.read_bytes()
            if command.split(b'\0', 1)[0].endswith(b'/mola-cli'):
                simple = b'/mola_state_estimation_simple/' in command
                break
        except OSError:
            continue
    pose_topic = '/lidar_odometry/pose' if simple or runtime.get('OMNIFLEET_ARCHITECTURE') == 'pure_mola' else '/state_estimation/pose'
    return {'protocol':'omnifleet-discovery','version':1,
            'robot_id':values['OMNIFLEET_ROBOT_ID'],'domain_id':domain,'rmw':runtime['RMW_IMPLEMENTATION'],
            'instance_id':hashlib.sha256(Path('/etc/machine-id').read_bytes()).hexdigest()[:32],
            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'zenoh_port':7447,'observed_namespace':'','pose_topic':pose_topic}


def announce():
    beacon = settings()
    interfaces = json.loads(subprocess.check_output(['ip','-j','-4','addr','show','up']))
    for interface in interfaces:
        if ('POINTOPOINT' in interface.get('flags', [])
                or not (Path('/sys/class/net') / interface['ifname'] / 'device').exists()):
            continue
        for address in interface.get('addr_info', []):
            if address.get('scope') != 'global' or not address.get('broadcast'):
                continue
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sender:
                sender.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
                sender.bind((address['local'],0))
                try:
                    packet = json.dumps({**beacon,'interface_priority':1}).encode()
                    sender.sendto(packet,(address['broadcast'],7446))
                except OSError as error:
                    print(interface['ifname'],str(error),flush=True)


if __name__ == '__main__':
    while True:
        try:
            announce()
        except (OSError,ValueError,KeyError,RuntimeError,subprocess.CalledProcessError) as error:
            print(str(error),flush=True)
        time.sleep(1)
