import os
import re
from pathlib import Path

import yaml


class MapCompatibilityError(RuntimeError):
    pass


class MapRegistry:
    REQUIRED_FIELDS = {
        "schema_version",
        "map_id",
        "backend",
        "operation",
        "created_at_utc",
        "ros_distro",
        "software_versions",
        "frames",
        "sensor_config_sha256",
        "extrinsics_sha256",
        "artifacts",
        "navigation_compatible",
        "validation_report",
    }
    VALID_BACKENDS = {"glim_cuda"}
    SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    SHA256 = re.compile(r"^[0-9a-f]{64}$")

    def __init__(self, root: Path | str):
        self.root = Path(root).expanduser()

    def write(self, manifest: dict) -> Path:
        self.validate(manifest)
        directory = self.root / manifest["backend"] / manifest["map_id"]
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / "manifest.yaml"
        temporary = destination.with_suffix(f".tmp-{os.getpid()}")
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            yaml.safe_dump(manifest, stream, sort_keys=False, allow_unicode=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        if os.name == "posix":
            descriptor = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return destination

    def load(self, backend: str, map_id: str) -> dict:
        self._validate_identifier("backend", backend)
        self._validate_identifier("map_id", map_id)
        path = self.root / backend / map_id / "manifest.yaml"
        if not path.is_file():
            raise FileNotFoundError(path)
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.validate(manifest)
        if manifest["backend"] != backend or manifest["map_id"] != map_id:
            raise ValueError("清单路径与地图标识不匹配")
        return manifest

    def assert_compatible(
        self,
        backend: str,
        map_id: str,
        *,
        sensor_config_sha256: str,
        extrinsics_sha256: str,
    ) -> dict:
        manifest = self.load(backend, map_id)
        if manifest["sensor_config_sha256"] != sensor_config_sha256:
            raise MapCompatibilityError("sensor configuration SHA256 mismatch")
        if manifest["extrinsics_sha256"] != extrinsics_sha256:
            raise MapCompatibilityError("extrinsics SHA256 mismatch")
        return manifest

    @classmethod
    def validate(cls, manifest: dict):
        if not isinstance(manifest, dict):
            raise ValueError("清单内容必须是映射结构")
        missing = cls.REQUIRED_FIELDS - set(manifest)
        if missing:
            raise ValueError(f"清单缺少字段：{sorted(missing)}")
        if manifest["schema_version"] != 1:
            raise ValueError("不支持的清单 schema_version")
        cls._validate_identifier("map_id", manifest["map_id"])
        cls._validate_identifier("backend", manifest["backend"])
        if manifest["backend"] not in cls.VALID_BACKENDS:
            raise ValueError("未知后端")
        if manifest["operation"] not in {"mapping", "localization"}:
            raise ValueError("清单 operation 必须为 mapping 或 localization")
        for field in (
            "created_at_utc",
            "ros_distro",
            "validation_report",
        ):
            cls._require_non_placeholder(field, manifest[field])
        for field in ("sensor_config_sha256", "extrinsics_sha256"):
            if not isinstance(manifest[field], str) or not cls.SHA256.fullmatch(
                manifest[field]
            ):
                raise ValueError(f"{field} 必须是小写 SHA256")
        expected_frames = {
            "map": "map",
            "odom": "odom",
            "base": "base_link",
            "lidar": "rslidar",
        }
        if manifest["frames"] != expected_frames:
            raise ValueError("清单中的坐标系不符合规范")
        if not isinstance(manifest["software_versions"], dict):
            raise ValueError("software_versions 必须是映射结构")
        if not isinstance(manifest["artifacts"], list):
            raise ValueError("artifacts 必须是列表")
        for artifact in manifest["artifacts"]:
            cls._require_non_placeholder("artifact", artifact)
            path = Path(artifact)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("artifacts 必须使用地图目录内的相对路径")
        if not isinstance(manifest["navigation_compatible"], bool):
            raise ValueError("navigation_compatible 必须是布尔值")

    @classmethod
    def _validate_identifier(cls, field: str, value: str):
        if not isinstance(value, str) or not cls.SAFE_ID.fullmatch(value):
            raise ValueError(f"{field} 包含不安全字符或占位符")

    @staticmethod
    def _require_non_placeholder(field: str, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"必须提供 {field}")
        if "<" in value or ">" in value:
            raise ValueError(f"{field} 包含占位符")
