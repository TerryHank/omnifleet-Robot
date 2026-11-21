from pathlib import Path
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    description = Path(get_package_share_directory("omnifleet_description"))
    robot_description = (description / "urdf" / "omnifleet_t2.urdf").read_text(
        encoding="utf-8"
    )
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="omnifleet_t2_robot_state_publisher",
            output="screen",
            parameters=[{
                "robot_description": robot_description,
                "frame_prefix": "",
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }],
        ),
    ])
