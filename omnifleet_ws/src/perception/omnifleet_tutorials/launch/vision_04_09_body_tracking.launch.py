"""Final presentation: official body_tracking with the existing Jetson perception."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration,PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

COURSE_FUNCTION = "04_09_body_tracking"

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("start_camera",default_value="false",description="复用104常驻相机"),
        DeclareLaunchArgument("use_gui",default_value="true",description="显示Fox实时结果"),
        DeclareLaunchArgument("enable_motion",default_value="false",description="沿用课程运动开关"),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(PathJoinSubstitution([
            FindPackageShare("omnifleet_vision"),"launch","course_function.launch.py"])),
            launch_arguments={"course_function":COURSE_FUNCTION,
                              "start_camera":LaunchConfiguration("start_camera"),
                              "use_gui":LaunchConfiguration("use_gui"),
                              "enable_motion":LaunchConfiguration("enable_motion")}.items())])
