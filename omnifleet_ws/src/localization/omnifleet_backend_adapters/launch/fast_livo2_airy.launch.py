import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    namespace = LaunchConfiguration('backend_namespace')
    share = Path(get_package_share_directory('omnifleet_backend_adapters'))
    outputs = ['cloud_registered', 'visualization_marker', 'cloud_visual_sub_map_before',
               'cloud_effected', 'Laser_map', 'path', 'planner_normal', 'voxels', 'dyn_obj',
               'dyn_obj_removed', 'dyn_obj_dbg_hist', 'mavros/vision_pose/pose', 'rgb_img',
               'LIVO2/imu_propagate', 'planes', 'tf', 'tf_static']
    remaps = [('/' + name, ['/', namespace, '/', name]) for name in outputs]
    remaps.append(('/aft_mapped_to_init', ['/', namespace, '/odom']))
    return LaunchDescription([
        DeclareLaunchArgument('robot_id', default_value=os.environ.get('OMNIFLEET_ROBOT_ID', 'robot_113')),
        DeclareLaunchArgument('backend_namespace', default_value='fast_livo2'),
        DeclareLaunchArgument('lidar_topic', default_value='/rslidar_points'),
        DeclareLaunchArgument('raw_imu_topic', default_value='/rslidar_imu_data'),
        DeclareLaunchArgument('imu_topic', default_value=['/', namespace, '/imu_corrected']),
        DeclareLaunchArgument('params_file', default_value=str(share / 'config/fast_livo2_airy_lio.yaml')),
        DeclareLaunchArgument('map_topic', default_value=['/', namespace, '/map']),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        Node(package='omnifleet_sensor_processing', executable='airy_imu_adapter_buffered',
             name='fast_livo_imu', namespace=namespace, output='screen',
             parameters=[str(share / 'config/airy_imu_correction.yaml'), {
                 'input_topic': LaunchConfiguration('raw_imu_topic'),
                 'output_topic': LaunchConfiguration('imu_topic'),
                 'output_frame': 'rslidar',
                 'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)}]),
        Node(package='fast_livo', executable='fastlivo_mapping', name='laserMapping',
             namespace=namespace, output='screen', remappings=remaps,
             parameters=[LaunchConfiguration('params_file'), {
                 'common.lid_topic': LaunchConfiguration('lidar_topic'),
                 'common.imu_topic': LaunchConfiguration('imu_topic'),
                 'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)}]),
        Node(package='omnifleet_mola_grid', executable='registered_cloud_grid',
             namespace=namespace, output='screen',
             remappings=[('map', LaunchConfiguration('map_topic'))],
             parameters=[{'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)}]),
    ])
