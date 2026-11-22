import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup = get_package_share_directory("omnifleet_bringup")
    return LaunchDescription([
        DeclareLaunchArgument("backend", default_value="mola"),
        DeclareLaunchArgument("map_id", default_value="active"),
        DeclareLaunchArgument("map_dir", default_value="/home/iecme/omnifleet_data/maps"),
        DeclareLaunchArgument("start_description", default_value="false"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(bringup, "launch", "robot.launch.py")
            ),
            launch_arguments={
                "use_sim_time": "false",
                "operation": "mapping",
                "localization_backend": LaunchConfiguration("backend"),
                "map_id": LaunchConfiguration("map_id"),
                "map_dir": LaunchConfiguration("map_dir"),
                "start_description": LaunchConfiguration("start_description"),
                "start_airy": "false",
                "use_camera": "false",
            }.items(),
        ),
    ])
