"""视觉模型训练的一键课程入口。"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


COURSE_FUNCTION = "02_11_model_training"


def generate_launch_description():
    """启动视觉模型训练，运动候选默认关闭。"""

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
                "dataset_yaml", default_value="", description="训练数据集 YAML 文件，必须显式提供。"
            ),
            DeclareLaunchArgument(
                "training_output", default_value="", description="训练输出目录，必须显式提供且已存在。"
            ),
            DeclareLaunchArgument(
                "training_name", default_value="omnifleet_course", description="本次训练实验名称。"
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
                    "dataset_yaml": LaunchConfiguration("dataset_yaml"),
                    "training_output": LaunchConfiguration("training_output"),
                    "training_name": LaunchConfiguration("training_name"),
                }.items(),
            ),
        ]
    )
