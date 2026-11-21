"""Native RTAB-Map ICP and grid output, isolated from the production map/TF owners."""
from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def _nodes(context):
    value=lambda key:LaunchConfiguration(key).perform(context)
    namespace=value('namespace').strip('/')
    database=Path(value('database_path')).expanduser()
    database.parent.mkdir(parents=True,exist_ok=True)
    resolution=float(value('resolution'))
    if resolution<=0:raise ValueError('resolution must be positive')
    use_icp=value('use_icp_odometry').lower()=='true'
    odom_topic='odom' if use_icp else value('external_odom_topic')
    tf=[('/tf',value('tf_topic')),('/tf_static',value('tf_static_topic'))]
    common={'frame_id':value('base_frame'),'publish_tf':False,'wait_for_transform':0.2}
    nodes=[]
    if use_icp:
        nodes.append(Node(package='rtabmap_odom',executable='icp_odometry',name='icp_odometry',
            namespace=namespace,output='screen',parameters=[common,{
                'odom_frame_id':namespace+'/odom','qos':2}],
            remappings=[('scan_cloud',value('cloud_topic')),('odom','odom'),*tf]))
    nodes.append(Node(package='rtabmap_slam',executable='rtabmap',name='rtabmap',namespace=namespace,
        output='screen',parameters=[common,{'map_frame_id':namespace+'/map','database_path':str(database),
            'subscribe_depth':False,'subscribe_rgb':False,'subscribe_scan_cloud':True,
            'subscribe_odom':True,'approx_sync':True,'qos_scan':2,'qos_odom':1,
            'Reg/Strategy':'1','Grid/Sensor':'0','Grid/3D':'false','Grid/RayTracing':'true',
            'Grid/CellSize':str(resolution)}],
        remappings=[('scan_cloud',value('cloud_topic')),('odom',odom_topic),('grid_map','map'),*tf]))
    return nodes

def generate_launch_description():
    defaults={'namespace':'rtabmap_trial','base_frame':'base_link',
              'cloud_topic':'/rslidar_points','tf_topic':'/tf',
              'tf_static_topic':'/tf_static','use_icp_odometry':'true',
              'external_odom_topic':'/rtabmap_trial/fixture_odom','resolution':'0.05',
              'database_path':'/home/iecme/omnifleet_a2_data/maps/rtabmap/trial.db'}
    return LaunchDescription([DeclareLaunchArgument(k,default_value=v) for k,v in defaults.items()]+[
        OpaqueFunction(function=_nodes)])
