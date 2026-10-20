"""One primary StateEstimationSimple shared by LiDAR, radar IMU and wheel odometry."""
from pathlib import Path
import json
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _start(context):
    config = Path('/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mola_state_estimation_simple/config')
    env = json.loads((config / 'tracked-integrated-live-runtime.json').read_text())
    map_path = LaunchConfiguration('map_path').perform(context).strip()
    initial_pose = LaunchConfiguration('initial_pose').perform(context).strip()
    if map_path and not Path(map_path).is_file():
        raise RuntimeError('MOLA map does not exist: ' + map_path)
    output = Path(LaunchConfiguration('map_dir').perform(context)) / 'experiments' / 'integrated'
    output.mkdir(parents=True, exist_ok=True)
    env.update(MOLA_LOAD_MM=map_path, MOLA_SAVE_MM=str(output / 'local_map.mm'),
               MOLA_MAPPING_ENABLED='false' if map_path else 'true',
               MOLA_START_ACTIVE='true' if not map_path or initial_pose else 'false')
    if initial_pose:
        pose = json.loads(initial_pose)
        if len(pose) != 6:
            raise RuntimeError('initial_pose requires [x,y,z,yaw,pitch,roll]')
        env['MOLA_LO_INITIAL_LOCALIZATION_METHOD'] = 'InitLocalization::FixedPose'
        env.update({key: str(float(value)) for key, value in zip(
            ['MOLA_INITIAL_X', 'MOLA_INITIAL_Y', 'MOLA_INITIAL_Z',
             'MOLA_INITIAL_YAW', 'MOLA_INITIAL_PITCH', 'MOLA_INITIAL_ROLL'], pose)})
    sensor = Path(get_package_share_directory('omnifleet_sensor_processing'))
    return [
        Node(package='omnifleet_sensor_processing', executable='airy_imu_adapter_buffered',
             name='omnifleet_t2_experiment_imu_adapter', output='screen', respawn=True,
             parameters=[str(sensor / 'config' / 'airy_imu_calibration.yaml')]),
        ExecuteProcess(name='mola_integrated_localization', output='screen', additional_env=env,
                       cmd=['/home/iecme/omnifleet_ws/install/mola_launcher/lib/mola_launcher/mola-cli',
                            str(config / 'tracked-integrated-live-system.yaml')]),
        Node(package='omnifleet_map_tf_generator', executable='mola_realtime_nav_grid.py',
             name='mola_realtime_nav_grid', output='screen', respawn=True),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('map_path', default_value=''),
        DeclareLaunchArgument('initial_pose', default_value=''),
        DeclareLaunchArgument('map_dir', default_value='/home/iecme/omnifleet_data/maps'),
        OpaqueFunction(function=_start),
    ])
