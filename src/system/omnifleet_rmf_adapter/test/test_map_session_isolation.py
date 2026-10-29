import json
from types import SimpleNamespace as NS

import pytest
from geometry_msgs.msg import PoseStamped

from omnifleet_rmf_adapter.map_hub import MapHub
from omnifleet_rmf_adapter.missions import Missions
from omnifleet_rmf_adapter.operator_controls import OperatorControls


def fixture(tmp_path):
    hub = MapHub.__new__(MapHub)
    hub.data, hub.reference = tmp_path, 'anchor'
    hub.names = {r: '/' + r for r in ('anchor', 'east', 'west')}
    states = {r: {'online': True, 'fresh': {'map': True}, 'samples': {
        'navigation': {'value': {'localization_epoch': r + '-current'}}}} for r in hub.names}
    saved = {'validated': True, 'epochs': {r: r + '-current' for r in hub.names},
             'transforms': {'anchor': [0., 0., 0.], 'east': [1., 2., .3], 'west': [-1., 0., 0.]}}
    return hub, states, saved


def store(hub, saved):
    (hub.data / 'fleet_alignment.json').write_text(json.dumps(saved))


def test_reference_can_use_its_current_map_without_any_saved_registration(tmp_path):
    hub, states, _ = fixture(tmp_path)
    assert hub.transforms(states) == {'anchor': [0., 0., 0.]}
    assert hub.valid_robots == {'anchor'}


def test_one_peer_restarting_does_not_invalidate_reference_or_other_peer(tmp_path):
    hub, states, saved = fixture(tmp_path)
    store(hub, saved)
    states['east']['samples']['navigation']['value']['localization_epoch'] = 'east-restarted'
    assert set(hub.transforms(states)) == {'anchor', 'west'}
    assert hub.valid_robots == {'anchor', 'west'}
    assert '本车定位会话已变化' in hub.validation_reasons['east']


def test_reference_new_session_keeps_only_its_own_identity_transform(tmp_path):
    hub, states, saved = fixture(tmp_path)
    store(hub, saved)
    states['anchor']['samples']['navigation']['value']['localization_epoch'] = 'new-anchor-map'
    assert hub.transforms(states) == {'anchor': [0., 0., 0.]}
    assert hub.valid_robots == {'anchor'}
    assert '参考车辆定位会话已变化' in hub.validation_reasons['east']


@pytest.mark.parametrize('fault', ['offline', 'stale_map', 'missing_epoch'])
def test_reference_is_not_usable_without_current_local_map_inputs(tmp_path, fault):
    hub, states, _ = fixture(tmp_path)
    if fault == 'offline':
        states['anchor']['online'] = False
    elif fault == 'stale_map':
        states['anchor']['fresh']['map'] = False
    else:
        states['anchor']['samples']['navigation']['value']['localization_epoch'] = ''
    hub.transforms(states)
    assert 'anchor' not in hub.valid_robots
    assert hub.validation_reasons['anchor']


@pytest.mark.parametrize('pose', [None, [1., 2.], [float('nan'), 0., 0.], ['x', 0., 0.]])
def test_bad_peer_transform_is_rejected_without_blocking_other_vehicles(tmp_path, pose):
    hub, states, saved = fixture(tmp_path)
    saved['transforms']['east'] = pose
    store(hub, saved)
    hub.transforms(states)
    assert hub.valid_robots == {'anchor', 'west'}


def test_unvalidated_registration_does_not_enable_peers(tmp_path):
    hub, states, saved = fixture(tmp_path)
    saved['validated'] = False
    store(hub, saved)
    hub.transforms(states)
    assert hub.valid_robots == {'anchor'}


@pytest.mark.parametrize('fault', ['offline', 'stale_map'])
def test_unavailable_peer_does_not_disable_other_vehicles(tmp_path, fault):
    hub, states, saved = fixture(tmp_path)
    store(hub, saved)
    if fault == 'offline':states['east']['online'] = False
    else:states['east']['fresh']['map'] = False
    hub.transforms(states)
    assert hub.valid_robots == {'anchor', 'west'}
    assert 'east' in hub.alignment  # Retain the known frame for last-body occupancy.


def test_current_reference_map_click_reaches_single_job_without_peer_registration(tmp_path):
    hub, states, _ = fixture(tmp_path)
    hub.transforms(states)
    for state in states.values():
        state['fresh']['fleet_client'] = True
        state['samples']['navigation']['value'].update(local_ready=True, navigation_active=False)
        state['samples']['control'] = {'value': {'control_gate_ready': True, 'stopped_seconds': 2.}}
        state['samples']['fleet_client'] = {'value': {'busy': False}}
    config = {'robots': {r: {'motion_enabled': True} for r in hub.names}, 'central': {
        'reference_robot': hub.reference, 'assignments': {r: {'robot_name': r} for r in hub.names}}}
    sent = []
    missions = Missions(config, hub, tmp_path, lambda *a, **k: sent.append((a, k)))
    try:
        owner = NS(snapshots=lambda: states, maps=hub, missions=missions,
                   execution_permissions=lambda _: ({}, {}, {'anchor': True}))
        operator = OperatorControls.__new__(OperatorControls)
        operator.owner, operator.stopped = owner, False
        message = PoseStamped()
        message.header.frame_id = 'fleet_map'
        message.pose.position.x, message.pose.position.y = 3., 4.
        message.pose.orientation.w = 1.
        operator.waypoint('anchor', message, single=True)
        assert operator.receipt['phase'] == 'accepted'
        assert missions.jobs['anchor']['source'] == 'single'
        assert missions.jobs['anchor']['points'][0]['pose'] == [3., 4., 0.]
        assert not sent  # Admission alone does not bypass the control-lease handshake.
    finally:
        missions.close()


def test_map_click_returns_the_specific_target_vehicle_blocker():
    owner = NS(snapshots=lambda: {}, maps=NS(valid_robots=set(),
        validation_reasons={'east': '本车定位会话已变化，等待重新配准'}))
    operator = OperatorControls.__new__(OperatorControls)
    operator.owner = owner
    OperatorControls.waypoint(operator, 'east', PoseStamped(), single=True)
    assert operator.receipt['phase'] == 'rejected'
    assert operator.receipt['message'] == owner.maps.validation_reasons['east']
