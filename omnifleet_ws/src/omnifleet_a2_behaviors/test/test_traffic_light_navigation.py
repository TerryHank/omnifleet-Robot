import json
from pathlib import Path

import pytest

from omnifleet_a2_behaviors.traffic_light_navigation import (
    TrafficDecision,
    TrafficLightPolicy,
    parse_confirmed_signal,
)


def message(signal, status="cascade_confirmed"):
    return json.dumps({"fused_state": signal, "fusion_status": status})


def test_only_confirmed_cascade_result_is_accepted():
    assert parse_confirmed_signal(message("red")) == "red"
    assert parse_confirmed_signal(message("yellow")) == "yellow"
    assert parse_confirmed_signal(message("green")) == "green"
    assert parse_confirmed_signal(message("red", "yolo_no_color")) is None
    assert parse_confirmed_signal("not-json") is None
    assert parse_confirmed_signal({"fused_state": "blue"}) is None


def test_two_consecutive_stop_frames_latch_stop():
    policy = TrafficLightPolicy(stop_confirmations=2, go_confirmations=3)

    first = policy.observe(message("red"))
    second = policy.observe(message("yellow"))

    assert first.decision is TrafficDecision.NONE
    assert second.decision is TrafficDecision.STOP
    assert policy.stopped is True


def test_unknown_never_releases_a_latched_stop():
    policy = TrafficLightPolicy(stop_confirmations=1, go_confirmations=2)
    assert policy.observe(message("red")).decision is TrafficDecision.STOP

    transition = policy.observe(message("unknown", "yolo_no_color"))

    assert transition.decision is TrafficDecision.NONE
    assert transition.stopped is True


def test_green_requires_three_consecutive_confirmations_to_resume():
    policy = TrafficLightPolicy(stop_confirmations=1, go_confirmations=3)
    policy.observe(message("yellow"))

    assert policy.observe(message("green")).decision is TrafficDecision.NONE
    assert policy.observe(message("green")).decision is TrafficDecision.NONE
    transition = policy.observe(message("green"))

    assert transition.decision is TrafficDecision.GO
    assert transition.stopped is False


def test_invalid_confirmation_counts_are_rejected():
    with pytest.raises(ValueError):
        TrafficLightPolicy(stop_confirmations=0)
    with pytest.raises(ValueError):
        TrafficLightPolicy(go_confirmations=0)


def test_navigation_and_optional_traffic_launch_are_separate_programs():
    supervisor = (
        Path(__file__).parents[1]
        / "omnifleet_a2_behaviors"
        / "traffic_light_nav_supervisor.py"
    ).read_text(encoding="utf-8")
    launch = (
        Path(__file__).parents[2]
        / "omnifleet_a2_tutorials"
        / "launch"
        / "traffic_light_navigation.launch.py"
    ).read_text(encoding="utf-8")

    assert '"/omnifleet_a2/vision/detections"' in supervisor
    assert '"/omnifleet_a2/navigation/traffic_light_pause"' in supervisor
    assert '"/cmd_vel"' not in supervisor
    assert "_publish_zero_lock" not in supervisor
    assert '"vision_02_14_traffic_light.launch.py"' in launch
    assert '"enable_motion": "false"' in launch
    assert 'executable="traffic_light_nav_supervisor"' in launch
