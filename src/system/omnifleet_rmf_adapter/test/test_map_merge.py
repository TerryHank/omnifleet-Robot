import copy
import hashlib
import json
import math
from types import SimpleNamespace as NS

from builtin_interfaces.msg import Time
from nav_msgs.msg import OccupancyGrid
import numpy as np
from rclpy.serialization import deserialize_message, serialize_message

from omnifleet_rmf_adapter.map_hub import MapHub
from omnifleet_rmf_adapter.map_merge import merge_grids


def grid(rows, resolution=1., origin=(0., 0., 0.)):
    result = OccupancyGrid()
    result.info.width, result.info.height = len(rows[0]), len(rows)
    result.info.resolution = resolution
    result.info.origin.position.x, result.info.origin.position.y = map(float, origin[:2])
    result.info.origin.orientation.z = math.sin(origin[2]/2)
    result.info.origin.orientation.w = math.cos(origin[2]/2)
    result.data = [v for row in rows for v in row]
    return result


def rows(result):
    return np.asarray(result.data).reshape(result.info.height, result.info.width).tolist()


def test_fill_unknown_expand_bounds_and_keep_occupied():
    a, b = grid([[0, -1], [100, -1]]), grid([[100, 0], [0, 100]])
    before = copy.deepcopy(a)
    merged, status = merge_grids({'a': a, 'b': b}, {'a': [0., 0., 0.], 'b': [1., 0., 0.]})
    assert rows(merged) == [[0, 100, 0], [100, 0, 100]]
    assert status['added_known_cells'] == {'a': 2, 'b': 4}
    assert rows(a) == rows(before)
    conflict, _ = merge_grids({'a': a, 'b': grid([[100, 0], [0, 0]])},
                              {'a': [0., 0., 0.], 'b': [0., 0., 0.]})
    assert rows(conflict) == [[100, 0], [100, 0]]


def test_rotated_vehicle_map_and_rotated_grid_origin():
    a = grid([[-1, -1], [-1, -1]])
    b = grid([[0, 100]])
    transforms = {'a': [0., 0., 0.], 'b': [2., 0., math.pi/2]}
    merged, _ = merge_grids({'a': a, 'b': b}, transforms)
    assert rows(merged) == [[-1, 0], [-1, 100]]
    b = grid([[0, 100]], origin=(2., 0., math.pi/2))
    merged, _ = merge_grids({'a': a, 'b': b}, {'a': [0., 0., 0.], 'b': [0., 0., 0.]})
    assert rows(merged) == [[-1, 0], [-1, 100]]


def test_negative_bounds_and_finer_resolution():
    a, b = grid([[100]]), grid([[0, 0], [0, -1]], .5)
    merged, _ = merge_grids({'a': a, 'b': b}, {'a': [0., 0., 0.], 'b': [-1., 0., 0.]})
    assert merged.info.origin.position.x == -1.
    assert rows(merged) == [[0, 0, 100, 100], [0, -1, 100, 100]]


def test_reference_only_keeps_original_lattice():
    a = grid([[0, 100], [-1, 0]], .1, (-.033, .087, 0.))
    merged, _ = merge_grids({'a': a}, {'a': [0., 0., 0.]})
    assert rows(merged) == rows(a)
    assert merged.info.width == a.info.width
    assert merged.info.origin == a.info.origin


def test_hub_publishes_and_transfers_same_fused_grid(tmp_path, monkeypatch):
    published = {}
    def publisher(kind, topic, qos):
        published[topic] = []
        return NS(publish=lambda m: published[topic].append(copy.deepcopy(m)))
    clock = [100.]
    monkeypatch.setattr('omnifleet_rmf_adapter.map_hub.time.monotonic', lambda: clock[0])
    node = NS(create_publisher=publisher, get_clock=lambda: NS(now=lambda: NS(to_msg=lambda: Time())))
    robots = ('a', 'b', 'unregistered')
    config = {'central': {'reference_robot': 'a', 'assignments': {
        r: {'namespace': '/'+r, 'robot_name': r} for r in robots}},
        'robots': {r: {'enabled': True} for r in robots}}
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({
        'validated': True, 'epochs': {'a': 'a', 'b': 'b'}, 'transforms': {'b': [1., 0., 0.]}}))
    states = {}
    for r, source in [('a', grid([[0, -1]])), ('b', grid([[100, 0]])),
                      ('unregistered', grid([[100]*10]))]:
        cache = tmp_path/'vehicle-cache'/r
        cache.mkdir(parents=True)
        (cache/'map.cdr').write_bytes(serialize_message(source))
        states[r] = {'online': True, 'fresh': {'map': True}, 'samples': {
            'map': {'value': {}}, 'navigation': {'value': {'localization_epoch': r}}}}
    hub = MapHub(node, config, tmp_path)
    hub.tick(states)
    shared = published['/fleet/map'][-1]
    assert rows(shared) == [[0, 100, 0]]
    assert hub.state['shared_map']['contributors'] == ['a', 'b']
    assert published['/fleet/global_costmap/costmap'][-1].data[1] == 100
    for r in robots:
        cache = tmp_path/'vehicle-cache'/r
        payload = (cache/'shared_map_out.cdr').read_bytes()
        assert payload == serialize_message(shared)
        receipt = json.loads((cache/'map_transfer.json').read_text())
        assert receipt['shared_payload_sha256'] == hashlib.sha256(payload).hexdigest()
        assert receipt['shared_cells_sha256'] == hashlib.sha256(memoryview(shared.data).cast('B')).hexdigest()
    cached = hub.merged_map
    previous_payload = (tmp_path/'vehicle-cache'/'a'/'shared_map_out.cdr').read_bytes()
    clock[0] += .2
    hub.tick(states)
    assert hub.merged_map is cached
    assert (tmp_path/'vehicle-cache'/'a'/'shared_map_out.cdr').read_bytes() == previous_payload
    states['b']['samples']['navigation']['value']['localization_epoch'] = 'new-session'
    clock[0] += .2
    hub.tick(states)
    assert rows(published['/fleet/map'][-1]) == [[0, -1]]
    assert hub.state['shared_map']['contributors'] == ['a']
