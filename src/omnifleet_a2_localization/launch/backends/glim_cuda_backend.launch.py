import os
import re
import shutil
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, OpaqueFunction, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


GLIM_ROOT = "/home/iecme/slam_overlays/glim_cuda_ws"


def _sanitized_ld_library_path():
    paths = [
        f"{GLIM_ROOT}/deps/lib",
        "/usr/local/cuda-12.6/lib64",
        "/usr/local/lib",
    ]
    paths.extend(
        path
        for path in os.environ.get("LD_LIBRARY_PATH", "").split(":")
        if path and not path.startswith("/opt/MVS") and path not in paths
    )
    return ":".join(paths)


def _runtime_localization_config(source_dir: Path, map_id: str) -> Path:
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", map_id)
    destination = Path("/tmp") / f"omnifleet_glim_localization_{safe_id}"
    shutil.copytree(source_dir, destination, dirs_exist_ok=True)

    config_file = destination / "config.json"
    content = config_file.read_text(encoding="utf-8")
    old = '"config_global_mapping": "config_global_mapping_gpu.json"'
    new = '"config_global_mapping": "config_global_mapping_localization.json"'
    if old not in content:
        raise RuntimeError(f"cannot select GLIM localization config in {config_file}")
    config_file.write_text(content.replace(old, new), encoding="utf-8")
    return destination


def _validate_glim_dump(path: Path):
    graph = path / "graph.txt"
    if not graph.is_file() or graph.stat().st_size == 0:
        raise RuntimeError(f"GLIM prior map is incomplete: missing {graph}")
    submap_data = sorted(path.glob("[0-9][0-9][0-9][0-9][0-9][0-9]/data.txt"))
    if not submap_data or any(item.stat().st_size == 0 for item in submap_data):
        raise RuntimeError(f"GLIM prior map is incomplete: no complete submap data under {path}")


def _backend(context):
    operation = LaunchConfiguration("operation").perform(context)
    if operation not in {"mapping", "slam_navigation", "localization"}:
        raise RuntimeError("GLIM CUDA supports mapping, mapping with Nav2, and prior-map localization")

    package_share = Path(get_package_share_directory("omnifleet_a2_localization"))
    packaged_config = package_share / "config" / "glim_cuda"
    map_root = Path(LaunchConfiguration("map_dir").perform(context)).expanduser()
    map_id = LaunchConfiguration("map_id").perform(context) or "active"
    dump_path = map_root / "glim_cuda" / map_id / "dump"
    saved_map_yaml = dump_path.parent / "map.yaml"
    dump_path.parent.mkdir(parents=True, exist_ok=True)
    Path("/var/log/omnifleet_a2/glim").mkdir(parents=True, exist_ok=True)

    localization = operation == "localization"
    requested_map_path = LaunchConfiguration("map_path").perform(context).strip()
    prior_map_path = Path(requested_map_path).expanduser() if requested_map_path else dump_path
    if localization:
        _validate_glim_dump(prior_map_path)
        if not saved_map_yaml.is_file():
            raise RuntimeError(
                f"prior-map localization is missing saved 2D map: {saved_map_yaml}"
            )
        config_path = _runtime_localization_config(packaged_config, map_id)
    else:
        config_path = packaged_config

    use_sim_time = LaunchConfiguration("use_sim_time")
    glim_node = Node(
        package="glim_ros",
        executable="glim_rosnode",
        name="glim_ros",
        output="both",
        parameters=[{
            "config_path": str(config_path),
            "dump_on_unload": False,
            "dump_path": str(dump_path),
            "map_path": str(prior_map_path) if localization else "",
            "initial_pose_x": ParameterValue(LaunchConfiguration("initial_pose_x"), value_type=float),
            "initial_pose_y": ParameterValue(LaunchConfiguration("initial_pose_y"), value_type=float),
            "initial_pose_z": ParameterValue(LaunchConfiguration("initial_pose_z"), value_type=float),
            "initial_pose_yaw": ParameterValue(LaunchConfiguration("initial_pose_yaw"), value_type=float),
            "use_sim_time": use_sim_time,
        }],
        on_exit=[EmitEvent(event=Shutdown(reason="GLIM process exited"))],
    )

    return [
        SetEnvironmentVariable("LD_LIBRARY_PATH", _sanitized_ld_library_path()),
        Node(
            package="omnifleet_a2_localization",
            executable="airy_imu_adapter_node",
            name="omnifleet_a2_airy_imu_adapter",
            output="screen",
            parameters=[{
                "input_topic": "/rslidar_imu_data",
                "output_topic": "/rslidar_imu_data_corrected",
                "output_frame": "rslidar",
                "rotation_xyzw": [
                    -0.7068467736244202,
                    0.7073657512664795,
                    -0.0005705897347070277,
                    0.000999057781882584,
                ],
                "use_sim_time": use_sim_time,
            }],
        ),
        glim_node,
        Node(
            package="omnifleet_a2_localization",
            executable="glim_odom_adapter",
            name="omnifleet_a2_glim_odom_adapter",
            output="screen",
            parameters=[{
                "input_topic": "/glim_ros/odom",
                "output_topic": "/odom",
                "odom_frame": "odom",
                "base_frame": "base_link",
                "use_sim_time": use_sim_time,
            }],
        ),
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="prior_map_server",
            output="screen",
            condition=IfCondition("true" if localization else "false"),
            parameters=[{
                "yaml_filename": str(saved_map_yaml),
                "topic_name": "map",
                "frame_id": "map",
                "use_sim_time": use_sim_time,
            }],
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_prior_map",
            output="screen",
            condition=IfCondition("true" if localization else "false"),
            parameters=[{
                "autostart": True,
                "node_names": ["prior_map_server"],
                "bond_timeout": 4.0,
                "use_sim_time": use_sim_time,
            }],
        ),
        Node(
            package="omnifleet_a2_localization",
            executable="glim_map_projector",
            name="omnifleet_a2_glim_map_projector",
            output="screen",
            condition=IfCondition("false" if localization else "true"),
            parameters=[{
                "input_topic": "/glim_ros/map",
                # Use only the newest raw Airy frame to mark ray-observed free
                # cells. Every accepted frame replaces the previous live grid;
                # GLIM aligned_points is neither subscribed nor accumulated.
                "bootstrap_input_topic": "/rslidar_points",
                "bootstrap_max_rate_hz": 0.10,
                "bootstrap_raytrace_max_range": ParameterValue(LaunchConfiguration("lidar_range_max"), value_type=float),
                "tf_latest_tolerance_sec": 0.10,
                "output_topic": "/map",
                # Complete GLIM snapshots provide the persistent obstacles.
                "resolution": 0.08,
                "ground_relative_min": ParameterValue(LaunchConfiguration("map_ground_relative_min"), value_type=float),
                "ground_relative_max": ParameterValue(LaunchConfiguration("map_ground_relative_max"), value_type=float),
                "obstacle_relative_min": ParameterValue(LaunchConfiguration("map_obstacle_relative_min"), value_type=float),
                "obstacle_relative_max": ParameterValue(LaunchConfiguration("map_obstacle_relative_max"), value_type=float),
                "robot_base_frame": "base_link",
                "ground_z_offset_from_base": 0.0,
                "robot_footprint_x_min": -0.06,
                "robot_footprint_x_max": 0.42,
                "robot_footprint_y_min": -0.16,
                "robot_footprint_y_max": 0.16,
                "use_sim_time": use_sim_time,
            }],
        ),
        Node(
            package="omnifleet_a2_localization",
            executable="depth_dropoff_detector",
            name="omnifleet_a2_depth_dropoff_detector",
            output="screen",
            parameters=[{"use_sim_time": use_sim_time}],
            condition=IfCondition(LaunchConfiguration("use_camera")),
        ),
        Node(
            package="omnifleet_a2_localization",
            executable="wheel_slip_detector",
            name="omnifleet_a2_wheel_slip_detector",
            output="screen",
            parameters=[{
                "wheel_odom_topic": "/omnifleet_a2/chassis/wheel_odometry",
                "primary_odom_topic": "/odom",
                "use_sim_time": use_sim_time,
            }],
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("operation", default_value="mapping"),
        DeclareLaunchArgument("map_id", default_value="active"),
        DeclareLaunchArgument("map_dir", default_value="/var/lib/omnifleet_a2/maps"),
        DeclareLaunchArgument("map_path", default_value=""),
        DeclareLaunchArgument("initial_pose_x", default_value="0.0"),
        DeclareLaunchArgument("initial_pose_y", default_value="0.0"),
        DeclareLaunchArgument("initial_pose_z", default_value="0.0"),
        DeclareLaunchArgument("initial_pose_yaw", default_value="0.0"),
        DeclareLaunchArgument("map_ground_relative_min", default_value="-0.03"),
        DeclareLaunchArgument("map_ground_relative_max", default_value="0.03"),
        DeclareLaunchArgument("map_obstacle_relative_min", default_value="0.06"),
        DeclareLaunchArgument("map_obstacle_relative_max", default_value="1.80"),
        DeclareLaunchArgument("lidar_range_min", default_value="0.18"),
        DeclareLaunchArgument("lidar_range_max", default_value="6.0"),
        DeclareLaunchArgument("use_camera", default_value="false"),
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        OpaqueFunction(function=_backend),
    ])
