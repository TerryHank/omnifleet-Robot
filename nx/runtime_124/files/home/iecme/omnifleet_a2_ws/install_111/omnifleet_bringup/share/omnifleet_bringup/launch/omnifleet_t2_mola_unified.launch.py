"""Path-compatible wrapper for the package's selectable unified launch."""
from launch import LaunchDescription
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('profile',default_value='simple_direct'),
        DeclareLaunchArgument('map_path',default_value='/home/iecme/omnifleet_a2_data/maps/home_legacy/foxglove_map.mm'),
        DeclareLaunchArgument('map_dir',default_value='/home/iecme/omnifleet_a2_data/maps/home_legacy'),
        DeclareLaunchArgument('initial_pose',default_value=''),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(Path(get_package_share_directory('omnifleet_bringup'))/'launch/mola_nav2_unified.launch.py')),
            launch_arguments={key:LaunchConfiguration(key) for key in ('profile','map_path','map_dir','initial_pose')}.items()),
    ])
