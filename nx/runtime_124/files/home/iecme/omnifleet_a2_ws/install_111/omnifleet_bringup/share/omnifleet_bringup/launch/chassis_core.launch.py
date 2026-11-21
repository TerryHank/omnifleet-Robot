from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    robot_description_file = PathJoinSubstitution(
        [FindPackageShare("omnifleet_a2_description"), "urdf", LaunchConfiguration("model")]
    )
    robot_description = ParameterValue(
        Command(["cat ", robot_description_file]), value_type=str
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("serial_port", default_value="/dev/myserial"),
            DeclareLaunchArgument(
                "steering_angle_target_topic",
                default_value="/omnifleet_a2/chassis/steering_angle_cmd",
            ),
            DeclareLaunchArgument("max_steering_angle_deg", default_value="15"),
            DeclareLaunchArgument("steering_center_offset_deg", default_value="0"),
            DeclareLaunchArgument("motion_watchdog_timeout_ms", default_value="1000"),
            DeclareLaunchArgument("watchdog_heartbeat_rate_hz", default_value="10.0"),
            DeclareLaunchArgument("model", default_value="lunshi_ackermann_lite.urdf"),
            Node(
                package="omnifleet_a2_bringup",
                executable="ackermann_driver",
                name="omnifleet_a2_driver",
                output="screen",
                emulate_tty=True,
                parameters=[
                    {
                        "serial_port": LaunchConfiguration("serial_port"),
                        # OEM-style PWM dead-zone offsets, split by motor and
                        # physical direction. NX re-sends them after each boot.
                        "motor_deadzone_pwm_m1_forward": 2050,
                        "motor_deadzone_pwm_m2_forward": 2250,
                        "motor_deadzone_pwm_m1_reverse": 2000,
                        "motor_deadzone_pwm_m2_reverse": 2200,
                        "max_steering_angle_deg": ParameterValue(
                            LaunchConfiguration("max_steering_angle_deg"), value_type=int
                        ),
                        "steering_center_offset_deg": ParameterValue(
                            LaunchConfiguration("steering_center_offset_deg"), value_type=int
                        ),
                        "motion_watchdog_timeout_ms": ParameterValue(
                            LaunchConfiguration("motion_watchdog_timeout_ms"),
                            value_type=int,
                        ),
                        "watchdog_heartbeat_rate_hz": ParameterValue(
                            LaunchConfiguration("watchdog_heartbeat_rate_hz"),
                            value_type=float,
                        ),
                        "steering_angle_target_topic": LaunchConfiguration(
                            "steering_angle_target_topic"
                        ),
                        "use_sim_time": use_sim_time,
                    }
                ],
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
        ]
    )
