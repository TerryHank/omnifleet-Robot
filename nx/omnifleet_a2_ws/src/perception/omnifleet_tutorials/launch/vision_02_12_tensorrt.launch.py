"""TensorRT 导出与基准测试的一键课程入口。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


COURSE_FUNCTION = "02_12_tensorrt"


def generate_launch_description():
    """启动TensorRT 导出与基准测试，运动候选默认关闭。"""

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "start_camera", default_value="false", description="是否另行启动相机；远端常驻相机已运行时保持关闭。"
            ),
            DeclareLaunchArgument(
                "enable_motion", default_value="false",
                description="是否发布运动候选；默认关闭，启用前必须确认安全仲裁链。",
            ),
            DeclareLaunchArgument(
                "use_gui", default_value="true", description="KCF 功能是否打开交互式选框窗口。"
            ),
            DeclareLaunchArgument(
                "tensorrt_mode", default_value="export", description="TensorRT 工具模式：export 或 benchmark。"
            ),
            DeclareLaunchArgument(
                "engine_path", default_value="", description="TensorRT 引擎路径，必须显式提供。"
            ),
            DeclareLaunchArgument(
                "report_path", default_value="", description="TensorRT 报告路径，必须显式提供。"
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("omnifleet_vision"), "launch", "course_function.launch.py"]
                    )
                ),
                launch_arguments={
                    "course_function": COURSE_FUNCTION,
                    "start_camera": LaunchConfiguration("start_camera"),
                    "enable_motion": LaunchConfiguration("enable_motion"),
                    "use_gui": LaunchConfiguration("use_gui"),
                    "tensorrt_mode": LaunchConfiguration("tensorrt_mode"),
                    "engine_path": LaunchConfiguration("engine_path"),
                    "report_path": LaunchConfiguration("report_path"),
                }.items(),
            ),
        ]
    )
