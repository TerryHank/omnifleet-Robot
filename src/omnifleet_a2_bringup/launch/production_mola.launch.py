import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    localization = get_package_share_directory("omnifleet_a2_localization")
    return LaunchDescription([
        DeclareLaunchArgument("map_id", default_value="active"),
        DeclareLaunchArgument("map_dir", default_value="/var/lib/omnifleet_a2/maps"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(localization, "launch", "mola_backend.launch.py")
            ),
            launch_arguments={
                "use_sim_time": "false",
                "operation": "mapping",
                "map_id": LaunchConfiguration("map_id"),
                "map_dir": LaunchConfiguration("map_dir"),
            }.items(),
        ),
    ])
