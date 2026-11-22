import importlib.util
from pathlib import Path
import sys

import pytest


CORE_PATH = (
    Path(__file__).parents[1]
    / "scripts"
    / "integration"
    / "course_controllers_core.py"
)
SPEC = importlib.util.spec_from_file_location("course_controllers_core", CORE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_lane_controller_is_disabled_and_stops_on_risk():
    lane = {"detected": True, "offset_normalized": 0.25}
    disabled = MODULE.lane_follow_command(lane, {"risk_level": "clear"}, False, 1.0, 1.0)
    danger = MODULE.lane_follow_command(lane, {"risk_level": "danger"}, True, 1.0, 1.0)
    assert disabled[:2] == danger[:2] == (0.0, 0.0)


def test_lane_controller_tracks_only_fresh_valid_lane():
    lane = {"detected": True, "offset_normalized": 0.5}
    moving = MODULE.lane_follow_command(lane, {"risk_level": "clear"}, True, 1.1, 1.0)
    stale = MODULE.lane_follow_command(lane, {"risk_level": "clear"}, True, 2.0, 1.0, timeout=0.5)
    assert moving == (0.4, -0.3, "lane_follow")
    assert stale[:2] == (0.0, 0.0)


def test_lane_controller_obeys_pedestrian_and_red_light_events():
    lane = {"detected": True, "offset_normalized": 0.0}
    event = {"primary_event": {"event_type": "pedestrian"}}
    stopped = MODULE.lane_follow_command(
        lane, {"risk_level": "clear"}, True, 1.0, 1.0, event_payload=event
    )
    assert stopped == (0.0, 0.0, "event_pedestrian")


def test_target_controller_requires_depth_and_respects_filter():
    payload = {
        "detections": [
            {"class": "person", "confidence": 0.9, "bbox": [700, 200, 100, 200]},
        ]
    }
    missing_depth = MODULE.target_follow_command(payload, True, 1.1, 1.0, class_filter="person")
    payload["detections"][0]["depth_m"] = 1.2
    moving = MODULE.target_follow_command(payload, True, 1.1, 1.0, class_filter="person")
    wrong_class = MODULE.target_follow_command(payload, True, 1.1, 1.0, class_filter="car")
    assert missing_depth[:2] == wrong_class[:2] == (0.0, 0.0)
    assert moving[0] == pytest.approx(0.06)


def test_target_controller_smoothly_approaches_one_meter_without_reversing():
    payload = {
        "detections": [
            {
                "class": "person",
                "confidence": 0.9,
                "bbox": [718, 200, 100, 200],
                "depth_m": 2.0,
            },
        ]
    }
    far = MODULE.target_follow_command(payload, True, 1.0, 1.0, class_filter="person")
    payload["detections"][0]["depth_m"] = 1.2
    near = MODULE.target_follow_command(payload, True, 1.0, 1.0, class_filter="person")
    payload["detections"][0]["depth_m"] = 1.1
    reached = MODULE.target_follow_command(payload, True, 1.0, 1.0, class_filter="person")
    payload["detections"][0]["depth_m"] = 0.7
    too_close = MODULE.target_follow_command(payload, True, 1.0, 1.0, class_filter="person")

    assert far == (0.4, 0.0, "target_follow")
    assert near[0] == pytest.approx(0.06)
    assert 0.0 < near[0] < far[0]
    assert reached == (0.0, 0.0, "target_distance_reached")
    assert too_close == (0.0, 0.0, "target_distance_reached")


def test_target_controller_accepts_low_rate_depth_but_stops_when_stale():
    payload = {
        "detections": [
            {
                "class": "person",
                "confidence": 0.9,
                "bbox": [718, 200, 100, 200],
                "depth_m": 1.5,
            },
        ]
    }
    fresh = MODULE.target_follow_command(payload, True, 2.1, 1.0, class_filter="person")
    stale = MODULE.target_follow_command(payload, True, 2.3, 1.0, class_filter="person")

    assert fresh[0] > 0.0
    assert stale == (0.0, 0.0, "target_timeout")


def test_green_light_does_not_directly_authorize_cruise():
    core_path = CORE_PATH.parent / "vision_integration_core.py"
    spec = importlib.util.spec_from_file_location("vision_integration_core", core_path)
    core = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = core
    spec.loader.exec_module(core)
    event = {"primary_event": {"event_type": "green_light", "priority": 10}}
    waiting = core.safe_velocity_command(event, True, 1.0, 1.0, 0.5, 0.4, 0.4, 0.3)
    event["cruise_allowed"] = True
    moving = core.safe_velocity_command(event, True, 1.0, 1.0, 0.5, 0.4, 0.4, 0.3)
    assert waiting[:2] == (0.0, 0.0)
    assert moving[:2] == (0.4, 0.0)
