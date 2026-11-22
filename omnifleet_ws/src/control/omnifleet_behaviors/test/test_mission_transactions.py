from omnifleet_behaviors.goal_transactions import Decision, GoalTransactions
from pathlib import Path


def test_patrol_restart_waits_for_action_result():
    transactions = GoalTransactions()
    running, decision = transactions.submit("patrol", {"revision": 4})
    assert decision is Decision.START
    assert transactions.goal_response(running.transaction_id, True) is Decision.WAIT

    replacement, decision = transactions.submit("home", {"revision": 2})
    assert decision is Decision.CANCEL
    assert transactions.cancel_response(running.transaction_id) is Decision.WAIT
    promoted, decision = transactions.result(running.transaction_id)
    assert decision is Decision.START
    assert promoted.transaction_id == replacement.transaction_id


def test_mission_node_does_not_override_rclpy_node_client_storage():
    source = (
        Path(__file__).parents[1] / "omnifleet_behaviors" / "mission_manager.py"
    ).read_text(encoding="utf-8")
    assert "self._clients =" not in source
