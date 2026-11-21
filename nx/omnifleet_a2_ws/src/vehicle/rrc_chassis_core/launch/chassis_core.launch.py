from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    robot_description_file = PathJoinSubstitution(
        [FindPackageShare("lunshi_chassis_description"), "urdf", LaunchConfiguration("model")]
    )
    robot_description = ParameterValue(
        Command(["cat ", robot_description_file]), value_type=str
    )
    safety_mux = PathJoinSubstitution(
        [FindPackageShare("rrc_chassis_core"), "config", "safety_mux.yaml"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("serial_port", default_value="/dev/myserial"),
            DeclareLaunchArgument("cmd_vel_timeout", default_value="0.5"),
            DeclareLaunchArgument("model", default_value="lunshi_ackermann_lite.urdf"),
            Node(
                package="twist_mux",
                executable="twist_mux",
                name="rrc_command_mux",
                output="screen",
                parameters=[safety_mux, {"use_sim_time": use_sim_time}],
                remappings=[("/cmd_vel_out", "/cmd_vel")],
            ),
            Node(
                package="yahboomcar_bringup",
                executable="Ackman_driver_R2",
                name="yahboom_r2_driver",
                output="screen",
                emulate_tty=True,
                parameters=[
                    {
                        "serial_port": LaunchConfiguration("serial_port"),
                        "xlinear_limit": 0.80,
                        "minimum_linear_speed": 0.45,
                        "angular_limit": 0.80,
                        "nav_use_rotvel": False,
                        "cmd_angular_to_steering": True,
                        "wheelbase": 0.362295943,
                        "steering_limit": 30.0,
                        "motion_command_rate": 20.0,
                        "cmd_vel_timeout": LaunchConfiguration("cmd_vel_timeout"),
                        "use_sim_time": use_sim_time,
                    }
                ],
            ),
            Node(
                package="yahboomcar_base_node",
                executable="base_node_R2",
                name="yahboom_r2_wheel_odometry",
                output="screen",
                emulate_tty=True,
                parameters=[
                    {
                        "pub_odom_tf": False,
                        "odom_frame": "odom",
                        # Wheel odometry is diagnostic only; GLIM exclusively owns TF.
                        "base_footprint_frame": "base_link",
                        "wheelbase": 0.362295943,
                        "use_sim_time": use_sim_time,
                    }
                ],
                remappings=[("/odom_raw", "/wheel/odometry")],
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[
                    {
                        "robot_description": robot_description,
                        "use_sim_time": use_sim_time,
                    }
                ],
            ),
            Node(
                package="rrc_chassis_core",
                executable="voltage_display_node.py",
                name="rrc_voltage_display",
                output="screen",
            ),
        ]
    )
