#!/usr/bin/env python3
"""调用 Ultralytics 训练接口的通用课程脚本。"""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile
from typing import Any

import yaml


def validate_training_inputs(model_path: str, data_path: str) -> tuple[Path, Path]:
    """检查模型和数据集配置均由调用者显式提供且确实存在。"""

    model = Path(model_path).expanduser().resolve()
    data = Path(data_path).expanduser().resolve()
    if not model.is_file():
        raise FileNotFoundError(f"找不到初始模型：{model}")
    if not data.is_file():
        raise FileNotFoundError(f"找不到数据集配置：{data}")
    return model, data


def build_training_arguments(
    data_path: str,
    project: str,
    name: str,
    epochs: int = 50,
    image_size: int = 640,
    device: str = "",
    batch: int = 16,
    resume: bool = False,
    amp: bool = False,
) -> dict[str, Any]:
    """生成可测试、无硬编码工程路径的训练参数。"""

    arguments: dict[str, Any] = {
        "data": str(Path(data_path).expanduser().resolve()),
        "project": str(Path(project).expanduser().resolve()),
        "name": str(name),
        "epochs": int(epochs),
        "imgsz": int(image_size),
        "batch": int(batch),
        "resume": bool(resume),
        "amp": bool(amp),
    }
    if device.strip():
        arguments["device"] = device.strip()
    return arguments


def write_resolved_dataset_yaml(data_path: Path, directory: Path) -> Path:
    """把数据集根目录解析成绝对路径，避免受当前工作目录影响。"""

    payload = yaml.safe_load(data_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("数据集 YAML 根节点必须是对象")
    raw_root = Path(str(payload.get("path", "."))).expanduser()
    root = raw_root if raw_root.is_absolute() else (data_path.parent / raw_root)
    payload["path"] = str(root.resolve())
    resolved = directory / "resolved_data.yaml"
    resolved.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return resolved


def train_model(
    model_path: str,
    data_path: str,
    project: str,
    name: str,
    epochs: int = 50,
    image_size: int = 640,
    device: str = "",
    batch: int = 16,
    resume: bool = False,
    amp: bool = False,
):
    """加载用户指定模型并调用训练接口，返回原始训练结果。"""

    model, data = validate_training_inputs(model_path, data_path)
    try:
        from ultralytics import YOLO
    except ImportError as error:
        raise RuntimeError("未安装 ultralytics，请先安装完整训练环境") from error
    with tempfile.TemporaryDirectory(prefix="omnifleet_training_") as temporary:
        resolved_data = write_resolved_dataset_yaml(data, Path(temporary))
        arguments = build_training_arguments(
            str(resolved_data), project, name, epochs, image_size, device, batch, resume, amp
        )
        return YOLO(str(model)).train(**arguments)


def parse_arguments() -> argparse.Namespace:
    """读取命令行训练参数。"""

    parser = argparse.ArgumentParser(description="训练视觉课程模型")
    parser.add_argument("--model", required=True, help="初始模型文件")
    parser.add_argument("--data", required=True, help="数据集 YAML 文件")
    parser.add_argument("--project", required=True, help="训练输出目录")
    parser.add_argument("--name", required=True, help="本次实验名称")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="")
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--amp", action="store_true",
        help="显式启用 AMP；默认关闭，避免联网下载额外自检模型。",
    )
    return parser.parse_args()


def main() -> None:
    """执行一次命令行训练任务。"""

    arguments = parse_arguments()
    train_model(
        arguments.model,
        arguments.data,
        arguments.project,
        arguments.name,
        arguments.epochs,
        arguments.imgsz,
        arguments.device,
        arguments.batch,
        arguments.resume,
        arguments.amp,
    )


if __name__ == "__main__":
    main()
