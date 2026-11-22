from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    transport = LaunchConfiguration("transport")
    serial_port = LaunchConfiguration("serial_port")
    serial_baud = LaunchConfiguration("serial_baud")
    bus = LaunchConfiguration("bus")
    address = LaunchConfiguration("address")
    enable_motion = LaunchConfiguration("enable_motion")
    motion_backend = LaunchConfiguration("motion_backend")
    cmd_vel_topic = LaunchConfiguration("cmd_vel_topic")
    return LaunchDescription(
        [
            DeclareLaunchArgument("transport", default_value="serial"),
            DeclareLaunchArgument(
                "serial_port", default_value="/dev/wonderecho_flash"
            ),
            DeclareLaunchArgument("serial_baud", default_value="115200"),
            DeclareLaunchArgument("bus", default_value="7"),
            DeclareLaunchArgument("address", default_value="52"),
            DeclareLaunchArgument("enable_motion", default_value="false"),
            DeclareLaunchArgument("motion_backend", default_value="twist"),
            DeclareLaunchArgument("cmd_vel_topic", default_value="/cmd_vel"),
            Node(
                package="omnifleet_behaviors",
                executable="wonderecho_voice",
                name="omnifleet_t2_wonderecho_voice",
                output="screen",
                parameters=[
                    {
                        "transport": transport,
                        "serial_port": serial_port,
                        "serial_baud": ParameterValue(
                            serial_baud, value_type=int
                        ),
                        "bus": ParameterValue(bus, value_type=int),
                        "address": ParameterValue(address, value_type=int),
                        "enable_motion": ParameterValue(
                            enable_motion, value_type=bool
                        ),
                        "motion_backend": motion_backend,
                        "cmd_vel_topic": cmd_vel_topic,
                    }
                ],
            ),
        ]
    )
