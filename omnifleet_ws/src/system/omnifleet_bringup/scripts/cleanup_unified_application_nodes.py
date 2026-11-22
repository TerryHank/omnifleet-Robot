#!/usr/bin/env python3
"""Remove stale application-layer MOLA/Nav2 processes before unified bringup."""

import os
from pathlib import Path
import signal
import time


PATTERNS = (
    "mola_nav2_unified.launch.py",
    "mola_no_wheel.launch.py",
    "mola_localization.launch.py",
    "navigation.launch.py",
    "nav2_direct.launch.py",
    "nav2_readiness_gate.py",
    "/mola-cli",
    "airy_imu_adapter_node",
    "base_link_rslidar_tf.py",
    "controller_server --ros-args",
    "planner_server --ros-args",
    "behavior_server --ros-args",
    "bt_navigator --ros-args",
    "lifecycle_manager_navigation",
)


def process_table():
    result = {}
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        try:
            cmd = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
            stat = (entry / "stat").read_text().split()
            ppid = int(stat[3])
        except (FileNotFoundError, PermissionError, ValueError, IndexError):
            continue
        result[pid] = (ppid, cmd)
    return result


def is_stale(pid, ppid, cmd):
    if pid in {os.getpid(), os.getppid()}:
        return False
    if not cmd:
        return False
    # Inspect argv positions: remap arguments can contain every node name.
    try:
        argv = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
        argv = [os.fsdecode(v) for v in argv if v]
    except OSError:
        return False
    executable = Path(argv[0]).name if argv else ""
    applications = {"nav_cloud_deskew", "mola-cli", "controller_server", "planner_server", "behavior_server", "bt_navigator", "lifecycle_manager"}
    if executable in applications:
        return True
    if executable.startswith("python") and len(argv) > 1:
        executable = Path(argv[1]).name
        if executable in {"nav2_readiness_gate.py", "airy_imu_adapter_node", "base_link_rslidar_tf.py", "lidar_velocity.py", "nav_cloud_deskew.py"}:
            return True
        if executable == "ros2" and len(argv) > 4 and argv[2] == "launch":
            return Path(argv[4]).name in {"mola_nav2_unified.launch.py", "mola_no_wheel.launch.py", "nav2_direct.launch.py", "mola_localization.launch.py", "navigation.launch.py"}
    return False



def signal_pids(pids, sig):
    for pid in pids:
        try:
            os.kill(pid, sig)
        except (ProcessLookupError, PermissionError):
            pass


def main():
    table = process_table()
    stale = sorted(pid for pid, (ppid, cmd) in table.items() if is_stale(pid, ppid, cmd))
    if stale:
        print("[unified-cleanup] stale application PIDs: " + " ".join(map(str, stale)), flush=True)
        signal_pids(stale, signal.SIGINT)
        time.sleep(1.5)
        remaining = [pid for pid in stale if Path(f"/proc/{pid}").exists()]
        signal_pids(remaining, signal.SIGTERM)
        time.sleep(1.5)
        remaining = [pid for pid in remaining if Path(f"/proc/{pid}").exists()]
        signal_pids(remaining, signal.SIGKILL)
        time.sleep(0.5)
    else:
        print("[unified-cleanup] no stale application processes", flush=True)
    print("[unified-cleanup] complete; base services were not targeted", flush=True)


if __name__ == "__main__":
    main()
