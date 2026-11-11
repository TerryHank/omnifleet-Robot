"""Gemini Pro via the installed official SDK v1 driver, native RGB/depth."""
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([IncludeLaunchDescription(PythonLaunchDescriptionSource(
        get_package_share_directory('orbbec_camera')+'/launch/astra_stereo_u3.launch.py'),
        launch_arguments={
            'camera_name':'camera', 'enable_color':'true', 'enable_depth':'true', 'enable_ir':'false',
            'color_width':'640', 'color_height':'480', 'color_fps':'30', 'color_format':'MJPG',
            'depth_width':'1280', 'depth_height':'800', 'depth_fps':'30', 'depth_format':'Y11',
            # Gemini Pro SDK v1 RGB exposure unit is 100 us; AE ceiling is unsupported.
            'enable_color_auto_exposure':'false', 'color_exposure':'100', 'color_gain':'64',
            'enable_ir_auto_exposure':'false',
            'depth_registration':'false', 'enable_point_cloud':'false',
            'enable_colored_point_cloud':'false', 'enable_publish_extrinsic':'true',
            'enable_soft_filter':'true', 'enable_depth_scale':'true',
        }.items()),
        Node(package='tf2_ros', executable='static_transform_publisher',
             name='gemini_pro_mount', arguments=['--x','0.05','--y','0','--z','0',
                 '--roll','0','--pitch','0','--yaw','0',
                 '--frame-id','rslidar','--child-frame-id','camera_link'])])
