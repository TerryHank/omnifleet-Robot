import json
from types import SimpleNamespace as NS

import pytest

from omnifleet_rmf_adapter.discovery import Registry, TTL, beacon_profile, new_vehicle
from omnifleet_rmf_adapter.discovery_manager import DiscoveryManager


def beacon(**fields):
    return {'protocol':'omnifleet-discovery','version':1,'robot_id':'rover_blue',
        'domain_id':91,'rmw':'rmw_zenoh_cpp','instance_id':'a'*32,'boot_id':'b'*32,
        'zenoh_port':7447,'observed_namespace':'','pose_topic':'/state_estimation/pose','interface_priority':1,**fields}


def test_endpoint_comes_from_datagram_source_not_claimed_host():
    profile=beacon_profile(beacon(host='203.0.113.200'), '192.168.20.11')
    assert profile['host']=='192.168.20.11'


@pytest.mark.parametrize('fields',[
    {'robot_id':'../shell'}, {'robot_id':'fleet'}, {'domain_id':True}, {'domain_id':233},
    {'zenoh_port':0}, {'rmw':'rmw_cyclonedds_cpp'}, {'instance_id':'not-a-machine'},
    {'observed_namespace':'/bad;command'}, {'pose_topic':'/../../file'},
])
def test_invalid_beacons_cannot_create_clients(fields):
    with pytest.raises(ValueError):beacon_profile(beacon(**fields),'192.168.20.11')


def test_expired_broadcast_leaves_and_new_address_rejoins_without_config_edit():
    r=Registry();r.observe(beacon(),'192.168.20.11',0)
    assert r.active(1)[0]['rover_blue']['host']=='192.168.20.11'
    assert r.active(TTL)[0]=={}
    r.observe(beacon(),'192.168.20.88',TTL+1)
    assert r.active(TTL+2)[0]['rover_blue']['host']=='192.168.20.88'


def test_repeated_broadcast_and_multiple_interfaces_do_not_duplicate_robot():
    r=Registry();r.observe(beacon(),'192.168.20.11',0);r.observe(beacon(),'10.20.0.11',1)
    r.observe(beacon(),'192.168.20.11',2)
    assert list(r.active(3)[0])==['rover_blue']
    assert r.active(3)[0]['rover_blue']['host']=='192.168.20.11'


def test_duplicate_identity_or_domain_is_quarantined():
    r=Registry();r.observe(beacon(),'192.168.20.11',0)
    r.observe(beacon(instance_id='c'*32),'192.168.20.12',1)
    assert r.active(2)==({},['rover_blue'])
    r=Registry();r.observe(beacon(),'192.168.20.11',0)
    r.observe(beacon(robot_id='other_rover',instance_id='c'*32),'192.168.20.12',1)
    assert r.active(2)==({},['other_rover','rover_blue'])


def test_cloned_machine_id_cannot_hide_two_vehicles_as_two_interfaces():
    r=Registry();r.observe(beacon(),'192.168.20.11',0)
    r.observe(beacon(boot_id='c'*32),'192.168.20.12',1)
    assert r.active(2)==({},['rover_blue'])


def test_unknown_vehicle_preserves_existing_names_and_has_no_motion_permission():
    names={'known':{'robot_name':'rover_blue','namespace':'/rover_blue'}}
    settings,assignment=new_vehicle(beacon_profile(beacon(),'192.168.20.11'),names)
    assert not settings['motion_enabled'] and 'host' not in settings
    assert assignment['robot_name']=='rover_blue_2'
    assert names=={'known':{'robot_name':'rover_blue','namespace':'/rover_blue'}}


def test_manager_stops_client_after_beacon_expiry_and_never_bootstraps_from_old_files(tmp_path):
    config=tmp_path/'framework.json'
    config.write_text(json.dumps({'central':{'domain_id':42},'robots':{}}))
    m=DiscoveryManager(config,tmp_path,'unused-runner')
    stopped=[];m.stop=lambda robot:(stopped.append(robot),m.children.pop(robot))
    m.children['rover_blue']=(NS(),beacon_profile(beacon(),'192.168.20.11'))
    m.tick(10)
    assert stopped==['rover_blue'] and not m.children
    assert json.loads((tmp_path/'discovery.json').read_text())['robots']=={}


def test_central_domain_is_not_attached_as_vehicle(tmp_path):
    config=tmp_path/'framework.json'
    config.write_text(json.dumps({'central':{'domain_id':42},'robots':{}}))
    m=DiscoveryManager(config,tmp_path,'unused-runner')
    m.registry.observe(beacon(domain_id=42),'192.168.20.11',0);m.tick(1)
    state=json.loads((tmp_path/'discovery.json').read_text())
    assert state['robots']=={} and state['conflicts']==['rover_blue']


def test_changed_endpoint_restarts_only_the_matching_isolated_client(tmp_path,monkeypatch):
    config=tmp_path/'framework.json'
    config.write_text(json.dumps({'central':{'domain_id':42},'robots':{'rover_blue':{'enabled':True}}}))
    launched=[]
    def spawn(command,env):
        launched.append((command,env));return NS(poll=lambda:None)
    monkeypatch.setattr('omnifleet_rmf_adapter.discovery_manager.subprocess.Popen',spawn)
    m=DiscoveryManager(config,tmp_path,'runner')
    m.registry.observe(beacon(),'192.168.20.11',0);m.tick(1)
    m.registry.observe(beacon(),'192.168.20.11',2);m.tick(3)
    assert len(launched)==1
    stopped=[];m.stop=lambda r:(stopped.append(r),m.children.pop(r))
    m.registry.observe(beacon(),'192.168.20.88',TTL+3);m.tick(TTL+4)
    assert stopped==['rover_blue'] and len(launched)==2
    session=json.loads((m.directory/'rover_blue.zenoh.json5').read_text())
    assert session['connect']['endpoints']==['tcp/192.168.20.88:7447']
    assert config.read_text().find('192.168')==-1


def test_central_enrolls_an_arbitrary_vehicle_without_restarting_or_granting_motion(tmp_path):
    from omnifleet_rmf_adapter.central import CentralObserver
    from omnifleet_rmf_adapter.identity import FleetIdentities
    from omnifleet_rmf_adapter.robot_names import RobotNames
    import time
    config={'robots':{},'central':{'assignments':{},'identity_revision':5}}
    path=tmp_path/'framework.json';path.write_text(json.dumps(config))
    profile=beacon_profile(beacon(),'192.168.20.11')
    (tmp_path/'discovery.json').write_text(json.dumps({'updated_monotonic':time.monotonic(),'robots':{'rover_blue':profile}}))
    hub=NS(names={},publishers={},create_vehicle_publishers=lambda ns:{})
    n=NS(data=tmp_path,config=config,identities=FleetIdentities(config,path),display_names=RobotNames(config,tmp_path),
        maps=hub,robot_publishers={},path_publishers={},robot_ids=[],missions=NS(follow={'order':[]}),
        operator=NS(bind=lambda:None),create_publisher=lambda *a:NS(),get_logger=lambda:NS(info=lambda *a:None))
    CentralObserver.sync_discovery(n)
    assert n.robot_ids==['rover_blue'] and hub.names=={'rover_blue':'/rover_blue'}
    assert config['central']['reference_robot']=='rover_blue' and hub.reference=='rover_blue'
    assert not config['robots']['rover_blue']['motion_enabled']
    assert config['central']['identity_revision']==6 and '192.168' not in path.read_text()
    CentralObserver.sync_discovery(n)
    assert n.robot_ids==['rover_blue'] and config['central']['identity_revision']==6
