import json
from pathlib import Path
import runpy
from concurrent.futures import ThreadPoolExecutor

from omnifleet_a2_bringup.vehicle_task_log import (
    classify_report,
    load_issues,
    persist_event,
    render_event,
    register_check_evidence,
    resolve_issue,
)


def test_preflight_radar_rejection_is_explicit_and_marks_no_motion():
    report = {
        "passed": False,
        "error": (
            "RuntimeError: radar_preflight_swept_collision="
            '{"time_s": 0.0, "point": [0.27, 0.0]}'
        ),
    }
    event = classify_report(report, "radius", "-30°", 2, "active", "active", "/tmp/raw.log")
    assert event["status"] == "REJECTED"
    assert event["reason_code"] == "RADAR_PREFLIGHT_COLLISION"
    assert event["nonzero_command_sent"] is False
    assert event["details"]["trigger_radius_m"] == 0.27
    assert event["details"]["point_classification"] == "疑似自车回波（未确认）"
    assert "拒绝运动" in event["reason"]


def test_near_margin_point_is_not_misreported_as_confirmed_self():
    report = {
        "passed": False,
        "error": (
            "RuntimeError: radar_preflight_swept_collision="
            '{"time_s": 0.0, "point": [0.45, 0.0]}'
        ),
    }
    event = classify_report(report, "radius", "30°", 2, "active", "active", "/tmp/raw.log")
    assert event["details"]["point_classification"] == "车体近旁点，来源未确认"


def test_point_without_collision_time_is_not_called_self_echo():
    report = {
        "passed": False,
        "error": 'RuntimeError: radar_preflight_swept_collision={"point": [0.27, 0.0]}',
    }
    event = classify_report(report, "radius", "-30°", 2, "active", "active", "/tmp/raw.log")
    assert event["details"]["point_classification"] == "位于车体范围，缺少时间证据，来源未确认"


def test_event_is_persisted_as_jsonl_json_and_chinese_text(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_NO_JOURNAL", "1")
    event = {
        "timestamp": "2026-08-26T00:00:00+08:00",
        "task": "radius",
        "target": "-30°",
        "status": "REJECTED",
        "phase": "预检",
        "reason_code": "RADAR_PREFLIGHT_COLLISION",
        "reason": "雷达近点，拒绝运动",
        "nonzero_command_sent": False,
        "exit_code": 2,
        "service_before": "active",
        "service_after": "active",
        "raw_log": "/tmp/raw.log",
        "details": {},
    }
    persist_event(event)
    assert json.loads((tmp_path / "last_status.json").read_text(encoding="utf-8"))["status"] == "REJECTED"
    assert "拒绝运动" in (tmp_path / "last_status.txt").read_text(encoding="utf-8")
    assert len((tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()) == 1
    assert "是否发过非零速度：否" in render_event(event)
    assert "闭环状态：待解决" in render_event(event)


def test_issue_requires_evidence_to_close_and_reopens_on_recurrence(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_NO_JOURNAL", "1")
    failure = {
        "timestamp": "2026-08-26T00:00:00+08:00", "task": "health", "target": "lidar",
        "status": "FAILED", "phase": "预检", "reason_code": "LIDAR_IP_UNREACHABLE",
        "reason": "雷达 IP 不通", "nonzero_command_sent": False,
        "service_before": "activating", "service_after": "activating", "details": {},
    }
    persist_event(failure)
    issue_id = next(iter(load_issues()))
    assert load_issues()[issue_id]["closure_status"] == "PENDING"

    before = load_issues()
    try:
        resolve_issue(issue_id, "雷达已恢复", [], "", "", "")
    except ValueError:
        pass
    else:
        raise AssertionError("无证据的闭环必须被拒绝")
    assert load_issues() == before

    evidence_ids = [
        register_check_evidence(
            "lidar", True, ["service active", "point cloud stable"], "boot-a",
            timestamp="2026-08-26T00:00:01+08:00",
        ),
        register_check_evidence(
            "lidar", True, ["service active", "point cloud stable"], "boot-a",
            timestamp="2026-08-26T00:01:01+08:00",
        ),
    ]
    resolved = resolve_issue(
        issue_id, "雷达已恢复",
        evidence_ids,
        "lidar_boot_stream_gate_v1", "network repair #123", "90 seconds",
    )
    assert resolved["state"] == "VERIFIED"
    assert load_issues()[issue_id]["resolution_evidence"] == evidence_ids
    last_failure = json.loads((tmp_path / "last_failure.json").read_text(encoding="utf-8"))
    assert last_failure["closure"]["status"] == "RESOLVED"
    assert "闭环状态：已完善" in (tmp_path / "last_failure.txt").read_text(encoding="utf-8")

    persist_event(dict(failure, timestamp="2026-08-26T00:01:00+08:00"))
    reopened = load_issues()[issue_id]
    assert reopened["closure_status"] == "PENDING"
    assert reopened["occurrences"] == 2
    assert reopened["reopen_count"] == 1
    assert len(reopened["closure_history"]) == 1


def test_same_reason_code_different_targets_are_separate_issues(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_NO_JOURNAL", "1")
    base = {
        "timestamp": "2026-08-26T00:00:00+08:00", "task": "health",
        "status": "FAILED", "phase": "预检", "reason_code": "DEVICE_UNREACHABLE",
        "reason": "设备不可达", "nonzero_command_sent": False,
        "service_before": "failed", "service_after": "failed", "details": {},
    }
    persist_event(dict(base, target="lidar"))
    persist_event(dict(base, target="camera"))
    issues = load_issues()
    assert len(issues) == 2
    assert {issue["target"] for issue in issues.values()} == {"lidar", "camera"}


def test_unknown_policy_and_fake_evidence_are_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_NO_JOURNAL", "1")
    persist_event({
        "timestamp": "2026-08-26T00:00:00+08:00", "task": "health", "target": "lidar",
        "status": "FAILED", "phase": "预检", "reason_code": "LIDAR_DATA_UNAVAILABLE",
        "reason": "no data", "nonzero_command_sent": False,
        "service_before": "active", "service_after": "active", "details": {},
    })
    issue_id = next(iter(load_issues()))
    for policy, evidence in (("made_up", ["fake"]), ("lidar_boot_stream_gate_v1", ["fake"])):
        try:
            resolve_issue(issue_id, "fake", evidence, policy, "fake", "fake")
        except ValueError:
            pass
        else:
            raise AssertionError("伪造策略或证据必须被拒绝")
    assert load_issues()[issue_id]["state"] == "OPEN"


def test_concurrent_events_keep_all_jsonl_rows(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_NO_JOURNAL", "1")

    def write_event(index):
        persist_event({
            "timestamp": f"2026-08-26T00:00:{index:02d}+08:00", "task": "parallel",
            "target": str(index), "status": "FAILED", "phase": "test",
            "reason_code": "PARALLEL_FAILURE", "reason": str(index),
            "nonzero_command_sent": False, "service_before": "n/a",
            "service_after": "n/a", "details": {},
        })

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(write_event, range(12)))
    rows = (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 12
    assert all(json.loads(row)["reason_code"] == "PARALLEL_FAILURE" for row in rows)
    assert len(load_issues()) == 12
    assert not list(tmp_path.glob("*.tmp"))


def test_failure_stays_visible_after_selftest_pass(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("OMNIFLEET_A2_TASK_LOG_NO_JOURNAL", "1")
    failure = {
        "timestamp": "2026-08-26T00:00:00+08:00", "task": "radius", "target": "-30°",
        "status": "REJECTED", "phase": "预检", "reason": "雷达近点",
        "nonzero_command_sent": False, "service_before": "active", "service_after": "active",
        "details": {},
    }
    passed = dict(failure, task="vehicle_logging_selftest", status="PASS", reason="日志正常")
    persist_event(failure)
    persist_event(passed)
    assert json.loads((tmp_path / "last_status.json").read_text(encoding="utf-8"))["status"] == "PASS"
    sticky = json.loads((tmp_path / "last_failure.json").read_text(encoding="utf-8"))
    assert sticky["status"] == "REJECTED"
    assert sticky["reason"] == "雷达近点"


def test_wrapper_has_lock_persistent_log_timeout_cleanup_and_service_proof():
    wrapper = (Path(__file__).parents[1] / "scripts" / "run_direct_serial_radius_test").read_text(encoding="utf-8")
    for required in (
        "flock -n",
        "timeout --signal=INT",
        "tee \"${session_log}\"",
        "restore_chassis",
        "--service-after",
        "MOTION_OWNER_CONFLICT",
        "SERVICE_RESTORE_FAILED",
        "OMNIFLEET_A2_TASK_LOG_FALLBACK",
        '"${6:-unknown}"',
    ):
        assert required in wrapper


def test_vehicle_status_explains_lidar_wait_and_recent_chassis_error():
    status = runpy.run_path(Path(__file__).parents[1] / "scripts" / "vehicle_status")
    state_hint = status["state_hint"]
    lidar_hint = state_hint("雷达", "activating", "start-pre", "success", 32, "")
    chassis_hint = state_hint(
        "底盘", "inactive", "dead", "success", 0,
        "STM32 did not echo Ackermann dead-zone PWM parameters",
    )
    assert "雷达 IP" in lidar_hint
    assert "已重试 32 次" in lidar_hint
    assert "STM32 未回显死区 PWM 参数" in chassis_hint
