from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    description_share = FindPackageShare('omnifleet_description')
    simulator_share = FindPackageShare('omnifleet_simulator')
    model = LaunchConfiguration('model')
    world = LaunchConfiguration('world')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config = LaunchConfiguration('rviz_config')

    robot_description = {
        'robot_description': Command(['xacro', ' ', model, ' ', 'use_gazebo:=true'])
    }

    gz_sim_launch = PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
    bridge_config = PathJoinSubstitution([simulator_share, 'config', 'ros_gz_bridge.yaml'])

    return LaunchDescription([
        DeclareLaunchArgument(
            'model',
            default_value=PathJoinSubstitution([description_share, 'urdf', 'lunshi_ackermann.urdf.xacro']),
            description='Absolute path to robot xacro file.'
        ),
        DeclareLaunchArgument(
            'world',
            default_value=PathJoinSubstitution([simulator_share, 'worlds', 'lunshi_sensor_test.sdf']),
            description='Gazebo Harmonic test world.'
        ),
        DeclareLaunchArgument('use_rviz', default_value='true', description='Start RViz2 with robot, TF, scan, and image displays.'),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=PathJoinSubstitution([description_share, 'rviz', 'lunshi_ackermann.rviz']),
            description='RViz2 config file.'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_sim_launch),
            launch_arguments={'gz_args': ['-r -v 4 ', world]}.items(),
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[robot_description, {'use_sim_time': True}],
        ),

        Node(
            package='ros_gz_sim',
            executable='create',
            output='screen',
            arguments=['-name', 'lunshi_chassis', '-topic', '/robot_description', '-z', '0.08'],
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            output='screen',
            parameters=[{'config_file': bridge_config, 'use_sim_time': True}],
        ),

        Node(
            condition=IfCondition(use_rviz),
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
        ),
    ])
