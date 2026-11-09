from pathlib import Path
import runpy

import pytest

SCRIPTS=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('robot,domain,user,group',[
    ('warehouse_rover',171,'fleet_agent','robots'),
    ('platform_B',86,'navigation','operators'),
])
def test_same_beacon_uses_each_vehicles_own_running_identity(monkeypatch,robot,domain,user,group):
    module=runpy.run_path(str(SCRIPTS/'fleet_beacon.py'))
    read_text,read_bytes,exists=Path.read_text,Path.read_bytes,Path.exists
    def text(path,*args,**kwargs):
        if str(path)=='/etc/omnifleet_t2/robot.env':
            return f'OMNIFLEET_ROBOT_ID={robot}\nROS_DOMAIN_ID={domain}\n'
        if str(path)=='/proc/sys/kernel/random/boot_id':return 'b'*32
        return read_text(path,*args,**kwargs)
    def data(path):
        if str(path)=='/proc/9123/environ':
            return f'RMW_IMPLEMENTATION=rmw_zenoh_cpp\0ROS_DOMAIN_ID={domain}\0HOME=/srv/{user}\0'.encode()
        if str(path)=='/etc/machine-id':return user.encode()
        return read_bytes(path)
    monkeypatch.setattr(Path,'read_text',text);monkeypatch.setattr(Path,'read_bytes',data)
    monkeypatch.setattr(Path,'exists',lambda path:True if str(path)=='/proc/9123/environ' else exists(path))
    monkeypatch.setattr('subprocess.check_output',lambda *a,**k:'9123')
    packet=module['settings']()
    assert packet['robot_id']==robot and packet['domain_id']==domain
    assert 'host' not in packet and 'ip' not in packet
    installer=runpy.run_path(str(SCRIPTS/'install_beacon.py'))
    unit=installer['service_unit'](user,group)
    assert 'User='+user in unit and 'Group='+group in unit
    assert 'ExecStart=/usr/bin/python3 /usr/local/lib/omnifleet-discovery/fleet_beacon.py' in unit
    assert '/home/' not in unit and 'iecme' not in unit


def test_portable_payload_has_no_specific_vehicles_or_ip_settings():
    for filename in ('fleet_beacon.py','install_beacon.py'):
        text=(SCRIPTS/filename).read_text()
        assert all(word not in text for word in ('robot_104','robot_113','192.168.','iecme'))
