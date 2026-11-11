import os
from pathlib import Path

from ament_index_python.packages import PackageNotFoundError, get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from nav2_common.launch import RewrittenYaml


NAVIGATION_NODES = [
    "controller_server",
    "planner_server",
    "smoother_server",
    "behavior_server",
    "bt_navigator",
    "waypoint_follower",
    "velocity_smoother",
]


NAV_PARAMETER_PATHS = {
    "local_inflation_radius": (
        "local_costmap.local_costmap.ros__parameters.inflation_layer.inflation_radius"
    ),
    "local_cost_scaling_factor": (
        "local_costmap.local_costmap.ros__parameters.inflation_layer.cost_scaling_factor"
    ),
    "global_inflation_radius": (
        "global_costmap.global_costmap.ros__parameters.inflation_layer.inflation_radius"
    ),
    "global_cost_scaling_factor": (
        "global_costmap.global_costmap.ros__parameters.inflation_layer.cost_scaling_factor"
    ),
    "global_costmap_resolution": (
        "global_costmap.global_costmap.ros__parameters.resolution"
    ),
    "local_controller_plugin": (
        "controller_server.ros__parameters.FollowPath.plugin"
    ),
}


LOCAL_OBSTACLE_CONFIGS = {
    "obstacle": "local_costmap_obstacle.yaml",
    "voxel": "local_costmap_voxel.yaml",
    "stvl": "local_costmap_stvl.yaml",
}

TERRAIN_CONFIGS = {
    "2d": None,
    "2_5d": "global_costmap_terrain.yaml",
}

PLANNER_CONFIGS = {
    # 生产默认：Hybrid-A* + Reeds-Shepp，能够表达阿克曼转弯约束和倒车段。
    "hybrid_astar": "planner_hybrid_astar.yaml",
    # 教学对照：NavFn使用同一个插件，通过use_astar切换A*与Dijkstra。
    "astar": "planner_navfn_astar.yaml",
    "dijkstra": "planner_navfn_dijkstra.yaml",
}


def _mode_parameter_files(context, package_share):
    """校验冷切换模式，并返回叠加在基础Nav2配置后的参数文件。"""

    terrain_mode = LaunchConfiguration("terrain_mode").perform(context).strip().lower()
    local_obstacle_mode = (
        LaunchConfiguration("local_obstacle_mode").perform(context).strip().lower()
    )
    planner_mode = LaunchConfiguration("planner_mode").perform(context).strip().lower()

    if terrain_mode not in TERRAIN_CONFIGS:
        raise RuntimeError(
            f"未知terrain_mode={terrain_mode!r}；只允许2d或2_5d"
        )
    if local_obstacle_mode not in LOCAL_OBSTACLE_CONFIGS:
        raise RuntimeError(
            "未知local_obstacle_mode="
            f"{local_obstacle_mode!r}；只允许obstacle、voxel或stvl"
        )
    if planner_mode not in PLANNER_CONFIGS:
        raise RuntimeError(
            f"未知planner_mode={planner_mode!r}；只允许hybrid_astar、astar或dijkstra"
        )

    if terrain_mode == "2_5d":
        try:
            get_package_share_directory("grid_map_msgs")
            get_package_share_directory("omnifleet_localization")
        except PackageNotFoundError as error:
            raise RuntimeError(
                "terrain_mode=2_5d不可用：缺少grid_map_msgs或omnifleet_localization"
            ) from error

    if local_obstacle_mode == "stvl":
        try:
            get_package_share_directory("spatio_temporal_voxel_layer")
        except PackageNotFoundError as error:
            raise RuntimeError(
                "local_obstacle_mode=stvl不可用："
                "远端未安装spatio_temporal_voxel_layer"
            ) from error

    overlays = [
        package_share / "config" / LOCAL_OBSTACLE_CONFIGS[local_obstacle_mode]
    ]
    terrain_config = TERRAIN_CONFIGS[terrain_mode]
    if terrain_config:
        overlays.append(package_share / "config" / terrain_config)
    # 规划器配置最后加载，使planner_mode成为全局规划算法的唯一选择入口。
    overlays.append(package_share / "config" / PLANNER_CONFIGS[planner_mode])
    for overlay in overlays:
        if not overlay.is_file():
            raise RuntimeError(f"模式参数文件不存在：{overlay}")
    return [str(overlay) for overlay in overlays], terrain_mode


def _nav_parameter_rewrites(context):
    rewrites = {}
    for argument, yaml_path in NAV_PARAMETER_PATHS.items():
        value = LaunchConfiguration(argument).perform(context)
        if value:
            rewrites[yaml_path] = value
    return rewrites


def _nav_nodes(context):
    package_share = Path(get_package_share_directory("omnifleet_planner"))
    source_params = LaunchConfiguration("params_file").perform(context)
    if not source_params:
        raise RuntimeError("params_file is required for GLIM Nav2 bringup")
    mode_parameter_files, terrain_mode = _mode_parameter_files(context, package_share)
    params = RewrittenYaml(
        source_file=source_params,
        param_rewrites=_nav_parameter_rewrites(context),
        convert_types=True,
    )
    navigate_to_pose_bt = os.path.join(
        package_share, "behavior_trees", "navigate_to_pose_ackermann.xml"
    )
    navigate_through_poses_bt = os.path.join(
        package_share, "behavior_trees", "navigate_through_poses_ackermann.xml"
    )
    use_sim_time = LaunchConfiguration("use_sim_time")
    lifecycle_nodes = list(NAVIGATION_NODES)
    nodes = []

    if terrain_mode == "2_5d":
        nodes.append(
            Node(
                package="omnifleet_localization",
                executable="terrain_mapper",
                name="terrain_mapper",
                output="screen",
                parameters=[
                    str(package_share / "config" / "terrain_2_5d.yaml"),
                    {"use_sim_time": use_sim_time},
                ],
            )
        )

    common = {
        # 后加载的模式文件只覆盖Costmap插件集合，不复制整份Nav2参数，
        # 从而确保规划器、控制器、footprint和安全参数在各模式间保持一致。
        "parameters": [params, *mode_parameter_files, {"use_sim_time": use_sim_time}],
        "output": "screen",
    }
    nodes.extend(
        [
            Node(
                package="nav2_controller",
                executable="controller_server",
                name="controller_server",
                remappings=[("cmd_vel", "/cmd_vel_nav_raw")],
                **common,
            ),
            Node(package="nav2_planner", executable="planner_server", name="planner_server", **common),
            Node(package="nav2_smoother", executable="smoother_server", name="smoother_server", **common),
            Node(
                package="nav2_behaviors",
                executable="behavior_server",
                name="behavior_server",
                remappings=[("cmd_vel", "/cmd_vel_nav_raw")],
                **common,
            ),
            Node(
                package="nav2_bt_navigator",
                executable="bt_navigator",
                name="bt_navigator",
                output="screen",
                parameters=[
                    params,
                    {
                        "use_sim_time": use_sim_time,
                        "default_nav_to_pose_bt_xml": navigate_to_pose_bt,
                        "default_nav_through_poses_bt_xml": navigate_through_poses_bt,
                    },
                ],
            ),
            Node(
                package="nav2_waypoint_follower",
                executable="waypoint_follower",
                name="waypoint_follower",
                **common,
            ),
            Node(
                package="nav2_velocity_smoother",
                executable="velocity_smoother",
                name="velocity_smoother",
                remappings=[
                    ("cmd_vel", "/cmd_vel_nav_raw"),
                    ("cmd_vel_smoothed", "/cmd_vel_nav_smoothed"),
                ],
                **common,
            ),
            Node(
                package="omnifleet_planner",
                executable="nav_steering_adapter",
                name="nav_steering_adapter",
                output="screen",
                parameters=[params, {"use_sim_time": use_sim_time}],
            ),
            Node(
                package="omnifleet_behaviors",
                executable="foxglove_nav_bridge",
                name="foxglove_nav_bridge",
                output="screen",
                parameters=[params, {"use_sim_time": use_sim_time}],
            ),
            Node(
                package="omnifleet_behaviors",
                executable="mission_manager",
                name="rrc_mission_manager",
                output="screen",
                parameters=[{"use_sim_time": use_sim_time}],
            ),
            Node(
                package="nav2_lifecycle_manager",
                executable="lifecycle_manager",
                name="lifecycle_manager_navigation",
                output="screen",
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "autostart": ParameterValue(
                            LaunchConfiguration("autostart"), value_type=bool
                        ),
                        "node_names": lifecycle_nodes,
                    }
                ],
            ),
        ]
    )
    return nodes


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("autostart", default_value="false"),
            DeclareLaunchArgument(
                "terrain_mode",
                default_value="2d",
                description=(
                    "全局地形模式：2d或2_5d。2_5d是在StaticLayer上叠加"
                    "TraversabilityLayer，不替代/map。"
                ),
            ),
            DeclareLaunchArgument(
                "local_obstacle_mode",
                default_value="obstacle",
                description="局部障碍层：obstacle、voxel或stvl。",
            ),
            DeclareLaunchArgument("local_inflation_radius", default_value=""),
            DeclareLaunchArgument("local_cost_scaling_factor", default_value=""),
            DeclareLaunchArgument("global_inflation_radius", default_value=""),
            DeclareLaunchArgument("global_cost_scaling_factor", default_value=""),
            DeclareLaunchArgument("global_costmap_resolution", default_value=""),
            DeclareLaunchArgument(
                "planner_mode",
                default_value="hybrid_astar",
                description=(
                    "全局规划模式：hybrid_astar、astar或dijkstra。"
                    "只有hybrid_astar保证阿克曼运动学与倒车路径。"
                ),
            ),
            DeclareLaunchArgument("local_controller_plugin", default_value=""),
            DeclareLaunchArgument(
                "params_file",
                default_value="",
                description="Required Nav2 parameter file supplied by the active GLIM bringup",
            ),
            OpaqueFunction(function=_nav_nodes),
        ]
    )
