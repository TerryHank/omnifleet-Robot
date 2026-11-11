from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    model = Path(get_package_share_directory('omnifleet_a2_description')) / 'urdf/lunshi_ackermann_lite.urdf'
    return LaunchDescription([
        Node(
            package='omnifleet_bringup', executable='ackermann_driver',
            name='omnifleet_a2_driver', output='screen',
            parameters=[{'serial_port': '/dev/myserial', 'xlinear_limit': 0.4,
                         'minimum_linear_speed': 0.0, 'angular_limit': 0.3,
                         'stationary_steering_angle_deg': 25.0,
                         'motion_command_rate': 20.0, 'cmd_vel_timeout': 0.35}],
            remappings=[('edition', '/omnifleet_a2/chassis/edition'),
                        ('/firmware/version', '/omnifleet_a2/chassis/firmware_version'),
                        ('voltage', '/omnifleet_a2/chassis/voltage'),
                        ('vel_raw', '/omnifleet_a2/chassis/velocity_raw'),
                        ('/motor_command_sent', '/omnifleet_a2/chassis/motor_command_sent')],
        ),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             name='robot_state_publisher', output='screen',
             parameters=[{'robot_description': model.read_text(), 'use_sim_time': False}]),
    ])
