"""Forward LAN discovery into NAT WSL. Resolves WSL's address, never vehicle addresses."""
import ipaddress
import json
from pathlib import Path
import socket
import subprocess
import time


def main():
    home = Path(__file__).resolve().parent
    config = json.loads((home/'relay.json').read_text())
    address, resolved = None, 0.
    stats = {'received':0,'forwarded':0}
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as receiver, socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sender:
        receiver.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        receiver.bind(('0.0.0.0',7446));receiver.settimeout(1)
        session = None
        while True:
            if session is None or session.poll() is not None:
                if session is not None:
                    try:
                        session.stdin.close()
                    except OSError:
                        pass
                address, resolved = None, 0.
                try:
                    session = subprocess.Popen([
                        'wsl.exe','-d',config['distribution'],'--exec','/bin/bash','-lc',
                        'systemctl --user start omnifleet-rmf.target || true; exec /bin/cat'],
                        stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW)
                except OSError:
                    session = None
                    time.sleep(1)
                    continue
            if time.monotonic()-resolved > 15:
                try:
                    result = subprocess.check_output(['wsl.exe','-d',config['distribution'],'--','hostname','-I'],
                        timeout=8,creationflags=subprocess.CREATE_NO_WINDOW).decode().split()
                    address = next(str(ipaddress.IPv4Address(ip)) for ip in result if ':' not in ip)
                except (OSError,ValueError,StopIteration,subprocess.SubprocessError):
                    address = None
                resolved = time.monotonic()
            try:
                data, source = receiver.recvfrom(4096)
            except socket.timeout:
                continue
            try:
                beacon = json.loads(data)
                if not isinstance(beacon,dict) or beacon.get('protocol') != 'omnifleet-discovery':
                    continue
                stats['received'] += 1
                if address:
                    packet = {'relay_token':config['token'],'source_ip':source[0],'beacon':beacon}
                    sender.sendto(json.dumps(packet).encode(),(address,7448))
                    stats['forwarded'] += 1
                    stats['last_source'] = source[0]
                    stats['last_received_unix'] = time.time()
                    temporary=home/'relay-status.tmp';temporary.write_text(json.dumps(stats))
                    temporary.replace(home/'relay-status.json')
            except (ValueError,OSError):
                continue


if __name__ == '__main__':
    try:
        main()
    except OSError as error:
        if getattr(error,'winerror',None) != 10048:
            raise
