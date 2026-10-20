"""KCF 目标跟踪的一键课程入口。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


COURSE_FUNCTION = "02_07_kcf"


def generate_launch_description():
    """启动KCF 目标跟踪，运动候选默认关闭。"""

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
                "tracking_scale", default_value="0.4",
                description="KCF 内部跟踪缩放比例；默认以约 614×512 追求最高稳定帧率。",
            ),
            DeclareLaunchArgument("roi_x", default_value="0", description="无界面模式初始框左上角 x。"),
            DeclareLaunchArgument("roi_y", default_value="0", description="无界面模式初始框左上角 y。"),
            DeclareLaunchArgument("roi_width", default_value="0", description="无界面模式初始框宽度。"),
            DeclareLaunchArgument("roi_height", default_value="0", description="无界面模式初始框高度。"),
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
                    "tracking_scale": LaunchConfiguration("tracking_scale"),
                    "roi_x": LaunchConfiguration("roi_x"),
                    "roi_y": LaunchConfiguration("roi_y"),
                    "roi_width": LaunchConfiguration("roi_width"),
                    "roi_height": LaunchConfiguration("roi_height"),
                }.items(),
            ),
        ]
    )
