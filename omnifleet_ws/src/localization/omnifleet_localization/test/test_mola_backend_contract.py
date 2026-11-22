import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1]
BACKEND = PACKAGE_ROOT / "launch" / "backends" / "mola_backend.launch.py"
CMAKE = PACKAGE_ROOT / "CMakeLists.txt"
PIPELINE = PACKAGE_ROOT / "config" / "mola" / "lidar3d-icp-nav2.yaml"


def test_mola_backend_is_valid_python():
    ast.parse(BACKEND.read_text(encoding="utf-8"), filename=str(BACKEND))


def test_mola_backend_is_optional_and_pins_the_non_rknn_pipeline():
    source = BACKEND.read_text(encoding="utf-8")

    assert 'get_package_share_directory("mola_lidar_odometry")' in source
    assert '"lidar3d-icp-nav2.yaml"' in source
    assert "lidar3d-gicp.yaml" not in source
    assert 'operation not in {"mapping", "slam_navigation"}' in source
    assert '"lidar_topic_name": "/rslidar_points"' in source
    assert '"imu_topic_name": "/rslidar_imu_data_corrected"' in source
    assert '"use_imu_for_lio": "True"' in source
    assert '"enforce_planar_motion": "True"' not in source
    assert '"mola_deskew_method": "MotionCompensationMethod::IMU"' in source
    assert '"mola_lo_reference_frame": "map"' in source
    assert 'executable="airy_imu_adapter_node"' in source
    assert '"input_topic": "/rslidar_imu_data"' in source
    assert '"output_topic": "/rslidar_imu_data_corrected"' in source
    assert '"output_frame": "rslidar"' in source
    assert '"linear_acceleration_scale": 9.80665' in source


def test_mola_native_map_output_is_scoped_to_a_safe_session_directory():
    source = BACKEND.read_text(encoding="utf-8")

    assert 're.fullmatch(r"[A-Za-z0-9._-]+", map_id)' in source
    assert 'map_id in {".", ".."}' in source
    assert '/ "mola"' in source
    assert 'session_dir = (backend_root / map_id).resolve()' in source
    assert 'if session_dir.parent != backend_root:' in source
    assert 'session_dir.mkdir(parents=True, exist_ok=True)' in source
    assert 'return session_dir / "local_map.mm"' in source
    assert 'SetEnvironmentVariable("MOLA_SAVE_MM", str(native_map_output))' in source


def test_mola_backend_has_single_rep105_tf_owners():
    source = BACKEND.read_text(encoding="utf-8")

    assert 'SetEnvironmentVariable("MOLA_LOCALIZATION_PUBLISH_TF", "true")' in source
    assert 'SetEnvironmentVariable("MOLA_VERBOSITY_MOLA_LO", "ERROR")' in source
    assert 'SetEnvironmentVariable("MOLA_OPTIMIZE_TWIST", "false")' in source
    assert 'SetEnvironmentVariable("MOLA_ICP_CLOUD_DECIMATION", "0.80")' in source
    assert 'SetEnvironmentVariable("MOLA_MAP_CLOUD_DECIMATION", "0.30")' in source
    assert 'SetEnvironmentVariable("MOLA_LOCAL_VOXELMAP_RESOLUTION", "0.60")' in source
    assert 'SetEnvironmentVariable("MOLA_PUBLISH_LOCAL_MAP_UPDATES_EVERY_N", "2")' in source
    assert 'SetEnvironmentVariable("MOLA_ROS2_PUBLISH_MAPS_PERIOD", "0.5")' in source
    assert 'SetEnvironmentVariable("MOLA_TF_FOOTPRINT_LINK", "")' in source
    assert '"publish_localization_following_rep105": "True"' in source
    assert '"forward_ros_tf_odom_to_mola": "False"' in source
    assert '"use_state_estimator": "False"' in source
    assert '"mola_bridge_odometry_frame": "odom"' in source
    assert 'executable="static_transform_publisher"' not in source
    assert 'executable="mola_odom_adapter"' not in source


def test_mola_backend_uses_the_official_mola_grid_output():
    source = BACKEND.read_text(encoding="utf-8")
    pipeline = PIPELINE.read_text(encoding="utf-8")

    assert 'executable="cloud_filter_cpp"' not in source
    assert 'src="/lidar_odometry/nav_grid_gridmap"' in source
    assert 'dst="/map"' in source
    assert "mp2p_icp_filters::FilterVoxelSlice" in pipeline
    assert "class: mrpt::maps::CVoxelMap" in pipeline
    assert 'target_layer: "nav_voxelmap"' in pipeline
    assert 'output_layer: "nav_grid"' in pipeline


def test_mola_backend_does_not_reintroduce_removed_control_or_pose_layers():
    source = BACKEND.read_text(encoding="utf-8").lower()

    for forbidden in (
        "ekf",
        "cmd_vel",
        "velocity_smoother",
        "collision_monitor",
        "foxglove",
        "twist_mux",
    ):
        assert forbidden not in source


def test_mola_adapter_is_removed_without_a_required_package_dependency():
    cmake = CMAKE.read_text(encoding="utf-8")
    package_xml = (PACKAGE_ROOT / "package.xml").read_text(encoding="utf-8")

    assert "scripts/mola_odom_adapter" not in cmake
    assert not (PACKAGE_ROOT / "scripts" / "mola_odom_adapter").exists()
    assert not (
        PACKAGE_ROOT / "omnifleet_localization" / "mola_odom_adapter.py"
    ).exists()
    assert "test_mola_backend_contract.py" in cmake
    assert "mola_lidar_odometry" not in package_xml
