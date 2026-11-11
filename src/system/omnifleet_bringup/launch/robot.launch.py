"""Cold-selectable production bringup for the tracked differential robot."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression


BACKENDS = {
    "mola": "mola_backend.launch.py",
    "cartographer_3d": "cartographer_3d_backend.launch.py",
}


def include(package, launch_file, arguments=None, condition=None):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(package), "launch", launch_file)
        ),
        launch_arguments=(arguments or {}).items(),
        condition=condition,
    )


def reject_chassis_launch_args(context, *args, **kwargs):
    for name in ("start_chassis", "start_chassis_core"):
        value = context.launch_configurations.get(name)
        if value is not None and str(value).strip().lower() in {
            "1", "true", "yes", "on"
        }:
            raise RuntimeError(
                f"{name} is removed: the chassis is managed only by "
                "omnifleet-t2-chassis.service via systemctl"
            )
    return []


def selected_backend(context):
    backend = LaunchConfiguration("localization_backend").perform(context).strip()
    if backend not in BACKENDS:
        raise RuntimeError(
            f"unsupported localization_backend={backend!r}; choose one of {sorted(BACKENDS)}"
        )
    operation = LaunchConfiguration("operation").perform(context).strip()
    if operation not in {"mapping", "slam_navigation"}:
        raise RuntimeError("operation must be mapping or slam_navigation")
    return [
        include(
            "omnifleet_localization",
            BACKENDS[backend],
            {
                "operation": operation,
                "map_id": LaunchConfiguration("map_id"),
                "map_dir": LaunchConfiguration("map_dir"),
                "map_path": LaunchConfiguration("map_path"),
                "use_camera": LaunchConfiguration("use_camera"),
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "map_ground_relative_min": "-0.03",
                "map_ground_relative_max": "0.03",
                "map_obstacle_relative_min": "0.06",
                "map_obstacle_relative_max": "2.0",
            },
        )
    ]


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument("operation", default_value="slam_navigation"),
        DeclareLaunchArgument("localization_backend", default_value="mola"),
        DeclareLaunchArgument("planner_mode", default_value="smac_2d"),
        DeclareLaunchArgument("controller_mode", default_value="dwb"),
        DeclareLaunchArgument("map_id", default_value="active"),
        DeclareLaunchArgument("map_dir", default_value="/home/iecme/omnifleet_data/maps"),
        DeclareLaunchArgument("map_path", default_value=""),
        DeclareLaunchArgument("start_description", default_value="true"),
        DeclareLaunchArgument("start_airy", default_value="false"),
        DeclareLaunchArgument("use_camera", default_value="false"),
        OpaqueFunction(function=reject_chassis_launch_args),
        include(
            "omnifleet_description",
            "t2_description.launch.py",
            {"use_sim_time": use_sim_time},
            condition=IfCondition(LaunchConfiguration("start_description")),
        ),
        include(
            "omnifleet_localization",
            "airy_gateway.launch.py",
            {"use_sim_time": use_sim_time},
            condition=IfCondition(LaunchConfiguration("start_airy")),
        ),
        OpaqueFunction(function=selected_backend),
        include(
            "omnifleet_planner",
            "navigation.launch.py",
            {"use_sim_time": use_sim_time, "autostart": "true"},
            condition=IfCondition(
                PythonExpression(["'", LaunchConfiguration("operation"), "' == 'slam_navigation'"])
            ),
        ),
    ])
