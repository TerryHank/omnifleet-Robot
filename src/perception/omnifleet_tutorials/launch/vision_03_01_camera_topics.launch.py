"""彩色与深度相机话题联调的一键课程入口。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


COURSE_FUNCTION = "03_01_camera_topics"


def generate_launch_description():
    """启动彩色与深度相机话题联调，运动候选默认关闭。"""

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
                }.items(),
            ),
        ]
    )
