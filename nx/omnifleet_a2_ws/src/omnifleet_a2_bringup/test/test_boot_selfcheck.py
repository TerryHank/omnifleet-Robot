import json
from pathlib import Path

from omnifleet_a2_bringup.boot_selfcheck import (
    apply_results,
    check_environment,
    claim_boot_run,
    persist_report,
    render_report,
)
from omnifleet_a2_bringup.vehicle_task_log import issue_id_for, load_issues


def _check(passed, evidence_id="evidence:test"):
    return {
        "id": "lidar",
        "label": "Airy 服务/数据",
        "passed": passed,
        "reason_code": "AIRY_DRIVER_NOT_ACTIVE",
        "task": "service_health_review",
        "target": "robosense_airy",
        "reason": "ok" if passed else "radar unavailable",
        "evidence": ["service=active"] if passed else ["service=activating"],
        "evidence_id": evidence_id,
        "recovery_candidates": [
            ("AIRY_DRIVER_NOT_ACTIVE", "service_health_review", "robosense_airy"),
        ] if passed else [],
    }


def test_one_pass_only_marks_recovered_not_verified(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_NO_JOURNAL", "1")
    apply_results([_check(False)], "boot-a")
    issue_id = issue_id_for("AIRY_DRIVER_NOT_ACTIVE", "service_health_review", "robosense_airy")
    assert load_issues()[issue_id]["state"] == "OPEN"
    apply_results([_check(True)], "boot-a")
    issue = load_issues()[issue_id]
    assert issue["state"] == "RECOVERED"
    assert issue["closure_status"] == "PENDING"
    assert issue["recovery_evidence"] == ["evidence:test"]


def test_environment_accepts_package_level_overlay_prefix(monkeypatch):
    monkeypatch.setenv("ROS_DISTRO", "humble")
    monkeypatch.setenv("ROS_DOMAIN_ID", "42")
    monkeypatch.setenv(
        "AMENT_PREFIX_PATH",
        "/home/iecme/omnifleet_a2_ws/install/omnifleet_a2_bringup:/opt/ros/humble",
    )
    assert check_environment()["passed"] is True


def test_boot_observation_can_only_be_claimed_once_per_boot(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_DIR", str(tmp_path))
    assert claim_boot_run("boot-a") is True
    assert claim_boot_run("boot-a") is False
    assert json.loads((tmp_path / "boot_runs" / "boot-a.json").read_text(encoding="utf-8"))["boot_id"] == "boot-a"


def test_boot_report_is_historical_and_latest(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_DIR", str(tmp_path))
    report = {
        "timestamp": "2026-08-26T02:00:00+08:00",
        "hostname": "robot", "boot_id": "boot-12345678", "run_id": "run-12345678",
        "passed": False, "nonzero_command_sent": False, "duration_seconds": 3.0,
        "code_sha256": "abc", "checks": [_check(False)], "issues": {},
    }
    historical = persist_report(report)
    assert historical.exists()
    assert historical != tmp_path / "last_boot_report.txt"
    assert (tmp_path / "last_boot_report.json").exists()
    assert json.loads((tmp_path / "last_boot_report.json").read_text(encoding="utf-8"))["run_id"] == "run-12345678"
    assert "闭环状态：待解决" in render_report(report)


def test_selfcheck_is_not_installed_as_a_robot_service_gate():
    workspace = Path(__file__).resolve().parents[3]
    deployed_units = list((workspace / "deploy" / "systemd").glob("*selfcheck*"))
    assert deployed_units == []


def test_selfcheck_source_contains_no_mutating_robot_commands():
    source = (Path(__file__).parents[1] / "omnifleet_a2_bringup" / "boot_selfcheck.py").read_text(encoding="utf-8")
    for forbidden in (
        "ros2 topic pub", "NavigateToPose", "FollowPath", "BackUp", "Spin",
        "systemctl start", "systemctl stop", "systemctl restart", "serial.Serial",
        "voltage",
    ):
        assert forbidden not in source
