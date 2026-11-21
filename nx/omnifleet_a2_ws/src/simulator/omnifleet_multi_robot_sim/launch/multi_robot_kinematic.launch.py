from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


ROBOTS = (
    ("robot1", -1.5, 0.0),
    ("robot2", -2.5, 1.2),
    ("robot3", -2.5, -1.2),
)


def _robot_actions(model):
    actions = []
    for name, initial_x, initial_y in ROBOTS:
        prefix = f"{name}/"
        robot_description = ParameterValue(Command(["xacro ", model]), value_type=str)
        actions.extend(
            [
                Node(
                    package="robot_state_publisher",
                    executable="robot_state_publisher",
                    namespace=name,
                    output="screen",
                    parameters=[
                        {
                            "robot_description": robot_description,
                            "frame_prefix": prefix,
                            "use_sim_time": False,
                        }
                    ],
                    remappings=[
                        ("joint_states", f"/{name}/joint_states"),
                        ("tf", "/tf"),
                        ("tf_static", "/tf_static"),
                    ],
                ),
                Node(
                    package="omnifleet_kinematic_sim",
                    executable="ackermann_sim_driver",
                    namespace=name,
                    name="ackermann_sim_driver",
                    output="screen",
                    parameters=[
                        {
                            "odom_frame": f"{name}/odom",
                            "base_frame": f"{name}/base_link",
                            "initial_x": initial_x,
                            "initial_y": initial_y,
                            "use_sim_time": False,
                        }
                    ],
                    remappings=[
                        ("/cmd_vel", f"/{name}/cmd_vel"),
                        ("/rrc_safety/zero_lock", f"/{name}/rrc_safety/zero_lock"),
                        ("/odom", f"/{name}/odom"),
                        ("/wheel/odometry", f"/{name}/wheel/odometry"),
                        ("/joint_states", f"/{name}/joint_states"),
                        ("/vel_raw", f"/{name}/vel_raw"),
                        ("/motor_command_sent", f"/{name}/motor_command_sent"),
                        ("/voltage", f"/{name}/voltage"),
                        ("/driver/mode", f"/{name}/driver/mode"),
                    ],
                ),
                Node(
                    package="tf2_ros",
                    executable="static_transform_publisher",
                    name=f"world_to_{name}_odom",
                    arguments=[
                        "--x", "0", "--y", "0", "--z", "0",
                        "--roll", "0", "--pitch", "0", "--yaw", "0",
                        "--frame-id", "world",
                        "--child-frame-id", f"{name}/odom",
                    ],
                ),
            ]
        )
    return actions


def generate_launch_description():
    package_share = FindPackageShare("omnifleet_multi_robot_sim")
    description_share = FindPackageShare("omnifleet_description")
    model = LaunchConfiguration("model")
    rviz = LaunchConfiguration("rviz")
    foxglove = LaunchConfiguration("foxglove")
    foxglove_port = LaunchConfiguration("foxglove_port")
    auto_demo = LaunchConfiguration("auto_demo")

    actions = [
        DeclareLaunchArgument(
            "model",
            default_value=PathJoinSubstitution(
                [description_share, "urdf", "lunshi_ackermann_lite.urdf"]
            ),
        ),
        DeclareLaunchArgument("rviz", default_value="false"),
        DeclareLaunchArgument("foxglove", default_value="true"),
        DeclareLaunchArgument("foxglove_port", default_value="8796"),
        DeclareLaunchArgument("auto_demo", default_value="false"),
    ]
    actions.extend(_robot_actions(model))
    actions.extend(
        [
            Node(
                package="omnifleet_multi_robot_sim",
                executable="fleet_controller",
                output="screen",
                parameters=[
                    {
                        "auto_demo": auto_demo,
                        "startup_settle_time": 5.0,
                        "use_sim_time": False,
                    }
                ],
            ),
            Node(
                condition=IfCondition(rviz),
                package="rviz2",
                executable="rviz2",
                output="screen",
                arguments=["-d", PathJoinSubstitution([package_share, "rviz", "multi_robot.rviz"])],
                parameters=[{"use_sim_time": False}],
            ),
            Node(
                condition=IfCondition(foxglove),
                package="foxglove_bridge",
                executable="foxglove_bridge",
                output="screen",
                parameters=[
                    {
                        "address": "0.0.0.0",
                        "port": ParameterValue(foxglove_port, value_type=int),
                    }
                ],
            ),
        ]
    )
    return LaunchDescription(actions)
