"""A2 navigation entrypoint; Airy, STM32 and MOLA are owned by their services."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    launch = Path(get_package_share_directory("omnifleet_bringup"))/"launch/navigation.launch.py"
    return LaunchDescription([IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(launch)),
        launch_arguments={"odom_topic": "/lidar_odometry/nav_odom",
                          "obstacle_topic": "/navigation/deskewed_points",
                          "obstacle_clearing": "true"}.items())])
