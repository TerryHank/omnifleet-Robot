import json
import os
import signal
import sys
import time

import pytest

from omnifleet_localization.process_supervisor import (
    ProcessRecord,
    ProcessSupervisor,
    UnsafeCommandError,
)


def test_rejects_foxglove_from_owned_process_command(tmp_path):
    supervisor = ProcessSupervisor(tmp_path)

    with pytest.raises(UnsafeCommandError):
        supervisor.start(
            ["ros2", "run", "foxglove_bridge", "foxglove_bridge"],
            transaction_id="tx-foxglove",
            mode="invalid",
        )


def test_persists_pid_pgid_command_and_transaction(tmp_path):
    supervisor = ProcessSupervisor(tmp_path)
    record = supervisor.start(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        transaction_id="tx-process",
        mode="test_mode",
    )
    try:
        persisted = json.loads((tmp_path / "backend.json").read_text(encoding="utf-8"))
        assert persisted["pid"] == record.pid
        assert persisted["pgid"] == record.pgid
        assert persisted["transaction_id"] == "tx-process"
        assert persisted["mode"] == "test_mode"
        assert persisted["command"] == [
            sys.executable,
            "-c",
            "import time; time.sleep(30)",
        ]
    finally:
        supervisor.stop(1.0)


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group semantics")
def test_stop_terminates_only_the_persisted_process_group(tmp_path):
    supervisor = ProcessSupervisor(tmp_path)
    record = supervisor.start(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        transaction_id="tx-stop",
        mode="test_mode",
    )

    supervisor.stop(1.0)

    time.sleep(0.05)
    with pytest.raises(ProcessLookupError):
        os.kill(record.pid, 0)


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group semantics")
def test_stop_waits_for_child_after_session_leader_exits(tmp_path):
    supervisor = ProcessSupervisor(tmp_path)
    script = """
import os
import signal
import time

child = os.fork()
if child == 0:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    time.sleep(30)
    os._exit(0)
signal.signal(signal.SIGINT, lambda *_: os._exit(0))
time.sleep(30)
"""
    record = supervisor.start(
        [sys.executable, "-c", script],
        transaction_id="tx-child",
        mode="test_mode",
    )
    time.sleep(0.2)
    try:
        assert supervisor.stop(1.0) is True
        assert supervisor._is_alive(record) is False
    finally:
        try:
            os.killpg(record.pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group semantics")
def test_graceful_interrupt_targets_only_the_session_leader(tmp_path, monkeypatch):
    supervisor = ProcessSupervisor(tmp_path)
    record = ProcessRecord(
        pid=101,
        pgid=202,
        command=["ros2", "launch", "package", "backend.launch.py"],
        start_time_utc="2026-07-13T00:00:00Z",
        transaction_id="tx-signal",
        mode="test_mode",
    )
    process_calls = []
    group_calls = []
    monkeypatch.setattr(os, "kill", lambda pid, sig: process_calls.append((pid, sig)))
    monkeypatch.setattr(
        os, "killpg", lambda pgid, sig: group_calls.append((pgid, sig))
    )

    supervisor._send(record, signal.SIGINT)
    supervisor._send(record, signal.SIGTERM)

    assert process_calls == [(record.pid, signal.SIGINT)]
    assert group_calls == [(record.pgid, signal.SIGTERM)]
