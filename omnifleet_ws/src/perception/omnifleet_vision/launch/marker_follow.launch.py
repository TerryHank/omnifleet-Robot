"""QR/AprilTag detection and KCF continuity through the existing object follower."""
from pathlib import Path
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def setup(context):
    kind = LaunchConfiguration('marker_kind').perform(context)
    if kind not in ('qr', 'apriltag'):
        raise ValueError('marker_kind must be qr or apriltag')
    share = Path(get_package_share_directory('omnifleet_vision'))
    prefix = '/vision/'+kind
    source = LaunchConfiguration('distance_source')
    motion = ParameterValue(LaunchConfiguration('enable_motion'), value_type=bool)
    settings = yaml.safe_load((share/'config/kcf_follower.yaml').read_text())['kcf_follower']['ros__parameters']
    settings.update(enable_motion=motion, use_gui=False, external_tracker=True, remote_roi=True,
                    sparse_depth=True, inline_sparse_depth=False, tracking_scale=1.,
                    tracker_color_topic=prefix+'/debug', output_image_topic=prefix+'/follow/image',
                    target_distance=ParameterValue(LaunchConfiguration('target_distance'),value_type=float))
    detector_params = dict(input_topic='/camera/color/image_raw', debug_topic=prefix+'/debug',
                           result_topic=prefix+'/result', distance_source=source, use_gui=False)
    detector_files = [str(share/'config/apriltag_36h11_210mm.yaml')] if kind=='apriltag' else []
    return [
        Node(package='omnifleet_vision', executable=kind+'_recognition_node.py', name='course_'+kind,
             parameters=detector_files+[detector_params], output='screen',
             prefix='/home/iecme/omnifleet_ws/.env/vision/bin/python',
             additional_env={'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}),
        Node(package='omnifleet_vision', executable='kcf_follower_node', name=kind+'_follower',
             parameters=[settings], output='screen', remappings=[
                 ('/cmd_vel_vision','/cmd_vel'), ('/vision/nanotrack/selected',prefix+'/tracks'),
                 ('/omnifleet_vision/kcf/status',prefix+'/follow/status'),
                 ('/omnifleet_vision/kcf/depth',prefix+'/follow/range'),
                 ('/omnifleet_vision/kcf/targets_3d',prefix+'/follow/targets_3d')])]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('marker_kind',default_value='qr'),
        DeclareLaunchArgument('distance_source',default_value='depth'),
        DeclareLaunchArgument('enable_motion',default_value='false'),
        DeclareLaunchArgument('target_distance',default_value='2.0'),
        OpaqueFunction(function=setup)])
