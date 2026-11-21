"""Follow a mouse-selected KCF target with the Ackermann chassis.

This program is mutually exclusive with the GLIM/Nav2 navigation program and
uses RGB-D input because distance is required for following.
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
            "course_function": "02_07_kcf",
            "start_camera": start_camera,
            "enable_motion": enable_motion,
            "use_gui": LaunchConfiguration("use_gui"),
            "tracking_scale": LaunchConfiguration("tracking_scale"),
            "roi_x": LaunchConfiguration("roi_x"),
            "roi_y": LaunchConfiguration("roi_y"),
            "roi_width": LaunchConfiguration("roi_width"),
            "roi_height": LaunchConfiguration("roi_height"),
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
                description="Open the KCF mouse-selection window.",
            ),
            DeclareLaunchArgument(
                "tracking_scale",
                default_value="0.4",
                description="KCF processing scale; 0.4 keeps tracking responsive on NX.",
            ),
            DeclareLaunchArgument("roi_x", default_value="0"),
            DeclareLaunchArgument("roi_y", default_value="0"),
            DeclareLaunchArgument("roi_width", default_value="0"),
            DeclareLaunchArgument("roi_height", default_value="0"),
            LogInfo(
                condition=UnlessCondition(enable_motion),
                msg="KCF following is observing only; chassis motion is disabled.",
            ),
            LogInfo(
                condition=IfCondition(enable_motion),
                msg="KCF following motion is enabled. Nav2 must be stopped first.",
            ),
            vision,
        ]
    )
