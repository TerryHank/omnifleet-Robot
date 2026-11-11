"""Offline-only entry: one official Smoother shared with the LiDAR frontend."""
from pathlib import Path
import json
from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    config = Path('/home/iecme/omnifleet_a2_ws/src/localization/omnifleet_mola/mola_state_estimation_smoother/config')
    env = json.loads((config / 'tracked-integrated-runtime.json').read_text())
    env.update(ROS_DOMAIN_ID='214', ROS_LOCALHOST_ONLY='1', RMW_IMPLEMENTATION='rmw_fastrtps_cpp')
    return LaunchDescription([
        ExecuteProcess(name='mola_integrated_offline', output='screen', additional_env=env,
                       cmd=['/home/iecme/omnifleet_a2_ws/install_111/mola_launcher/lib/mola_launcher/mola-cli',
                            str(config / 'tracked-integrated-system.yaml')]),
    ])
