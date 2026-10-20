from pathlib import Path

import yaml


PACKAGE_ROOT = Path(__file__).parents[1]


def test_configuration_keeps_production_and_test_backends():
    modes = yaml.safe_load(
        (PACKAGE_ROOT / "config" / "modes.yaml").read_text(encoding="utf-8")
    )["modes"]
    assert set(modes) == {"cartographer_3d", "mola"}

    mola = modes["mola"]
    assert mola["operations"] == ["mapping", "slam_navigation"]
    assert "localization" not in mola["operations"]
    assert mola["map_to_odom_owner"] == "mola_bridge_ros2"
    assert mola["odom_to_base_owner"] == "omnifleet_t2_driver"
    assert mola["odom_message_owner"] == "omnifleet_t2_driver"
    assert "/odom" in mola["required_outputs"]
    assert "/map" in mola["operation_required_outputs"]["slam_navigation"]
    assert mola["navigation_operations"] == ["slam_navigation"]

    cartographer = modes["cartographer_3d"]
    assert cartographer["operations"] == ["mapping", "slam_navigation"]
    assert cartographer["map_to_odom_owner"] == "cartographer_node"
    assert cartographer["odom_to_base_owner"] == "cartographer_node"
    assert cartographer["odom_message_owner"] == "omnifleet_t2_cartographer_odom_adapter"
    assert cartographer["required_saved_artifacts"] == ["map.pbstream"]


def test_backend_versions_are_kept_in_the_cold_switch_catalog():
    modes = yaml.safe_load(
        (PACKAGE_ROOT / "config" / "modes.yaml").read_text(encoding="utf-8")
    )["modes"]
    assert modes["mola"]["software_versions"]["mola_lidar_odometry"] == "3.2.0"
    assert modes["mola"]["required_saved_artifacts"] == ["local_map.mm"]


def test_all_remaining_yaml_files_parse():
    for path in (PACKAGE_ROOT / "config").rglob("*.yaml"):
        assert yaml.safe_load(path.read_text(encoding="utf-8")) is not None, path
