"""Vehicle-local ROS names; identity is retained for fleet metadata."""
import json,os
from pathlib import Path
ROOT=Path('/home/iecme/omnifleet_ws/src/system/omnifleet_fleet')
def robot_id(value=None):
    value=os.environ.get('OMNIFLEET_ROBOT_ID','') if value is None else str(value)
    if not value:raise ValueError('missing robot identity')
    return value
def frame(name):return name.lstrip('/')
def remaps():
    rules=[]
    if os.environ.get('OMNIFLEET_FOXGLOVE_DIRECT_ACTIONS')!='1':
        for action in ('navigate_to_pose','navigate_through_poses'):
            for suffix in ('','/_action/send_goal','/_action/get_result','/_action/cancel_goal','/_action/feedback','/_action/status'):
                rules.append(('bt_navigator:/'+action+suffix,'/navigation_backend/'+action+suffix))
    for action,destination in (('follow_waypoints','follow_waypoints'),('navigate_to_pose','fleet_waypoint_to_pose')):
        for suffix in ('','/_action/send_goal','/_action/get_result','/_action/cancel_goal','/_action/feedback','/_action/status'):
            rules.append(('waypoint_follower:/'+action+suffix,'/navigation_backend/'+destination+suffix))
    for node in ('controller_server','behavior_server','bt_navigator'):
        for source in ('cmd_vel','/cmd_vel'):rules.append((node+':'+source,'/navigation/nav_cmd_vel'))
    rules.append(('/lidar_odometry/nav_grid_gridmap','/map'))
    return rules
def ros_args():
    args=['--ros-args','-r','__ns:=/']
    for src,dst in remaps():args+=['-r',src+':='+dst]
    return args
def scoped(description):
    from launch import LaunchDescription
    from launch_ros.actions import SetRemap
    return LaunchDescription([*[SetRemap(src=a,dst=b) for a,b in remaps()],*description.entities])
def resolve_scope(value=None):
    rid=robot_id(value)
    return {'schema_version':1,'robot_identity':rid,'ros_namespace':'','frame_prefix':'','source':'vehicle_local',
            'topics':{'raw_lidar':'/rslidar_points','pose':'/lidar_odometry/pose','odom':'/odom','tf':'/tf','tf_static':'/tf_static','deskewed_points':'/navigation/deskewed_points','map':'/map'},
            'frames':{'map':'map','odom':'odom','base':'base_link','lidar':'rslidar','navigation_lidar':'navigation_lidar'}}
def resolved_scope(value=None):return resolve_scope(value)
def write_resolved(path,value=None):
    target=Path(path);tmp=target.with_suffix(target.suffix+'.tmp')
    tmp.write_text(json.dumps(resolve_scope(value),indent=2)+'\n');tmp.replace(target);return target
