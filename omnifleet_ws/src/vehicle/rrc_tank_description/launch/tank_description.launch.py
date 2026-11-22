from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    urdf = Path(get_package_share_directory('rrc_tank_description')) / 'urdf' / 'rrc_tank.urdf'
    robot_description = urdf.read_text(encoding='utf-8')
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='tank_robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}],
        )
    ])
