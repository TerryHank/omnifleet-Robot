from fleet_scope import frame
"""System-owned Nav2 bringup using the active final localization state."""

from pathlib import Path
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from nav2_common.launch import RewrittenYaml
from launch_ros.actions import Node, SetParameter


def generate_launch_description():
    height_overlay = Path('/home/iecme/omnifleet_ws/install/nav2_costmap_2d')
    if not (height_overlay / 'lib/libnav2_costmap_2d_core.so').exists():
        raise RuntimeError('Nav2 高度过滤修复库缺失，请恢复或构建 nav2_height_ws')
    planner = Path(get_package_share_directory("omnifleet_planner"))
    odom_input = ("" + "/state_estimation/pose"
                  if os.environ.get("OMNIFLEET_STATE_FUSION", "false").lower() in {"1", "true", "yes"}
                  else LaunchConfiguration("odom_topic"))
    bt_template = planner / "behavior_trees" / "navigate_through_poses_with_selectors.xml"
    bt_scoped = str(bt_template)
    configured_params = RewrittenYaml(
        source_file="/home/iecme/omnifleet_ws/src/planning/omnifleet_planner/config/nav2_t2.yaml",
        root_key="",
        param_rewrites={
            "transform_tolerance": LaunchConfiguration("transform_tolerance"),
            "local_costmap.local_costmap.ros__parameters.obstacle_layer.publish_voxel_map": LaunchConfiguration("publish_voxel_debug"),
            "global_costmap.global_costmap.ros__parameters.obstacle_layer.publish_voxel_map": LaunchConfiguration("publish_voxel_debug"),
            "odom_topic": odom_input,
            "bt_navigator.ros__parameters.global_frame": frame("map"),
            "bt_navigator.ros__parameters.robot_base_frame": frame("base_link"),
            "behavior_server.ros__parameters.global_frame": frame("map"),
            "behavior_server.ros__parameters.robot_base_frame": frame("base_link"),
            "local_costmap.local_costmap.ros__parameters.robot_base_frame": frame("base_link"),
            "global_costmap.global_costmap.ros__parameters.robot_base_frame": frame("base_link"),
            "local_costmap.local_costmap.ros__parameters.lidar.sensor_frame": frame("rslidar"),
            "local_costmap.local_costmap.ros__parameters.lidar_clearing.sensor_frame": frame("rslidar"),
            "global_costmap.global_costmap.ros__parameters.lidar.sensor_frame": frame("rslidar"),
            "global_costmap.global_costmap.ros__parameters.lidar_clearing.sensor_frame": frame("rslidar"),
            "global_costmap.global_costmap.ros__parameters.static_layer.map_topic": ""+"/map",
            "default_nav_through_poses_bt_xml": bt_scoped,
            "local_costmap.local_costmap.ros__parameters.global_frame": ("odom" if os.environ.get("OMNIFLEET_ARCHITECTURE")=="rep105" else "map"),
            "global_costmap.global_costmap.ros__parameters.global_frame": frame("map"),
            "local_costmap.local_costmap.ros__parameters.global_frame": frame("map"),
            "local_costmap.local_costmap.ros__parameters.obstacle_layer.lidar.topic": LaunchConfiguration("obstacle_topic"),
            "global_costmap.global_costmap.ros__parameters.obstacle_layer.lidar.topic": LaunchConfiguration("obstacle_topic"),
            "local_costmap.local_costmap.ros__parameters.obstacle_layer.lidar_clearing.topic": LaunchConfiguration("obstacle_topic"),
            "global_costmap.global_costmap.ros__parameters.obstacle_layer.lidar_clearing.topic": LaunchConfiguration("obstacle_topic"),
            # The deskewed cloud is expressed in map. Raytracing must still
            # start at the physical LiDAR, not at the map origin.
            "local_costmap.local_costmap.ros__parameters.obstacle_layer.lidar.sensor_frame": frame("rslidar"),
            "global_costmap.global_costmap.ros__parameters.obstacle_layer.lidar.sensor_frame": frame("rslidar"),
            "local_costmap.local_costmap.ros__parameters.obstacle_layer.lidar_clearing.sensor_frame": frame("rslidar"),
            "global_costmap.global_costmap.ros__parameters.obstacle_layer.lidar_clearing.sensor_frame": frame("rslidar"),
            "local_costmap.local_costmap.ros__parameters.obstacle_layer.lidar_clearing.clearing": LaunchConfiguration("obstacle_clearing"),
            "global_costmap.global_costmap.ros__parameters.obstacle_layer.lidar_clearing.clearing": LaunchConfiguration("obstacle_clearing"),
        },
        convert_types=True,
    )
    sensor_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="robot_sensor_extrinsics",
        output="screen",
        arguments=[
            "-0.041", "0.0", "0.15", "0.0", "0.0", "0.0",
            frame("base_link"),
            frame("rslidar"),
        ],
    )
    return LaunchDescription([
        DeclareLaunchArgument("transform_tolerance", default_value="0.8"),
        DeclareLaunchArgument("publish_voxel_debug", default_value=os.environ.get('OMNIFLEET_COSTMAP_TRACE','false')),
        DeclareLaunchArgument("odom_topic", default_value="/lidar_odometry/pose"),
        DeclareLaunchArgument("obstacle_topic", default_value="/lidar_odometry/nav_voxelmap_points"),
        DeclareLaunchArgument("obstacle_clearing", default_value="false"),
        GroupAction(actions=[
            SetEnvironmentVariable('LD_LIBRARY_PATH', str(height_overlay / 'lib') + ':' + os.environ.get('LD_LIBRARY_PATH', '')),
            SetEnvironmentVariable('AMENT_PREFIX_PATH', str(height_overlay) + ':' + os.environ.get('AMENT_PREFIX_PATH', '')),
            SetParameter(name="odom_topic", value=odom_input),
            sensor_tf,
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(planner / "launch" / "navigation.launch.py")
                ),
                launch_arguments={
                    "use_sim_time": "false",
                    "autostart": "true",
                    "params_file": configured_params,
                }.items(),
            ),
        ])
    ])


_unscoped_generate = generate_launch_description
def generate_launch_description():
    from fleet_scope import scoped
    return scoped(_unscoped_generate())
