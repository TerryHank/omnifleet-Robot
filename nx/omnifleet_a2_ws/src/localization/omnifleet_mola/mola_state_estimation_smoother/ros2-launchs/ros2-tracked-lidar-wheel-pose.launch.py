from pathlib import Path
import os
from ament_index_python.packages import get_package_prefix, get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    runtime = Path(get_package_prefix('mola_state_estimation_smoother')) / 'lib' / 'official_pose'
    env = {'MOLA_WITH_GUI': 'false', 'MOLA_REQUIRE_FRESH_REFERENCE_POSE': 'true',
           'MOLA_MODULES_LIB_PATH': str(runtime),
           'LD_LIBRARY_PATH': str(runtime) + ':' + str(runtime / 'deps')}
    share = Path(get_package_share_directory('mola_state_estimation_smoother'))
    return LaunchDescription([
        ExecuteProcess(name='mola_wheel_pose_smoother', output='screen', additional_env=env,
                       respawn=True, respawn_delay=2.0,
                       cmd=['/home/iecme/omnifleet_a2_ws/install_111/mola_launcher/lib/mola_launcher/mola-cli',
                            str(share / 'mola-cli-launchs' / 'tracked_lidar_wheel_pose.yaml')]),
    ])
