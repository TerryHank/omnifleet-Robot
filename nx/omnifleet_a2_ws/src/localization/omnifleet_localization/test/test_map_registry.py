import pytest

from omnifleet_localization.map_registry import MapCompatibilityError, MapRegistry


def _manifest(map_id="20260711T010203Z-lab"):
    return {
        "schema_version": 1,
        "map_id": map_id,
        "backend": "glim_cuda",
        "operation": "mapping",
        "created_at_utc": "2026-07-11T01:02:03Z",
        "ros_distro": "humble",
        "software_versions": {"glim": "1.2.2"},
        "frames": {
            "map": "map",
            "odom": "odom",
            "base": "base_link",
            "lidar": "rslidar",
        },
        "sensor_config_sha256": "a" * 64,
        "extrinsics_sha256": "b" * 64,
        "artifacts": ["dump/graph.txt"],
        "navigation_compatible": True,
        "validation_report": "validation/report.md",
    }


def test_manifest_is_written_atomically_under_glim_map_id(tmp_path):
    registry = MapRegistry(tmp_path)
    path = registry.write(_manifest())
    assert path == tmp_path / "glim_cuda" / "20260711T010203Z-lab" / "manifest.yaml"
    assert registry.load("glim_cuda", "20260711T010203Z-lab") == _manifest()
    assert not list(path.parent.glob("*.tmp-*"))


def test_manifest_rejects_placeholders_and_changed_sensor_hash(tmp_path):
    registry = MapRegistry(tmp_path)
    with pytest.raises(ValueError):
        registry.write(_manifest("<map_id>"))
    registry.write(_manifest())
    with pytest.raises(MapCompatibilityError):
        registry.assert_compatible(
            "glim_cuda",
            "20260711T010203Z-lab",
            sensor_config_sha256="c" * 64,
            extrinsics_sha256="b" * 64,
        )
