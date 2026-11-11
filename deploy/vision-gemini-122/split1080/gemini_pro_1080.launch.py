"""Native 1080p RGB and independent depth for Gemini Pro 122."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import EmitEvent, ExecuteProcess, GroupAction, IncludeLaunchDescription
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import SetRemap


def generate_launch_description():
    config = Path(__file__).with_name("rgb1080-calibration.yaml")
    camera_launch = Path(get_package_share_directory("orbbec_camera")) / "launch/astra_stereo_u3.launch.py"
    return LaunchDescription([GroupAction([
        SetRemap(src="/tf", dst="/camera/sdk_tf"),
        SetRemap(src="/tf_static", dst="/camera/sdk_tf_static"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(camera_launch)),
            launch_arguments={
                "serial_number": "AY2755200NT",
                "color_width": "1920",
                "color_height": "1080",
                "color_fps": "30",
                "color_format": "RGB",
                "color_info_url": config.as_uri(),
                "depth_width": "640",
                "depth_height": "400",
                "depth_fps": "30",
                "depth_format": "Y11",
                "depth_registration": "false",
                "enable_ir": "false",
                "enable_point_cloud": "false",
                "publish_tf": "true",
                "enable_publish_extrinsic": "true",
            }.items(),
        ),
        ExecuteProcess(
            cmd=["/usr/bin/python3", str(Path(__file__).with_name("camera_watchdog.py"))],
            output="screen",
            on_exit=[EmitEvent(event=Shutdown(reason="Gemini Pro stream watchdog exited"))],
        ),
    ])])
