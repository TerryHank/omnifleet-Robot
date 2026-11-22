import os
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml


class MapMismatchError(RuntimeError):
    pass


class MissionStore:
    SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    SHA256 = re.compile(r"^[0-9a-f]{64}$")

    def __init__(self, root: Path | str):
        self.root = Path(root).expanduser()

    def save(
        self,
        mission_id: str,
        *,
        map_id: str,
        map_sha256: str,
        frame: str,
        poses: list,
        loop: bool = False,
    ) -> dict:
        self._validate_identity(mission_id, map_id, map_sha256, frame)
        self._validate_poses(poses)
        self.root.mkdir(parents=True, exist_ok=True)
        destination = self.root / f"{mission_id}.yaml"
        revision = 1
        if destination.is_file():
            existing = yaml.safe_load(destination.read_text(encoding="utf-8"))
            revision = int(existing.get("revision", 0)) + 1
        document = {
            "schema_version": 1,
            "revision": revision,
            "mission_id": mission_id,
            "map_id": map_id,
            "map_sha256": map_sha256,
            "frame": frame,
            "poses": poses,
            "loop": bool(loop),
            "timestamp": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        }
        temporary = destination.with_suffix(f".tmp-{os.getpid()}")
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            yaml.safe_dump(document, stream, sort_keys=False, allow_unicode=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        if os.name == "posix":
            descriptor = os.open(self.root, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return document

    def load(self, mission_id: str, *, map_id: str, map_sha256: str) -> dict:
        self._validate_identifier("mission_id", mission_id)
        self._validate_identifier("map_id", map_id)
        self._validate_sha(map_sha256)
        path = self.root / f"{mission_id}.yaml"
        if not path.is_file():
            raise FileNotFoundError(path)
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.validate(document)
        if document["map_id"] != map_id:
            raise MapMismatchError("mission map_id does not match the active map")
        if document["map_sha256"] != map_sha256:
            raise MapMismatchError("mission map SHA256 does not match the active map")
        return document

    @classmethod
    def validate(cls, document: dict):
        required = {
            "schema_version",
            "revision",
            "mission_id",
            "map_id",
            "map_sha256",
            "frame",
            "poses",
            "timestamp",
            "loop",
        }
        if not isinstance(document, dict) or required - set(document):
            raise ValueError("任务文档不完整")
        if document["schema_version"] != 1 or int(document["revision"]) < 1:
            raise ValueError("不支持的任务文档结构或版本")
        cls._validate_identity(
            document["mission_id"],
            document["map_id"],
            document["map_sha256"],
            document["frame"],
        )
        cls._validate_poses(document["poses"])
        if not isinstance(document["loop"], bool):
            raise ValueError("任务 loop 字段必须是布尔值")
        if not isinstance(document["timestamp"], str) or not document["timestamp"]:
            raise ValueError("任务必须包含时间戳")

    @classmethod
    def _validate_identity(cls, mission_id, map_id, map_sha256, frame):
        cls._validate_identifier("mission_id", mission_id)
        cls._validate_identifier("map_id", map_id)
        cls._validate_sha(map_sha256)
        if frame != "map":
            raise ValueError("任务坐标系必须为 map")

    @classmethod
    def _validate_identifier(cls, field, value):
        if not isinstance(value, str) or not cls.SAFE_ID.fullmatch(value):
            raise ValueError(f"{field} 不安全")

    @classmethod
    def _validate_sha(cls, value):
        if not isinstance(value, str) or not cls.SHA256.fullmatch(value):
            raise ValueError("map_sha256 必须是小写 SHA256")

    @staticmethod
    def _validate_poses(poses):
        if not isinstance(poses, list) or not poses:
            raise ValueError("任务至少需要一个位姿")
        for pose in poses:
            if not isinstance(pose, dict):
                raise ValueError("任务位姿必须是映射结构")
            position = pose.get("position")
            orientation = pose.get("orientation")
            if not isinstance(position, dict) or not isinstance(orientation, dict):
                raise ValueError("任务位姿缺少 position 或 orientation")
            if set(position) != {"x", "y", "z"}:
                raise ValueError("任务位置字段无效")
            if set(orientation) != {"x", "y", "z", "w"}:
                raise ValueError("任务姿态字段无效")
            values = list(position.values()) + list(orientation.values())
            if not all(isinstance(value, (int, float)) for value in values):
                raise ValueError("任务位姿值必须是数字")
