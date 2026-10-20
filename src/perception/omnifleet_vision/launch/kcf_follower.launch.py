from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = Path(get_package_share_directory("omnifleet_vision"))
    default_params = share / "config" / "kcf_follower.yaml"

    arguments = [
        DeclareLaunchArgument("params_file", default_value=str(default_params)),
        DeclareLaunchArgument(
            "tracker_color_topic", default_value="/camera/color/image_raw"
        ),
        DeclareLaunchArgument(
            "aligned_color_topic", default_value="/camera/color/image_raw"
        ),
        DeclareLaunchArgument(
            "depth_topic",
            default_value="/camera/depth/image_raw",
        ),
        DeclareLaunchArgument(
            "output_image_topic",
            default_value="/omnifleet_vision/kcf/image",
        ),
        DeclareLaunchArgument("cmd_vel_topic", default_value="/cmd_vel_vision"),
        DeclareLaunchArgument("enable_motion", default_value="false"),
        DeclareLaunchArgument("use_gui", default_value="true"),
        DeclareLaunchArgument("tracking_scale", default_value="0.4"),
        DeclareLaunchArgument("roi_x", default_value="0"),
        DeclareLaunchArgument("roi_y", default_value="0"),
        DeclareLaunchArgument("roi_width", default_value="0"),
        DeclareLaunchArgument("roi_height", default_value="0"),
        DeclareLaunchArgument("target_distance", default_value="0.8"),
        DeclareLaunchArgument("max_pair_delta", default_value="0.8"),
        DeclareLaunchArgument("tracking_timeout", default_value="0.5"),
        DeclareLaunchArgument("depth_timeout", default_value="0.5"),
        DeclareLaunchArgument("control_rate", default_value="10.0"),
        DeclareLaunchArgument("minimum_linear_speed", default_value="0.40"),
        DeclareLaunchArgument("max_linear_speed", default_value="0.40"),
        DeclareLaunchArgument("linear_deadband", default_value="0.15"),
    ]

    node = Node(
        package="omnifleet_vision",
        executable="kcf_follower_node",
        name="kcf_follower",
        output="screen",
        parameters=[
            LaunchConfiguration("params_file"),
            {
                "tracker_color_topic": LaunchConfiguration("tracker_color_topic"),
                "aligned_color_topic": LaunchConfiguration("aligned_color_topic"),
                "depth_topic": LaunchConfiguration("depth_topic"),
                "output_image_topic": LaunchConfiguration("output_image_topic"),
                "cmd_vel_topic": LaunchConfiguration("cmd_vel_topic"),
                "enable_motion": ParameterValue(
                    LaunchConfiguration("enable_motion"), value_type=bool
                ),
                "use_gui": ParameterValue(
                    LaunchConfiguration("use_gui"), value_type=bool
                ),
                "tracking_scale": ParameterValue(
                    LaunchConfiguration("tracking_scale"), value_type=float
                ),
                "roi_x": ParameterValue(LaunchConfiguration("roi_x"), value_type=int),
                "roi_y": ParameterValue(LaunchConfiguration("roi_y"), value_type=int),
                "roi_width": ParameterValue(
                    LaunchConfiguration("roi_width"), value_type=int
                ),
                "roi_height": ParameterValue(
                    LaunchConfiguration("roi_height"), value_type=int
                ),
                "target_distance": ParameterValue(
                    LaunchConfiguration("target_distance"), value_type=float
                ),
                "max_pair_delta": ParameterValue(
                    LaunchConfiguration("max_pair_delta"), value_type=float
                ),
                "tracking_timeout": ParameterValue(
                    LaunchConfiguration("tracking_timeout"), value_type=float
                ),
                "depth_timeout": ParameterValue(
                    LaunchConfiguration("depth_timeout"), value_type=float
                ),
                "control_rate": ParameterValue(
                    LaunchConfiguration("control_rate"), value_type=float
                ),
                "minimum_linear_speed": ParameterValue(
                    LaunchConfiguration("minimum_linear_speed"), value_type=float
                ),
                "max_linear_speed": ParameterValue(
                    LaunchConfiguration("max_linear_speed"), value_type=float
                ),
                "linear_deadband": ParameterValue(
                    LaunchConfiguration("linear_deadband"), value_type=float
                ),
            },
        ],
    )

    return LaunchDescription(arguments + [node])
