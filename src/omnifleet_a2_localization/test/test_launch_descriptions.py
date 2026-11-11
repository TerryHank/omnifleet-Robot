import ast
from pathlib import Path


PACKAGE_ROOT = Path(__file__).parents[1]
BACKEND = PACKAGE_ROOT / "launch" / "backends" / "glim_cuda_backend.launch.py"
CONFIG_ROS = PACKAGE_ROOT / "config" / "glim_cuda" / "config_ros.json"


def test_public_and_internal_launches_are_valid_python():
    for path in (
        BACKEND,
        PACKAGE_ROOT / "launch" / "glim_cuda.launch.py",
    ):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        assert any(
            isinstance(node, ast.FunctionDef) and node.name == "generate_launch_description"
            for node in tree.body
        )


def test_glim_backend_uses_native_tf_standard_odom_and_nav2_owned_obstacle_cloud():
    source = BACKEND.read_text(encoding="utf-8")
    config = CONFIG_ROS.read_text(encoding="utf-8")
    assert 'executable="glim_odom_adapter"' in source
    assert '"output_topic": "/odom"' in source
    assert '"base_frame": "base_link"' in source
    assert 'name="omnifleet_a2_lidar_obstacle_filter"' not in source
    assert '"output_topic": "/omnifleet_a2/lidar/obstacles"' not in source
    assert '"points_topic": "/rslidar_points"' in config
    assert 'executable="airy_imu_adapter_node"' in source
    assert '"output_topic": "/rslidar_imu_data_corrected"' in source
    assert '"imu_topic": "/rslidar_imu_data_corrected"' in config
    assert 'executable="glim_map_projector"' in source
    assert 'executable="map_odom_corrector"' not in source
    assert "/odometry/filtered" not in source
    assert "rtabmap" not in source.lower()


def test_native_airy_obstacle_cloud_has_no_neighbor_or_multiframe_filtering():
    source = BACKEND.read_text(encoding="utf-8")
    cmake = (PACKAGE_ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "cloud_filter_cpp" not in source
    assert "cloud_filter_cpp" not in cmake
    for name in (
        "neighbor_min_points",
        "temporal_window_frames",
        "temporal_required_frames",
        "VoxelNeighborTemporalFilter",
    ):
        assert name not in source


def test_removed_filter_parameters_are_not_exposed_by_glim():
    public_launch = (
        PACKAGE_ROOT / "launch" / "glim_cuda.launch.py"
    ).read_text(encoding="utf-8")
    for removed in (
        "obstacle_z_min",
        "obstacle_z_max",
        "lidar_voxel_size",
        "lidar_max_rate",
    ):
        assert removed not in public_launch
        assert removed not in BACKEND.read_text(encoding="utf-8")


def test_map_projector_uses_the_native_map_plane():
    source = BACKEND.read_text(encoding="utf-8")
    assert '"ground_z_offset_from_base": 0.0' in source


def test_live_mapping_projects_only_glim_global_map_snapshots():
    source = BACKEND.read_text(encoding="utf-8")
    assert '"input_topic": "/glim_ros/map"' in source
    assert '"resolution": 0.08' in source


def test_projector_launch_contains_no_temporal_evidence_policy():
    source = BACKEND.read_text(encoding="utf-8")
    for removed in (
        "free_confirmation_scans",
        "free_candidate_ttl",
        "quality_hit_required",
        "strong_hit_required",
        "persistent_hit_required",
        "hit_spatial_tolerance_cells",
    ):
        assert removed not in source


def test_prior_map_localization_does_not_reproject_live_aligned_scans():
    source = BACKEND.read_text(encoding="utf-8")

    assert "from launch.conditions import IfCondition" in source
    assert 'package="nav2_map_server"' in source
    assert 'name="prior_map_server"' in source
    assert '"yaml_filename": str(saved_map_yaml)' in source
    assert 'name="lifecycle_manager_prior_map"' in source
    assert 'condition=IfCondition("false" if localization else "true")' in source


def test_glim_initial_pose_defaults_remain_map_specific():
    public_launch = (
        PACKAGE_ROOT / "launch" / "glim_cuda.launch.py"
    ).read_text(encoding="utf-8")
    backend = BACKEND.read_text(encoding="utf-8")
    expected = "0.0"
    assert f'"initial_pose_z": "{expected}"' in public_launch
    assert f'DeclareLaunchArgument("initial_pose_z", default_value="{expected}")' in backend


def test_glim_prefers_its_cuda_overlay_without_mvs_libusb_pollution():
    source = BACKEND.read_text(encoding="utf-8")
    assert 'f"{GLIM_ROOT}/deps/lib"' in source
    assert '"/usr/local/cuda-12.6/lib64"' in source
    assert 'not path.startswith("/opt/MVS")' in source


def test_mapping_backend_does_not_inject_a_command_lock():
    source = BACKEND.read_text(encoding="utf-8")
    assert 'executable="manual_safety_release"' not in source
    assert 'LaunchConfiguration("manual_control_unlock")' not in source
    assert 'package="nav2_collision_monitor"' not in source
    assert 'name="lifecycle_manager_mapping_safety"' not in source


def test_public_launch_has_no_manual_unlock_gate():
    public_launch = (PACKAGE_ROOT / "launch" / "glim_cuda.launch.py").read_text(
        encoding="utf-8"
    )
    assert "manual_control_unlock" not in public_launch
