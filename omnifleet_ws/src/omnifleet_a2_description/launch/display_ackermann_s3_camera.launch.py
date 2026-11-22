from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    model = LaunchConfiguration('model')
    default_model = PathJoinSubstitution([
        FindPackageShare('omnifleet_a2_description'),
        'urdf',
        'lunshi_chassis_ackermann_s3_camera.urdf',
    ])

    return LaunchDescription([
        DeclareLaunchArgument('model', default_value=default_model),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': Command(['cat ', model])}],
            output='screen',
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen',
        ),
    ])
