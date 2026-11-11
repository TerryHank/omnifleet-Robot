import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Start the GLIM backend and its navigation-facing adapters only."""
    share = get_package_share_directory("omnifleet_a2_localization")
    argument_defaults = {
        # GLIM operating mode and persistent map location.
        "operation": "mapping",
        "map_id": "active",
        "map_dir": "/var/lib/omnifleet_a2/maps",
        "map_path": "",
        # Prior-map localization seed in the GLIM map frame.
        "initial_pose_x": "0.0",
        "initial_pose_y": "0.0",
        # GLIM的初始位姿属于雷达/IMU；该高度使map.z=0落在轮胎接地点。
        "initial_pose_z": "0.0",
        "initial_pose_yaw": "0.0",
        # LiDAR range used by the current map-projection path.
        "lidar_range_min": "0.18",
        "lidar_range_max": "6.0",
        # The MVS camera branch is optional and never blocks core GLIM startup.
        "use_camera": "false",
        "use_sim_time": "false",
    }
    forwarded = {
        name: LaunchConfiguration(name) for name in argument_defaults
    }
    backend = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(share, "launch", "glim_cuda_backend.launch.py")
        ),
        launch_arguments=forwarded.items(),
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument(name, default_value=value)
            for name, value in argument_defaults.items()
        ]
        + [backend]
    )
