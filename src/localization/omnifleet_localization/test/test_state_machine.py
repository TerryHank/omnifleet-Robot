import pytest

from omnifleet_localization.state_machine import InvalidTransition, State, SwitchStateMachine


def test_successful_switch_follows_all_stop_and_start_gates():
    machine = SwitchStateMachine()

    machine.begin("tx-1")
    assert machine.state is State.STOPPING
    machine.lock_zero_speed()
    machine.old_backend_stopped()
    assert machine.state is State.VERIFYING_STOP
    machine.old_tf_owners_absent()
    assert machine.state is State.STARTING
    machine.backend_started()
    assert machine.state is State.VERIFYING_START
    machine.backend_healthy()
    assert machine.state is State.RUNNING


def test_backend_cannot_start_before_zero_lock_and_old_owner_verification():
    machine = SwitchStateMachine()
    machine.begin("tx-2")

    with pytest.raises(InvalidTransition):
        machine.old_backend_stopped()
    with pytest.raises(InvalidTransition):
        machine.backend_started()


def test_any_failure_enters_safe_bringup_and_retains_zero_lock():
    machine = SwitchStateMachine()
    machine.begin("tx-3")
    machine.lock_zero_speed()

    machine.fail("health timeout")

    assert machine.state is State.SAFE_BRINGUP
    assert machine.zero_speed_locked is True
    assert machine.message == "health timeout"


def test_stop_only_transaction_finishes_idle_with_zero_lock():
    machine = SwitchStateMachine()
    machine.begin("tx-stop")
    machine.lock_zero_speed()
    machine.old_backend_stopped()
    machine.old_tf_owners_absent()

    machine.stop_complete()

    assert machine.state is State.IDLE
    assert machine.zero_speed_locked is True
