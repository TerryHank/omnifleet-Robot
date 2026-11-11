import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


BACKENDS = {
    "mola": "production_mola.launch.py",
    "glim_cuda": "production_glim_cuda.launch.py",
    "cartographer_3d": "production_cartographer_3d.launch.py",
}


def _selected_backend(context):
    backend = LaunchConfiguration("backend").perform(context)
    if backend not in BACKENDS:
        raise RuntimeError(f"backend must be one of {sorted(BACKENDS)}, got {backend!r}")
    launch_file = os.path.join(
        get_package_share_directory("omnifleet_a2_bringup"),
        "launch",
        BACKENDS[backend],
    )
    return [IncludeLaunchDescription(
        PythonLaunchDescriptionSource(launch_file),
        launch_arguments={
            "use_sim_time": "false",
            "map_id": LaunchConfiguration("map_id"),
            "map_dir": LaunchConfiguration("map_dir"),
        }.items(),
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("backend", default_value="mola"),
        DeclareLaunchArgument("map_id", default_value="active"),
        DeclareLaunchArgument("map_dir", default_value="/var/lib/omnifleet_a2/maps"),
        OpaqueFunction(function=_selected_backend),
    ])
