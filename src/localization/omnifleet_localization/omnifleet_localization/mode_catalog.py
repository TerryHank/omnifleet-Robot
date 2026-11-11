import shlex
import re
from pathlib import Path

import yaml


class ModeCatalog:
    REQUIRED_KEYS = {
        "launch_package",
        "launch_file",
        "operations",
        "required_topics",
        "required_outputs",
        "map_to_odom_owner",
        "odom_to_base_owner",
        "navigation_capable",
        "shutdown_timeout_sec",
    }

    def __init__(self, path: Path | str):
        self.path = Path(path).expanduser()
        document = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        if document.get("schema_version") != 1:
            raise ValueError("不支持的模式配置版本")
        self.modes = document.get("modes", {})
        if not self.modes:
            raise ValueError("模式目录为空")
        for mode, contract in self.modes.items():
            missing = self.REQUIRED_KEYS - set(contract)
            if missing:
                raise ValueError(f"{mode} 缺少字段：{sorted(missing)}")
            if "foxglove" in str(contract).lower():
                raise ValueError(f"{mode} 非法占用了 Foxglove")

    def require(self, mode: str, operation: str) -> dict:
        if mode not in self.modes:
            raise ValueError(f"未知的 SLAM 模式：{mode}")
        contract = self.modes[mode]
        if operation not in contract["operations"]:
            raise ValueError(f"{mode} 不支持操作 {operation}")
        return contract

    def launch_command(
        self,
        mode: str,
        operation: str,
        map_id: str,
        *,
        map_root: str,
        main_setup: str,
        launch_arguments: dict[str, object] | None = None,
    ) -> list[str]:
        contract = self.require(mode, operation)
        commands = [
            "set -eo pipefail",
            "source /opt/ros/humble/setup.bash",
            f"source {shlex.quote(main_setup)}",
        ]
        overlay = contract.get("environment_setup")
        if overlay:
            commands.append(f"source {overlay}")
        commands.append("set -u")
        launch = " ".join(
            [
                "exec ros2 launch",
                shlex.quote(contract["launch_package"]),
                shlex.quote(contract["launch_file"]),
                f"operation:={shlex.quote(operation)}",
                f"map_id:={shlex.quote(map_id)}",
                f"map_dir:={shlex.quote(map_root)}",
            ]
        )
        for name, value in (launch_arguments or {}).items():
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
                raise ValueError(f"不安全的启动参数名称：{name}")
            if value is None or str(value) == "":
                continue
            launch += f" {name}:={shlex.quote(str(value))}"
        commands.append(launch)
        shell = "; ".join(commands)
        if "foxglove" in shell.lower():
            raise ValueError("后端命令中不能包含 Foxglove")
        return ["/bin/bash", "-lc", shell]
