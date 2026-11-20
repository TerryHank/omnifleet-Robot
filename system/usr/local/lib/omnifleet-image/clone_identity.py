#!/usr/bin/python3
"""Initialize a fresh clone's LAN identity before the existing robot services."""
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess
import time


def main():
    subprocess.run(['nm-online', '-s', '-q', '--timeout=30'], check=False)
    addresses = json.loads(subprocess.check_output(['ip', '-j', '-4', 'addr', 'show', 'up']))
    routes = json.loads(subprocess.check_output(['ip', '-j', '-4', 'route', 'show', 'default']))
    physical = {p.name for p in Path('/sys/class/net').iterdir() if (p / 'device').exists()}
    preferred = [r['dev'] for r in sorted(routes, key=lambda r: r.get('metric', 0)) if r.get('dev') in physical]
    candidates = []
    for interface in addresses:
        name = interface['ifname']
        if name not in physical:
            continue
        for address in interface.get('addr_info', []):
            ip = address.get('local', '')
            if address.get('family') != 'inet' or address.get('scope') != 'global':
                continue
            if ip in {'192.168.1.102', '192.168.144.108', '192.168.254.1'}:
                continue
            candidates.append((preferred.index(name) if name in preferred else 100, name, ip))
    address = min(candidates)[2] if candidates else None
    machine = Path('/etc/machine-id').read_text().strip()
    state = Path('/var/lib/omnifleet-image/identity.json')
    old = json.loads(state.read_text()) if state.exists() else {
        'robot_id': 'robot_104', 'domain_id': 104, 'lan_address': '192.168.3.104'}
    if old.get('initial_lan_address'):
        robot, domain = old['robot_id'], old['domain_id']
    else:
        tail = int(address.rsplit('.', 1)[1]) if address else None
        robot = 'robot_' + str(tail) if tail is not None else 'robot_nx_' + machine[:8]
        domain = tail % 233 if tail is not None else int(machine[:8], 16) % 233
        if address:
            occupied = set()
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
                receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                deadline = time.monotonic() + 2.2
                try:
                    receiver.bind(('', 7446))
                except OSError as error:
                    if error.errno != 98:
                        raise
                    # An occupied discovery port must not block identity or SSH keys.
                    deadline = 0
                while time.monotonic() < deadline:
                    receiver.settimeout(max(0.01, deadline - time.monotonic()))
                    try:
                        raw, source = receiver.recvfrom(65535)
                    except socket.timeout:
                        break
                    try:
                        packet = json.loads(raw)
                        if packet.get('protocol') == 'omnifleet-discovery' and source[0] != address:
                            occupied.add(packet.get('domain_id'))
                    except (ValueError, UnicodeError):
                        pass
            if domain in occupied:
                domain = next((value for value in range(233) if value not in occupied), domain)
    manifest = json.loads(Path('/usr/local/share/omnifleet-image/identity-files.json').read_text())
    for relative in manifest:
        path = Path('/') / relative
        original = path.read_text()
        text = re.sub(r'\b' + re.escape(old['robot_id']) + r'\b', robot, original)
        text = re.sub(r'\bCAR-IECME' + re.escape(old['robot_id'].removeprefix('robot_')) + r'\b',
                      'CAR-IECME' + robot.removeprefix('robot_'), text)
        text = re.sub(r'\bROS_DOMAIN_ID=' + str(old['domain_id']) + r'\b', 'ROS_DOMAIN_ID=' + str(domain), text)
        text = re.sub(r'(?<=["\'])' + str(old['domain_id']) + '/', str(domain) + '/', text)
        text = text.replace('f1000000000000000000000000000104', hashlib.sha256(('zenoh-router:' + machine).encode()).hexdigest()[:32])
        if address and old['lan_address']:
            text = text.replace(old['lan_address'], address)
        if text != original:
            path.write_text(text)
    hostname = 'omnifleet-nx-' + machine[:8]
    Path('/etc/hostname').write_text(hostname + '\n')
    hosts = Path('/etc/hosts')
    lines = [line for line in hosts.read_text().splitlines() if not re.match(r'^127\.0\.1\.1\s', line)]
    hosts.write_text('\n'.join(lines) + '\n127.0.1.1 ' + hostname + '\n')
    state.parent.mkdir(parents=True, exist_ok=True)
    identity = {'robot_id': robot, 'domain_id': domain, 'lan_address': address,
                'initial_lan_address': old.get('initial_lan_address') or address,
                'hostname': hostname, 'public_identity_owner': 'dispatcher'}
    state.write_text(json.dumps(identity, indent=2) + '\n')
    subprocess.run(['hostname', hostname], check=True)
    subprocess.run(['ssh-keygen', '-A'], check=True)
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    print(json.dumps(identity), flush=True)


if __name__ == '__main__':
    main()
