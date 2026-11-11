from pathlib import Path

import pytest
import yaml

from omnifleet_behaviors.storage import MapMismatchError, MissionStore


POSES = [
    {
        "position": {"x": 1.0, "y": 2.0, "z": 0.0},
        "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
    }
]


def test_storage_is_versioned_atomic_and_increments_revision(tmp_path: Path):
    store = MissionStore(tmp_path)
    first = store.save(
        "route-a", map_id="map-a", map_sha256="a" * 64, frame="map", poses=POSES
    )
    second = store.save(
        "route-a", map_id="map-a", map_sha256="a" * 64, frame="map", poses=POSES
    )

    assert first["schema_version"] == 1
    assert first["revision"] == 1
    assert second["revision"] == 2
    assert not list(tmp_path.glob("*.tmp-*"))
    on_disk = yaml.safe_load((tmp_path / "route-a.yaml").read_text())
    assert on_disk == second


def test_load_rejects_map_id_or_hash_mismatch(tmp_path: Path):
    store = MissionStore(tmp_path)
    store.save(
        "home", map_id="map-a", map_sha256="b" * 64, frame="map", poses=POSES
    )

    with pytest.raises(MapMismatchError, match="map_id"):
        store.load("home", map_id="map-b", map_sha256="b" * 64)
    with pytest.raises(MapMismatchError, match="SHA256"):
        store.load("home", map_id="map-a", map_sha256="c" * 64)


@pytest.mark.parametrize("mission_id", ["../escape", "/absolute", "<route>", ""])
def test_unsafe_mission_ids_are_rejected(tmp_path: Path, mission_id: str):
    store = MissionStore(tmp_path)
    with pytest.raises(ValueError):
        store.save(
            mission_id,
            map_id="map-a",
            map_sha256="d" * 64,
            frame="map",
            poses=POSES,
        )

