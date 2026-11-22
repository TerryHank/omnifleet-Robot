"""Tracked chassis STM32 driver with standard REP-105 odometry output."""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("serial_port", default_value="/dev/omnifleet_t2_stm32"),
            DeclareLaunchArgument("track_separation_m", default_value="0.33"),
            DeclareLaunchArgument("cmd_vel_timeout", default_value="0.35"),
            DeclareLaunchArgument("max_angular_speed_rps", default_value="2.0"),
            DeclareLaunchArgument("publish_odom_tf", default_value=os.environ.get("OMNIFLEET_PUBLISH_ODOM_TF", "true")),
            Node(
                package="omnifleet_bringup",
                executable="t2_driver",
                name="omnifleet_t2_driver",
                output="screen",
                emulate_tty=True,
                parameters=[
                    {
                        "serial_port": LaunchConfiguration("serial_port"),
                        "odom_frame": "odom",
                        "base_frame": "base_link",
                        "imu_link": "imu_link",
                        "motion_command_rate": 20.0,
                        "track_separation_m": ParameterValue(
                            LaunchConfiguration("track_separation_m"), value_type=float
                        ),
                        "cmd_vel_timeout": ParameterValue(
                            LaunchConfiguration("cmd_vel_timeout"), value_type=float
                        ),
                        "max_angular_speed_rps": ParameterValue(
                            LaunchConfiguration("max_angular_speed_rps"), value_type=float
                        ),
                        "publish_odom_tf": ParameterValue(
                            LaunchConfiguration("publish_odom_tf"), value_type=bool
                        ),
                        "use_sim_time": use_sim_time,
                    }
                ],
            ),
        ]
    )
