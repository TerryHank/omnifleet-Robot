from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = Path(get_package_share_directory('omnifleet_person_follow'))
    config = share / 'config/person_follow.yaml'
    return LaunchDescription([
        DeclareLaunchArgument('enable_motion', default_value='false'),
        Node(package='tros_person_following', executable='tros_person_following',
             name='tros_person_following_node', output='screen',
             parameters=[str(share / 'config/tros_104.yaml')],
             remappings=[('tros_tracking_status', '/vision/person_follow/tros_status'),
                         ('enable_follow', '/vision/person_follow/enable_follow'),
                         ('predict_trajectory', '/vision/person_follow/tros_prediction')],
             additional_env={'ZENOH_CONFIG_OVERRIDE':'transport/shared_memory/enabled=false;transport/shared_memory/transport_optimization/enabled=false'}),
        Node(package='omnifleet_person_follow', executable='person_follow_node',
             name='course_gesture_person_follow', output='screen',
             prefix='/home/iecme/omnifleet_ws/.env/vision/bin/python',
             parameters=[str(config), {'camera_backend': 'orbbec', 'use_local_frames': False,
                 'enable_motion': ParameterValue(LaunchConfiguration('enable_motion'), value_type=bool)}],
             additional_env={'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'OPENCV_FOR_THREADS_NUM': '1',
                 'ZENOH_CONFIG_OVERRIDE':'transport/shared_memory/enabled=false;transport/shared_memory/transport_optimization/enabled=false'})])
