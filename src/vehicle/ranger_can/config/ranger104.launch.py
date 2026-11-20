"""Ranger SDK telemetry and 104's existing odometry/raw feedback topics."""

import sys
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    receiver = Path(__file__).resolve().parents[1] / "can_receiver.py"
    return LaunchDescription([
        DeclareLaunchArgument("port_name"),
        Node(
            package="ranger_base",
            executable="ranger_base_node",
            name="omnifleet_t2_driver",
            output="screen",
            parameters=[{
                "port_name": LaunchConfiguration("port_name"),
                "robot_model": "ranger_mini_v3",
                "receive_only": False,
                "publish_odom_tf": False,
                "odom_topic_name": "/ranger_sdk/odom",
            }],
            remappings=[("/cmd_vel", "/navigation/cmd_vel_safe")],
            on_exit=Shutdown(reason="Ranger SDK exited"),
        ),
        ExecuteProcess(
            cmd=[sys.executable, str(receiver), "--ros-args", "-r", "__node:=ranger_can_feedback"],
            output="screen",
            on_exit=Shutdown(reason="104 CAN feedback node exited"),
        ),
    ])
