import time
from types import SimpleNamespace

from omnifleet_waypoint_ui.waypoint_ui_bridge import WaypointUiBridge


def bridge_state():
    state = SimpleNamespace(
        last_error_hint=None,
        last_error_key="",
        last_error_at=0.0,
        publishes=0,
    )
    state.publish_catalog = lambda: setattr(state, "publishes", state.publishes + 1)
    return state


def test_specific_error_is_exposed_and_generic_followup_cannot_replace_it():
    state = bridge_state()
    WaypointUiBridge.record_navigation_error(
        state,
        "deviated from ordered route; stopped without shortcut replanning",
        "bt_navigator",
    )
    assert state.last_error_hint["code"] == "ordered_route_deviation"
    assert state.publishes == 1
    WaypointUiBridge.record_navigation_error(state, "Goal failed", "bt_navigator")
    assert state.last_error_hint["code"] == "ordered_route_deviation"
    assert state.publishes == 1


def test_repeated_error_is_deduplicated():
    state = bridge_state()
    raw = "stale localization transform: age_ms=550"
    WaypointUiBridge.record_navigation_error(state, raw, "bt_navigator")
    WaypointUiBridge.record_navigation_error(state, raw, "bt_navigator")
    assert state.last_error_hint["occurrences"] == 2
    assert state.publishes == 1


def test_clear_removes_stale_error():
    state = bridge_state()
    state.last_error_hint = {"code": "goal_failed"}
    state.last_error_key = "goal_failed"
    state.last_error_at = time.time()
    WaypointUiBridge.clear_error_hint(state)
    assert state.last_error_hint is None
    assert state.last_error_key == ""
    assert state.last_error_at == 0.0
