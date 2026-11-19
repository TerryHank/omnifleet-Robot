from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import ExecuteProcess


def generate_launch_description():
    camera_launch = Path(get_package_share_directory('orbbec_camera')) / 'launch' / 'gemini345_lg.launch.py'
    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(camera_launch)), launch_arguments={
            'camera_name': 'camera',
            'enable_color': 'false',
            'depth_width': '640',
            'depth_height': '480',
            'uvc_backend': 'v4l2',
            'diagnostic_period': '0.0',
            'enable_frame_sync': 'false',
            'color_qos': 'SENSOR_DATA',
            'color.image_raw.enable_pub_plugins': '["image_transport/raw"]',
            'color_qos_depth': '1',
            'depth_qos': 'SENSOR_DATA',
            'depth_qos_depth': '1',
            'enable_point_cloud': 'false',
            'enable_publish_extrinsic': 'true',
            'depth_registration': 'false',
            'enable_color_undistortion': 'true',
            'align_mode': 'HW',
            'depth_fps': '30',
        }.items()),
        ExecuteProcess(
            cmd=['/usr/bin/python3', '/home/iecme/orbbec345lg-v2.10.6/rgb1080.py'],
            output='screen',
            respawn=True,
            respawn_delay=2.0,
        ),
    ])
