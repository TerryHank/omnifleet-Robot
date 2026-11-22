"""Install on this vehicle without any vehicle or dispatch-host IP argument."""
import datetime
import grp
import os
from pathlib import Path
import pwd
import runpy
import subprocess


SCRIPT = Path('/usr/local/lib/omnifleet-discovery/fleet_beacon.py')
SERVICE = Path('/etc/systemd/system/omnifleet-discovery-beacon.service')


def service_unit(user, group):
    return '\n'.join([
        '[Unit]', 'Description=OmniFleet LAN identity broadcast (no motion commands)',
        'After=network-online.target omnifleet-local-navigation.service', 'Wants=network-online.target', '',
        '[Service]', 'User='+user, 'Group='+group, 'Type=simple',
        'ExecStart=/usr/bin/python3 '+str(SCRIPT), 'Restart=always', 'RestartSec=3', '',
        '[Install]', 'WantedBy=multi-user.target', '',
    ])


def main():
    if os.geteuid() != 0:
        raise SystemExit('Run on the vehicle: sudo python3 install_beacon.py')
    source = Path(__file__).resolve().with_name('fleet_beacon.py')
    values = runpy.run_path(str(source))['robot_config']()
    robot, domain = values['OMNIFLEET_ROBOT_ID'], int(values['ROS_DOMAIN_ID'])
    user = subprocess.check_output(['systemctl','show','omnifleet-local-navigation.service','-p','User','--value'],text=True).strip() or 'root'
    group = subprocess.check_output(['systemctl','show','omnifleet-local-navigation.service','-p','Group','--value'],text=True).strip()
    if not group:
        account = pwd.getpwuid(int(user)) if user.isdigit() else pwd.getpwnam(user)
        group = grp.getgrgid(account.pw_gid).gr_name
    if not subprocess.check_output(['systemctl','show','omnifleet-local-navigation.service','-p','LoadState','--value'],text=True).strip() == 'loaded':
        raise SystemExit('Install the local navigation service before the broadcast service')
    # Save replaced files without changing robot identity or navigation configuration.
    content = source.read_bytes()
    unit = service_unit(user, group).encode()
    previous = [(SCRIPT,content),(SERVICE,unit)]
    if any(path.exists() and path.read_bytes()!=data for path,data in previous):
        backup = Path('/var/backups/omnifleet-discovery')/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True)
        for path,data in previous:
            if path.exists():
                (backup/path.name).write_bytes(path.read_bytes())
        print('Backup:',backup)
    SCRIPT.parent.mkdir(parents=True,exist_ok=True)
    SCRIPT.write_bytes(content);SCRIPT.chmod(0o644)
    SERVICE.write_bytes(unit);SERVICE.chmod(0o644)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    subprocess.run(['systemctl','enable','omnifleet-discovery-beacon.service'],check=True)
    subprocess.run(['systemctl','restart','omnifleet-discovery-beacon.service'],check=True)
    print('Broadcast installed:',robot,'domain',domain,'user',user,'(no IP configuration)')


if __name__ == '__main__':
    main()
