from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    model = LaunchConfiguration("model")
    use_rviz = LaunchConfiguration("use_rviz")
    use_sim_time = LaunchConfiguration("use_sim_time")
    description_share = FindPackageShare("omnifleet_description")
    robot_description = ParameterValue(Command(["xacro ", model]), value_type=str)

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "model",
                default_value=PathJoinSubstitution(
                    [description_share, "urdf", "lunshi_ackermann_lite.urdf"]
                ),
            ),
            DeclareLaunchArgument("use_rviz", default_value="false"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                output="screen",
                parameters=[
                    {
                        "robot_description": robot_description,
                        "use_sim_time": use_sim_time,
                    }
                ],
            ),
            Node(
                package="omnifleet_kinematic_sim",
                executable="ackermann_sim_driver",
                name="ackermann_sim_driver",
                output="screen",
                parameters=[{"use_sim_time": use_sim_time}],
            ),
            Node(
                condition=IfCondition(use_rviz),
                package="rviz2",
                executable="rviz2",
                output="screen",
                arguments=[
                    "-d",
                    PathJoinSubstitution(
                        [description_share, "rviz", "lunshi_ackermann.rviz"]
                    ),
                ],
                parameters=[{"use_sim_time": use_sim_time}],
            ),
        ]
    )
