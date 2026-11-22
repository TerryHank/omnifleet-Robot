"""清理旧的手动会话，并启动全新的 GLIM 在线建图与 Nav2 导航教学流程。"""

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
    robot_share = get_package_share_directory("omnifleet_a2_bringup")

    # 教学入口只负责把参数原样传给生产 Bringup，不在这里复制算法实现。
    # 对比实验必须遵守“一次只改一个变量”：其余参数保持下方默认基线不变。
    core = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_share, "launch", "robot.launch.py")
        ),
        launch_arguments={
            "operation": "slam_navigation",
            "map_id": LaunchConfiguration("map_label"),
            "map_dir": LaunchConfiguration("map_dir"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "start_chassis": LaunchConfiguration("start_chassis"),
            "use_camera": LaunchConfiguration("use_camera"),
            "lidar_range_min": LaunchConfiguration("lidar_range_min"),
            "lidar_range_max": LaunchConfiguration("lidar_range_max"),
            # 地形与局部障碍物模式：决定加载哪组 Costmap 图层。
            "terrain_mode": LaunchConfiguration("terrain_mode"),
            "local_obstacle_mode": LaunchConfiguration("local_obstacle_mode"),
            # 局部代价地图对比参数：主要影响控制器附近的避障距离和代价分布。
            "local_inflation_radius": LaunchConfiguration(
                "local_inflation_radius"
            ),
            "local_cost_scaling_factor": LaunchConfiguration(
                "local_cost_scaling_factor"
            ),
            # 全局代价地图对比参数：主要影响全局路径与障碍物的距离、地图精细度。
            "global_inflation_radius": LaunchConfiguration(
                "global_inflation_radius"
            ),
            "global_cost_scaling_factor": LaunchConfiguration(
                "global_cost_scaling_factor"
            ),
            "global_costmap_resolution": LaunchConfiguration(
                "global_costmap_resolution"
            ),
            # 规划与控制算法对比参数。
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
            "grep -qx /omnifleet_a2/system/stop_manual_stack; then "
            "echo '[mapping_keyboard] 正在结束旧建图/导航会话'; "
            "timeout 8s ros2 service call /omnifleet_a2/system/stop_manual_stack "
            "std_srvs/srv/Trigger '{}' >/tmp/rrc_workflow_preflight.log 2>&1 || true; "
            "sleep 3; fi",
        ],
        output="screen",
    )

    keyboard_command = (
        "source /opt/ros/humble/setup.bash; "
        "source ~/omnifleet_a2_ws/install/setup.bash; "
        "set -a; [ -f /etc/rrc/robot.env ] && source /etc/rrc/robot.env; set +a; "
        "export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-42}; "
        "exec ros2 run omnifleet_a2_bringup keyboard_teleop"
    )
    keyboard = ExecuteProcess(
        cmd=[
            "xterm",
            "-T",
            "RRC 在线建图导航键盘控制（i/,前后，j/l左右，k停止）",
            "-e",
            "bash",
            "-lc",
            keyboard_command,
        ],
        output="screen",
    )

    # 每次启动都把本轮实验取值打印到终端，便于记录并避免“参数改了但不知道改了什么”。
    comparison_settings_log = LogInfo(
        msg=[
            "【本轮对比实验参数】全局规划器=", LaunchConfiguration("planner_mode"),
            "；全局膨胀半径=", LaunchConfiguration("global_inflation_radius"), " m",
            "；全局代价衰减系数=", LaunchConfiguration("global_cost_scaling_factor"),
            "；全局地图分辨率=", LaunchConfiguration("global_costmap_resolution"), " m/格",
            "；局部障碍层=", LaunchConfiguration("local_obstacle_mode"),
            "；局部膨胀半径=", LaunchConfiguration("local_inflation_radius"), " m",
            "；局部代价衰减系数=", LaunchConfiguration("local_cost_scaling_factor"),
            "；局部控制器=", LaunchConfiguration("local_controller_plugin"),
        ]
    )

    start_after_reset = RegisterEventHandler(
        OnProcessExit(
            target_action=preflight,
            on_exit=[
                LogInfo(msg="旧会话已清理，开始全新的GLIM在线建图与Nav2导航"),
                comparison_settings_log,
                core,
                keyboard,
            ],
        )
    )

    return LaunchDescription([
        # -------------------- 在线建图基础参数 --------------------
        DeclareLaunchArgument(
            "map_label",
            default_value="fresh_mapping",
            description="新地图标签；管理器会自动添加UTC时间戳，绝不会加载旧图。",
        ),
        DeclareLaunchArgument(
            "map_dir",
            default_value="/var/lib/omnifleet_a2/maps",
            description="[默认] 地图保存根目录。",
        ),
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="[默认] 实车保持false。",
        ),
        DeclareLaunchArgument(
            "start_chassis",
            default_value="false",
            description="独立底盘服务已运行时保持false。",
        ),
        DeclareLaunchArgument(
            "use_camera",
            default_value="false",
            description="[默认] 是否接入可选MVS相机支线。",
        ),
        DeclareLaunchArgument(
            "lidar_range_min",
            default_value="0.18",
            description="[教学] 点云最小保留距离，单位m。",
        ),
        DeclareLaunchArgument(
            "lidar_range_max",
            default_value="8.0",
            description="[教学] 点云最大保留距离，单位m。",
        ),
        # -------------------- 对比实验参数 --------------------
        # 这些参数均有默认值，不输入也能运行。做对比时只覆盖当前实验变量。
        DeclareLaunchArgument(
            "terrain_mode",
            default_value="2d",
            description="[教学] 全局地形模式：2d或2_5d。",
        ),
        DeclareLaunchArgument(
            "local_obstacle_mode",
            default_value="obstacle",
            description="[教学] 局部障碍层：obstacle、voxel或stvl。",
        ),
        DeclareLaunchArgument(
            "local_inflation_radius",
            default_value="0.22",
            description="[教学] Local Costmap膨胀半径，单位m。",
        ),
        DeclareLaunchArgument(
            "local_cost_scaling_factor",
            default_value="8.0",
            description="[教学] Local Costmap膨胀代价衰减系数。",
        ),
        DeclareLaunchArgument(
            "global_inflation_radius",
            default_value="0.22",
            description="[教学] Global Costmap膨胀半径，单位m。",
        ),
        DeclareLaunchArgument(
            "global_cost_scaling_factor",
            default_value="8.0",
            description="[教学] Global Costmap膨胀代价衰减系数。",
        ),
        DeclareLaunchArgument(
            "global_costmap_resolution",
            default_value="0.05",
            description="[教学] Global Costmap分辨率，单位m/格。",
        ),
        DeclareLaunchArgument(
            "planner_mode",
            default_value="hybrid_astar",
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
