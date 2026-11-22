from pathlib import Path
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_name = "mvs_camera_driver"
    share_dir = Path(get_package_share_directory(package_name))
    runtime_lib_dir = share_dir / "mvs"
    existing_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    ld_library_path = str(runtime_lib_dir)
    if existing_ld_path:
        ld_library_path = f"{ld_library_path}:{existing_ld_path}"
    config_file = share_dir / "config" / "mv_dt01snu_rgbd.yaml"

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=str(config_file),
                description="MV-DT01SNU RGB-D parameter file",
            ),
            Node(
                package=package_name,
                executable="mvs_camera_node",
                name="mvs_camera_node",
                output="screen",
                parameters=[LaunchConfiguration("params_file")],
                additional_env={
                    "MVCAM_COMMON_RUNENV": str(runtime_lib_dir),
                    "LD_LIBRARY_PATH": ld_library_path,
                },
            ),
        ]
    )
