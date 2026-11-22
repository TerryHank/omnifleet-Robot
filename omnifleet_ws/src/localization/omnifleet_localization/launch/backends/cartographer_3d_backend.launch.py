"""Cartographer 3D backend for the RoboSense Airy production chain."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _nodes(context):
    if LaunchConfiguration("operation").perform(context) not in {
        "mapping",
        "slam_navigation",
    }:
        raise RuntimeError("Cartographer 3D only supports mapping or slam_navigation")

    share = Path(get_package_share_directory("omnifleet_localization"))
    configuration_directory = share / "config" / "cartographer_3d"
    use_sim_time = LaunchConfiguration("use_sim_time")
    return [
        Node(
            package="omnifleet_localization",
            executable="airy_imu_adapter_node",
            name="omnifleet_t2_airy_imu_adapter",
            output="screen",
            parameters=[{
                "input_topic": "/rslidar_imu_data",
                "output_topic": "/rslidar_imu_data_corrected",
                "output_frame": "rslidar",
                "rotation_xyzw": [
                    -0.7068467736244202,
                    0.7073657512664795,
                    -0.0005705897347070277,
                    0.000999057781882584,
                ],
                "use_sim_time": use_sim_time,
            }],
        ),
        Node(
            package="omnifleet_localization",
            executable="airy_imu_adapter_node",
            name="omnifleet_t2_cartographer_imu_adapter",
            output="screen",
            parameters=[{
                "input_topic": "/rslidar_imu_data_corrected",
                "output_topic": "/omnifleet_t2/cartographer/imu",
                "output_frame": "base_link",
                "rotation_xyzw": [0.0, 0.0, 0.0, 1.0],
                "linear_acceleration_scale": 9.80665,
                "angular_velocity_bias": [
                    -0.00597255,
                    -0.01907346,
                    -0.00108195,
                ],
                "drop_non_increasing_timestamps": True,
                "use_sim_time": use_sim_time,
            }],
        ),
        Node(
            package="cartographer_ros",
            executable="cartographer_node",
            name="cartographer_node",
            output="screen",
            parameters=[{"use_sim_time": use_sim_time}],
            arguments=[
                "-configuration_directory", str(configuration_directory),
                "-configuration_basename", "omnifleet_3d.lua",
            ],
            remappings=[
                ("points2", "/rslidar_points"),
                ("imu", "/omnifleet_t2/cartographer/imu"),
                ("odom", "/omnifleet_t2/chassis/wheel_odometry"),
            ],
        ),
        Node(
            package="cartographer_ros",
            executable="cartographer_occupancy_grid_node",
            name="cartographer_occupancy_grid_node",
            output="screen",
            parameters=[{"use_sim_time": use_sim_time}],
            arguments=["-resolution", "0.08", "-publish_period_sec", "1.0"],
        ),
        Node(
            package="omnifleet_localization",
            executable="cartographer_odom_adapter",
            name="omnifleet_t2_cartographer_odom_adapter",
            output="screen",
            parameters=[{"use_sim_time": use_sim_time}],
        ),
        Node(
            package="omnifleet_localization",
            executable="wheel_slip_detector",
            name="omnifleet_t2_wheel_slip_detector",
            output="screen",
            parameters=[{
                "wheel_odom_topic": "/omnifleet_t2/chassis/wheel_odometry",
                "primary_odom_topic": "/odom",
                "use_sim_time": use_sim_time,
            }],
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument("operation", default_value="mapping"),
        DeclareLaunchArgument("map_id", default_value="active"),
        DeclareLaunchArgument("map_dir", default_value="/home/iecme/omnifleet_data/maps"),
        OpaqueFunction(function=_nodes),
    ])
