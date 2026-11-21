from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("device", default_value="/dev/video0"),
        DeclareLaunchArgument(
            "topic", default_value="/camera/color/image_raw/compressed"
        ),
        Node(
            package="omnifleet_bringup",
            executable="usb_camera_publisher",
            name="tutorial_usb_camera",
            output="screen",
            parameters=[{
                "device": LaunchConfiguration("device"),
                "topic": LaunchConfiguration("topic"),
                "frame_id": "camera_link",
                "fps": 15.0,
            }],
        ),
    ])
