from pathlib import Path

import yaml


PACKAGE_ROOT = Path(__file__).parents[1]
WORKSPACE_ROOT = PACKAGE_ROOT.parents[1]
BRINGUP_ROOT = WORKSPACE_ROOT / "system" / "omnifleet_bringup"


def test_cartographer_3d_is_a_navigation_backend():
    modes = yaml.safe_load(
        (PACKAGE_ROOT / "config" / "modes.yaml").read_text(encoding="utf-8")
    )["modes"]
    contract = modes["cartographer_3d"]
    assert contract["operations"] == ["mapping", "slam_navigation"]
    assert contract["map_to_odom_owner"] == "cartographer_node"
    assert contract["odom_to_base_owner"] == "cartographer_node"
    assert contract["odom_message_owner"] == "omnifleet_t2_cartographer_odom_adapter"
    assert contract["navigation_operations"] == ["slam_navigation"]
    assert contract["required_saved_artifacts"] == ["map.pbstream"]


def test_cartographer_3d_launch_uses_airy_imu_wheel_odom_and_one_cloud():
    launch = (
        PACKAGE_ROOT / "launch" / "backends" / "cartographer_3d_backend.launch.py"
    ).read_text(encoding="utf-8")
    config = (
        PACKAGE_ROOT / "config" / "cartographer_3d" / "omnifleet_3d.lua"
    ).read_text(encoding="utf-8")

    assert 'package="cartographer_ros"' in launch
    assert 'executable="cartographer_node"' in launch
    assert '("points2", "/rslidar_points")' in launch
    assert '("imu", "/omnifleet_t2/cartographer/imu")' in launch
    assert '("odom", "/omnifleet_t2/chassis/wheel_odometry")' in launch
    assert launch.count('executable="airy_imu_adapter_node"') == 2
    assert '"input_topic": "/rslidar_imu_data"' in launch
    assert '"output_topic": "/rslidar_imu_data_corrected"' in launch
    assert '"input_topic": "/rslidar_imu_data_corrected"' in launch
    assert '"output_frame": "base_link"' in launch
    assert '"linear_acceleration_scale": 9.80665' in launch
    assert '"angular_velocity_bias": [' in launch
    assert '"drop_non_increasing_timestamps": True' in launch
    assert 'executable="cartographer_odom_adapter"' in launch
    assert 'executable="cartographer_occupancy_grid_node"' in launch
    assert 'arguments=["-resolution", "0.08", "-publish_period_sec", "1.0"]' in launch
    assert 'executable="cloud_filter_cpp"' not in launch

    assert 'tracking_frame = "base_link"' in config
    assert 'published_frame = "base_link"' in config
    assert "provide_odom_frame = true" in config
    assert "publish_frame_projected_to_2d = true" in config
    assert "use_odometry = true" in config
    assert "num_point_clouds = 1" in config
    assert "MAP_BUILDER.use_trajectory_builder_3d = true" in config
    assert "TRAJECTORY_BUILDER_3D.num_accumulated_range_data = 1" in config


def test_production_launch_routes_cartographer_without_a_manager():
    cmake = (PACKAGE_ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    package = (PACKAGE_ROOT / "package.xml").read_text(encoding="utf-8")
    imu_source = (PACKAGE_ROOT / "src" / "airy_imu_adapter_node.cpp").read_text(
        encoding="utf-8"
    )
    robot_launch = (BRINGUP_ROOT / "launch" / "robot.launch.py").read_text(
        encoding="utf-8"
    )
    production = (BRINGUP_ROOT / "launch" / "production.launch.py").read_text(
        encoding="utf-8"
    )

    assert "scripts/cartographer_odom_adapter" in cmake
    assert "cartographer_ros_msgs" in package
    assert 'declare_parameter<double>("linear_acceleration_scale", 1.0)' in imu_source
    assert 'declare_parameter<bool>("drop_non_increasing_timestamps", false)' in imu_source
    assert '"angular_velocity_bias", {0.0, 0.0, 0.0}' in imu_source
    assert "angular_velocity[0] - angular_velocity_bias_[0]" in imu_source
    assert "stamp_ns <= last_stamp_ns_" in imu_source
    assert '"localization_backend", default_value="mola"' in robot_launch
    assert 'DeclareLaunchArgument("backend", default_value="mola")' in production
    assert '"localization_backend": LaunchConfiguration("backend")' in production
    assert '"cartographer_3d": "cartographer_3d_backend.launch.py"' in robot_launch
    assert "slam_manager" not in robot_launch
