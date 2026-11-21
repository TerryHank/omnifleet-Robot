from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare('omnifleet_description')
    model = LaunchConfiguration('model')
    use_gui = LaunchConfiguration('use_gui')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config = LaunchConfiguration('rviz_config')

    robot_description = {
        'robot_description': Command(['xacro', ' ', model, ' ', 'use_gazebo:=false'])
    }

    return LaunchDescription([
        DeclareLaunchArgument(
            'model',
            default_value=PathJoinSubstitution([pkg_share, 'urdf', 'lunshi_ackermann.urdf.xacro']),
            description='Absolute path to robot xacro file.'
        ),
        DeclareLaunchArgument('use_gui', default_value='true', description='Start joint_state_publisher_gui for RViz steering/wheel test.'),
        DeclareLaunchArgument('use_rviz', default_value='true', description='Start RViz2.'),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=PathJoinSubstitution([pkg_share, 'rviz', 'lunshi_ackermann.rviz']),
            description='RViz2 config file.'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[robot_description]
        ),
        Node(
            condition=IfCondition(use_gui),
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),
        Node(
            condition=IfCondition(use_rviz),
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config]
        ),
    ])
