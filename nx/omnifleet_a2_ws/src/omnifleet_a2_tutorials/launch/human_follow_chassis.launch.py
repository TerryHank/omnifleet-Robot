"""Follow a detected person with the Ackermann chassis.

This program is mutually exclusive with the GLIM/Nav2 navigation program.
When motion is explicitly enabled, vision publishes ``/cmd_vel`` directly;
Nav2 must be stopped because the two programs are mutually exclusive.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    start_camera = LaunchConfiguration("start_camera")
    enable_motion = LaunchConfiguration("enable_motion")

    vision = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("omnifleet_a2_vision"), "launch", "course_function.launch.py"]
            )
        ),
        launch_arguments={
            "course_function": "04_02_human_object_follow",
            "start_camera": start_camera,
            "enable_motion": enable_motion,
            "use_gui": LaunchConfiguration("use_gui"),
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "start_camera",
                default_value="true",
                description="Start the RGB-D camera as part of this manually selected program.",
            ),
            DeclareLaunchArgument(
                "enable_motion",
                default_value="false",
                description="Enable chassis following only after a lifted-wheel check.",
            ),
            DeclareLaunchArgument(
                "use_gui",
                default_value="true",
                description="Show the person detection and distance debug window.",
            ),
            LogInfo(
                condition=UnlessCondition(enable_motion),
                msg="Human following is observing only; chassis motion is disabled.",
            ),
            LogInfo(
                condition=IfCondition(enable_motion),
                msg="Human following motion is enabled. Nav2 must be stopped first.",
            ),
            vision,
        ]
    )
