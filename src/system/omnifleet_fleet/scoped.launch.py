from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,IncludeLaunchDescription,OpaqueFunction
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from fleet_scope import scoped

def include(context):
    package=LaunchConfiguration('target_package').perform(context)
    filename=LaunchConfiguration('target_launch').perform(context)
    path=Path(filename) if filename.startswith('/') else Path(get_package_share_directory(package))/'launch'/filename
    return [IncludeLaunchDescription(AnyLaunchDescriptionSource(str(path)))]

def generate_launch_description():
    return scoped(LaunchDescription([DeclareLaunchArgument('target_package'),
        DeclareLaunchArgument('target_launch'),OpaqueFunction(function=include)]))
