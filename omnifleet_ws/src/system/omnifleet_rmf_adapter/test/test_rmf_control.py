from types import SimpleNamespace
from datetime import datetime
import pytest
from omnifleet_rmf_adapter.rmf_fleet import LiveFleet, CommandHandle
from rmf_adapter import graph


class Update:
    def update_position(self, starts):
        self.starts = starts

    def update_lost_position(self, *args):
        self.lost = args

    def submit_direct_request(self, payload, request_id, callback):
        self.response = callback

    def cancel_task(self, task_id, labels, callback):
        self.canceled = task_id
        callback(True)


def setup_fleet():
    sent = []
    fleet = LiveFleet(None, None, lambda *args, **kwargs: sent.append(args))
    update = Update()
    fleet.command = SimpleNamespace(update=update, tick=lambda state: None)
    fleet.names = ['origin', 'back_030']
    fleet.epoch = 'current'
    state = {'online': True, 'samples': {
        'navigation': {'value': {'localization_epoch': 'current',
            'fleet_enabled': True, 'fleet_lease_fresh': True, 'local_ready': True}},
        'pose': {'value': {'x': 0.0, 'y': 0.0, 'yaw': 0.0, 'frame_id': 'map'}},
        'control': {'value': {'nav_active': False, 'stopped_seconds': 1.0, 'control_gate_ready': True}}}}
    return fleet, update, state, sent


def test_cancel_during_submission_cancels_accepted_task():
    fleet, update, state, sent = setup_fleet()
    fleet.submit(state, 'back_030', 'first')
    fleet.cancel('cancel')
    update.response({'success': True, 'state': {'booking': {'id': 'accepted'}}})
    assert update.canceled == 'accepted'
    assert fleet.task_id == 'accepted'
    assert fleet.requests['cancel-pending-submission']['phase'] == 'cancel_issued'
    fleet.updates.put({'type': 'task_state_update', 'data': {
        'booking': {'id': 'accepted'}, 'status': 'canceled'}})
    fleet.tick(state)
    assert fleet.task_id is None
    assert fleet.pending_submission is None
    assert not fleet.cancel_pending
    assert sent[-1][0] == 'cancel'


def test_concurrent_submission_and_unknown_destination_rejected():
    fleet, update, state, sent = setup_fleet()
    with pytest.raises(ValueError):
        fleet.submit(state, 'uncommissioned', 'unknown')
    fleet.submit(state, 'back_030', 'first')
    with pytest.raises(ValueError):
        fleet.submit(state, 'origin', 'second')
    fleet.submit(state, 'back_030', 'first')
    assert len(fleet.requests) == 1


def test_failed_submission_does_not_leave_cancel_pending():
    fleet, update, state, sent = setup_fleet()
    fleet.submit(state, 'back_030', 'first')
    fleet.cancel('cancel')
    update.response({'success': False})
    assert not fleet.cancel_pending
    assert fleet.pending_submission is None


def setup_command():
    fleet, update, state, sent = setup_fleet()
    fleet.adapter = SimpleNamespace(now=lambda: datetime.fromtimestamp(100))
    fleet.graph = graph.Graph()
    fleet.graph.add_waypoint(fleet.map_name, [0.0, 0.0])
    fleet.graph.add_waypoint(fleet.map_name, [0.3, 0.0])
    fleet.graph.add_bidir_lane(0, 1)
    command = CommandHandle(fleet)
    command.update = update
    fleet.command = command
    return fleet, command, state, sent


def test_path_waits_until_planned_time_and_callback_runs_once():
    fleet, command, state, sent = setup_command()
    finished = []
    command.follow_new_path([SimpleNamespace(position=[0.0, 0.0, 0.0], time=datetime.fromtimestamp(110))],
                            lambda *args: None, lambda: finished.append(True))
    command.tick(state)
    command.tick(state)
    assert finished == []
    fleet.task_id = 'whole-task'
    fleet.adapter.now = lambda: datetime.fromtimestamp(110)
    command.tick(state)
    command.tick(state)
    assert finished == [True]
    assert fleet.task_id == 'whole-task'
    assert not any(op[0] == 'navigate' for op in sent)


def test_replacement_path_waits_for_stop_and_discards_old_callback():
    fleet, command, state, sent = setup_command()
    finished = []
    command.follow_new_path([SimpleNamespace(position=[0.3, 0.0, 0.0], time=datetime.fromtimestamp(100))],
                            lambda *args: None, lambda: finished.append('old'))
    command.tick(state)
    state['samples']['control']['value']['nav_active'] = True
    command.follow_new_path([SimpleNamespace(position=[0.0, 0.0, 0.0], time=datetime.fromtimestamp(100))],
                            lambda *args: None, lambda: finished.append('new'))
    command.tick(state)
    assert command.stopping
    assert finished == []
    state['samples']['control']['value']['nav_active'] = False
    command.tick(state)
    command.tick(state)
    assert finished == ['new']


def test_result_history_survives_unrelated_latest_event():
    fleet, command, state, sent = setup_command()
    command.follow_new_path([SimpleNamespace(position=[0.3, 0.0, 0.0], time=datetime.fromtimestamp(110))],
                            lambda *args: None, lambda: None)
    command.tick(state)
    state['samples']['fleet_client'] = {'value': {
        'event': {'request_id': 'unrelated', 'phase': 'stopped'},
        'history': {command.request: {'request_id': command.request, 'phase': 'completed'}}}}
    state['samples']['control']['value']['nav_active'] = True
    command.tick(state)
    assert command.request is not None
    state['samples']['control']['value']['nav_active'] = False
    command.tick(state)
    assert command.request is None
    assert command.wait_until == datetime.fromtimestamp(110)


def test_old_map_session_is_not_reported_or_executed():
    fleet, command, state, sent = setup_command()
    command.follow_new_path([SimpleNamespace(position=[0.3, 0.0, 0.0], time=datetime.fromtimestamp(100))],
                            lambda *args: None, lambda: None)
    state['samples']['navigation']['value']['localization_epoch'] = 'replaced'
    command.tick(state)
    assert not hasattr(command.update, 'starts')
    assert not command.path
    assert ('disarm', 'rmf-health-disarm') in sent
    assert not any(op[0] == 'navigate' for op in sent)


@pytest.mark.parametrize('field,value', [('control_gate_ready', False), ('manual_active', True), ('estop', True)])
def test_unsafe_control_state_rejects_task(field, value):
    fleet, update, state, sent = setup_fleet()
    state['samples']['control']['value'][field] = value
    with pytest.raises(ValueError):
        fleet.submit(state, 'back_030', 'unsafe')


def test_terminal_update_before_submit_response_is_not_lost():
    fleet, update, state, sent = setup_fleet()
    fleet.updates.put({'type': 'task_state_update', 'data': {
        'booking': {'id': 'accepted'}, 'status': 'completed'}})
    fleet.tick(state)
    fleet.submit(state, 'origin', 'first')
    update.response({'success': True, 'state': {'booking': {'id': 'accepted'}}})
    fleet.tick(state)
    assert fleet.task_id is None
