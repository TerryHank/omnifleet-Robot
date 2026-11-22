import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    localization = get_package_share_directory("omnifleet_a2_localization")
    bringup = get_package_share_directory("omnifleet_a2_bringup")
    common = {"use_sim_time": LaunchConfiguration("use_sim_time")}
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument("map_id", default_value="active"),
        DeclareLaunchArgument("map_dir", default_value="/var/lib/omnifleet_a2/maps"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(localization, "launch", "cartographer_3d_backend.launch.py")
            ),
            launch_arguments={
                **common,
                "operation": "slam_navigation",
                "map_id": LaunchConfiguration("map_id"),
                "map_dir": LaunchConfiguration("map_dir"),
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(bringup, "launch", "production_common_navigation.launch.py")
            ),
            launch_arguments=common.items(),
        ),
    ])
