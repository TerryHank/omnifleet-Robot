"""Official Nav2 lifecycle entry shared by the three cold-start backends."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    share = get_package_share_directory("omnifleet_a2_planner")
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument("planner_mode", default_value="hybrid_astar"),
        DeclareLaunchArgument("controller_mode", default_value="rpp"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(share, "launch", "navigation.launch.py")
            ),
            launch_arguments={
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "autostart": "true",
                "params_file": os.path.join(share, "config", "nav2_glim.yaml"),
                "planner_mode": LaunchConfiguration("planner_mode"),
                "controller_mode": LaunchConfiguration("controller_mode"),
            }.items(),
        ),
    ])
