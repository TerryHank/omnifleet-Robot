from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config = Path(get_package_share_directory("omnifleet_vr_bridge")) / "config" / "vr_bridge.yaml"
    return LaunchDescription(
        [
            Node(
                package="omnifleet_vr_bridge",
                executable="vr_bridge",
                name="omnifleet_vr_bridge",
                output="screen",
                parameters=[str(config)],
            )
        ]
    )
