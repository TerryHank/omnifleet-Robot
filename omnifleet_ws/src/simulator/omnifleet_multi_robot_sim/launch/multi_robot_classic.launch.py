from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


ROBOTS = (
    ("robot1", "-1.5", "0.0"),
    ("robot2", "-2.5", "1.2"),
    ("robot3", "-2.5", "-1.2"),
)


def _robot_actions(model):
    state_publishers = []
    spawners = []
    static_transforms = []
    for name, x, y in ROBOTS:
        prefix = f"{name}/"
        robot_description = ParameterValue(
            Command(
                [
                    "xacro ",
                    model,
                    " robot_namespace:=/",
                    name,
                    " frame_prefix:=",
                    prefix,
                    " mapping_sensors:=false stable_drive:=true publish_odom_tf:=true",
                ]
            ),
            value_type=str,
        )
        state_publishers.append(
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                namespace=name,
                output="screen",
                parameters=[
                    {
                        "robot_description": robot_description,
                        "frame_prefix": prefix,
                        "use_sim_time": True,
                    }
                ],
                remappings=[("tf", "/tf"), ("tf_static", "/tf_static")],
            )
        )
        # The xacro already owns the plugin namespace. Do not pass
        # spawn_entity.py's -robot_namespace, which would apply it twice.
        spawners.append(
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                namespace=name,
                output="screen",
                arguments=[
                    "-entity",
                    name,
                    "-topic",
                    "robot_description",
                    "-x",
                    x,
                    "-y",
                    y,
                    "-z",
                    "0.065",
                ],
            )
        )
        static_transforms.append(
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
            )
        )
    return state_publishers + static_transforms + [TimerAction(period=3.0, actions=spawners)]


def generate_launch_description():
    package_share = FindPackageShare("omnifleet_multi_robot_sim")
    description_share = FindPackageShare("omnifleet_description")
    model = LaunchConfiguration("model")
    world = LaunchConfiguration("world")
    gui = LaunchConfiguration("gui")
    rviz = LaunchConfiguration("rviz")
    foxglove = LaunchConfiguration("foxglove")
    foxglove_port = LaunchConfiguration("foxglove_port")
    auto_demo = LaunchConfiguration("auto_demo")

    actions = [
        DeclareLaunchArgument(
            "model",
            default_value=PathJoinSubstitution(
                [description_share, "urdf", "lunshi_ackermann_lite_gazebo_classic.urdf.xacro"]
            ),
        ),
        DeclareLaunchArgument(
            "world",
            default_value=PathJoinSubstitution([package_share, "worlds", "multi_robot_open.world"]),
        ),
        DeclareLaunchArgument("gui", default_value="true"),
        DeclareLaunchArgument("rviz", default_value="true"),
        DeclareLaunchArgument("foxglove", default_value="true"),
        DeclareLaunchArgument("foxglove_port", default_value="8796"),
        DeclareLaunchArgument("auto_demo", default_value="true"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"])
            ),
            launch_arguments={
                "world": world,
                "gui": gui,
                "server": "true",
                "verbose": "false",
                "pause": "false",
            }.items(),
        ),
    ]
    actions.extend(_robot_actions(model))
    actions.extend(
        [
            Node(
                package="omnifleet_multi_robot_sim",
                executable="fleet_controller",
                output="screen",
                parameters=[{"auto_demo": auto_demo, "use_sim_time": True}],
            ),
            Node(
                condition=IfCondition(rviz),
                package="rviz2",
                executable="rviz2",
                output="screen",
                arguments=["-d", PathJoinSubstitution([package_share, "rviz", "multi_robot.rviz"])],
                parameters=[{"use_sim_time": True}],
            ),
            Node(
                condition=IfCondition(foxglove),
                package="foxglove_bridge",
                executable="foxglove_bridge",
                output="screen",
                parameters=[{"port": ParameterValue(foxglove_port, value_type=int)}],
            ),
        ]
    )
    return LaunchDescription(actions)
