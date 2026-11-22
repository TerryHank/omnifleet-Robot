"""Gemini Pro official SDK v1 native RGB and millimetre depth."""
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch_ros.actions import Node, SetRemap
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    return LaunchDescription([GroupAction([
        # Keep the Jetson-linked camera process out of the JPEG encoding path.
        SetRemap(src='/camera/color/image_raw/compressed', dst='/camera/color/driver_compressed_unused'),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
        get_package_share_directory('orbbec_camera')+'/launch/astra_stereo_u3.launch.py'),
        launch_arguments={
            'camera_name':'camera', 'enable_color':'true', 'enable_depth':'true', 'enable_ir':'false',
            'color_width':'640', 'color_height':'480', 'color_fps':'30', 'color_format':'MJPG',
            'depth_width':'640', 'depth_height':'400', 'depth_fps':'30', 'depth_format':'Y11',
            # Gemini Pro SDK v1 RGB exposure unit is 100 us; AE ceiling is unsupported.
            'enable_color_auto_exposure':'true', 'color_exposure':'-1', 'color_gain':'64',
            'enable_ir_auto_exposure':'false',
            'color_info_url':'',
            'depth_registration':'false', 'align_mode':'HW', 'enable_point_cloud':'false',
            'enable_colored_point_cloud':'false', 'enable_publish_extrinsic':'true',
            'enable_soft_filter':'true', 'enable_depth_scale':'true',
        }.items()),
        ]), Node(package='image_transport', executable='republish', name='gemini_pro_rgb_jpeg',
                arguments=['raw', 'compressed'],
                remappings=[('in', '/camera/color/image_raw'),
                            ('out/compressed', '/camera/color/image_raw/compressed')],
                respawn=True, respawn_delay=2.0)])

