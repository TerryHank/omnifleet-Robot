from pathlib import Path


ROOT = Path(__file__).parents[1]
VERIFIER = (ROOT / "omnifleet_multi_robot_sim" / "multi_waypoint_verifier.py").read_text(encoding="utf-8")
SCRIPT = (ROOT.parents[2] / "scripts" / "smoke_test_multi_waypoint.sh").read_text(encoding="utf-8")


def test_verifier_route_and_acceptance_contract():
    assert 'DEFAULT_WAYPOINTS = ((-0.5, 0.0), (0.5, 0.0), (1.5, 0.0))' in VERIFIER
    assert '"--waypoints-json"' in VERIFIER
    assert "expected_indices = list(range(waypoint_count))" in VERIFIER
    assert 'expected_route_robots = ["robot1"] * waypoint_count' in VERIFIER
    assert '"/robot1/waypoints"' in VERIFIER
    for check in (
        "same_robot_completed_route",
        "waypoints_completed_in_order",
        "completed_count_matches_route",
        "robot1_entity_displacement",
        "other_robots_zero_command_stable",
        "minimum_distance_safe",
        "stopped_stably",
    ):
        assert check in VERIFIER


def test_smoke_isolation_and_cleanup_contract():
    assert 'ROS_DOMAIN_ID:-98' in SCRIPT
    assert '127.0.0.1:11398' in SCRIPT
    assert 'gui:=false rviz:=false foxglove:=false auto_demo:=false' in SCRIPT
    assert 'kill -INT -- "-${LAUNCH_PID}"' in SCRIPT
    assert "killall" not in SCRIPT and "pkill" not in SCRIPT
