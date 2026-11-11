"""Cancel prior-map waypoint navigation and end the manual stack safely."""

from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo


def generate_launch_description():
    return LaunchDescription([
        LogInfo(msg="正在取消导航目标、锁定零速度并关闭手动导航栈"),
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                "set -e; timeout 15s ros2 service call "
                "/omnifleet_a2/system/stop_manual_stack std_srvs/srv/Trigger '{}'",
            ],
            output="screen",
        ),
    ])
