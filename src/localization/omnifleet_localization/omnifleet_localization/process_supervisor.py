import json
import os
import signal
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence


class UnsafeCommandError(ValueError):
    pass


@dataclass(frozen=True)
class ProcessRecord:
    pid: int
    pgid: int
    command: list[str]
    start_time_utc: str
    transaction_id: str
    mode: str


class ProcessSupervisor:
    def __init__(self, state_dir: Path | str):
        self.state_dir = Path(state_dir).expanduser()
        self.state_file = self.state_dir / "backend.json"
        self._process: subprocess.Popen | None = None
        self._log_stream = None

    def start(
        self,
        command: Sequence[str],
        *,
        transaction_id: str,
        mode: str,
        environment: Mapping[str, str] | None = None,
        cwd: Path | str | None = None,
        log_path: Path | str | None = None,
    ) -> ProcessRecord:
        normalized = [str(token) for token in command]
        self._validate_command(normalized)
        if self._process is not None and self._process.poll() is None:
            raise RuntimeError("已有托管后端正在运行")

        self.state_dir.mkdir(parents=True, exist_ok=True)
        stdout = None
        if log_path is not None:
            path = Path(log_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            self._log_stream = path.open("a", encoding="utf-8", buffering=1)
            stdout = self._log_stream

        process = subprocess.Popen(
            normalized,
            cwd=str(Path(cwd).expanduser()) if cwd is not None else None,
            env=dict(environment) if environment is not None else None,
            stdout=stdout,
            stderr=subprocess.STDOUT if stdout is not None else None,
            start_new_session=True,
        )
        self._process = process
        pgid = os.getpgid(process.pid) if os.name == "posix" else process.pid
        record = ProcessRecord(
            pid=process.pid,
            pgid=pgid,
            command=normalized,
            start_time_utc=datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            transaction_id=transaction_id,
            mode=mode,
        )
        self._write_record(record)
        return record

    def stop(self, timeout_sec: float) -> bool:
        if timeout_sec <= 0:
            raise ValueError("timeout_sec 必须为正数")
        record = self.load_record()
        if record is None:
            return True
        if record.pid <= 1 or record.pgid <= 1:
            raise RuntimeError("拒绝向不安全的 PID 或 PGID 发送信号")

        if not self._is_alive(record):
            self._cleanup()
            return True

        self._send(record, signal.SIGINT)
        if not self._wait(record, timeout_sec):
            self._send(record, signal.SIGTERM)
        if not self._wait(record, min(timeout_sec, 5.0)):
            self._send(record, signal.SIGKILL)
        stopped = self._wait(record, min(timeout_sec, 5.0))
        if stopped:
            self._cleanup()
        return stopped

    def load_record(self) -> ProcessRecord | None:
        if not self.state_file.is_file():
            return None
        document = json.loads(self.state_file.read_text(encoding="utf-8"))
        return ProcessRecord(**document)

    def is_running(self) -> bool:
        record = self.load_record()
        return record is not None and self._is_alive(record)

    @staticmethod
    def _validate_command(command: Sequence[str]):
        if not command:
            raise ValueError("必须提供命令")
        lowered = " ".join(command).lower()
        if "foxglove" in lowered:
            raise UnsafeCommandError("Foxglove Bridge cannot be a managed process")

    def _write_record(self, record: ProcessRecord):
        temporary = self.state_file.with_suffix(f".tmp-{os.getpid()}")
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(asdict(record), stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.state_file)

    def _is_alive(self, record: ProcessRecord) -> bool:
        if self._process is not None and self._process.pid == record.pid:
            self._process.poll()
        if os.name == "posix":
            if Path("/proc").is_dir():
                return self._linux_group_has_live_members(record.pgid)
            try:
                os.killpg(record.pgid, 0)
                return True
            except ProcessLookupError:
                return False
        if self._process is not None and self._process.pid == record.pid:
            return self._process.poll() is None
        return False

    @staticmethod
    def _linux_group_has_live_members(pgid: int) -> bool:
        for stat_path in Path("/proc").glob("[0-9]*/stat"):
            try:
                stat = stat_path.read_text(encoding="utf-8")
                fields = stat[stat.rfind(")") + 2 :].split()
                state = fields[0]
                process_group = int(fields[2])
            except (FileNotFoundError, IndexError, PermissionError, ValueError):
                continue
            if process_group == pgid and state != "Z":
                return True
        return False

    def _send(self, record: ProcessRecord, sig: signal.Signals):
        try:
            if os.name == "posix":
                if sig == signal.SIGINT:
                    os.kill(record.pid, sig)
                else:
                    os.killpg(record.pgid, sig)
            elif self._process is not None:
                if sig in {signal.SIGINT, signal.SIGTERM}:
                    self._process.terminate()
                else:
                    self._process.kill()
        except ProcessLookupError:
            return

    def _wait(self, record: ProcessRecord, timeout_sec: float) -> bool:
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            if not self._is_alive(record):
                return True
            time.sleep(0.05)
        return not self._is_alive(record)

    def _cleanup(self):
        self.state_file.unlink(missing_ok=True)
        if self._log_stream is not None:
            self._log_stream.close()
            self._log_stream = None
        self._process = None
