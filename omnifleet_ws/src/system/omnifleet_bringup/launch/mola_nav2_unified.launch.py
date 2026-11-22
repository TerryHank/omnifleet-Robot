"""System-owned Native GICP + radar IMU + wheel-pose primary Smoother + Nav2 launch."""
import os
from pathlib import Path

from ament_index_python.packages import get_package_prefix, get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription,
    OpaqueFunction, RegisterEventHandler, EmitEvent,
)
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

PROFILES = {'integrated', 'simple_direct', 'simple_direct_observation', 'simple_rep105', 'smoother_direct'}
DEFAULT_MAP = ''


def _validate_native_map(path: str) -> None:
    """Reject legacy maps before Matcher_Cov2Cov can load them."""
    import os
    import subprocess
    import tempfile

    metric_maps_prefix = Path(get_package_prefix("mola_metric_maps"))
    mp2p_prefix = Path(get_package_prefix("mp2p_icp_core"))
    plugin = metric_maps_prefix / "lib/libmola_metric_maps.so.3.2.1"
    mm2txt = mp2p_prefix / "bin/mm2txt"
    if not plugin.is_file() or not mm2txt.is_file():
        raise RuntimeError('Native map validator is unavailable')
    lib_dirs = [
        str(Path(get_package_prefix(name)) / "lib")
        for name in ("mp2p_icp_core", "mola_metric_maps", "mola_imu_preintegration", "mola_lidar_odometry")
    ]
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = ':'.join(lib_dirs + [env.get('LD_LIBRARY_PATH', '')])
    env['LD_PRELOAD'] = str(plugin)
    with tempfile.TemporaryDirectory(prefix='native-map-check-') as cwd:
        result = subprocess.run(
            [str(mm2txt), path], cwd=cwd, env=env,
            capture_output=True, text=True, timeout=20)
    output = result.stdout + '\n' + result.stderr
    if 'HashedVoxelPointCloud' in output:
        raise RuntimeError('legacy mola::HashedVoxelPointCloud map is incompatible with Matcher_Cov2Cov')
    if 'KeyframePointCloudMap' not in output:
        first = output.splitlines()[0] if output.splitlines() else 'saved_map validation failed'
        raise RuntimeError('saved_map must be a valid mola::KeyframePointCloudMap; ' + first)


def _start(context):
    import subprocess
    for unit in ('omnifleet-t2-mola.service', 'omnifleet-t2-pure-lio-nav2.service'):
        if subprocess.run(['systemctl', 'is-active', '--quiet', unit]).returncode == 0:
            raise RuntimeError('The application stack is already managed by systemd: ' + unit +
                               '; restart its services instead of starting a duplicate launch')
    profile = LaunchConfiguration('profile').perform(context).strip()
    map_path = LaunchConfiguration('map_path').perform(context).strip()
    map_dir = LaunchConfiguration('map_dir').perform(context).strip()
    initial_pose = LaunchConfiguration('initial_pose').perform(context).strip()
    map_reload_mode = LaunchConfiguration('map_reload_mode').perform(context).strip().lower() in {'1', 'true', 'yes', 'on'}
    auto_relocalization = LaunchConfiguration('auto_relocalization').perform(context).strip().lower() in {'1', 'true', 'yes', 'on'}
    startup_mode = LaunchConfiguration('startup_mode').perform(context).strip()
    timing_trace = LaunchConfiguration('timing_trace').perform(context).strip()
    timing_trace_dir = LaunchConfiguration('timing_trace_dir').perform(context).strip()
    callback_trace_file = LaunchConfiguration('callback_trace_file').perform(context).strip()
    rmw_trace_file = LaunchConfiguration('rmw_trace_file').perform(context).strip()
    if startup_mode not in {'saved_map', 'mapping'}:
        raise RuntimeError(f'unknown startup mode: {startup_mode}')
    if startup_mode == 'mapping':
        map_path = ''
        initial_pose = ''
        auto_relocalization = False
    elif not map_path:
        raise RuntimeError('saved_map mode requires a nonempty map_path')
    if profile not in PROFILES:
        raise RuntimeError(f'unknown architecture profile: {profile}')
    if map_path and not Path(map_path).expanduser().is_file():
        raise RuntimeError(f'common .mm map does not exist: {map_path}')
    if startup_mode == 'saved_map':
        _validate_native_map(map_path)

    command = [
        'ros2', 'launch', 'omnifleet_bringup', 'mola_localization.launch.py',
        'profile:=' + profile, 'map_path:=' + (map_path or ' '), 'map_dir:=' + map_dir,
        'map_reload_mode:=' + ('true' if map_reload_mode else 'false'),
        'timing_trace:=' + timing_trace, 'timing_trace_dir:=' + timing_trace_dir,
    ]
    if initial_pose:
        command.append('initial_pose:=' + initial_pose)
    trace_env = {}
    if callback_trace_file:
        trace_env['MOLA_CALLBACK_TRACE_FILE'] = callback_trace_file
    if rmw_trace_file:
        trace_env['RMW_ZENOH_TRACE_FILE'] = rmw_trace_file
    mola = ExecuteProcess(name='mola_gate', output='screen', cmd=command,
                          additional_env=trace_env or None)

    nav2_share = Path(get_package_share_directory('omnifleet_bringup'))
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(nav2_share / 'launch' / 'navigation.launch.py')),
        launch_arguments={
            'transform_tolerance': '0.8',
            'odom_topic': '/lidar_odometry/pose',
            'obstacle_topic': '/navigation/deskewed_points',
            'obstacle_clearing': 'true',
        }.items(),
    )
    readiness = Node(
        package='omnifleet_bringup', executable='nav2_readiness_gate.py',
        output='screen', arguments=['--wait-timeout', '0', '--monitor-only'])
    affinity = ExecuteProcess(
        name='cpu_affinity', output='screen',
        cmd=['bash', '-c',
             'CPU_AFFINITY_ROOT=/home/iecme/.local/share/omnifleet_t2/cpu-affinity '
             'exec /home/iecme/omnifleet_ws/src/system/operator_tools/ops/apply_cpu_affinity_113.sh'])
    cleanup = Node(
        package='omnifleet_bringup',
        executable='cleanup_unified_application_nodes.py', output='screen')
    auto = None
    if auto_relocalization and not map_reload_mode and not initial_pose:
        script = Path('/home/iecme/omnifleet_ws/src/system/omnifleet_fleet/relocalization/mola_auto_relocalize.sh')
        if not script.is_file():
            raise RuntimeError(f'MOLA auto-relocalization helper does not exist: {script}')
        auto = ExecuteProcess(name='mola_auto_relocalization', output='screen', cmd=['bash', str(script), map_path])

    def after_auto(event, _context):
        return [nav2, readiness] if event.returncode == 0 else [EmitEvent(event=Shutdown(reason='MOLA auto-relocalization failed'))]

    def after_readiness(event, _context):
        return [affinity] if event.returncode == 0 else [EmitEvent(event=Shutdown(reason='Nav2 readiness failed'))]

    def after_affinity(event, _context):
        return [] if event.returncode == 0 else [EmitEvent(event=Shutdown(reason='CPU affinity failed'))]

    def after_cleanup(event, _context):
        if event.returncode != 0:
            return [EmitEvent(event=Shutdown(reason='application cleanup failed'))]
        if auto is None:
            return [mola, RegisterEventHandler(OnProcessStart(target_action=mola, on_start=[nav2, readiness]))]
        return [
            mola,
            RegisterEventHandler(OnProcessStart(target_action=mola, on_start=[auto])),
            RegisterEventHandler(OnProcessExit(target_action=auto, on_exit=after_auto)),
        ]

    return [
        RegisterEventHandler(OnProcessExit(target_action=cleanup, on_exit=after_cleanup)),
        RegisterEventHandler(OnProcessExit(target_action=readiness, on_exit=after_readiness)),
        RegisterEventHandler(OnProcessExit(target_action=affinity, on_exit=after_affinity)),
        RegisterEventHandler(OnProcessExit(target_action=mola, on_exit=[EmitEvent(event=Shutdown(reason='MOLA process exited'))])),
        cleanup,
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('profile', default_value='integrated'),
        DeclareLaunchArgument('startup_mode', default_value='mapping', description='saved_map or mapping'),
        DeclareLaunchArgument('map_path', default_value=DEFAULT_MAP),
        DeclareLaunchArgument('map_dir', default_value='/home/iecme/omnifleet_data/maps/home_legacy'),
        DeclareLaunchArgument('initial_pose', default_value=''),
        DeclareLaunchArgument('map_reload_mode', default_value='true'),
        DeclareLaunchArgument('auto_relocalization', default_value='false'),
        DeclareLaunchArgument('timing_trace', default_value='false'),
        DeclareLaunchArgument('timing_trace_dir', default_value='/home/iecme/.local/share/omnifleet_t2/mola-timing'),
        DeclareLaunchArgument('callback_trace_file', default_value=''),
        DeclareLaunchArgument('rmw_trace_file', default_value=''),
        OpaqueFunction(function=_start),
    ])


_unscoped_generate = generate_launch_description


def generate_launch_description():
    from fleet_scope import scoped
    return scoped(_unscoped_generate())



