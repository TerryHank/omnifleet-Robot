from copy import deepcopy
import json
import math

from nav_msgs.msg import OccupancyGrid
import pytest

from omnifleet_rmf_adapter.shared_costmap import DEFAULTS, SharedCostmap, inflate
from omnifleet_rmf_adapter.map_hub import peer_grid


def grid(width=21, height=21, resolution=.1):
    result = OccupancyGrid()
    result.info.width, result.info.height, result.info.resolution = width, height, resolution
    result.info.origin.orientation.w = 1.
    result.data = [0]*(width*height)
    return result


def test_costs_match_nav2_exponential_and_publication_scale():
    source = grid()
    source.data[10*21+10] = 100
    result = inflate(source, DEFAULTS)
    assert result.data[10*21+10] == 100
    for cells in (1, 2, 3, 4):
        raw = int(252*math.exp(-3.*(cells*source.info.resolution-.01)))
        assert result.data[10*21+10+cells] == 1+(raw-1)*97//251
    assert result.data[10*21+15] == 0
    assert source.data[10*21+11] == 0


def test_no_obstacles_do_not_create_border_costs_and_unknown_stays_unknown():
    source = grid()
    source.data[0] = -1
    assert list(inflate(source, DEFAULTS).data) == list(source.data)
    source.data[10*21+10] = 100
    source.data[10*21+11] = -1
    assert inflate(source, DEFAULTS).data[10*21+11] == -1
    assert inflate(source, {**DEFAULTS, 'robot_radius': .2}).data[10*21+11] == 99


def test_radius_and_scaling_have_independent_effects():
    source = grid()
    source.data[10*21+10] = 100
    original = inflate(source, DEFAULTS)
    assert inflate(source, {**DEFAULTS, 'inflation_radius': .6}).data[10*21+15] > 0
    assert inflate(source, {**DEFAULTS, 'cost_scaling_factor': 6.}).data[10*21+12] < original.data[10*21+12]
    assert list(inflate(source, {**DEFAULTS, 'inflation_radius': 0.}).data) == list(source.data)


def test_shared_overview_contains_both_vehicles_equally():
    source = grid(61, 21)
    occupied = peer_grid(source, [([1., 1., 0.], .39), ([4., 1., 0.], .39)])
    occupied.data = [max(0, c) for c in occupied.data]
    result = inflate(occupied, DEFAULTS)
    for col in (10, 40):
        assert result.data[10*61+col] == 100
        assert 0 < result.data[10*61+col+6] < 100


def test_configuration_is_independent_persistent_and_revision_checked(tmp_path):
    seed = {'revision': 0, 'parameters': deepcopy(DEFAULTS), 'seed': {'robot_name': 'car1', 'copied_once': True}}
    (tmp_path/'shared_costmap.json').write_text(json.dumps(seed))
    owner = SharedCostmap(tmp_path)
    owner.configure({'shared_costmap_revision': 0, 'parameters': {'inflation_radius': .6}})
    assert seed['parameters']['inflation_radius'] == .4
    restored = SharedCostmap(tmp_path)
    assert restored.saved['parameters']['inflation_radius'] == .6
    assert restored.saved['revision'] == 1
    with pytest.raises(ValueError, match='另一个前端'):
        owner.configure({'shared_costmap_revision': 0, 'parameters': {'inflation_radius': .5}})


@pytest.mark.parametrize('parameters', [{'inflation_radius': -1}, {'inflation_radius': True}, {'cost_scaling_factor': float('nan')}, {'cost_scaling_factor': 0}, {'robot_radius': 0}, {'footprint_padding': 9}, {'unknown': 1}, {}])
def test_invalid_shared_configuration_rejected(tmp_path, parameters):
    owner = SharedCostmap(tmp_path)
    with pytest.raises(ValueError):owner.configure({'shared_costmap_revision': 0, 'parameters': parameters})
    assert not owner.path.exists()


def test_map_hub_publishes_independent_costs_for_all_vehicles_and_keeps_peer_views(tmp_path, monkeypatch):
    from types import SimpleNamespace as NS
    from builtin_interfaces.msg import Time
    from rclpy.serialization import serialize_message, deserialize_message
    from omnifleet_rmf_adapter.map_hub import MapHub
    published = {}
    def publisher(kind, topic, qos):
        published[topic] = []
        return NS(publish=lambda message: published[topic].append(message))
    clock = [100.]
    monkeypatch.setattr('omnifleet_rmf_adapter.map_hub.time.monotonic', lambda: clock[0])
    node = NS(create_publisher=publisher, get_clock=lambda: NS(now=lambda: NS(to_msg=lambda: Time())))
    config = {'central': {'reference_robot': 'a', 'assignments': {r: {'namespace': '/'+r, 'robot_name': r} for r in ('a', 'b')}},
              'robots': {r: {'enabled': True} for r in ('a', 'b')}}
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({'validated': True, 'epochs': {'a': 'a', 'b': 'b'}, 'transforms': {'b': [0., 0., 0.]}}))
    states = {}
    for robot, x in [('a', 1.), ('b', 4.)]:
        cache = tmp_path/'vehicle-cache'/robot
        cache.mkdir(parents=True)
        source = grid(61, 21)
        source.header.frame_id = 'map'
        (cache/'map.cdr').write_bytes(serialize_message(source))
        states[robot] = {'online': True, 'fresh': {'map': True}, 'samples': {'map': {'value': {}}, 'navigation': {'value': {'localization_epoch': robot}}, 'pose': {'value': {'x': x, 'y': 1., 'yaw': 0.}}}}
    hub = MapHub(node, config, tmp_path)
    hub.tick(states)
    shared = published['/fleet/global_costmap/costmap'][-1]
    assert shared.header.frame_id == 'fleet_map'
    assert shared.data[10*61+10] == shared.data[10*61+40] == 100
    assert published['/a/navigation/peer_map'][-1].data[10*61+10] == -1
    assert published['/a/navigation/peer_map'][-1].data[10*61+40] == 100
    assert hub.state['shared_costmap']['owner'] == 'wsl'
    assert shared.data[10*61+19] == 0
    hub.shared_costmap.configure({'shared_costmap_revision': 0, 'parameters': {'inflation_radius': .6}})
    clock[0] += .2
    hub.tick(states)
    assert published['/fleet/global_costmap/costmap'][-1].data[10*61+19] > 0
    cached = deserialize_message((tmp_path/'shared_costmap.cdr').read_bytes(), OccupancyGrid)
    assert list(cached.data) == list(published['/fleet/global_costmap/costmap'][-1].data)
