"""Save and view the current pure 2D map, then end its unified launch."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("map_dir", default_value="~/robot_maps"),
        DeclareLaunchArgument("viewer", default_value="eog"),
        Node(
            package="omnifleet_behaviors",
            executable="map_save_view_stop",
            name="mapping_save_view_stop",
            output="screen",
            parameters=[{
                "map_root": LaunchConfiguration("map_dir"),
                "backend": "glim_cuda",
                "label": "mapping_finished",
                "viewer": LaunchConfiguration("viewer"),
                "workflow": "纯二维建图",
            }],
        ),
    ])
