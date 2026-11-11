"""Reuse the existing native RTAB-Map entry with isolated backend topic defaults."""
import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import SetParameter, SetRemap
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    robot = LaunchConfiguration('robot_id')
    namespace = LaunchConfiguration('backend_namespace')
    native = Path(get_package_share_directory('omnifleet_bringup')) / 'launch/rtabmap_lidar_grid.launch.py'
    return LaunchDescription([
        DeclareLaunchArgument('robot_id', default_value=os.environ.get('OMNIFLEET_ROBOT_ID', 'robot_113')),
        DeclareLaunchArgument('backend_namespace', default_value='rtabmap_trial'),
        DeclareLaunchArgument('lidar_topic', default_value='/rslidar_points'),
        DeclareLaunchArgument('base_frame', default_value='base_link'),
        DeclareLaunchArgument('map_topic', default_value=['/', namespace, '/map']),
        DeclareLaunchArgument('database_path', default_value='/home/iecme/omnifleet_data/maps/rtabmap/trial.db'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        GroupAction([
            SetParameter(name='use_sim_time', value=ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)),
            SetRemap(src='map', dst=LaunchConfiguration('map_topic')),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(str(native)), launch_arguments={
                'namespace': namespace, 'base_frame': LaunchConfiguration('base_frame'),
                'cloud_topic': LaunchConfiguration('lidar_topic'),
                'tf_topic': '/tf', 'tf_static_topic': '/tf_static',
                'database_path': LaunchConfiguration('database_path'), 'resolution': '0.1',
            }.items()),
        ]),
    ])
