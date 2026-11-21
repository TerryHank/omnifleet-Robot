from pathlib import Path


SOURCE = (Path(__file__).parents[1] / "omnifleet_multi_robot_sim" / "fleet_controller.py").read_text(encoding="utf-8")


def test_goal_service_and_status_contract():
    for topic in ("/fleet/goal", "/goal_pose", "/fleet/status", "/fleet/events"):
        assert topic in SOURCE
    for service in ("/fleet/cancel_all", "/fleet/clear_queue"):
        assert service in SOURCE
    for field in ("completed_count", "min_pair_distance", '"queue"', '"online"', '"state"'):
        assert field in SOURCE


def test_direct_robot_goal_and_twist_contract():
    assert 'f"/{name}/goal_pose"' in SOURCE
    assert 'f"/{name}/cmd_vel"' in SOURCE
    assert "create_timer(0.05" in SOURCE
    assert "DurabilityPolicy.TRANSIENT_LOCAL" in SOURCE


def test_path_route_contract_and_progress_metadata():
    assert 'Path, "/fleet/waypoints"' in SOURCE
    assert 'f"/{name}/waypoints"' in SOURCE
    assert '"route_rejected"' in SOURCE
    for field in ("route_id", "waypoint_index", "waypoint_count"):
        assert field in SOURCE
    assert "if robot.task.route_id is None:" in SOURCE
