#!/usr/bin/env python3
"""通过 trtexec 导出和基准测试 TensorRT 引擎。"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


def resolve_trtexec(executable: str = "trtexec") -> str:
    """解析 trtexec 路径，找不到时给出明确错误。"""

    candidate = Path(executable).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    resolved = shutil.which(executable)
    if not resolved:
        raise FileNotFoundError(f"找不到 trtexec：{executable}")
    return resolved


def build_export_command(
    onnx_path: str,
    engine_path: str,
    executable: str = "trtexec",
    fp16: bool = False,
    workspace_mb: int = 2048,
    input_shapes: str = "",
) -> list[str]:
    """构造 ONNX 到 TensorRT 引擎的参数列表，不使用 shell 拼接。"""

    onnx = Path(onnx_path).expanduser().resolve()
    if not onnx.is_file():
        raise FileNotFoundError(f"找不到 ONNX 模型：{onnx}")
    engine = Path(engine_path).expanduser().resolve()
    command = [
        resolve_trtexec(executable),
        f"--onnx={onnx}",
        f"--saveEngine={engine}",
        # TensorRT 10 的 memPoolSize 在省略单位时按 MiB 解释；附加 MiB 会被部分版本误读。
        f"--memPoolSize=workspace:{int(workspace_mb)}",
    ]
    if fp16:
        command.append("--fp16")
    if input_shapes.strip():
        command.append(f"--shapes={input_shapes.strip()}")
    return command


def build_benchmark_command(
    engine_path: str,
    executable: str = "trtexec",
    warmup_ms: int = 200,
    duration_seconds: int = 10,
    iterations: int = 0,
) -> list[str]:
    """构造已导出引擎的基准测试参数列表。"""

    engine = Path(engine_path).expanduser().resolve()
    if not engine.is_file():
        raise FileNotFoundError(f"找不到 TensorRT 引擎：{engine}")
    command = [
        resolve_trtexec(executable),
        f"--loadEngine={engine}",
        f"--warmUp={int(warmup_ms)}",
        f"--duration={int(duration_seconds)}",
    ]
    if iterations > 0:
        command.append(f"--iterations={int(iterations)}")
    return command


def parse_trtexec_metrics(output: str) -> dict:
    """从 trtexec 文本中提取吞吐量和常见毫秒指标。"""

    metrics: dict[str, float] = {}
    throughput = re.search(r"Throughput:\s*([0-9.]+)\s*qps", output, re.IGNORECASE)
    if throughput:
        metrics["throughput_qps"] = float(throughput.group(1))
    patterns = {
        "latency_mean_ms": r"Latency:.*?mean\s*=\s*([0-9.]+)\s*ms",
        "latency_median_ms": r"Latency:.*?median\s*=\s*([0-9.]+)\s*ms",
        "gpu_compute_mean_ms": r"GPU Compute Time:.*?mean\s*=\s*([0-9.]+)\s*ms",
        "enqueue_mean_ms": r"Enqueue Time:.*?mean\s*=\s*([0-9.]+)\s*ms",
    }
    for name, pattern in patterns.items():
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            metrics[name] = float(match.group(1))
    return metrics


def run_trtexec(command: Sequence[str], timeout_seconds: int = 1800) -> dict:
    """安全执行 trtexec，并把命令、耗时、日志和指标整理成报告。"""

    if not command:
        raise ValueError("trtexec 命令不能为空")
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            timeout=int(timeout_seconds),
            shell=False,
        )
        elapsed = time.perf_counter() - start
        combined = f"{completed.stdout}\n{completed.stderr}"
        return {
            "started_at_utc": started_at,
            "command": list(command),
            "success": completed.returncode == 0,
            "return_code": completed.returncode,
            "elapsed_seconds": round(elapsed, 3),
            "metrics": parse_trtexec_metrics(combined),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as error:
        elapsed = time.perf_counter() - start
        return {
            "started_at_utc": started_at,
            "command": list(command),
            "success": False,
            "return_code": None,
            "elapsed_seconds": round(elapsed, 3),
            "metrics": {},
            "stdout": error.stdout or "",
            "stderr": f"执行超时：{error}",
        }


def write_report(report: dict, report_path: str) -> Path:
    """将导出或基准测试报告写为 UTF-8 JSON。"""

    path = Path(report_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_engine(
    onnx_path: str,
    engine_path: str,
    report_path: str,
    executable: str = "trtexec",
    fp16: bool = False,
    workspace_mb: int = 2048,
    input_shapes: str = "",
    timeout_seconds: int = 1800,
) -> dict:
    """导出引擎并生成 JSON 报告。"""

    command = build_export_command(
        onnx_path, engine_path, executable, fp16, workspace_mb, input_shapes
    )
    report = run_trtexec(command, timeout_seconds)
    report["operation"] = "export"
    report["onnx_path"] = str(Path(onnx_path).expanduser().resolve())
    report["engine_path"] = str(Path(engine_path).expanduser().resolve())
    write_report(report, report_path)
    return report


def benchmark_engine(
    engine_path: str,
    report_path: str,
    executable: str = "trtexec",
    warmup_ms: int = 200,
    duration_seconds: int = 10,
    iterations: int = 0,
    timeout_seconds: int = 1800,
) -> dict:
    """基准测试引擎并生成 JSON 报告。"""

    command = build_benchmark_command(
        engine_path, executable, warmup_ms, duration_seconds, iterations
    )
    report = run_trtexec(command, timeout_seconds)
    report["operation"] = "benchmark"
    report["engine_path"] = str(Path(engine_path).expanduser().resolve())
    write_report(report, report_path)
    return report


def parse_arguments() -> argparse.Namespace:
    """读取导出或基准测试命令行参数。"""

    parser = argparse.ArgumentParser(description="TensorRT 引擎导出与基准测试")
    parser.add_argument("--trtexec", default="/usr/src/tensorrt/bin/trtexec")
    parser.add_argument("--timeout", type=int, default=1800)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    export_parser = subparsers.add_parser("export", help="从 ONNX 导出引擎")
    export_parser.add_argument("--onnx", required=True)
    export_parser.add_argument("--engine", required=True)
    export_parser.add_argument("--report", required=True)
    export_parser.add_argument("--fp16", action="store_true")
    export_parser.add_argument("--workspace", type=int, default=2048)
    export_parser.add_argument("--shapes", default="")
    benchmark_parser = subparsers.add_parser("benchmark", help="测试现有引擎")
    benchmark_parser.add_argument("--engine", required=True)
    benchmark_parser.add_argument("--report", required=True)
    benchmark_parser.add_argument("--warmup", type=int, default=200)
    benchmark_parser.add_argument("--duration", type=int, default=10)
    benchmark_parser.add_argument("--iterations", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    """执行命令行请求并以退出码反映执行结果。"""

    arguments = parse_arguments()
    if arguments.operation == "export":
        report = export_engine(
            arguments.onnx,
            arguments.engine,
            arguments.report,
            arguments.trtexec,
            arguments.fp16,
            arguments.workspace,
            arguments.shapes,
            arguments.timeout,
        )
    else:
        report = benchmark_engine(
            arguments.engine,
            arguments.report,
            arguments.trtexec,
            arguments.warmup,
            arguments.duration,
            arguments.iterations,
            arguments.timeout,
        )
    if not report["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
