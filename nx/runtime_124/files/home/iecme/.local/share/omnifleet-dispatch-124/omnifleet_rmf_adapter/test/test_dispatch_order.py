from concurrent.futures import Future

import pytest

from omnifleet_rmf_adapter.traffic import Traffic
from test_missions import fleet, save, start


def crossing(f):
    f.states['b']['samples']['pose']['value'].update(x=9., y=0.)
    save(f, 'a', [[8., 0., 0.]])
    save(f, 'b', [[0., 0., 0.]])


def test_order_persists_without_motion_and_appends_new_discovery(fleet):
    traffic = fleet.owner.traffic
    fleet.owner.command({'op': 'dispatch_order', 'order': ['b', 'c', 'a']}, fleet.states)
    assert not fleet.sent
    restored = Traffic(fleet.owner)
    assert restored.order() == ['b', 'c', 'a']
    fleet.maps.names['discovered_vehicle'] = '/new_prefix'
    assert restored.order() == ['b', 'c', 'a', 'discovered_vehicle']
    assert restored.snapshot()['order_revision'] == 1
    assert [r['car'] for r in restored.rows()] == restored.order()
    assert [r['task_priority'] for r in restored.rows()] == [4, 3, 2, 1]


@pytest.mark.parametrize('order', [['a', 'a', 'c'], ['a', 'b'], ['a', 'b', 'wrong'], ['a', 'b', []]])
def test_invalid_order_cannot_change_priority(fleet, order):
    with pytest.raises(ValueError):fleet.owner.traffic.set_order({'order': order})
    assert fleet.owner.traffic.order() == ['a', 'b', 'c']
    assert not fleet.sent


def test_stale_frontend_cannot_overwrite_order(fleet):
    fleet.owner.traffic.set_order({'order': ['b', 'a', 'c']})
    with pytest.raises(ValueError, match='另一个前端'):
        fleet.owner.traffic.set_order({'order': ['c', 'b', 'a'], 'order_revision': 0})
    assert fleet.owner.traffic.order() == ['b', 'a', 'c']


@pytest.mark.parametrize('group', ['follow', 'formation'])
def test_active_group_order_cannot_be_rearranged(fleet, group):
    if group == 'follow':fleet.owner.follow.update(active=True)
    else:fleet.owner.formation.active = True
    with pytest.raises(ValueError, match='停止'):
        fleet.owner.traffic.set_order({'order': ['b', 'a', 'c']})


def test_leader_priority_ignores_old_manual_scores_without_corridors(fleet):
    crossing(fleet)
    fleet.owner.traffic.settings('b', {'task_priority': 100, 'local_priority': 100})
    start(fleet, 'b');start(fleet, 'a');fleet.tick(10)
    assert not fleet.owner.traffic.saved['zones']
    assert fleet.owner.jobs['a']['phase'] == 'EXECUTING'
    assert fleet.owner.jobs['b']['phase'] == 'YIELDING'
    assert [p[2] for p in fleet.sent if p[0] == 'navigate'] == ['a']


def test_later_planning_completion_cannot_steal_leader_priority(fleet):
    crossing(fleet)
    pending = Future()
    planner = fleet.owner.onboard_planner
    fleet.owner.onboard_planner = lambda r, targets, states: pending if r == 'a' else planner(r, targets, states)
    start(fleet, 'b');start(fleet, 'a');fleet.tick(10)
    assert not [p for p in fleet.sent if p[0] == 'navigate']
    pending.set_result({'path': [[0., 0., 0.], [8., 0., 0.]], 'targets': fleet.owner.jobs['a']['points']})
    fleet.tick(15)
    assert [p[2] for p in fleet.sent if p[0] == 'navigate'] == ['a']


def test_reorder_does_not_preempt_existing_navigation(fleet):
    crossing(fleet)
    start(fleet, 'b');fleet.tick(10)
    assert fleet.owner.jobs['b']['phase'] == 'EXECUTING'
    fleet.owner.traffic.set_order({'order': ['a', 'b', 'c']})
    start(fleet, 'a');fleet.tick(10)
    assert fleet.owner.jobs['b']['phase'] == 'EXECUTING'
    assert [p[2] for p in fleet.sent if p[0] == 'navigate'] == ['b']
    assert not [p for p in fleet.sent if p[0] == 'disarm']


def test_nonconflicting_paths_can_still_run_together(fleet):
    save(fleet, 'a', [[1., 0., 0.]])
    save(fleet, 'b', [[1., 4., 0.]])
    start(fleet, 'b');start(fleet, 'a');fleet.tick(10)
    assert [p[2] for p in fleet.sent if p[0] == 'navigate'] == ['a', 'b']
