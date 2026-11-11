"""MOLA Simple backend using the official REP-105 external-odometry mode."""

import re
from pathlib import Path

from ament_index_python.packages import (
    PackageNotFoundError,
    get_package_share_directory,
)
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetRemap


def _mola_paths():
    try:
        share = Path(get_package_share_directory("mola_lidar_odometry"))
    except PackageNotFoundError as exc:
        raise RuntimeError(
            "MOLA backend is optional and is not installed; install the pinned "
            "ROS 2 Humble MOLA packages or select localization_backend:=glim_cuda"
        ) from exc

    upstream_launch = share / "ros2-launchs" / "ros2-lidar-odometry.launch.py"
    # The 3.0 default GICP pipeline enters an RKNN code path that is not
    # compatible with Jammy's nanoflann 1.4.2.  The official standard-ICP
    # pipeline avoids that path and is therefore deliberately pinned here.
    pipeline = (
        Path(get_package_share_directory("omnifleet_a2_localization"))
        / "config"
        / "mola"
        / "lidar3d-icp-nav2.yaml"
    )
    for path in (upstream_launch, pipeline):
        if not path.is_file():
            raise RuntimeError(f"incomplete MOLA installation: missing {path}")
    return upstream_launch, pipeline


def _native_map_output(context):
    map_id = LaunchConfiguration("map_id").perform(context).strip()
    if (
        not re.fullmatch(r"[A-Za-z0-9._-]+", map_id)
        or map_id in {".", ".."}
    ):
        raise RuntimeError(
            "unsafe MOLA map_id; expected only [A-Za-z0-9._-] characters"
        )

    backend_root = (
        Path(LaunchConfiguration("map_dir").perform(context)).expanduser()
        / "mola"
    ).resolve()
    session_dir = (backend_root / map_id).resolve()
    if session_dir.parent != backend_root:
        raise RuntimeError("unsafe MOLA map_id path")
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir / "local_map.mm"


def _backend(context):
    operation = LaunchConfiguration("operation").perform(context)
    if operation not in {"mapping", "slam_navigation"}:
        raise RuntimeError(
            "MOLA is experimental and currently supports only mapping and "
            "online slam_navigation; prior-map localization remains on GLIM"
        )

    upstream_launch, pipeline = _mola_paths()
    native_map_output = _native_map_output(context)
    mola_arguments = {
        "lidar_topic_name": "/rslidar_points",
        "lidar_topic_type": "PointCloud2",
        "imu_topic_name": "/rslidar_imu_data_corrected",
        "lidar_qos_reliability": "best_effort",
        "lidar_qos_depth": "1",
        "use_imu_for_lio": "True",
        "mola_deskew_method": "MotionCompensationMethod::IMU",
        "mola_tf_base_link": "base_link",
        "mola_lo_reference_frame": "map",
        "mola_state_estimator_reference_frame": "map",
        "mola_bridge_odometry_frame": "odom",
        "mola_lo_pipeline": str(pipeline),
        "publish_localization_following_rep105": "True",
        "forward_ros_tf_odom_to_mola": "False",
        "use_state_estimator": "False",
        "start_active": "True",
        "start_mapping_enabled": "True",
        "use_mola_gui": "False",
        "use_rviz": "False",
        "use_diagnostic_aggregator": "False",
        "use_sim_time": LaunchConfiguration("use_sim_time").perform(context),
    }

    return [
        # Official Simple + REP-105 mode: BridgeROS2 reads the chassis-owned
        # odom->base_link edge and publishes the complementary map->odom edge.
        SetEnvironmentVariable("MOLA_LOCALIZATION_PUBLISH_TF", "true"),
        SetEnvironmentVariable("MOLA_LOCALIZATION_PUBLISH_ODOM_MSGS", "true"),
        SetEnvironmentVariable("MOLA_SAVE_MM", str(native_map_output)),
        # Airy XYZIRT exposes the generic `ring` channel expected by MOLA.
        SetEnvironmentVariable("MOLA_VERBOSITY_MOLA_LO", "ERROR"),
        # The vehicle is capped near 0.4 m/s and already uses IMU deskew.
        # Twist re-optimization occasionally reruns ICP for >0.7 s on Orin,
        # which violates the live odometry freshness gate.
        SetEnvironmentVariable("MOLA_OPTIMIZE_TWIST", "false"),
        # Keep enough indoor geometry for 0.4 m/s navigation while bounding
        # worst-case ICP time below the 0.5 s odometry freshness gate.
        SetEnvironmentVariable("MOLA_ICP_CLOUD_DECIMATION", "0.80"),
        SetEnvironmentVariable("MOLA_MAP_CLOUD_DECIMATION", "0.30"),
        SetEnvironmentVariable("MOLA_LOCAL_VOXELMAP_RESOLUTION", "0.60"),
        # Disable BridgeROS2's optional base_footprint static edge; the robot
        # description remains the only owner of fixed body frames.
        SetEnvironmentVariable("MOLA_TF_FOOTPRINT_LINK", ""),
        # The official mp2p_icp pipeline adds a CVoxelMap and derives the
        # COccupancyGridMap2D layer consumed below.  No project-owned map node
        # sits between MOLA and Nav2.
        SetEnvironmentVariable("MOLA_NAV_GRID_RESOLUTION", "0.10"),
        SetEnvironmentVariable(
            "MOLA_NAV_GRID_Z_MIN", LaunchConfiguration("map_obstacle_relative_min")
        ),
        SetEnvironmentVariable(
            "MOLA_NAV_GRID_Z_MAX", LaunchConfiguration("map_obstacle_relative_max")
        ),
        # The Airy SDK publishes acceleration in g and labels the factory IMU
        # axes as rslidar.  Correct both before handing the ROS Imu message to
        # MOLA; the output is expressed in the already-published rslidar frame.
        Node(
            package="omnifleet_a2_localization",
            executable="airy_imu_adapter_node",
            name="omnifleet_a2_airy_imu_adapter",
            output="screen",
            parameters=[{
                "input_topic": "/rslidar_imu_data",
                "output_topic": "/rslidar_imu_data_corrected",
                "output_frame": "rslidar",
                "linear_acceleration_scale": 9.80665,
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }],
        ),
        GroupAction(
            actions=[
                SetRemap(
                    src="/lidar_odometry/nav_grid_gridmap",
                    dst="/map",
                ),
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(str(upstream_launch)),
                    launch_arguments=mola_arguments.items(),
                ),
            ]
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
        DeclareLaunchArgument("use_camera", default_value="false"),
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        OpaqueFunction(function=_backend),
    ])
