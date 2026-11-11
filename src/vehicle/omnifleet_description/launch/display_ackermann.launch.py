from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    model = LaunchConfiguration('model')
    robot_description_file = PathJoinSubstitution([
        FindPackageShare('omnifleet_description'), 'urdf', model
    ])
    robot_description = Command(['cat ', robot_description_file])

    return LaunchDescription([
        DeclareLaunchArgument(
            'model',
            default_value='lunshi_ackermann_lite.urdf',
            description='URDF file name: lunshi_ackermann_lite.urdf or lunshi_ackermann_optimized.urdf'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen'
        ),
    ])
