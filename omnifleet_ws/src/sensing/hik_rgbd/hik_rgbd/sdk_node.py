"""Load the driver's single configuration for the familiar official ROS entry points."""
import sys
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from omnifleet_hikrobot_rgbd.camera_node import main as camera_main


def main(args=None):
    parameters = Path(get_package_share_directory("omnifleet_hikrobot_rgbd")) / "config" / "mv_dt01snu.yaml"
    arguments = list(sys.argv[1:] if args is None else args)
    camera_main(args=["--ros-args", "--params-file", str(parameters), "--", *arguments])
