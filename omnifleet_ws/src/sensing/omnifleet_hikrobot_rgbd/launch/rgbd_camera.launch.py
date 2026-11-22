from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from pathlib import Path


def generate_launch_description():
    share = Path(get_package_share_directory("omnifleet_hikrobot_rgbd"))
    return LaunchDescription([
        Node(
            package="omnifleet_hikrobot_rgbd",
            executable="camera_node",
            name="mv_dt01snu_camera",
            output="screen",
            parameters=[str(share / "config" / "mv_dt01snu.yaml")],
            additional_env={
                "ZENOH_CONFIG_OVERRIDE":
                    "transport/shared_memory/enabled=false;transport/shared_memory/transport_optimization/enabled=false"
            },
        )
    ])
