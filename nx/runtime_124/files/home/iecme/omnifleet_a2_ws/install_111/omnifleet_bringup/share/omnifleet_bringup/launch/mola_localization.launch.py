from fleet_scope import frame
"""System-owned MOLA, radar IMU and navigation-grid bringup."""

from pathlib import Path
import json
import os
import shlex

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
    LogInfo,
    EmitEvent,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetRemap


PROFILES = {"integrated", "simple_direct", "simple_direct_observation", "simple_rep105", "smoother_direct"}


def _as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _launch(context):
    for name in ("start_chassis", "start_chassis_core"):
        value = context.launch_configurations.get(name)
        if value is not None and _as_bool(value):
            raise RuntimeError(
                f"{name} is removed: the chassis is managed only by "
                "omnifleet-t2-chassis.service via systemctl"
            )
    profile = LaunchConfiguration("profile").perform(context).strip()
    map_reload_mode = _as_bool(LaunchConfiguration("map_reload_mode").perform(context))
    if profile not in PROFILES:
        raise RuntimeError(
            f"unknown profile {profile!r}; expected one of {sorted(PROFILES)}"
        )
    mode_file = Path('/home/iecme/omnifleet_a2_ws/deploy/111-standard/config/architecture.env')
    configured_mode = 'pure_mola'
    if mode_file.is_file():
        values={}
        for line in mode_file.read_text().splitlines():
            if '=' in line:
                key,value=line.split('=',1);values[key.strip()]=value.strip()
        configured_mode=values.get('OMNIFLEET_ARCHITECTURE',configured_mode)
    required_mode='rep105' if profile in {'simple_rep105','smoother_direct'} else 'pure_mola'
    if configured_mode != required_mode:
        raise RuntimeError(
            f"architecture mismatch: profile {profile!r} requires {required_mode!r}, "
            f"but /home/iecme/omnifleet_a2_ws/deploy/111-standard/config/architecture.env selects {configured_mode!r}; "
            "run switch_architecture.sh before launching"
        )
    if profile == "integrated":
        return [IncludeLaunchDescription(PythonLaunchDescriptionSource(
            "/home/iecme/omnifleet_a2_ws/src/system/omnifleet_bringup/launch/mola_integrated_localization.launch.py"),
            launch_arguments={
                "map_path": LaunchConfiguration("map_path"),
                "map_reload_mode": LaunchConfiguration("map_reload_mode"),
                "initial_pose": LaunchConfiguration("initial_pose"),
                "map_dir": LaunchConfiguration("map_dir"),
            }.items())]
    sensor_share = Path(
        get_package_share_directory("omnifleet_sensor_processing")
    )
    localization_share = Path(get_package_share_directory("omnifleet_localization"))
    mola_share = Path(get_package_share_directory("mola_lidar_odometry"))
    smoother_share = Path(
        get_package_share_directory("mola_state_estimation_smoother")
    )
    upstream_launch = mola_share / "ros2-launchs" / "ros2-lidar-odometry.launch.py"
    smoother_system = (
        smoother_share / "mola-cli-launchs" / "state_estimator_ros2.yaml"
    )
    pipeline = mola_share / "pipelines" / "lidar3d-gicp.yaml"
    calibration = sensor_share / "config" / "airy_imu_calibration.yaml"
    smoother_config = smoother_share / "params" / "smoother_lio_only.yaml"
    for path in (
        upstream_launch,
        smoother_system,
        pipeline,
        calibration,
        smoother_config,
    ):
        if not path.is_file():
            raise RuntimeError(f"missing experiment dependency: {path}")

    output_root = Path(
        LaunchConfiguration("map_dir").perform(context)
    ).expanduser().resolve() / "experiments" / profile
    output_root.mkdir(parents=True, exist_ok=True)

    map_path = LaunchConfiguration("map_path").perform(context).strip()
    if map_path and not Path(map_path).expanduser().is_file():
        raise RuntimeError(f"initial MOLA map does not exist: {map_path}")
    initial_pose = LaunchConfiguration('initial_pose').perform(context).strip()
    timing_trace = _as_bool(LaunchConfiguration('timing_trace').perform(context))
    timing_trace_dir = Path(LaunchConfiguration('timing_trace_dir').perform(context).strip()).expanduser().resolve()
    if timing_trace:
        timing_trace_dir.mkdir(parents=True, exist_ok=True)

    height_file = Path('/home/iecme/.local/share/omnifleet_t2/map-height.json')
    heights = json.loads(height_file.read_text()) if height_file.exists() else {'slice_z_min': -0.03, 'slice_z_max': 2.0}
    use_smoother = profile == "smoother_direct"
    fusion_enabled = _as_bool(os.environ.get("OMNIFLEET_STATE_FUSION", "false"))
    if fusion_enabled and profile != "simple_direct":
        raise RuntimeError("Wheel velocity fusion requires the simple_direct profile")
    actions = [
        SetEnvironmentVariable("MOLA_LOCALIZATION_PUBLISH_TF", "false" if fusion_enabled else "true"),
        SetEnvironmentVariable("MOLA_LOCALIZATION_PUBLISH_ODOM_MSGS", "true"),
        SetEnvironmentVariable("MOLA_SAVE_MM", str(output_root / "local_map.mm")),
        SetEnvironmentVariable("MOLA_VERBOSITY_MOLA_LO", "WARN"),
        SetEnvironmentVariable("MOLA_LO_PUBLISH_DESKEWED_SCANS", "false"),
        SetEnvironmentVariable("MOLA_LO_PUBLISH_NAVIGATION_DESKEWED_SCANS", "true"),
        SetEnvironmentVariable("ROS_ARGS", '["-r", "/lidar_odometry/deskewed_scan_points:=/navigation/deskewed_points"]'),
        SetEnvironmentVariable("ROS_ARGS", '["-r", "/lidar_odometry/deskewed_scan_points:=/navigation/deskewed_points"]'),
        SetEnvironmentVariable("MOLA_LO_DEBUG_ICP_QUALITY", "false"),
        # Preserve sensor acquisition time; ROS use_sim_time remains false.
        SetEnvironmentVariable("MOLA_ROS2_PUBLISH_IN_SIM_TIME", "true"),
        SetEnvironmentVariable("MOLA_ROS2_TRANSFORM_TOLERANCE", "0.0"),
        SetEnvironmentVariable("MOLA_OPTIMIZE_TWIST", "false"),
        SetEnvironmentVariable("MOLA_LOCALMAP_CLASS", "mola::KeyframePointCloudMap"),
        SetEnvironmentVariable("MOLA_LOCALMAP_APPROXIMATE_COV", "false"),
        SetEnvironmentVariable("MOLA_TBB_THREADS", os.environ.get("MOLA_TBB_THREADS", "4")),
        SetEnvironmentVariable("MOLA_MAX_ICP_ITERATIONS", "50"),
        SetEnvironmentVariable("MOLA_DECIMATED_POINTS_MAP", "3000"),
        SetEnvironmentVariable("MOLA_CLOUD_DECIMATION_VOXEL_SIZE_MAP", "0.15"),
        SetEnvironmentVariable("MOLA_ICP_CLOUD_DECIMATION", "0.60"),
        SetEnvironmentVariable("MOLA_MAP_CLOUD_DECIMATION", "0.30"),
        SetEnvironmentVariable("MOLA_LOCAL_VOXELMAP_RESOLUTION", "0.60"),
        SetEnvironmentVariable("MOLA_TF_FOOTPRINT_LINK", ""),
        SetEnvironmentVariable("MOLA_NAV_GRID_RESOLUTION", "0.10"),
        SetEnvironmentVariable("MOLA_NAV_GRID_Z_MIN", str(heights['slice_z_min'])),
        SetEnvironmentVariable("MOLA_NAV_GRID_Z_MAX", str(heights['slice_z_max'])),
        SetEnvironmentVariable("MOLA_PUBLISH_LOCAL_MAP_UPDATES_EVERY_N", "2"),
        SetEnvironmentVariable("MOLA_ROS2_PUBLISH_MAPS_PERIOD", "0.5"),
        SetEnvironmentVariable("MOLA_SAVE_DEBUG_TRACES", "true" if timing_trace else "false"),
        SetEnvironmentVariable("MOLA_DEBUG_TRACES_FILE", str(timing_trace_dir / "mola-debug-traces.csv")),
        SetEnvironmentVariable("LIDAR_POSE_X", "0.005230903625488281"),
        SetEnvironmentVariable("LIDAR_POSE_Y", "2.514570951461792e-08"),
        SetEnvironmentVariable("LIDAR_POSE_Z", "0.3160250782966614"),
        SetEnvironmentVariable("LIDAR_POSE_YAW", "0.0"),
        SetEnvironmentVariable("LIDAR_POSE_PITCH", "-2.3494320489470027e-07"),
        SetEnvironmentVariable("LIDAR_POSE_ROLL", "0.0"),
        SetEnvironmentVariable("IMU_POSE_X", "0.005230903625488281"),
        SetEnvironmentVariable("IMU_POSE_Y", "2.514570951461792e-08"),
        SetEnvironmentVariable("IMU_POSE_Z", "0.3160250782966614"),
        SetEnvironmentVariable("IMU_POSE_YAW", "0.0"),
        SetEnvironmentVariable("IMU_POSE_PITCH", "-2.3494320489470027e-07"),
        SetEnvironmentVariable("IMU_POSE_ROLL", "0.0"),
    ]
    if map_path and not initial_pose and not map_reload_mode:
        actions.append(LogInfo(msg='Saved map loaded in localization-only mode. Set initial pose via /initialpose or /relocalize_near_pose, then set MOLA active=true; Nav2 waits for localization.'))
    if map_path and map_reload_mode:
        actions.append(LogInfo(msg='Saved map loaded in map-reload mode. MOLA starts active with IMU deskew and continuous ICP; loaded map remains read-only.'))
    if use_smoother:
        actions.extend([
            SetEnvironmentVariable("MOLA_LINK_FIRST_POSE_SIGMA", "1e-6"),
            SetEnvironmentVariable("MOLA_NAVSTATE_ENFORCE_PLANAR_MOTION", "true"),
            SetEnvironmentVariable("MOLA_INITIAL_TWIST_SIGMA_LIN", "0.05"),
            SetEnvironmentVariable("MOLA_INITIAL_TWIST_SIGMA_ANG", "0.05"),
            SetEnvironmentVariable("MOLA_STATE_ESTIMATOR_PUBLISH_RATE", "10"),
            SetEnvironmentVariable("MOLA_PUBLISH_MAP_TO_ODOM_TF", "true"),
            SetEnvironmentVariable("MOLA_STATE_ESTIMATOR_PUBLISH_TWIST", "true"),
            SetEnvironmentVariable("MOLA_MAP_TO_ODOM_FRAME", "wheel_odom"),
            SetEnvironmentVariable("MOLA_MAP_TO_ODOM_CHILD_FRAME", "odom"),
        ])

    imu_adapter = Node(
        package="omnifleet_sensor_processing",
        executable="airy_imu_adapter_buffered",
        name="omnifleet_t2_experiment_imu_adapter",
        output="screen",
        respawn=True,
        respawn_delay=2.0,
        parameters=[str(calibration)],
    )
    if map_reload_mode or profile not in {"simple_direct_observation"}:
        actions.append(imu_adapter)

    use_imu = map_reload_mode or profile not in {"simple_direct_observation"}
    mola_arguments = {
        # BridgeROS2 resolves its input names independently of the ROS namespace;
        # pass absolute robot-scoped topics so the sensor subscriptions are real.
        "lidar_topic_name": os.environ.get("OMNIFLEET_LIDAR_POINTS_TOPIC", "/rslidar_points"),
        "lidar_topic_type": "PointCloud2",
        "imu_topic_name": os.environ.get("OMNIFLEET_LIDAR_IMU_TOPIC", "/rslidar_imu_data_corrected") if use_imu else "",
        "lidar_qos_reliability": "best_effort",
        "lidar_qos_depth": "1",
        "imu_qos_reliability": "best_effort",
        "imu_qos_depth": "1000",
        "use_imu_for_lio": "True",
        "ignore_lidar_pose_from_tf": "True",
        "ignore_imu_pose_from_tf": "True",
        "mola_deskew_method": "MotionCompensationMethod::IMU",
        "mola_tf_base_link": frame("base_link"),
        "mola_lo_reference_frame": frame("map"),
        "mola_state_estimator_reference_frame": frame("map"),
        "mola_bridge_odometry_frame": frame("odom"),
        "mola_lo_pipeline": str(pipeline),
        "mola_initial_map_mm_file": map_path,
        # REP-105: MOLA emits map -> odom; the chassis owns odom -> base_link.
        "publish_localization_following_rep105": "True",
        "forward_ros_tf_odom_to_mola": "False",
        "use_state_estimator": "False",
        "enforce_planar_motion": "False",
        "localization_publish_tf_source": "lidar_odometry",
        "localization_publish_odom_source": "lidar_odometry",
        "start_active": "True" if map_reload_mode or initial_pose or not map_path else "False",
        "start_mapping_enabled": "True" if not map_path else "False",
        "use_mola_gui": "False",
        "use_rviz": "False",
        "use_diagnostic_aggregator": "False",
        "use_sim_time": "False",
    }
    if initial_pose:
        mola_arguments['initial_pose']=initial_pose
        mola_arguments['initial_localization_method']='InitLocalization::FixedPose'
    if use_smoother:
        # The LIO process publishes pose messages only. A separate Smoother
        # fuses those poses with /odom and owns the sole map -> odom TF.
        mola_arguments.update({
            "publish_localization_following_rep105": "False",
        })
    elif profile in {"simple_direct", "simple_direct_observation"}:
        # Official MOLA direct mode: publish map -> base_link and do not
        # query an external wheel odom TF for REP-105 composition.
        mola_arguments.update({
            "publish_localization_following_rep105": "False",
            "forward_ros_tf_odom_to_mola": "False",
            "enforce_planar_motion": "False" if fusion_enabled else "True",
        })
    elif profile == "simple_rep105":
        # Official Simple Estimator REP-105 path: feed wheel odometry as a
        # direct nav_msgs/Odometry source while the chassis owns odom->base_link.
        mola_arguments.update({
            "forward_ros_tf_odom_to_mola": "False",
            "odom_topic_name": os.environ.get("OMNIFLEET_WHEEL_ODOM_TOPIC", "/wheel/odometry"),
            "odom_sensor_label": "wheel_odom",
            "enforce_planar_motion": "True",
        })
    lio_group_actions = [
        # LIO is the only MOLA TF publisher and follows REP-105.
        SetEnvironmentVariable(
            "MOLA_LOCALIZATION_PUBLISH_TF",
            "false" if use_smoother or fusion_enabled else "true",
        ),
        SetRemap(src="/lidar_odometry/nav_grid_gridmap", dst="/map"),
        SetRemap(src="/lidar_odometry/deskewed_scan_points", dst="/navigation/deskewed_points"),
        ExecuteProcess(
            name="mola_latest_process",
            output="screen",
            cmd=[
                "bash", "-lc",
                "source /home/iecme/omnifleet_a2_ws/src/system/omnifleet_fleet/env.bash; "
                "exec ros2 launch " + shlex.quote(str(upstream_launch)) + " " +
                " ".join(
                    f"{key}:={shlex.quote(str(value))}"
                    for key, value in list(mola_arguments.items()) + [
                        ("use_namespace", "false"),
                        ("namespace", ""),
                        ("use_namespaced_tf", "false"),
                    ]
                    if value not in ("", None)
                ),
            ],
        ),
    ]
    actions.append(
        GroupAction(scoped=True, actions=lio_group_actions)
    )
    if profile in {"simple_direct", "simple_direct_observation"}:
        actions.append(Node(package="omnifleet_sensor_processing", executable="lidar_velocity.py", output="screen", respawn=True, respawn_delay=2.0))
    nav_grid = Node(
        package="omnifleet_map_tf_generator",
        executable="mola_realtime_nav_grid.py",
        name="mola_realtime_nav_grid",
        output="screen",
        respawn=True,
        respawn_delay=2.0,
        remappings=[
            ("/tf", "" + "/tf"),
            ("/tf_static", "" + "/tf_static"),
        ],
    )
    actions.append(nav_grid)
    if use_smoother:
        actions.append(
            GroupAction(scoped=True, actions=[
                SetEnvironmentVariable(
                    "MOLA_STATE_ESTIMATOR_YAML", str(smoother_config)
                ),
                SetEnvironmentVariable("ODOM1_TOPIC", "/lidar_odometry/pose"),
                SetEnvironmentVariable("ODOM1_LABEL", "lidar_odom"),
                SetEnvironmentVariable("ODOM2_TOPIC", os.environ.get("OMNIFLEET_WHEEL_ODOM_TOPIC", "/wheel/odometry")),
                SetEnvironmentVariable("ODOM2_LABEL", "wheel_odom"),
                SetEnvironmentVariable("ODOM3_TOPIC", ""),
                SetEnvironmentVariable("ODOM4_TOPIC", ""),
                SetEnvironmentVariable("IMU_TOPIC", ""),
                SetEnvironmentVariable("GNSS_TOPIC", ""),
                SetEnvironmentVariable("MOLA_WITH_GUI", "false"),
                SetEnvironmentVariable("MOLA_TF_MAP", "map"),
                SetEnvironmentVariable("MOLA_TF_BASE_LINK", "base_link"),
                SetEnvironmentVariable("MOLA_TF_FOOTPRINT_LINK", ""),
                SetEnvironmentVariable(
                    "MOLA_FORWARD_ROS_TF_ODOM_TO_MOLA", "false"
                ),
                SetEnvironmentVariable("MOLA_LOCALIZATION_PUBLISH_TF", "true"),
                SetEnvironmentVariable("MOLA_PUBLISH_TWIST_FROM_LATEST_ODOM", "true"),
                SetEnvironmentVariable("MOLA_LATEST_ODOM_TWIST_SOURCE", "wheel_odom"),
                SetEnvironmentVariable("MOLA_LATEST_ODOM_TWIST_MAX_AGE", "0.5"),
                SetEnvironmentVariable(
                    "MOLA_LOCALIZATION_PUBLISH_ODOM_MSGS", "true"
                ),
                SetEnvironmentVariable(
                    "MOLA_LOCALIZATION_PUBLISH_TF_SOURCE",
                    "state_estimation/map_odom",
                ),
                SetEnvironmentVariable(
                    "MOLA_LOCALIZATION_PUBLISH_ODOM_MSGS_SOURCE",
                    "state_estimation",
                ),
                Node(
                    package="mola_launcher",
                    executable="mola-cli",
                    namespace="mola_smoother",
                    name="mola_smoother_cli",
                    output="screen",
                    arguments=[str(smoother_system)],
                    remappings=[("/tf", "/tf"), ("/tf_static", "/tf_static")],
                ),
            ])
        )
    if fusion_enabled:
        actions.append(IncludeLaunchDescription(PythonLaunchDescriptionSource(
            str(smoother_share / "ros2-launchs" / "ros2-tracked-lidar-wheel-pose.launch.py"))))
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("profile", default_value="integrated"),
        DeclareLaunchArgument('initial_pose',default_value='',description='[x,y,z,yaw_deg,pitch_deg,roll_deg] in the saved map; otherwise wait for initial localization'),
        DeclareLaunchArgument('map_reload_mode',default_value='false',description='Continue active MOLA ICP and local-map updates after loading a saved map'),
        DeclareLaunchArgument('timing_trace',default_value='false',description='Save native MOLA per-scan debug traces to timing_trace_dir'),
        DeclareLaunchArgument('timing_trace_dir',default_value='/home/iecme/.local/share/omnifleet_t2/mola-timing'),
        DeclareLaunchArgument(
            "map_dir", default_value="/var/lib/omnifleet_a2/maps"
        ),
        DeclareLaunchArgument(
            "map_path",
            # Fresh mapping is the safe default. Pass an explicit .mm path
            # only when intentionally running localization from a saved map.
            default_value="",
        ),
        OpaqueFunction(function=_launch),
    ])


_unscoped_generate = generate_launch_description
def generate_launch_description():
    from fleet_scope import scoped
    return scoped(_unscoped_generate())
