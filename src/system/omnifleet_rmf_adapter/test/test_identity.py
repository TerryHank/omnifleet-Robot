import copy
import json
from types import SimpleNamespace as NS

import pytest

from omnifleet_rmf_adapter.identity import FleetIdentities


def make_config(tmp_path):
    config = {'central': {'assignments': {r: {'robot_name': r, 'namespace': '/' + r} for r in ('robot_104', 'robot_113')}},
              'robots': {'robot_104': {'host': '192.168.3.104', 'domain_id': 104}, 'robot_113': {'host': '192.168.3.113', 'domain_id': 113}}}
    path = tmp_path / 'framework.json'
    path.write_text(json.dumps(config))
    return config, path, FleetIdentities(config, path)


@pytest.mark.parametrize('prefix', ['', '一号车', '113', 'car/1', 'car-1', 'fleet', 'robot_104', 'x' * 41])
def test_invalid_or_duplicate_prefix_is_rejected(tmp_path, prefix):
    config, path, identity = make_config(tmp_path)
    before = path.read_bytes()
    with pytest.raises(ValueError):
        identity.target('robot_113', prefix)
    assert path.read_bytes() == before


def test_real_identity_persists_and_commands_resolve_to_same_vehicle(tmp_path):
    config, path, identity = make_config(tmp_path)
    hardware = copy.deepcopy(config['robots'])
    identity.commit('robot_113', 'car_1')
    assert config['central']['assignments']['robot_113'] == {'robot_name': 'car_1', 'namespace': '/car_1'}
    assert config['robots'] == hardware
    restored = json.loads(path.read_text())
    assert FleetIdentities(restored, path).revision == 1
    packet = identity.command({'robot_id': 'car_1', 'order': ['car_1', 'robot_104'], 'identity_revision': 1})
    assert packet['robot_id'] == 'robot_113' and packet['order'] == ['robot_113', 'robot_104']
    with pytest.raises(ValueError, match='ID 已更新'):
        identity.command({'robot_id': 'robot_113'})
    with pytest.raises(ValueError, match='ID 不存在'):
        identity.command({'robot_id': 'robot_113', 'identity_revision': 1})


def node_fixture(tmp_path):
    from omnifleet_rmf_adapter.map_hub import MapHub
    config, path, identity = make_config(tmp_path)
    created, destroyed = [], []
    def create(typ, topic, qos):
        publisher = NS(topic=topic)
        created.append(publisher)
        return publisher
    hub = NS(node=NS(create_publisher=create), latched=10, names={'robot_104': '/robot_104', 'robot_113': '/robot_113'},
             publishers={'robot_113': {k: NS(topic='old/' + k) for k in ('map', 'peer', 'description')}},
             seen={('robot_113', 'map'): 1, ('robot_104', 'tf_static'): 1, ('robot_113', 'description'): 'old'}, last_map_publish=5.)
    hub.create_vehicle_publishers = lambda ns, tracking: MapHub.create_vehicle_publishers(hub, ns, tracking)
    node = NS(identities=identity, missions=NS(formation=NS(active=False),follow={'active': False}, jobs={}), maps=hub,
              create_publisher=create, destroy_publisher=destroyed.append,operator=NS(bind=lambda:None),
              robot_publishers={'robot_113': NS(topic='old/status')}, path_publishers={'robot_113': NS(topic='old/path')})
    states = {'robot_113': {'online': True, 'samples': {'control': {'value': {'stopped_seconds': 2.}}}}}
    return node, states, created, destroyed, path


def test_reassignment_recreates_actual_publishers_and_invalidates_exported_frames(tmp_path):
    from omnifleet_rmf_adapter.central import CentralObserver
    node, states, created, destroyed, path = node_fixture(tmp_path)
    result = CentralObserver.reassign_identity(node, {'connection_id': 'robot_113', 'prefix': 'car_1'}, states)
    assert result['robot_id'] == 'car_1' and result['identity_revision'] == 1
    assert {p.topic for p in created} == {'/car_1/map', '/car_1/navigation/peer_map', '/car_1/robot_description', '/car_1/rmf/connection_status', '/car_1/missions/preview_path','/car_1/global_costmap/costmap','/car_1/local_costmap/costmap'}
    assert len(destroyed) == 5 and node.maps.names['robot_113'] == '/car_1'
    assert not node.maps.seen and node.maps.last_map_publish == 0.


def test_busy_vehicle_cannot_change_identity(tmp_path):
    from omnifleet_rmf_adapter.central import CentralObserver
    node, states, created, destroyed, path = node_fixture(tmp_path)
    states['robot_113']['samples']['control']['value']['nav_active'] = True
    with pytest.raises(ValueError, match='停稳'):
        CentralObserver.reassign_identity(node, {'connection_id': 'robot_113', 'prefix': 'car_1'}, states)
    assert not created and not destroyed and node.identities.revision == 0


def test_failed_commit_removes_only_new_publishers_and_retains_old_identity(tmp_path):
    from omnifleet_rmf_adapter.central import CentralObserver
    node, states, created, destroyed, path = node_fixture(tmp_path)
    def fail(*args):
        raise RuntimeError('write failed')
    node.identities.commit = fail
    with pytest.raises(RuntimeError, match='write failed'):
        CentralObserver.reassign_identity(node, {'connection_id': 'robot_113', 'prefix': 'car_1'}, states)
    assert destroyed == created and len(created) == 7
    assert node.maps.names['robot_113'] == '/robot_113' and node.robot_publishers['robot_113'].topic == 'old/status'
