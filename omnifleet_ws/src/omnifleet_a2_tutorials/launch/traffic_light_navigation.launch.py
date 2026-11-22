"""Enable traffic-light recognition on top of an independent Nav2 launch."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    start_camera = LaunchConfiguration("start_camera")
    use_gui = LaunchConfiguration("use_gui")
    stop_confirmations = LaunchConfiguration("stop_confirmations")
    go_confirmations = LaunchConfiguration("go_confirmations")
    green_release_delay_sec = LaunchConfiguration("green_release_delay_sec")

    recognition = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("omnifleet_a2_tutorials"),
                    "launch",
                    "vision_02_14_traffic_light.launch.py",
                ]
            )
        ),
        launch_arguments={
            "start_camera": start_camera,
            "enable_motion": "false",
            "use_gui": use_gui,
        }.items(),
    )

    supervisor = Node(
        package="omnifleet_a2_behaviors",
        executable="traffic_light_nav_supervisor",
        name="omnifleet_a2_traffic_light_supervisor",
        output="screen",
        parameters=[
            {
                "detection_topic": "/omnifleet_a2/vision/detections",
                "stop_confirmations": ParameterValue(
                    stop_confirmations, value_type=int
                ),
                "go_confirmations": ParameterValue(go_confirmations, value_type=int),
                "green_release_delay_sec": ParameterValue(
                    green_release_delay_sec, value_type=float
                ),
            }
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("start_camera", default_value="false"),
            DeclareLaunchArgument("use_gui", default_value="true"),
            DeclareLaunchArgument("stop_confirmations", default_value="2"),
            DeclareLaunchArgument("go_confirmations", default_value="3"),
            DeclareLaunchArgument("green_release_delay_sec", default_value="0.25"),
            recognition,
            supervisor,
        ]
    )
