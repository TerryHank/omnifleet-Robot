from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share=Path(get_package_share_directory('omnifleet_person_follow'))
    motion=LaunchConfiguration('enable_motion')
    transport={'ZENOH_CONFIG_OVERRIDE':'transport/shared_memory/enabled=false;transport/shared_memory/transport_optimization/enabled=false;connect/timeout_ms=12000;transport/unicast/open_timeout=8000'}
    return LaunchDescription([
        DeclareLaunchArgument('enable_motion',default_value='false'),
        Node(package='body_tracking',executable='body_tracking',namespace='body_tracking_104',output='screen',
             parameters=[str(share/'config/body_tracking_104.yaml'),{
                 'enable_motion':ParameterValue(motion,value_type=bool)}],
             remappings=[('body_tracking_cmd','/vision/body_tracking/cmd_vel'),
                         ('body_tracking_state','/vision/body_tracking/native_status')],
             arguments=['--ros-args','--log-level','error'],additional_env=transport),
        Node(package='omnifleet_person_follow',executable='person_follow_node',
             name='course_gesture_person_follow',output='screen',
             prefix='/home/iecme/omnifleet_ws/.env/vision/bin/python',
             parameters=[str(share/'config/person_follow.yaml'),{
                 'controller_backend':'body_tracking', 'auto_follow':False,
                 'camera_backend':'orbbec', 'use_local_frames':False, 'depth_max_m':6.0,
                 'image_topic':'/camera/color/native1080',
                 'face_model_path':'',
                 'jpeg_quality':60, 'preview_interval_s':0.125,
                 'enable_motion':ParameterValue(motion,value_type=bool),
                 'status_topic':'/vision/body_tracking/status',
                 'debug_image_topic':'/vision/body_tracking/debug',
                 'debug_compressed_topic':'/vision/course_gui/course_04_09_body_tracking/debug/compressed'}],
             additional_env={**transport,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','OPENCV_FOR_THREADS_NUM':'1'})])
