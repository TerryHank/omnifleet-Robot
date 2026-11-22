"""Announce the local robot on each LAN interface; no ROS commands or fixed peer addresses."""
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import time


def settings():
    unit = 'omnifleet-a2-navigation.service'
    pid = subprocess.check_output(['systemctl','show',unit,'-p','MainPID','--value'],text=True).strip()
    if not pid.isdigit() or int(pid)==0:
        raise RuntimeError('Native Ackermann navigation is offline')
    pairs = (Path('/proc') / pid / 'environ').read_bytes().split(b'\0')
    runtime = dict(p.decode().split('=',1) for p in pairs if b'=' in p)
    if runtime.get('RMW_IMPLEMENTATION') != 'rmw_fastrtps_cpp':
        raise RuntimeError('Native navigation is not using Fast DDS')
    return {'protocol':'omnifleet-discovery','version':1,
            'robot_id':'robot_124','domain_id':int(runtime['ROS_DOMAIN_ID']),
            'rmw':runtime['RMW_IMPLEMENTATION'],
            'instance_id':hashlib.sha256(Path('/etc/machine-id').read_bytes()).hexdigest()[:32],
            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'discovery_port':42100,'observed_namespace':'','pose_topic':'/lidar_odometry/pose'}


def announce():
    beacon = settings()
    # Peers use a separate DDS participant domain; the local observer uses the native domain.
    beacon['domain_id'] = 124
    active = Path('/run/omnifleet-124-ddsrouter/lan-address')
    if not active.is_file():
        return
    advertised_address = active.read_text().strip()
    interfaces = json.loads(subprocess.check_output(['ip','-j','-4','addr','show','up']))
    for interface in interfaces:
        if ('POINTOPOINT' in interface.get('flags', [])
                or not (Path('/sys/class/net') / interface['ifname'] / 'device').exists()):
            continue
        for address in interface.get('addr_info', []):
            if address.get('scope') != 'global' or not address.get('broadcast') or address.get('local') != advertised_address:
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
