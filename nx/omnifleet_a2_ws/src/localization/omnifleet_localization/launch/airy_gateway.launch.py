"""RoboSense Airy driver entry used by systemd and optional manual bringup."""

from pathlib import Path

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _airy_extrinsics(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))["base_to_airy"]


def _airy_nodes(context):
    calibration_path = Path(
        LaunchConfiguration("calibration_path").perform(context)
    ).expanduser()
    if not calibration_path.is_file():
        raise RuntimeError(f"Airy calibration file not found: {calibration_path}")
    extrinsics = _airy_extrinsics(calibration_path)
    translation = [str(float(value)) for value in extrinsics["translation_m"]]
    rotation = [str(float(value)) for value in extrinsics["rotation_rpy_rad"]]
    return [
        Node(
            package="rslidar_sdk",
            executable="rslidar_sdk_node",
            output="screen",
            parameters=[{"config_path": LaunchConfiguration("config_path")}],
            remappings=[
                ("param_handle:__node", "robosense_airy_driver"),
            ],
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="base_to_airy",
            output="screen",
            arguments=[
                "--x", translation[0],
                "--y", translation[1],
                "--z", translation[2],
                "--roll", rotation[0],
                "--pitch", rotation[1],
                "--yaw", rotation[2],
                "--frame-id", extrinsics["parent_frame"],
                "--child-frame-id", extrinsics["child_frame"],
            ],
        ),
    ]


def generate_launch_description():
    package_share = Path(get_package_share_directory("omnifleet_localization"))
    return LaunchDescription([
        DeclareLaunchArgument(
            "config_path",
            default_value=str(package_share / "config" / "airy" / "airy.yaml"),
            description="RoboSense Airy SDK YAML configuration.",
        ),
        DeclareLaunchArgument(
            "calibration_path",
            default_value="/var/lib/omnifleet_t2/calibration/extrinsics.yaml",
            description="Runtime-owned right-handed Airy extrinsic calibration.",
        ),
        OpaqueFunction(function=_airy_nodes),
    ])
