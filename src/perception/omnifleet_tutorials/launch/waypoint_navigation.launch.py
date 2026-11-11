"""Load one saved GLIM map and start Nav2 waypoint navigation."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    LogInfo,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    robot_share = get_package_share_directory("omnifleet_bringup")
    core = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_share, "launch", "robot.launch.py")
        ),
        launch_arguments={
            "operation": "localization",
            "map_id": LaunchConfiguration("map_id"),
            "map_dir": LaunchConfiguration("map_dir"),
            "map_path": LaunchConfiguration("map_path"),
            "initial_pose_x": LaunchConfiguration("initial_pose_x"),
            "initial_pose_y": LaunchConfiguration("initial_pose_y"),
            "initial_pose_z": LaunchConfiguration("initial_pose_z"),
            "initial_pose_yaw": LaunchConfiguration("initial_pose_yaw"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "start_chassis": LaunchConfiguration("start_chassis"),
            "start_mid360": LaunchConfiguration("start_mid360"),
            "host_ip": LaunchConfiguration("host_ip"),
            "lidar_ip": LaunchConfiguration("lidar_ip"),
            "use_camera": LaunchConfiguration("use_camera"),
            "navigation_ground_offset_z": LaunchConfiguration(
                "navigation_ground_offset_z"
            ),
            "obstacle_z_min": LaunchConfiguration("obstacle_z_min"),
            "obstacle_z_max": LaunchConfiguration("obstacle_z_max"),
            "lidar_range_min": LaunchConfiguration("lidar_range_min"),
            "lidar_range_max": LaunchConfiguration("lidar_range_max"),
            "lidar_voxel_size": LaunchConfiguration("lidar_voxel_size"),
            "lidar_max_rate": LaunchConfiguration("lidar_max_rate"),
            "terrain_mode": LaunchConfiguration("terrain_mode"),
            "local_obstacle_mode": LaunchConfiguration("local_obstacle_mode"),
            "local_inflation_radius": LaunchConfiguration(
                "local_inflation_radius"
            ),
            "local_cost_scaling_factor": LaunchConfiguration(
                "local_cost_scaling_factor"
            ),
            "global_inflation_radius": LaunchConfiguration(
                "global_inflation_radius"
            ),
            "global_cost_scaling_factor": LaunchConfiguration(
                "global_cost_scaling_factor"
            ),
            "global_costmap_resolution": LaunchConfiguration(
                "global_costmap_resolution"
            ),
            "planner_mode": LaunchConfiguration("planner_mode"),
            "local_controller_plugin": LaunchConfiguration(
                "local_controller_plugin"
            ),
        }.items(),
    )

    preflight = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            "if ros2 service list 2>/dev/null | "
            "grep -qx /rrc_system/stop_manual_stack; then "
            "echo '[waypoint_navigation] 正在取消旧航点并结束旧会话'; "
            "timeout 8s ros2 service call /rrc_system/stop_manual_stack "
            "std_srvs/srv/Trigger '{}' >/tmp/rrc_workflow_preflight.log 2>&1 || true; "
            "sleep 3; fi",
        ],
        output="screen",
    )

    start_after_reset = RegisterEventHandler(
        OnProcessExit(
            target_action=preflight,
            on_exit=[
                LogInfo(msg="旧会话已清理，加载已保存GLIM地图并启动航点导航"),
                core,
            ],
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "map_id",
            description="[必填] mapping_save_view_stop输出的已保存地图ID。",
        ),
        DeclareLaunchArgument(
            "map_dir", default_value="~/robot_maps",
            description="[默认] 已保存地图的根目录。",
        ),
        DeclareLaunchArgument(
            "map_path", default_value="",
            description="[条件] 指定GLIM dump路径；通常留空并由map_id查找。",
        ),
        DeclareLaunchArgument(
            "initial_pose_x", default_value="0.0",
            description="[默认] 旧地图中的初始x，单位m。",
        ),
        DeclareLaunchArgument(
            "initial_pose_y", default_value="0.0",
            description="[默认] 旧地图中的初始y，单位m。",
        ),
        DeclareLaunchArgument(
            "initial_pose_z", default_value="0.0",
            description="[默认] 旧地图中的初始z，单位m。",
        ),
        DeclareLaunchArgument(
            "initial_pose_yaw", default_value="0.0",
            description="[默认] 旧地图中的初始yaw，单位rad。",
        ),
        DeclareLaunchArgument(
            "use_sim_time", default_value="false",
            description="[默认] 实车保持false。",
        ),
        DeclareLaunchArgument(
            "start_chassis", default_value="false",
            description="[默认] 底盘已由systemd自启时保持false。",
        ),
        DeclareLaunchArgument(
            "start_mid360", default_value="false",
            description="[默认] MID-360已由systemd自启时保持false。",
        ),
        DeclareLaunchArgument(
            "host_ip", default_value="192.168.1.5",
            description="[条件] start_mid360=true时使用的主机IP。",
        ),
        DeclareLaunchArgument(
            "lidar_ip", default_value="192.168.1.121",
            description="[条件] start_mid360=true时使用的雷达IP。",
        ),
        DeclareLaunchArgument(
            "use_camera", default_value="false",
            description="[默认] 是否接入可选MVS相机支线。",
        ),
        DeclareLaunchArgument(
            "navigation_ground_offset_z", default_value="0.374553341297",
            description="[标定] nav_map到GLIM map的固定高度，单位m。",
        ),
        DeclareLaunchArgument(
            "obstacle_z_min", default_value="-0.03",
            description="[教学] 导航障碍最低高度，单位m。",
        ),
        DeclareLaunchArgument(
            "obstacle_z_max", default_value="0.75",
            description="[教学] 导航障碍最高高度，单位m。",
        ),
        DeclareLaunchArgument(
            "lidar_range_min", default_value="0.18",
            description="[教学] 点云最小保留距离，单位m。",
        ),
        DeclareLaunchArgument(
            "lidar_range_max", default_value="8.0",
            description="[教学] 点云最大保留距离，单位m。",
        ),
        DeclareLaunchArgument(
            "lidar_voxel_size", default_value="0.08",
            description="[教学] 点云降采样体素边长，单位m。",
        ),
        DeclareLaunchArgument(
            "lidar_max_rate", default_value="10.0",
            description="[默认] 障碍点云最大输出频率，单位Hz。",
        ),
        DeclareLaunchArgument(
            "terrain_mode", default_value="2d",
            description="[教学] 全局地形模式：2d或2_5d。",
        ),
        DeclareLaunchArgument(
            "local_obstacle_mode", default_value="obstacle",
            description="[教学] 局部障碍层：obstacle、voxel或stvl。",
        ),
        DeclareLaunchArgument(
            "local_inflation_radius", default_value="0.22",
            description="[教学] Local Costmap膨胀半径，单位m。",
        ),
        DeclareLaunchArgument(
            "local_cost_scaling_factor", default_value="8.0",
            description="[教学] Local Costmap膨胀代价衰减系数。",
        ),
        DeclareLaunchArgument(
            "global_inflation_radius", default_value="0.22",
            description="[教学] Global Costmap膨胀半径，单位m。",
        ),
        DeclareLaunchArgument(
            "global_cost_scaling_factor", default_value="8.0",
            description="[教学] Global Costmap膨胀代价衰减系数。",
        ),
        DeclareLaunchArgument(
            "global_costmap_resolution", default_value="0.05",
            description="[教学] Global Costmap分辨率，单位m/格。",
        ),
        DeclareLaunchArgument(
            "planner_mode", default_value="hybrid_astar",
            description="[教学] 全局规划：hybrid_astar、astar或dijkstra。",
        ),
        DeclareLaunchArgument(
            "local_controller_plugin",
            default_value="nav2_mppi_controller::MPPIController",
            description="[默认] 局部控制器；生产使用MPPI Ackermann。",
        ),
        start_after_reset,
        preflight,
    ])
