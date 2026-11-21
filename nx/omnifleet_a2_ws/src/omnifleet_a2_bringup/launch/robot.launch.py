"""阿克曼小车的统一生产启动入口。

参数分类：
- 默认参数：声明了 default_value，不传也能启动。
- 必填参数：未声明 default_value，启动命令必须显式提供；本文件当前没有此类参数。
- 条件参数：本身有默认值，但只在特定模式或子系统启用时生效。

生产环境默认由 systemd 持有 STM32 和 Airy，因此 start_chassis、start_airy
默认均为 false，避免同一硬件被两个进程重复打开。
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression


SUPPORTED_MAPPING_PROFILES = {"lidar", "pure_visual", "visual_lidar"}


def _include(package, launch_file, arguments=None, condition=None):
    """按ROS包名包含下级Launch，并统一传递参数和启动条件。"""

    share = get_package_share_directory(package)
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(share, "launch", launch_file)),
        launch_arguments=(arguments or {}).items(),
        condition=condition,
    )


def _validate_mapping_profile(context):
    """在创建后端进程前拒绝非法或尚未验收的组合。"""

    profile = LaunchConfiguration("mapping_profile").perform(context)
    operation = LaunchConfiguration("operation").perform(context)
    if profile not in SUPPORTED_MAPPING_PROFILES:
        raise RuntimeError(
            f"不支持的mapping_profile={profile}；"
            f"可选值为{sorted(SUPPORTED_MAPPING_PROFILES)}"
        )
    if profile != "lidar" and operation != "mapping":
        raise RuntimeError(
            f"{profile}当前仅开放mapping旁路验收，尚未接管Nav2或生产TF"
        )
    if profile != "lidar" and LaunchConfiguration("use_camera").perform(
        context
    ).lower() == "true":
        raise RuntimeError(
            "视觉profile只消费现有相机服务话题，use_camera必须保持false"
        )
    return []


def _visual_backend(context):
    """仅在显式视觉profile下解析和包含可选视觉overlay。"""

    profile = LaunchConfiguration("mapping_profile").perform(context)
    if profile == "lidar":
        return []
    return [
        _include(
            "omnifleet_visual_mapping",
            "visual_mapping.launch.py",
            {
                "mapping_profile": profile,
                "map_id": LaunchConfiguration("map_id"),
                "map_dir": LaunchConfiguration("map_dir"),
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "gate_timeout_sec": LaunchConfiguration(
                    "visual_gate_timeout_sec"
                ),
                "resume_existing_database": LaunchConfiguration(
                    "visual_resume_existing_database"
                ),
            },
        )
    ]


def _lidar_backend(context):
    if LaunchConfiguration("mapping_profile").perform(context) == "pure_visual":
        return []
    backend = LaunchConfiguration("localization_backend").perform(context)
    launch_files = {
        "mola": "mola_backend.launch.py",
        "glim_cuda": "glim_cuda_backend.launch.py",
        "cartographer_3d": "cartographer_3d_backend.launch.py",
    }
    if backend not in launch_files:
        raise RuntimeError(
            f"localization_backend必须是{sorted(launch_files)}，当前为{backend!r}"
        )
    arguments = {
        "operation": LaunchConfiguration("operation"),
        "map_id": LaunchConfiguration("map_id"),
        "map_dir": LaunchConfiguration("map_dir"),
        "use_sim_time": LaunchConfiguration("use_sim_time"),
    }
    if backend in {"mola", "glim_cuda"}:
        arguments.update({
            "map_path": LaunchConfiguration("map_path"),
            "initial_pose_x": LaunchConfiguration("initial_pose_x"),
            "initial_pose_y": LaunchConfiguration("initial_pose_y"),
            "initial_pose_z": LaunchConfiguration("initial_pose_z"),
            "initial_pose_yaw": LaunchConfiguration("initial_pose_yaw"),
            "use_camera": LaunchConfiguration("use_camera"),
        })
    if backend == "glim_cuda":
        arguments.update({
            "lidar_range_min": LaunchConfiguration("lidar_range_min"),
            "lidar_range_max": LaunchConfiguration("lidar_range_max"),
        })
    return [
        _include(
            "omnifleet_a2_localization",
            launch_files[backend],
            arguments,
        )
    ]


def generate_launch_description():
    """声明整车参数并组装底盘、传感器、MOLA、二维Nav2和管理节点。"""

    use_sim_time = LaunchConfiguration("use_sim_time")
    mapping_profile = LaunchConfiguration("mapping_profile")
    navigation_share = get_package_share_directory("omnifleet_a2_planner")
    nav_params = os.path.join(navigation_share, "config", "nav2_glim.yaml")
    return LaunchDescription([
        # 通用运行模式与地图参数。教学主流程使用slam_navigation直接建图并导航；
        # localization仅保留给显式加载旧地图的高级工作流。
        DeclareLaunchArgument(
            "use_sim_time", default_value="false",
            description="[默认] 是否使用仿真时钟；实车保持false。",
        ),
        DeclareLaunchArgument(
            "operation", default_value="mapping",
            description=(
                "[默认] 运行模式：mapping、slam_navigation或localization；"
                "默认只建图；教学主流程使用slam_navigation直接建图并导航。"
            ),
        ),
        DeclareLaunchArgument(
            "mapping_profile", default_value="lidar",
            description=(
                "[默认] 建图后端：lidar、pure_visual或visual_lidar；"
                "默认lidar使用当前MOLA主线。视觉模式当前为隔离旁路。"
            ),
        ),
        DeclareLaunchArgument(
            "localization_backend", default_value="mola",
            description=(
                "[默认] 激光SLAM后端：mola；"
                "GLIM CUDA和Cartographer 3D保留为显式切换测试支线。"
            ),
        ),
        DeclareLaunchArgument(
            "visual_gate_timeout_sec", default_value="90.0",
            description="[条件] 视觉旁路等待新鲜且同步输入的最长秒数。",
        ),
        DeclareLaunchArgument(
            "visual_resume_existing_database", default_value="false",
            description="[条件] 是否显式续写同名视觉RTAB-Map数据库。",
        ),
        DeclareLaunchArgument(
            "map_id", default_value="active",
            description=(
                "[条件] mapping/slam_navigation中作为新会话标签；"
                "localization时必须对应map_dir下已登记的旧地图。"
            ),
        ),
        DeclareLaunchArgument(
            "map_dir", default_value="/var/lib/omnifleet_a2/maps",
            description="[默认] GLIM地图、清单和dump的根目录。",
        ),
        DeclareLaunchArgument(
            "map_path", default_value="",
            description=(
                "[条件] localization使用的GLIM dump路径；留空时按map_dir和map_id查找。"
            ),
        ),

        # GLIM旧地图定位所需的初始6DoF；在线建图时GLIM以传感器起点建立自身map。
        DeclareLaunchArgument(
            "initial_pose_x", default_value="0.0",
            description="[条件] localization初始位置x，单位m。",
        ),
        DeclareLaunchArgument(
            "initial_pose_y", default_value="0.0",
            description="[条件] localization初始位置y，单位m。",
        ),
        DeclareLaunchArgument(
            "initial_pose_z", default_value="0.0",
            description=(
                "[条件] localization初始位置z，单位m；在线建图的全局高度由"
                "GLIM内部坐标系决定，不使用该参数移动二维导航平面。"
            ),
        ),
        DeclareLaunchArgument(
            "initial_pose_yaw", default_value="0.0",
            description="[条件] localization初始航向角yaw，单位rad。",
        ),
        # 当前地图投影链使用的激光距离参数。
        DeclareLaunchArgument(
            "lidar_range_min", default_value="0.18",
            description="[默认] 导航点云最小保留距离，单位m。",
        ),
        DeclareLaunchArgument(
            "lidar_range_max", default_value="6.0",
            description="[默认] 导航点云最大保留距离，单位m。",
        ),

        # 硬件参数。只有让本Launch直接持有对应硬件时才使用。
        DeclareLaunchArgument(
            "start_chassis", default_value="false",
            description="[默认] 是否由本Launch启动STM32底盘；生产环境由systemd持有。",
        ),
        DeclareLaunchArgument(
            "start_airy", default_value="false",
            description="[默认] 是否由本Launch直接启动Airy；生产环境由systemd持有。",
        ),
        DeclareLaunchArgument(
            "max_steering_angle_deg", default_value="15",
            description="[默认] NX启动时下发给STM32的最大转向角，单位deg。",
        ),
        DeclareLaunchArgument(
            "steering_center_offset_deg", default_value="0",
            description="[默认] NX启动时下发给STM32的舵机中点偏移，单位deg。",
        ),
        DeclareLaunchArgument(
            "motion_watchdog_timeout_ms", default_value="1000",
            description="[默认] STM32失联刹停阈值，单位ms；NX启动和动态参数均可下发。",
        ),
        DeclareLaunchArgument(
            "watchdog_heartbeat_rate_hz", default_value="10.0",
            description="[默认] NX发给STM32的独立看门狗心跳频率，单位Hz。",
        ),
        DeclareLaunchArgument(
            "use_camera", default_value="false",
            description="[默认] 是否启用可选MVS相机支线；不影响Airy主链。",
        ),

        # 地图模式和局部障碍模式彼此独立：
        # - terrain_mode只决定Global Costmap是否叠加2.5D可通行性层；
        # - local_obstacle_mode只决定实时点云进入Local Costmap的方式。
        # 2.5D模式仍保留二维/map和StaticLayer，不会用GridMap替代静态底图。
        DeclareLaunchArgument(
            "terrain_mode", default_value="2d",
            description=(
                "[默认] 全局地形模式：2d或2_5d；默认2d。"
                "2_5d会保留/map，并叠加GridMap可通行性代价。"
            ),
        ),
        DeclareLaunchArgument(
            "local_obstacle_mode", default_value="obstacle",
            description=(
                "[默认] Local Costmap障碍层：obstacle、voxel或stvl；"
                "默认使用外部已过滤点云对应的ObstacleLayer。"
            ),
        ),

        # Global/Local Costmap膨胀参数及全局规划实验选择。
        # 学生只需在launch命令末尾追加“参数名:=值”，不需要改YAML文件。
        DeclareLaunchArgument(
            "local_inflation_radius", default_value="0.45",
            description="[默认] Local Costmap障碍膨胀半径，单位m。",
        ),
        DeclareLaunchArgument(
            "local_cost_scaling_factor", default_value="2.0",
            description="[默认] Local Costmap膨胀代价衰减系数。",
        ),
        DeclareLaunchArgument(
            "global_inflation_radius", default_value="0.45",
            description="[默认] Global Costmap障碍膨胀半径，单位m。",
        ),
        DeclareLaunchArgument(
            "global_cost_scaling_factor", default_value="2.0",
            description="[默认] Global Costmap膨胀代价衰减系数。",
        ),
        DeclareLaunchArgument(
            "global_costmap_resolution", default_value="0.05",
            description=(
                "[默认] Global Costmap分辨率，单位m/格；用于观察地图精细度和"
                "规划耗时的对比实验。"
            ),
        ),
        DeclareLaunchArgument(
            "planner_mode", default_value="hybrid_astar",
            description=(
                "[默认] 全局规划实验模式：hybrid_astar、astar或dijkstra。"
                "hybrid_astar是保证阿克曼转弯约束和倒车规划的生产模式；"
                "astar、dijkstra用于二维搜索路径对比。"
            ),
        ),
        DeclareLaunchArgument(
            "controller_mode", default_value="rpp",
            description=(
                "[默认] 局部路径跟踪控制器：rpp或mppi；默认保留已验证的RPP，"
                "使用controller_mode:=mppi冷切换MPPI。"
            ),
        ),
        DeclareLaunchArgument(
            "local_controller_plugin",
            default_value="",
            description="[兼容] 非空时直接覆盖controller_mode选择的插件名。",
        ),

        OpaqueFunction(function=_validate_mapping_profile),

        # 可选硬件启动段：false时完全不创建对应驱动进程。
        _include(
            "omnifleet_a2_bringup", "chassis_core.launch.py",
            {
                "use_sim_time": use_sim_time,
                "max_steering_angle_deg": LaunchConfiguration(
                    "max_steering_angle_deg"
                ),
                "steering_center_offset_deg": LaunchConfiguration(
                    "steering_center_offset_deg"
                ),
                "motion_watchdog_timeout_ms": LaunchConfiguration(
                    "motion_watchdog_timeout_ms"
                ),
                "watchdog_heartbeat_rate_hz": LaunchConfiguration(
                    "watchdog_heartbeat_rate_hz"
                ),
            },
            IfCondition(LaunchConfiguration("start_chassis")),
        ),
        _include(
            "omnifleet_a2_localization", "airy_gateway.launch.py",
            condition=IfCondition(
                PythonExpression([
                    "'", mapping_profile, "' != 'pure_visual' and '",
                    LaunchConfiguration("start_airy"), "' == 'true'"
                ])
            ),
        ),
        _include(
            "omnifleet_a2_localization", "includes/tof_rgbd_sensor.launch.py",
            condition=IfCondition(
                PythonExpression([
                    "'", mapping_profile, "' == 'lidar' and '",
                    LaunchConfiguration("use_camera"), "' == 'true'"
                ])
            ),
        ),

        # 冷启动时直接选择一个后端，不再由常驻管理进程派生子进程。
        OpaqueFunction(function=_lidar_backend),

        # 纯建图不创建Nav2进程；localization或高级slam_navigation模式才装配Nav2。
        _include(
            "omnifleet_a2_planner", "navigation.launch.py",
            {
                "use_sim_time": use_sim_time,
                "autostart": "true",
                "params_file": nav_params,
                "terrain_mode": LaunchConfiguration("terrain_mode"),
                "local_obstacle_mode": LaunchConfiguration("local_obstacle_mode"),
                "local_inflation_radius": LaunchConfiguration("local_inflation_radius"),
                "local_cost_scaling_factor": LaunchConfiguration("local_cost_scaling_factor"),
                "global_inflation_radius": LaunchConfiguration("global_inflation_radius"),
                "global_cost_scaling_factor": LaunchConfiguration("global_cost_scaling_factor"),
                "global_costmap_resolution": LaunchConfiguration("global_costmap_resolution"),
                "planner_mode": LaunchConfiguration("planner_mode"),
                "controller_mode": LaunchConfiguration("controller_mode"),
                "local_controller_plugin": LaunchConfiguration("local_controller_plugin"),
            },
            IfCondition(
                PythonExpression([
                    "'", mapping_profile, "' == 'lidar' and '",
                    LaunchConfiguration("operation"), "' != 'mapping'"
                ])
            ),
        ),

        OpaqueFunction(function=_visual_backend),
    ])
