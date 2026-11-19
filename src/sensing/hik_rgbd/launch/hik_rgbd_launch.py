from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = Path(get_package_share_directory("hik_rgbd"))
    return LaunchDescription([
        DeclareLaunchArgument("start_camera", default_value="true"),
        DeclareLaunchArgument("use_rviz", default_value="false"),
        Node(
            package="hik_rgbd", executable="image_pipeline_all_in_one",
            name="mv_dt01snu_camera", output="screen",
            condition=IfCondition(LaunchConfiguration("start_camera")),
            additional_env={"ZENOH_CONFIG_OVERRIDE":
                "transport/shared_memory/enabled=false;transport/shared_memory/transport_optimization/enabled=false"},
        ),
        Node(
            package="rviz2", executable="rviz2", output="screen",
            arguments=["-d", str(share / "config" / "hik_camera.rviz")],
            condition=IfCondition(LaunchConfiguration("use_rviz")),
        ),
    ])
