#!/usr/bin/env python3
"""Read-only boot health check with persistent reports and issue tracking."""

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import re
import signal
import uuid

from omnifleet_a2_bringup.vehicle_task_log import (
    issue_id_for,
    load_issues,
    mark_issue_recovered,
    persist_event,
    register_check_evidence,
    render_issue,
    state_root,
    write_state_files,
)


SERVICES = (
    "omnifleet-a2-chassis.service",
    "omnifleet-a2-airy.service",
    "omnifleet-a2-foxglove-bridge.service",
)


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _current_boot_id():
    path = Path("/proc/sys/kernel/random/boot_id")
    return path.read_text(encoding="utf-8").strip() if path.exists() else "unknown"


def claim_boot_run(boot_id):
    latest = state_root() / "last_boot_report.json"
    if latest.exists():
        try:
            if json.loads(latest.read_text(encoding="utf-8")).get("boot_id") == boot_id:
                return False
        except (OSError, json.JSONDecodeError):
            pass
    run_root = state_root() / "boot_runs"
    run_root.mkdir(parents=True, exist_ok=True)
    marker = run_root / f"{boot_id}.json"
    try:
        descriptor = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump({"boot_id": boot_id, "started_at": _now()}, stream, ensure_ascii=False)
        stream.write("\n")
    return True


def _run(command, timeout=5.0):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=os.name != "nt",
    )
    try:
        output, error = process.communicate(timeout=timeout)
        return process.returncode, output.strip(), error.strip()
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        try:
            process.communicate(timeout=1.0)
        except subprocess.TimeoutExpired:
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.communicate()
        return 124, "", "timeout"


def _service_state(unit):
    code, output, error = _run([
        "systemctl", "show", unit, "--no-pager",
        "--property=ActiveState", "--property=SubState",
        "--property=NRestarts", "--property=ActiveEnterTimestamp",
    ])
    values = {}
    for line in output.splitlines():
        key, _, value = line.partition("=")
        values[key] = value
    values["query_ok"] = code == 0
    values["query_error"] = error
    return values


def _services_ready():
    return all(_service_state(unit).get("ActiveState") == "active" for unit in SERVICES)


def wait_for_services(seconds):
    deadline = time.monotonic() + max(0.0, seconds)
    while not _services_ready() and time.monotonic() < deadline:
        time.sleep(min(5.0, max(0.1, deadline - time.monotonic())))


def _nodes():
    code, output, error = _run(["ros2", "node", "list"], timeout=5.0)
    return code, set(output.splitlines()), error


def _topic_sample(topic, field):
    code, output, error = _run(
        ["ros2", "topic", "echo", "--once", topic, "--field", field],
        timeout=5.0,
    )
    return code == 0 and bool(output), error or output


def _topic_stamps(topic, count=2):
    stamps = []
    for _ in range(count):
        code, output, error = _run(
            ["ros2", "topic", "echo", "--once", topic, "--field", "header.stamp"],
            timeout=5.0,
        )
        seconds = re.search(r"^sec:\s*(\d+)\s*$", output, re.MULTILINE)
        nanoseconds = re.search(r"^nanosec:\s*(\d+)\s*$", output, re.MULTILINE)
        if code != 0 or not seconds or not nanoseconds:
            return False, [], error or output or "missing stamp"
        stamps.append(int(seconds.group(1)) + int(nanoseconds.group(1)) / 1_000_000_000)
    now = time.time()
    monotonic = all(later > earlier for earlier, later in zip(stamps, stamps[1:]))
    fresh = all(-2.0 <= now - stamp <= 5.0 for stamp in stamps)
    return monotonic and fresh, stamps, f"monotonic={monotonic} fresh={fresh} max_age={max(now - stamp for stamp in stamps):.3f}s"


def _result(check_id, label, passed, reason_code, task, target, reason, evidence, recovery_candidates):
    return {
        "id": check_id,
        "label": label,
        "passed": bool(passed),
        "reason_code": reason_code,
        "task": task,
        "target": target,
        "reason": reason,
        "evidence": list(evidence),
        "recovery_candidates": list(recovery_candidates),
    }


def check_chassis():
    state = _service_state("omnifleet-a2-chassis.service")
    evidence = [
        f"service={state.get('ActiveState', 'unknown')}/{state.get('SubState', 'unknown')}",
        f"restarts={state.get('NRestarts', 'unknown')}",
        f"serial_link={Path('/dev/myserial').resolve() if Path('/dev/myserial').exists() else 'missing'}",
    ]
    if state.get("ActiveState") != "active":
        return _result(
            "chassis", "底盘服务/反馈链", False,
            "CHASSIS_SERVICE_NOT_ACTIVE", "service_health_review", "chassis",
            "开机自检：底盘服务不是 active",
            evidence, [],
        )
    code, nodes, error = _nodes()
    expected = {
        "/omnifleet_a2_driver",
        "/robot_state_publisher",
    }
    missing = sorted(expected - nodes)
    sampled, sample_error = _topic_sample("/odom", "twist.twist")
    topology_code, topology, _ = _run(["ros2", "topic", "info", "/cmd_vel", "-v"])
    publisher_match = re.search(r"Publisher count:\s*(\d+)", topology)
    publisher_count = int(publisher_match.group(1)) if publisher_match else -1
    publisher_section = topology.partition("Subscription count:")[0]
    publisher_nodes = set(re.findall(r"Node name:\s*([^\s]+)", publisher_section))
    publisher_ok = publisher_count in (0, 1)
    if code != 0 or missing or not sampled or not publisher_ok:
        evidence.extend([
            "missing_nodes=" + (",".join(missing) if missing else "none"),
            "feedback_sample=" + ("ok" if sampled else (sample_error or error or "missing")),
            "command_publisher=" + (
                "none" if publisher_count == 0
                else ",".join(sorted(publisher_nodes)) if publisher_ok and publisher_nodes
                else f"unexpected_count_or_owner:{publisher_count}"
            ),
        ])
        return _result(
            "chassis", "底盘服务/反馈链", False,
            "CHASSIS_FEEDBACK_MISSING", "boot_selfcheck", "chassis_feedback",
            "开机自检：底盘节点或里程计反馈不完整",
            evidence, [],
        )
    evidence.extend([
        "required_nodes=present",
        "odom=sampled",
        "command_publisher=" + (
            "none" if publisher_count == 0 else ",".join(sorted(publisher_nodes))
        ),
    ])
    return _result(
        "chassis", "底盘服务/反馈链", True,
        "CHASSIS_FEEDBACK_MISSING", "boot_selfcheck", "chassis_feedback",
        "底盘服务、节点和里程计反馈正常",
        evidence,
        [
            ("CHASSIS_SERVICE_NOT_ACTIVE", "service_health_review", "chassis"),
            ("CHASSIS_FEEDBACK_MISSING", "boot_selfcheck", "chassis_feedback"),
        ],
    )


def check_lidar():
    state = _service_state("omnifleet-a2-airy.service")
    evidence = [
        f"service={state.get('ActiveState', 'unknown')}/{state.get('SubState', 'unknown')}",
        f"restarts={state.get('NRestarts', 'unknown')}",
    ]
    if state.get("ActiveState") != "active":
        return _result(
            "lidar", "Airy 服务/数据", False,
            "AIRY_DRIVER_NOT_ACTIVE", "service_health_review", "robosense_airy",
            "开机自检：Airy 驱动服务未进入 active",
            evidence, [],
        )
    lidar_ok, lidar_stamps, lidar_error = _topic_stamps("/rslidar_points")
    imu_ok, imu_stamps, imu_error = _topic_stamps("/rslidar_imu_data")
    evidence.extend([
        "lidar_stamps=" + (str(lidar_stamps) if lidar_ok else (lidar_error or "missing")),
        "imu_stamps=" + (str(imu_stamps) if imu_ok else (imu_error or "missing")),
    ])
    if not (lidar_ok and imu_ok):
        return _result(
            "lidar", "Airy 服务/数据", False,
            "AIRY_DATA_UNAVAILABLE", "boot_selfcheck", "airy_stream",
            "开机自检：Airy 驱动已启动，但点云或 IMU 数据不可用",
            evidence, [],
        )
    return _result(
        "lidar", "Airy 服务/数据", True,
        "AIRY_DATA_UNAVAILABLE", "boot_selfcheck", "airy_stream",
        "Airy 服务、点云和 IMU 数据正常",
        evidence,
        [
            ("AIRY_DRIVER_NOT_ACTIVE", "service_health_review", "robosense_airy"),
            ("AIRY_DATA_UNAVAILABLE", "boot_selfcheck", "airy_stream"),
        ],
    )


def check_foxglove():
    state = _service_state("omnifleet-a2-foxglove-bridge.service")
    code, nodes, error = _nodes()
    expected_node = "/omnifleet_a2_foxglove_bridge"
    passed = state.get("ActiveState") == "active" and code == 0 and expected_node in nodes
    evidence = [
        f"service={state.get('ActiveState', 'unknown')}/{state.get('SubState', 'unknown')}",
        "foxglove_node=" + ("present" if expected_node in nodes else (error or "missing")),
    ]
    return _result(
        "foxglove", "Foxglove 服务/节点", passed,
        "FOXGLOVE_UNAVAILABLE", "boot_selfcheck", "foxglove",
        "Foxglove 服务与 ROS 节点正常" if passed else "开机自检：Foxglove 服务或 ROS 节点不可用",
        evidence,
        [("FOXGLOVE_UNAVAILABLE", "boot_selfcheck", "foxglove")] if passed else [],
    )


def check_issue_store():
    try:
        issues = load_issues()
        return _result(
            "issue_store", "日志/闭环台账", True,
            "ISSUE_STORE_UNAVAILABLE", "boot_selfcheck", "issue_store",
            "日志和问题闭环台账可读写",
            [f"issue_count={len(issues)}", f"state_root={state_root()}"],
            [("ISSUE_STORE_UNAVAILABLE", "boot_selfcheck", "issue_store")],
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return _result(
            "issue_store", "日志/闭环台账", False,
            "ISSUE_STORE_UNAVAILABLE", "boot_selfcheck", "issue_store",
            f"开机自检：日志或问题台账不可用：{error}",
            [], [],
        )


def check_environment():
    expected_prefix = "/home/iecme/omnifleet_a2_ws/install"
    prefixes = os.environ.get("AMENT_PREFIX_PATH", "").split(":")
    prefix_present = any(
        prefix == expected_prefix or prefix.startswith(expected_prefix + "/")
        for prefix in prefixes
    )
    passed = (
        os.environ.get("ROS_DISTRO") == "humble"
        and os.environ.get("ROS_DOMAIN_ID") == "42"
        and prefix_present
    )
    evidence = [
        f"ROS_DISTRO={os.environ.get('ROS_DISTRO', 'missing')}",
        f"ROS_DOMAIN_ID={os.environ.get('ROS_DOMAIN_ID', 'missing')}",
        f"robot_overlay={'present' if prefix_present else 'missing'}",
    ]
    return _result(
        "environment", "ROS 环境/工作空间", passed,
        "BOOT_ENVIRONMENT_INVALID", "boot_selfcheck", "ros_environment",
        "ROS Humble、Domain 42 和生产 overlay 正常" if passed else "开机自检：ROS 环境或生产 overlay 不正确",
        evidence,
        [("BOOT_ENVIRONMENT_INVALID", "boot_selfcheck", "ros_environment")] if passed else [],
    )
def apply_results(results, boot_id):
    for check in results:
        if not check["passed"]:
            persist_event({
                "timestamp": _now(),
                "task": check["task"],
                "target": check["target"],
                "status": "FAILED",
                "phase": "开机自检",
                "reason_code": check["reason_code"],
                "reason": check["reason"],
                "nonzero_command_sent": False,
                "exit_code": 1,
                "service_before": "开机自检",
                "service_after": "未改变",
                "raw_log": None,
                "details": {
                    "boot_id": boot_id,
                    "evidence": check["evidence"],
                    "evidence_id": check.get("evidence_id"),
                },
            })
            continue
        for reason_code, task, target in check["recovery_candidates"]:
            issue_id = issue_id_for(reason_code, task, target)
            issue = load_issues().get(issue_id)
            if issue and issue.get("state") != "VERIFIED":
                mark_issue_recovered(
                    issue_id,
                    "开机自检已观测到当前恢复，但仍需闭环策略验证",
                    [check["evidence_id"]],
                )


def render_report(report):
    lines = [
        "OmniFleet 开机自检报告",
        f"时间：{report['timestamp']}",
        f"主机：{report['hostname']}  boot_id：{report['boot_id']}",
        f"run_id：{report.get('run_id', '未知')}  耗时：{report.get('duration_seconds', '未知')}s",
        f"自检代码 SHA-256：{report.get('code_sha256', '未知')}",
        f"结果：{'通过' if report['passed'] else '失败'}",
        "是否发过非零速度：否",
        "",
        "=== 自检项 ===",
    ]
    for check in report["checks"]:
        lines.append(f"[{'PASS' if check['passed'] else 'FAIL'}] {check['label']}：{check['reason']}")
        if check["evidence"]:
            lines.append("  证据：" + "；".join(check["evidence"]))
        if not check["passed"]:
            lines.append("  闭环状态：待解决")
    lines.extend(["", "=== 问题闭环 ==="])
    issues = report["issues"]
    if issues:
        ordered = sorted(issues.values(), key=lambda item: item.get("state") == "VERIFIED")
        lines.append("\n\n".join(render_issue(issue) for issue in ordered))
    else:
        lines.append("暂无问题记录")
    return "\n".join(lines) + "\n"


def persist_report(report):
    root = state_root() / "boot_reports"
    root.mkdir(parents=True, exist_ok=True)
    stamp = report["timestamp"].replace(":", "-")
    stem = f"{stamp}_{report['boot_id'][:8]}_{report['run_id'][:8]}"
    json_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    text = render_report(report)
    files = (
        (root / f"{stem}.json", json_text),
        (root / f"{stem}.txt", text),
        (state_root() / "last_boot_report.json", json_text),
        (state_root() / "last_boot_report.txt", text),
    )
    write_state_files(files)
    return root / f"{stem}.txt"


def run_selfcheck(wait_seconds, boot_id=None):
    started = time.monotonic()
    wait_for_services(wait_seconds)
    boot_id = boot_id or _current_boot_id()
    run_id = uuid.uuid4().hex
    results = [check_environment(), check_chassis(), check_lidar(), check_foxglove(), check_issue_store()]
    evidence_time = _now()
    for check in results:
        check["evidence_id"] = register_check_evidence(
            check["id"], check["passed"], check["evidence"], boot_id, evidence_time,
        )
    apply_results(results, boot_id)
    passed = all(check["passed"] for check in results)
    summary_evidence_id = register_check_evidence(
        "boot_summary", passed,
        [f"{check['id']}={'PASS' if check['passed'] else 'FAIL'}" for check in results],
        boot_id, _now(),
    )
    summary_issue_id = issue_id_for("BOOT_SELFCHECK_FAILED", "boot_selfcheck", "whole_vehicle")
    if passed and summary_issue_id in load_issues() and load_issues()[summary_issue_id].get("state") != "VERIFIED":
        mark_issue_recovered(
            summary_issue_id,
            "本次开机自检全部通过，但历史失败仍需稳定窗口验证",
            [summary_evidence_id],
        )
    report = {
        "timestamp": _now(),
        "hostname": socket.gethostname(),
        "boot_id": boot_id,
        "run_id": run_id,
        "passed": passed,
        "nonzero_command_sent": False,
        "duration_seconds": round(time.monotonic() - started, 3),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "checks": results,
        "issues": load_issues(),
        "summary_evidence_id": summary_evidence_id,
    }
    report_path = persist_report(report)
    persist_event({
        "timestamp": report["timestamp"],
        "task": "boot_selfcheck",
        "target": "whole_vehicle",
        "status": "PASS" if passed else "FAILED",
        "phase": "开机自检",
        "reason_code": "BOOT_SELFCHECK_COMPLETED" if passed else "BOOT_SELFCHECK_FAILED",
        "reason": "开机自检全部通过" if passed else "开机自检发现待解决问题",
        "nonzero_command_sent": False,
        "exit_code": 0 if passed else 2,
        "service_before": "只读自检",
        "service_after": "未改变",
        "raw_log": str(report_path),
        "details": {"boot_id": boot_id, "failed_checks": [c["id"] for c in results if not c["passed"]]},
    })
    report["issues"] = load_issues()
    persist_report(report)
    subprocess.run(
        [
            "logger", "-t", "omnifleet-boot-selfcheck", "--",
            f"结果={'PASS' if passed else 'FAIL'} 报告={report_path} 待解决={len([c for c in results if not c['passed']])}",
        ],
        check=False,
    )
    return report, report_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="OmniFleet 开机只读自检")
    parser.add_argument("--wait-seconds", type=float, default=90.0)
    args = parser.parse_args(argv)
    boot_id = _current_boot_id()
    if not claim_boot_run(boot_id):
        print(f"本次开机已完成自检，跳过重复执行：boot_id={boot_id}")
        return 0
    try:
        report, path = run_selfcheck(args.wait_seconds, boot_id)
    except Exception as error:
        report = {
            "timestamp": _now(), "hostname": socket.gethostname(), "boot_id": boot_id,
            "run_id": uuid.uuid4().hex,
            "passed": False, "nonzero_command_sent": False, "duration_seconds": None,
            "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "checks": [{
                "id": "selfcheck_runtime", "label": "自检程序", "passed": False,
                "reason": f"自检未完整完成：{error}", "evidence": [],
            }],
            "issues": {},
        }
        try:
            path = persist_report(report)
        except Exception:
            raise
        print(render_report(report), end="")
        print(f"报告文件：{path}")
        return 1
    print(render_report(report), end="")
    print(f"报告文件：{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
