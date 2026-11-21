from pathlib import Path
import json
import math
import os
import sys

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _start(context):
    release=Path(__file__).resolve().parent
    stage=release.parent
    runtime=json.loads((release/'runtime124.json').read_text())
    install=release/'full-arm64-install'
    runtime['AMENT_PREFIX_PATH']=str(install)+':'+os.environ.get('AMENT_PREFIX_PATH','')
    runtime['LD_LIBRARY_PATH']=':'.join([
        str(install/'lib'),str(release/'runtime-deps'),str(release/'ros-core-lib')
    ])
    recovery=LaunchConfiguration('restore_snapshot').perform(context)=='true'
    activate=json.loads((stage/'124-before-cutover-pose.json').read_text()) if recovery else {}
    runtime.update(MOLA_LOAD_MM=activate.get('compatible_map_path',''),
                   MOLA_SAVE_MM=str(stage/'mola105-current-map.mm') if os.environ.get('ROS_DOMAIN_ID') == '42' else '',
                   MOLA_MAPPING_ENABLED='true',MOLA_START_ACTIVE='true')
    grid_environment={}
    if recovery:
        runtime['MOLA_LO_INITIAL_LOCALIZATION_METHOD']='InitLocalization::FixedPose'
        runtime.update(dict(zip(
            ('MOLA_INITIAL_X','MOLA_INITIAL_Y','MOLA_INITIAL_Z','MOLA_INITIAL_YAW','MOLA_INITIAL_PITCH','MOLA_INITIAL_ROLL'),
            map(str,[*activate['map_base'][:3],*(math.degrees(v) for v in activate['map_base'][3:])]),
        )))
        seed=stage/'124-before-cutover-grid.npy'
        if seed.is_file():
            grid_environment['OMNIFLEET_MIGRATION_GRID_SEED']=str(seed)
    sensor=Path(get_package_share_directory('omnifleet_sensor_processing'))
    return [
        Node(package='omnifleet_sensor_processing', executable='airy_imu_adapter_buffered',
             name='omnifleet_t2_experiment_imu_adapter',output='screen',respawn=True,
             parameters=[str(sensor/'config'/'airy_imu_calibration.yaml')]),
        ExecuteProcess(name='mola105',output='screen',additional_env=runtime,
                       cmd=[str(install/'lib'/'mola_launcher'/'mola-cli'),
                            str(release/'live-candidate'/'tracked-mapper-candidate.yaml')]),
        ExecuteProcess(name='map_to_odom_124',output='screen',respawn=True,
                       cmd=[sys.executable,str(release/'current_pose.py'),'--ros-args','-p','publish_tf:=true']),
        ExecuteProcess(name='mola_grid_124',output='screen',respawn=True,
                       additional_env=grid_environment,
                       cmd=[sys.executable,str(release/'nav_grid124.py')]),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('restore_snapshot',default_value='false'),
        OpaqueFunction(function=_start),
    ])

