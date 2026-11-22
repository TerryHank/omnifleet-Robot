"""OpenCV Zoo MediaPipe 手势人体跟随综合案例。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


COURSE_FUNCTION = "04_08_gesture_person_follow"


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "start_camera", default_value="false",
            description="是否启动 MV-DT01SNU 相机；常驻相机已运行时保持关闭。",
        ),
        DeclareLaunchArgument(
            "enable_motion", default_value="false",
            description="是否向 local_navigation 的手动输入发布动作；默认只识别和显示。",
        ),
        DeclareLaunchArgument(
            "use_gui", default_value="true", description="是否打开带手势和跟随状态的窗口。"
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution([
                FindPackageShare("omnifleet_vision"), "launch", "course_function.launch.py"
            ])),
            launch_arguments={
                "course_function": COURSE_FUNCTION,
                "start_camera": LaunchConfiguration("start_camera"),
                "enable_motion": LaunchConfiguration("enable_motion"),
                "use_gui": LaunchConfiguration("use_gui"),
            }.items(),
        ),
    ])
