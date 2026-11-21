"""Real-robot Nav2-only entry; start after MOLA publishes map -> odom."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    planner = get_package_share_directory("omnifleet_planner")
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(planner, "launch", "navigation.launch.py")
            ),
            launch_arguments={
                "use_sim_time": "false",
                "autostart": "true",
            }.items(),
        ),
    ])
