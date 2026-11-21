from copy import deepcopy

import pytest

from omnifleet_rmf_adapter.traffic import Traffic, crosses, waiting_pose
from test_missions import fleet, save, start


ZONE = {'id': 'hall', 'a': [2., 0.], 'b': [6., 0.], 'width': 1.}


def configure(f):
    f.owner.command({'op': 'traffic_configure', 'zones': [ZONE]}, f.states)


def position(f, r, x, y):
    f.states[r]['samples']['pose']['value'].update(x=x, y=y)


def executing(f, r, end):
    save(f, r, [end]);start(f, r);f.tick(9)
    return f.owner.jobs[r]


def test_crossing_checks_segment_interiors_and_body_margin():
    assert crosses([[0., 0., 0.], [8., 0., 0.]], ZONE)
    assert crosses([[4., .9, 0.]], ZONE)
    assert not crosses([[0., 3., 0.], [8., 3., 0.]], ZONE)
    assert not crosses([], ZONE)
    assert not crosses([waiting_pose(ZONE, 'a')], ZONE)


def test_configuration_and_restart_never_send_commands(fleet):
    configure(fleet)
    assert not fleet.sent
    restored = Traffic(fleet.owner)
    assert restored.saved['zones'] == [ZONE]
    assert not restored.saved['locks']


@pytest.mark.parametrize('field,value', [('width', 0), ('width', float('nan')), ('a', [1]), ('a', [float('inf'), 0]), ('id', '../hall'), ('b', [2., 0.])])
def test_invalid_zone_rejected(fleet, field, value):
    z = {**ZONE, field: value}
    with pytest.raises(ValueError):fleet.owner.traffic.configure({'zones': [z]}, fleet.states)
    assert not fleet.owner.traffic.saved['zones']


def test_configuration_rejects_motion_or_unknown_pose(fleet):
    fleet.states['a']['samples']['control']['value']['nav_active'] = True
    with pytest.raises(ValueError):configure(fleet)
    fleet.states['a']['samples']['control']['value']['nav_active'] = False
    fleet.states['a']['fresh']['pose'] = False
    with pytest.raises(ValueError):configure(fleet)


def test_second_frontend_cannot_overwrite_newer_corridor_definition(fleet):
    configure(fleet)
    with pytest.raises(ValueError, match='另一个前端'):
        fleet.owner.traffic.configure({'zones': [], 'traffic_revision': 0}, fleet.states)
    assert fleet.owner.traffic.saved['zones'] == [ZONE]


def test_stale_wheel_feedback_cannot_release_reserved_corridor(fleet):
    configure(fleet);traffic = fleet.owner.traffic
    traffic.acquire('a', {'id': 'first'}, [[0., 0.], [8., 0.]])
    fleet.states['a']['samples']['control']['value']['velocity_age'] = 2.
    traffic.tick(fleet.states)
    assert traffic.saved['locks']
    with pytest.raises(ValueError):traffic.recover({'acknowledge': '通道已清空'}, fleet.states)


def test_all_resources_are_acquired_atomically(fleet):
    zones = [ZONE, {**ZONE, 'id': 'next', 'a': [10., 0.], 'b': [12., 0.]}]
    fleet.owner.traffic.configure({'zones': zones}, fleet.states)
    traffic = fleet.owner.traffic
    assert traffic.acquire('b', {'id': 'b'}, [[9., 0.], [14., 0.]])[0]
    assert not traffic.acquire('a', {'id': 'a'}, [[0., 0.], [14., 0.]])[0]
    assert 'hall' not in traffic.saved['locks']


def test_first_admitted_robot_cannot_be_preempted(fleet):
    configure(fleet);traffic = fleet.owner.traffic
    assert traffic.acquire('a', {'id': 'first'}, [[0., 0.], [8., 0.]])[0]
    assert not traffic.acquire('b', {'id': 'second', 'task_priority': 100}, [[8., 0.], [0., 0.]])[0]
    assert traffic.saved['locks']['hall']['robot'] == 'a'


def test_cancel_or_restart_inside_does_not_release(fleet):
    configure(fleet);traffic = fleet.owner.traffic
    traffic.acquire('a', {'id': 'first'}, [[0., 0.], [8., 0.]])
    position(fleet, 'a', 4., 0.)
    restored = Traffic(fleet.owner);restored.tick(fleet.states)
    assert restored.saved['locks']['hall']['robot'] == 'a'
    assert not restored.acquire('b', {'id': 'second'}, [[8., 0.], [0., 0.]])[0]
    position(fleet, 'a', 8., 0.);restored.tick(fleet.states)
    assert not restored.saved['locks']


def test_offline_owner_never_releases_lock(fleet):
    configure(fleet);traffic = fleet.owner.traffic
    traffic.acquire('a', {'id': 'first'}, [[0., 0.], [8., 0.]])
    fleet.states['a']['online'] = False;traffic.tick(fleet.states)
    assert traffic.saved['locks']
    assert not traffic.acquire('b', {'id': 'second'}, [[8., 0.], [0., 0.]])[0]


def test_unowned_physical_occupant_blocks_even_without_job(fleet):
    configure(fleet);position(fleet, 'c', 4., 0.)
    traffic = fleet.owner.traffic;traffic.tick(fleet.states)
    assert not traffic.acquire('a', {'id': 'first'}, [[0., 0.], [8., 0.]])[0]
    assert traffic.zones[0]['state'] == 'BLOCKED'


def test_actual_intrusion_stops_owner(fleet):
    configure(fleet)
    job = executing(fleet, 'a', [8., 0., 0.])
    assert job['phase'] == 'EXECUTING'
    position(fleet, 'c', 4., 0.);fleet.tick()
    assert job['phase'] in ('STOPPING', 'FAILED')
    assert fleet.owner.traffic.saved['locks']['hall']['robot'] == 'a'


def test_reference_session_change_stops_and_never_auto_resumes(fleet):
    configure(fleet);job = executing(fleet, 'a', [8., 0., 0.])
    fleet.states['a']['samples']['navigation']['value']['localization_epoch'] = 'changed'
    fleet.tick(2)
    assert job['phase'] in ('STOPPING', 'FAILED', 'INVALIDATED')
    assert fleet.owner.traffic.saved['locks']
    assert fleet.owner.traffic.reason


def test_recover_requires_ack_idle_and_outside(fleet):
    configure(fleet);traffic = fleet.owner.traffic
    traffic.acquire('a', {'id': 'first'}, [[0., 0.], [8., 0.]])
    with pytest.raises(ValueError):traffic.recover({}, fleet.states)
    position(fleet, 'a', 4., 0.)
    with pytest.raises(ValueError):traffic.recover({'acknowledge': '通道已清空'}, fleet.states)
    position(fleet, 'a', 8., 0.)
    traffic.recover({'acknowledge': '通道已清空'}, fleet.states)
    assert not traffic.saved['locks']


def test_vehicle_order_chooses_winner_before_any_navigation(fleet):
    configure(fleet)
    position(fleet, 'b', 9., 0.)
    fleet.owner.traffic.set_order({'order': ['b', 'a', 'c'], 'order_revision': 0})
    save(fleet, 'a', [[8., 0., 0.]]);save(fleet, 'b', [[0., 0., 0.]])
    start(fleet, 'a');start(fleet, 'b');fleet.tick(10)
    assert fleet.owner.jobs['b']['phase'] == 'EXECUTING'
    assert fleet.owner.jobs['a']['phase'] == 'YIELDING'
    assert fleet.owner.traffic.saved['locks']['hall']['robot'] == 'b'
    assert fleet.owner.traffic.snapshot()['zones'][0]['queue'] == ['a']
    navigations = [p for p in fleet.sent if p[0] == 'navigate']
    assert [p[2] for p in navigations] == ['b']


def test_scheduled_task_sends_no_arm_or_navigation_before_time(fleet, monkeypatch):
    clock = [1000.];monkeypatch.setattr('omnifleet_rmf_adapter.missions.time.time', lambda: clock[0])
    fleet.owner.traffic.settings('a', {'not_before': 1100})
    save(fleet, 'a', [[1., 0., 0.]]);start(fleet, 'a');fleet.tick(8)
    assert not fleet.sent
    assert fleet.owner.jobs['a']['phase'] == 'SCHEDULED'
    clock[0] = 1101.;fleet.tick(8)
    assert fleet.owner.jobs['a']['phase'] == 'EXECUTING'


@pytest.mark.parametrize('packet', [{'task_priority': -1}, {'task_priority': True}, {'local_priority': 101}, {'not_before': float('inf')}])
def test_invalid_dispatch_metadata_rejected(fleet, packet):
    with pytest.raises(ValueError):fleet.owner.traffic.settings('a', packet)


def test_traffic_call_uses_each_robot_map_and_safe_waiting_point(fleet):
    configure(fleet)
    fleet.maps.alignment['b'] = [10., 0., 0.]
    result = fleet.owner.command({'op': 'traffic_call', 'robot_id': 'b', 'corridor': 'hall', 'side': 'a', 'action': 'wait'}, fleet.states)
    assert result['phase'] == 'accepted'
    assert fleet.owner.jobs['b']['points'][0]['pose'][0] == pytest.approx(waiting_pose(ZONE, 'a')[0]-10.)
    assert not fleet.sent


def test_dynamic_formation_and_trail_cannot_bypass_exclusive_corridors(fleet):
    configure(fleet)
    for op in ('formation_start', 'follow_start'):
        with pytest.raises(ValueError, match='窄道'):fleet.owner.command({'op': op, 'order': ['a', 'b']}, fleet.states)


def test_table_preserves_world_start_target_and_settings_without_fake_pose(fleet):
    fleet.owner.traffic.settings('a', {'title': '搬运', 'task_priority': 3, 'local_priority': 2})
    job = executing(fleet, 'a', [1., 0., 0.])
    rows = fleet.owner.snapshot()['dispatch_rows']
    row = rows[0]
    assert row['car'] == 'a' and row['title'] == '搬运'
    assert row['init_pose'] == [0., 0., 0.] and row['target_pose'] == [1., 0., 0.]
    assert row['task_priority'] == 3 and row['local_priority'] == 3
    fleet.states['a']['fresh']['pose'] = False;fleet.owner.traffic.tick(fleet.states)
    assert fleet.owner.snapshot()['dispatch_rows'][0]['pose'] is None


def test_fox_markers_use_ros_float_fields_even_for_integer_coordinates(fleet):
    from types import SimpleNamespace as NS
    from omnifleet_rmf_adapter.operator_controls import OperatorControls
    configure(fleet)
    fleet.owner.config['central']={'assignments':{r:{'robot_name':r} for r in fleet.maps.names}}
    published=[]
    owner=NS(data=fleet.root,config=fleet.config,maps=fleet.maps,identities=NS(revision=0),missions=fleet.owner,
             snapshots=lambda:fleet.states,create_subscription=lambda *a:None,create_timer=lambda *a:None,
             create_publisher=lambda *a:NS(publish=published.append))
    controls=OperatorControls(owner)
    controls.publish_waypoints()
    markers=published[-1].markers
    assert len(markers)==5
    assert markers[1].ns=='traffic_corridors'
    assert markers[-1].text=='hall / FREE'
