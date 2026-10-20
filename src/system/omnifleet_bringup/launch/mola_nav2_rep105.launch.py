"""REP-105 alias using the same checked unified launch and common map."""
from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    unified=Path(__file__).with_name('mola_nav2_unified.launch.py')
    return LaunchDescription([
        DeclareLaunchArgument('map_path',default_value='/home/iecme/omnifleet_data/maps/home_legacy/foxglove_map.mm'),
        DeclareLaunchArgument('map_dir',default_value='/home/iecme/omnifleet_data/maps/home_legacy'),
        DeclareLaunchArgument('initial_pose',default_value=''),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(unified)),launch_arguments={
            'profile':'simple_rep105','map_path':LaunchConfiguration('map_path'),'map_dir':LaunchConfiguration('map_dir'),
            'initial_pose':LaunchConfiguration('initial_pose')}.items()),
    ])
