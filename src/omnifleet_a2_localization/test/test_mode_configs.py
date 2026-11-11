from pathlib import Path

import yaml


PACKAGE_ROOT = Path(__file__).parents[1]


def test_configuration_keeps_glim_and_adds_optional_mola_contract():
    modes = yaml.safe_load(
        (PACKAGE_ROOT / "config" / "modes.yaml").read_text(encoding="utf-8")
    )["modes"]
    assert set(modes) == {"glim_cuda", "cartographer_3d", "mola"}
    contract = modes["glim_cuda"]
    assert contract["map_to_odom_owner"] == "glim_ros"
    assert contract["odom_to_base_owner"] == "glim_ros"
    assert contract["odom_message_owner"] == "omnifleet_a2_glim_odom_adapter"
    assert "use_ekf" not in contract
    assert "/odom" in contract["required_outputs"]
    assert contract["navigation_capable"] is True

    mola = modes["mola"]
    assert mola["operations"] == ["mapping", "slam_navigation"]
    assert "localization" not in mola["operations"]
    assert mola["map_to_odom_owner"] == "mola_bridge_ros2"
    assert mola["odom_to_base_owner"] == "omnifleet_a2_driver"
    assert mola["odom_message_owner"] == "omnifleet_a2_driver"
    assert "/odom" in mola["required_outputs"]
    assert "/map" in mola["operation_required_outputs"]["slam_navigation"]
    assert mola["navigation_operations"] == ["slam_navigation"]

    cartographer = modes["cartographer_3d"]
    assert cartographer["operations"] == ["mapping", "slam_navigation"]
    assert cartographer["map_to_odom_owner"] == "cartographer_node"
    assert cartographer["odom_to_base_owner"] == "cartographer_node"
    assert cartographer["odom_message_owner"] == "omnifleet_a2_cartographer_odom_adapter"
    assert cartographer["required_saved_artifacts"] == ["map.pbstream"]


def test_backend_versions_are_kept_in_the_cold_switch_catalog():
    modes = yaml.safe_load(
        (PACKAGE_ROOT / "config" / "modes.yaml").read_text(encoding="utf-8")
    )["modes"]
    assert modes["glim_cuda"]["software_versions"] == {
        "omnifleet_a2_localization": "0.3.0",
        "glim": "1.2.2",
    }
    assert modes["mola"]["software_versions"]["mola_lidar_odometry"] == "3.0.0"
    assert modes["mola"]["required_saved_artifacts"] == ["local_map.mm"]
    assert "glim" not in modes["mola"]["software_versions"]

def test_glim_owns_rep105_tf_and_uses_latest_airy_points():
    config = (PACKAGE_ROOT / "config" / "glim_cuda" / "config_ros.json").read_text(
        encoding="utf-8"
    )
    assert '"acc_scale": 9.80665' in config
    assert '"base_frame_id": "base_link"' in config
    assert '"imu_topic": "/rslidar_imu_data_corrected"' in config
    assert '"points_topic": "/rslidar_points"' in config
    assert '"depth": 3' in config
    assert '"reliability": "reliable"' in config
    assert '"publish_odom_to_base_tf": true' in config
    assert '"publish_map_to_odom_tf": true' in config
    assert '"publish_imu2lidar": false' in config


def test_glim_prior_map_localization_is_explicit_and_validated():
    localization = (
        PACKAGE_ROOT / "config" / "glim_cuda" / "config_global_mapping_localization.json"
    ).read_text(encoding="utf-8")
    launch = (
        PACKAGE_ROOT / "launch" / "backends" / "glim_cuda_backend.launch.py"
    ).read_text(encoding="utf-8")
    assert '"so_name": "libprior_map_localization.so"' in localization
    assert "_validate_glim_dump" in launch
    assert '"map_path": str(prior_map_path) if localization else ""' in launch
    assert "odometry_max_pending_frames" not in launch


def test_all_remaining_yaml_files_parse():
    for path in (PACKAGE_ROOT / "config").rglob("*.yaml"):
        assert yaml.safe_load(path.read_text(encoding="utf-8")) is not None, path
