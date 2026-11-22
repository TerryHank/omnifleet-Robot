from omnifleet_local_navigation.task_policy import TaskPolicy, Ticket


def test_fleet_revision_update_and_duplicate_are_idempotent():
    policy = TaskPolicy()
    current = Ticket('task-1', 'FLEET', 3, 'epoch-1')
    updated = Ticket('task-1', 'FLEET', 4, 'epoch-1')

    assert policy.request(current) == 'START'
    assert policy.request(current) == 'DUPLICATE'
    assert policy.update_fleet(updated, stop_first=False)
    assert policy.current == updated
    assert policy.request(current) == 'DUPLICATE'
    assert not policy.update_fleet(Ticket('task-1', 'FLEET', 5, 'epoch-2'), stop_first=False)


def test_route_revision_waits_for_cancel_and_stop_confirmation():
    policy = TaskPolicy()
    current = Ticket('task-1', 'FLEET', 3, 'epoch-1')
    updated = Ticket('task-1', 'FLEET', 4, 'epoch-1')

    assert policy.request(current) == 'START'
    assert policy.update_fleet(updated, stop_first=True)
    assert policy.current == current
    assert policy.pending == updated and policy.canceling
    assert policy.canceled_and_stopped() == updated
    assert policy.current == updated and not policy.canceling
