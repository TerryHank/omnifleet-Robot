#!/usr/bin/env python3
"""Persistent, human-readable audit events for whole-vehicle motion tests."""

import argparse
from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import threading
import time

try:
    import fcntl
except ImportError:  # Windows-only unit tests; production is Linux.
    fcntl = None


RESULT_PREFIX = "CODEX_SERIAL_RADIUS_RESULT="
FOOTPRINT = (-0.06, 0.42, -0.16, 0.16)
CLOSURE_POLICIES = {
    "chassis_service_feedback_gate_v1": {"check_ids": {"chassis"}, "min_samples": 2, "min_seconds": 30},
    "stm32_startup_handshake_gate_v1": {"check_ids": {"chassis"}, "min_samples": 2, "min_seconds": 30},
    "lidar_boot_stream_gate_v1": {"check_ids": {"lidar"}, "min_samples": 2, "min_seconds": 30},
    "foxglove_boot_gate_v1": {"check_ids": {"foxglove"}, "min_samples": 2, "min_seconds": 30},
    "issue_store_gate_v1": {"check_ids": {"issue_store"}, "min_samples": 2, "min_seconds": 30},
    "boot_environment_gate_v1": {"check_ids": {"environment"}, "min_samples": 2, "min_seconds": 30},
    "boot_selfcheck_gate_v1": {"check_ids": {"boot_summary"}, "min_samples": 2, "min_seconds": 30},
}
_THREAD_LOCK = threading.RLock()


def state_root():
    override = os.environ.get("OMNIFLEET_A2_TASK_LOG_DIR")
    if override:
        return Path(override)
    return Path("/var/log/omnifleet_a2/vehicle_tasks")


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _write_atomic(path, content):
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def _state_lock():
    root = state_root()
    root.mkdir(parents=True, exist_ok=True)
    with _THREAD_LOCK:
        with (root / ".state.lock").open("a+", encoding="utf-8") as stream:
            if fcntl is not None:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if fcntl is not None:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _issue_id(reason_code, task, target):
    scope = f"{task}\0{target}".encode("utf-8")
    return f"{reason_code}:{hashlib.sha256(scope).hexdigest()[:12]}"


def issue_id_for(reason_code, task, target):
    return _issue_id(reason_code, task, target)


def _load_issues_unlocked():
    path = state_root() / "issues.json"
    if not path.exists():
        return {}
    stored = json.loads(path.read_text(encoding="utf-8"))
    normalized = {}
    for issue in stored.values():
        issue = dict(issue)
        issue_id = issue.get("issue_id") or _issue_id(
            issue.get("reason_code", "UNKNOWN"),
            issue.get("task", "未知"),
            issue.get("target", "未知"),
        )
        issue["issue_id"] = issue_id
        if "state" not in issue:
            if issue.get("closure_status") == "RESOLVED":
                issue["state"] = "RECOVERED"
                issue["closure_status"] = "PENDING"
                issue["legacy_resolution_note"] = issue.get("resolution_note")
            else:
                issue["state"] = "OPEN"
        issue.setdefault("reopen_count", 0)
        issue.setdefault("closure_history", [])
        normalized[issue_id] = issue
    return normalized


def load_issues():
    with _state_lock():
        return _load_issues_unlocked()


def _save_issues(issues):
    root = state_root()
    root.mkdir(parents=True, exist_ok=True)
    _write_atomic(root / "issues.json", json.dumps(issues, ensure_ascii=False, indent=2) + "\n")


def write_state_files(files):
    with _state_lock():
        for path, content in files:
            path.parent.mkdir(parents=True, exist_ok=True)
            _write_atomic(path, content)


def _load_evidence_unlocked():
    path = state_root() / "evidence_index.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def register_check_evidence(check_id, passed, details, boot_id, timestamp=None):
    timestamp = timestamp or _now()
    digest_source = json.dumps(
        [boot_id, check_id, timestamp, bool(passed), details],
        ensure_ascii=False, sort_keys=True,
    ).encode("utf-8")
    evidence_id = "evidence:" + hashlib.sha256(digest_source).hexdigest()[:20]
    item = {
        "evidence_id": evidence_id,
        "timestamp": timestamp,
        "boot_id": boot_id,
        "check_id": check_id,
        "passed": bool(passed),
        "details": list(details),
    }
    with _state_lock():
        index = _load_evidence_unlocked()
        index[evidence_id] = item
        _write_atomic(
            state_root() / "evidence_index.json",
            json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        )
        with (state_root() / "evidence.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
    return evidence_id


def _validate_closure_evidence(issue, evidence_ids, policy_id):
    policy = CLOSURE_POLICIES.get(policy_id)
    if policy is None:
        raise ValueError(f"未注册的闭环策略：{policy_id}")
    index = _load_evidence_unlocked()
    try:
        evidence = [index[evidence_id] for evidence_id in evidence_ids]
    except KeyError as error:
        raise ValueError(f"证据 ID 不存在：{error.args[0]}") from error
    if len(evidence) < policy["min_samples"]:
        raise ValueError(f"证据数不足：至少需要 {policy['min_samples']} 条")
    if any(not item.get("passed") for item in evidence):
        raise ValueError("闭环证据中包含未通过的自检项")
    if any(item.get("check_id") not in policy["check_ids"] for item in evidence):
        raise ValueError("证据类型与闭环策略不匹配")
    times = sorted(datetime.fromisoformat(item["timestamp"]) for item in evidence)
    last_seen = datetime.fromisoformat(issue["last_seen"])
    if times[0] <= last_seen:
        raise ValueError("闭环证据必须晚于最后一次故障")
    elapsed = (times[-1] - times[0]).total_seconds()
    if elapsed < policy["min_seconds"]:
        raise ValueError(f"稳定时间窗不足：{elapsed:.1f}s < {policy['min_seconds']}s")
    return evidence, f"{elapsed:.1f}s（策略要求 >= {policy['min_seconds']}s）"


def render_issue(issue):
    closed = issue.get("state") == "VERIFIED"
    lines = [
        f"[{'已完善' if closed else '待解决'}] {issue.get('reason_code', 'UNKNOWN')}",
        f"问题 ID：{issue.get('issue_id', '未知')}",
        f"问题：{issue.get('summary', '未知')}",
        f"最近发现：{issue.get('last_seen', '未知')}  次数：{issue.get('occurrences', 1)}",
    ]
    if closed:
        lines.append(f"完善时间：{issue.get('resolved_at', '未知')}")
        lines.append(f"完善说明：{issue.get('resolution_note', '未填写')}")
        if issue.get("resolution_evidence"):
            lines.append("验证依据：" + "；".join(issue["resolution_evidence"]))
        lines.append(f"验证策略：{issue.get('verification_policy', '未知')}")
        lines.append(f"稳定时间窗：{issue.get('stability_window', '未知')}")
    else:
        lines.append("闭环状态：待解决")
        if issue.get("state") == "RECOVERED":
            lines.append("子状态：当前已恢复，但验证材料不完整，不得标记已完善")
            if issue.get("recovery_note"):
                lines.append(f"恢复说明：{issue['recovery_note']}")
            if issue.get("recovery_evidence"):
                lines.append("恢复证据：" + "；".join(issue["recovery_evidence"]))
        if issue.get("reopen_count"):
            lines.append(f"复发次数：{issue['reopen_count']}")
    return "\n".join(lines)


def _track_issue(event):
    if event.get("status") not in {"REJECTED", "ABORTED", "FAILED"}:
        return
    reason_code = event.get("reason_code") or "UNSPECIFIED_FAILURE"
    issue_id = _issue_id(reason_code, event.get("task", "未知"), event.get("target", "未知"))
    event["issue_id"] = issue_id
    issues = _load_issues_unlocked()
    previous = issues.get(issue_id, {})
    history = list(previous.get("closure_history", []))
    reopen_count = int(previous.get("reopen_count", 0))
    if previous.get("state") == "VERIFIED":
        history.append({
            "resolved_at": previous.get("resolved_at"),
            "resolution_note": previous.get("resolution_note"),
            "verification_policy": previous.get("verification_policy"),
            "stability_window": previous.get("stability_window"),
        })
        reopen_count += 1
    issues[issue_id] = {
        "issue_id": issue_id,
        "reason_code": reason_code,
        "state": "OPEN",
        "closure_status": "PENDING",
        "summary": event.get("reason", "未知问题"),
        "task": event.get("task", "未知"),
        "target": event.get("target", "未知"),
        "first_seen": previous.get("first_seen", event.get("timestamp", _now())),
        "last_seen": event.get("timestamp", _now()),
        "occurrences": int(previous.get("occurrences", 0)) + 1,
        "resolved_at": None,
        "resolution_note": None,
        "resolution_evidence": [],
        "verification_policy": None,
        "stability_window": None,
        "change_ref": None,
        "reopen_count": reopen_count,
        "closure_history": history,
    }
    _save_issues(issues)


def resolve_issue(issue_id, note, evidence, policy_id, change_ref, stability_window):
    if not evidence or not policy_id or not change_ref or not stability_window:
        raise ValueError("必须提供注册验证策略、修复/恢复引用和已落盘证据 ID")
    with _state_lock():
        issues = _load_issues_unlocked()
        if issue_id not in issues:
            raise KeyError(issue_id)
        issue = issues[issue_id]
        verified_evidence, measured_window = _validate_closure_evidence(issue, evidence, policy_id)
        issue.update({
            "state": "VERIFIED",
            "closure_status": "RESOLVED",
            "resolved_at": _now(),
            "resolution_note": note,
            "resolution_evidence": [item["evidence_id"] for item in verified_evidence],
            "verification_policy": policy_id,
            "change_ref": change_ref,
            "stability_window": measured_window,
            "requested_stability_window": stability_window,
        })
        _save_issues(issues)

        failure_path = state_root() / "last_failure.json"
        if failure_path.exists():
            failure = json.loads(failure_path.read_text(encoding="utf-8"))
            failure_issue_id = failure.get("issue_id") or _issue_id(
                failure.get("reason_code", "UNKNOWN"), failure.get("task", "未知"), failure.get("target", "未知"),
            )
            if failure_issue_id == issue_id:
                failure["closure"] = {
                    "status": "RESOLVED",
                    "resolved_at": issue["resolved_at"],
                    "note": note,
                    "evidence": [item["evidence_id"] for item in verified_evidence],
                }
                _write_atomic(failure_path, json.dumps(failure, ensure_ascii=False, indent=2) + "\n")
                _write_atomic(state_root() / "last_failure.txt", render_event(failure) + "\n")

        event = {
            "timestamp": issue["resolved_at"],
            "task": "issue_resolution",
            "target": issue_id,
            "status": "RESOLVED",
            "phase": "闭环验证",
            "reason_code": issue["reason_code"],
            "reason": note,
            "nonzero_command_sent": False,
            "exit_code": 0,
            "service_before": "只读验证",
            "service_after": "只读验证",
            "raw_log": None,
            "details": {"resolution_evidence": [item["evidence_id"] for item in verified_evidence]},
        }
        _persist_event_locked(event)
        return issue


def mark_issue_recovered(issue_id, note, evidence):
    if not evidence:
        raise ValueError("标记当前恢复至少需要一条证据")
    with _state_lock():
        issues = _load_issues_unlocked()
        if issue_id not in issues:
            raise KeyError(issue_id)
        issue = issues[issue_id]
        if issue.get("state") == "VERIFIED":
            return issue
        issue.update({
            "state": "RECOVERED",
            "closure_status": "PENDING",
            "recovered_at": _now(),
            "recovery_note": note,
            "recovery_evidence": list(evidence),
        })
        _save_issues(issues)
        return issue


def _point_to_footprint(point):
    x_min, x_max, y_min, y_max = FOOTPRINT
    x, y = float(point[0]), float(point[1])
    dx = max(x_min - x, 0.0, x - x_max)
    dy = max(y_min - y, 0.0, y - y_max)
    return math.hypot(dx, dy)


def _extract_collision(error, marker):
    if marker not in error:
        return None
    payload = error.split(marker, 1)[1].lstrip("= :")
    try:
        value, _ = json.JSONDecoder().raw_decode(payload)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _radar_details(report, error):
    marker = None
    phase = None
    nonzero_sent = None
    if "radar_preflight_swept_collision" in error:
        marker = "radar_preflight_swept_collision"
        phase = "预检"
        nonzero_sent = False
    elif "radar_swept_collision" in error:
        marker = "radar_swept_collision"
        phase = "运动中"
        nonzero_sent = True
    if marker is None:
        return {}, phase, nonzero_sent

    collision = _extract_collision(error, marker) or {}
    point = collision.get("point")
    details = {"collision_time_s": collision.get("time_s"), "trigger_point": point}
    if isinstance(point, list) and len(point) >= 2:
        distance = _point_to_footprint(point)
        radius = math.hypot(float(point[0]), float(point[1]))
        details["trigger_radius_m"] = round(radius, 4)
        details["point_to_static_footprint_m"] = round(distance, 4)
        collision_time = collision.get("time_s")
        at_start = collision_time is not None and float(collision_time) <= 0.001
        if at_start and distance == 0.0:
            details["point_classification"] = "疑似自车回波（未确认）"
        elif collision_time is None and distance == 0.0:
            details["point_classification"] = "位于车体范围，缺少时间证据，来源未确认"
        elif distance <= 0.10:
            details["point_classification"] = "车体近旁点，来源未确认"
        else:
            details["point_classification"] = "外部或未知点"

    radar_guard = report.get("motion", {}).get("radar_guard", {})
    if radar_guard.get("minimum_seen_m") is not None:
        details["minimum_seen_m"] = radar_guard["minimum_seen_m"]
    return details, phase, nonzero_sent


def classify_report(report, task, target, exit_code, service_before, service_after, raw_log):
    error = str(report.get("error") or report.get("motion", {}).get("cancel_reason") or "")
    details, phase, nonzero_sent = _radar_details(report, error)
    passed = bool(report.get("passed"))
    if passed:
        status = "PASS"
        reason_code = "COMPLETED"
        reason = "测试完成"
        phase = phase or "完成"
    elif "radar_preflight_swept_collision" in error:
        status = "REJECTED"
        reason_code = "RADAR_PREFLIGHT_COLLISION"
        reason = "启动前的预测路径内发现近距离雷达点，已拒绝运动"
    elif "radar_swept_collision" in error:
        status = "ABORTED"
        reason_code = "RADAR_RUNTIME_COLLISION"
        reason = "运动中预测路径出现近距离雷达点，已停车"
    elif "radar_obstacle_topic_unavailable" in error or "radar_stale" in error:
        status = "REJECTED"
        reason_code = "RADAR_UNAVAILABLE"
        reason = "雷达障碍数据不可用或已过期，已拒绝运动"
        phase = phase or "预检"
        nonzero_sent = False
    elif "insufficient_speed_feedback_frames" in error:
        status = "REJECTED"
        reason_code = "CHASSIS_FEEDBACK_MISSING"
        reason = "底盘速度反馈不足，已拒绝运动"
        phase = phase or "预检"
        nonzero_sent = False
    else:
        status = "FAILED"
        reason_code = "TEST_FAILED"
        reason = error or "测试未完成且没有返回明确原因"
        phase = phase or "未知"

    details["raw_error"] = error or None
    return {
        "timestamp": _now(),
        "task": task,
        "target": target,
        "status": status,
        "phase": phase,
        "reason_code": reason_code,
        "reason": reason,
        "nonzero_command_sent": nonzero_sent,
        "exit_code": int(exit_code),
        "service_before": service_before,
        "service_after": service_after,
        "raw_log": raw_log,
        "details": details,
    }


def render_event(event):
    labels = {
        "PASS": "通过",
        "RUNNING": "执行中",
        "REJECTED": "拒绝启动",
        "ABORTED": "已中止并停车",
        "FAILED": "失败",
        "RESOLVED": "已完善",
        "RECOVERED": "当前恢复（仍待闭环）",
    }
    lines = [
        "OmniFleet 整车任务最后状态",
        f"时间：{event.get('timestamp', '未知')}",
        f"任务：{event.get('task', '未知')}  目标：{event.get('target', '未知')}",
        f"结果：{labels.get(event.get('status'), event.get('status', '未知'))}",
        f"阶段：{event.get('phase', '未知')}",
        f"原因：{event.get('reason', '未知')}",
    ]
    details = event.get("details") or {}
    if details.get("trigger_point") is not None:
        lines.append(f"触发点：{details['trigger_point']}")
    if details.get("point_classification"):
        lines.append(f"点判断：{details['point_classification']}")
    if details.get("trigger_radius_m") is not None:
        lines.append(f"点到 base_link：{details['trigger_radius_m']:.3f} m")
    sent = event.get("nonzero_command_sent")
    lines.append("是否发过非零速度：" + ("是" if sent is True else "否" if sent is False else "无法确认"))
    lines.append(f"底盘服务：执行前 {event.get('service_before', '未知')}，执行后 {event.get('service_after', '未知')}")
    if event.get("status") in {"REJECTED", "ABORTED", "FAILED"}:
        closure = event.get("closure") or {}
        if closure.get("status") == "RESOLVED":
            lines.append("闭环状态：已完善")
            lines.append(f"完善说明：{closure.get('note', '未填写')}")
        else:
            lines.append("闭环状态：待解决")
    if event.get("raw_log"):
        lines.append(f"原始日志：{event['raw_log']}")
    return "\n".join(lines)


def _persist_event_locked(event):
    root = state_root()
    root.mkdir(parents=True, exist_ok=True)
    _track_issue(event)
    serialized = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
    with (root / "events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(serialized + "\n")
    for name, content in (
        ("last_status.json", json.dumps(event, ensure_ascii=False, indent=2) + "\n"),
        ("last_status.txt", render_event(event) + "\n"),
    ):
        _write_atomic(root / name, content)
    if event.get("status") in {"REJECTED", "ABORTED", "FAILED"}:
        for name, content in (
            ("last_failure.json", json.dumps(event, ensure_ascii=False, indent=2) + "\n"),
            ("last_failure.txt", render_event(event) + "\n"),
        ):
            _write_atomic(root / name, content)
    if os.environ.get("OMNIFLEET_A2_TASK_LOG_NO_JOURNAL") != "1":
        subprocess.run(
            ["logger", "-t", "omnifleet-task", "--", render_event(event).replace("\n", " | ")],
            check=False,
        )
    return event


def persist_event(event):
    with _state_lock():
        return _persist_event_locked(event)


def _load_result(path):
    report = None
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(RESULT_PREFIX):
            try:
                report = json.loads(line[len(RESULT_PREFIX):])
            except json.JSONDecodeError:
                report = None
    return report


def _record_from_args(args):
    details = json.loads(args.details_json) if args.details_json else {}
    sent = {"true": True, "false": False, "unknown": None}[args.nonzero_command_sent]
    return persist_event({
        "timestamp": _now(),
        "task": args.task,
        "target": args.target,
        "status": args.status,
        "phase": args.phase,
        "reason_code": args.reason_code,
        "reason": args.reason,
        "nonzero_command_sent": sent,
        "exit_code": args.exit_code,
        "service_before": args.service_before,
        "service_after": args.service_after,
        "raw_log": args.raw_log,
        "details": details,
    })


def main(argv=None):
    parser = argparse.ArgumentParser(description="记录并查看 OmniFleet 整车任务状态")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="解析直串测试输出并持久化")
    ingest.add_argument("--task", default="direct_serial_radius_test")
    ingest.add_argument("--target", required=True)
    ingest.add_argument("--exit-code", type=int, required=True)
    ingest.add_argument("--service-before", required=True)
    ingest.add_argument("--service-after", required=True)
    ingest.add_argument("--result-file", required=True)

    record = subparsers.add_parser("record", help="写入一个明确的任务事件")
    record.add_argument("--task", required=True)
    record.add_argument("--target", default="无")
    record.add_argument("--status", required=True)
    record.add_argument("--phase", required=True)
    record.add_argument("--reason-code", required=True)
    record.add_argument("--reason", required=True)
    record.add_argument("--nonzero-command-sent", choices=("true", "false", "unknown"), default="unknown")
    record.add_argument("--exit-code", type=int, default=0)
    record.add_argument("--service-before", default="未知")
    record.add_argument("--service-after", default="未知")
    record.add_argument("--raw-log", default=None)
    record.add_argument("--details-json", default="{}")

    show = subparsers.add_parser("show", help="显示最后一次整车任务结果")
    show.add_argument("--json", action="store_true")
    issues_parser = subparsers.add_parser("issues", help="显示问题闭环台账")
    issues_parser.add_argument("--json", action="store_true")
    resolve = subparsers.add_parser("resolve", help="将经验证的问题标记为已完善")
    resolve.add_argument("--issue-id", required=True)
    resolve.add_argument("--note", required=True)
    resolve.add_argument("--evidence", action="append", default=[])
    resolve.add_argument("--policy-id", required=True)
    resolve.add_argument("--change-ref", required=True)
    resolve.add_argument("--stability-window", required=True)
    args = parser.parse_args(argv)

    if args.command == "ingest":
        report = _load_result(args.result_file)
        if report is None:
            report = {"passed": False, "error": "测试没有输出可解析的结果"}
        event = classify_report(
            report, args.task, args.target, args.exit_code,
            args.service_before, args.service_after, args.result_file,
        )
        persist_event(event)
        print(render_event(event))
        return 0
    if args.command == "record":
        event = _record_from_args(args)
        print(render_event(event))
        return 0
    if args.command == "issues":
        issues = load_issues()
        if args.json:
            print(json.dumps(issues, ensure_ascii=False, indent=2))
        elif issues:
            ordered = sorted(issues.values(), key=lambda item: item.get("closure_status") == "RESOLVED")
            print("\n\n".join(render_issue(issue) for issue in ordered))
        else:
            print("暂无问题记录")
        return 0
    if args.command == "resolve":
        try:
            issue = resolve_issue(
                args.issue_id, args.note, args.evidence,
                args.policy_id, args.change_ref, args.stability_window,
            )
        except KeyError:
            print(f"问题不存在：{args.issue_id}")
            return 2
        except ValueError as error:
            print(f"拒绝闭环：{error}")
            return 2
        print(render_issue(issue))
        return 0

    path = state_root() / "last_status.json"
    if not path.exists():
        print("暂无整车任务记录")
        return 1
    event = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(event, ensure_ascii=False, indent=2) if args.json else render_event(event))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
