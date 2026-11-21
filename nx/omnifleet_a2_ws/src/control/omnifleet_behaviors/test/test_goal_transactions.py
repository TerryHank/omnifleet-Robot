import math
from omnifleet_behaviors.goal_transactions import Decision, GoalTransactions
from omnifleet_behaviors.foxglove_nav_bridge import _approach_xy
from pathlib import Path


def test_new_goal_cancels_and_waits_for_prior_result():
    transactions = GoalTransactions()
    first, decision = transactions.submit("single", "first")
    assert decision is Decision.START
    assert transactions.goal_response(first.transaction_id, accepted=True) is Decision.WAIT

    second, decision = transactions.submit("multi", "second")
    assert decision is Decision.CANCEL
    assert transactions.cancel_response(first.transaction_id) is Decision.WAIT
    assert transactions.current.transaction_id == first.transaction_id

    promoted, decision = transactions.result(first.transaction_id)
    assert decision is Decision.START
    assert promoted.transaction_id == second.transaction_id


def test_latest_goal_replaces_pending_goal_without_duplicate_start():
    transactions = GoalTransactions()
    first, _ = transactions.submit("single", "first")
    second, decision = transactions.submit("single", "second")
    assert decision is Decision.WAIT
    third, decision = transactions.submit("single", "third")
    assert decision is Decision.WAIT

    assert transactions.goal_response(first.transaction_id, accepted=True) is Decision.CANCEL
    promoted, decision = transactions.result(first.transaction_id)
    assert decision is Decision.START
    assert promoted.transaction_id == third.transaction_id
    assert promoted.transaction_id != second.transaction_id


def test_rejected_goal_promotes_pending_transaction():
    transactions = GoalTransactions()
    first, _ = transactions.submit("single", "first")
    second, _ = transactions.submit("multi", "second")

    promoted, decision = transactions.goal_rejected(first.transaction_id)
    assert decision is Decision.START
    assert promoted.transaction_id == second.transaction_id


def test_bridge_does_not_override_rclpy_node_client_storage():
    source = (
        Path(__file__).parents[1] / "omnifleet_behaviors" / "foxglove_nav_bridge.py"
    ).read_text(encoding="utf-8")
    assert "self._clients =" not in source


def test_precise_parking_approach_point_follows_goal_arrow():
    x, y = _approach_xy(10.0, 5.0, 0.0, 1.26)
    assert math.isclose(x, 8.74, abs_tol=1.0e-9)
    assert math.isclose(y, 5.0, abs_tol=1.0e-9)

    x, y = _approach_xy(10.0, 5.0, math.pi / 2.0, 1.26)
    assert math.isclose(x, 10.0, abs_tol=1.0e-9)
    assert math.isclose(y, 3.74, abs_tol=1.0e-9)
