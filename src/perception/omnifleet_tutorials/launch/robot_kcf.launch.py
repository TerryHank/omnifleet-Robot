"""One-command OmniFleet KCF tracking workflow.

Starts the RGB-D camera by default, then starts the reusable KCF node. The
production chassis is always owned by ``omnifleet-t2-chassis.service``.
Vehicle motion is disabled by default and, when enabled, is published only to
``/cmd_vel_vision`` for downstream safety arbitration.
"""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    LogInfo,
    OpaqueFunction,
    TimerAction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def reject_chassis_launch_args(context, *args, **kwargs):
    for name in ("start_chassis", "start_chassis_core"):
        value = context.launch_configurations.get(name)
        if value is not None and str(value).strip().lower() in {
            "1", "true", "yes", "on"
        }:
            raise RuntimeError(
                f"{name} is removed: the chassis is managed only by "
                "omnifleet-t2-chassis.service via systemctl"
            )
    return []


def generate_launch_description():
    start_camera = LaunchConfiguration("start_camera")
    enable_motion = LaunchConfiguration("enable_motion")

    camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare(LaunchConfiguration("camera_package")),
                    "launch",
                    LaunchConfiguration("camera_launch_file"),
                ]
            )
        ),
        condition=IfCondition(start_camera),
    )

    vision = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("omnifleet_vision"), "launch", "kcf_follower.launch.py"]
            )
        ),
        launch_arguments={
            "tracker_color_topic": LaunchConfiguration("tracker_color_topic"),
            "aligned_color_topic": LaunchConfiguration("aligned_color_topic"),
            "depth_topic": LaunchConfiguration("depth_topic"),
            "output_image_topic": LaunchConfiguration("output_image_topic"),
            "cmd_vel_topic": LaunchConfiguration("cmd_vel_topic"),
            "enable_motion": enable_motion,
            "use_gui": LaunchConfiguration("use_gui"),
            "roi_x": LaunchConfiguration("roi_x"),
            "roi_y": LaunchConfiguration("roi_y"),
            "roi_width": LaunchConfiguration("roi_width"),
            "roi_height": LaunchConfiguration("roi_height"),
            "target_distance": LaunchConfiguration("target_distance"),
            "max_pair_delta": LaunchConfiguration("max_pair_delta"),
            "tracking_timeout": LaunchConfiguration("tracking_timeout"),
            "depth_timeout": LaunchConfiguration("depth_timeout"),
            "control_rate": LaunchConfiguration("control_rate"),
            "minimum_linear_speed": LaunchConfiguration("minimum_linear_speed"),
            "max_linear_speed": LaunchConfiguration("max_linear_speed"),
            "linear_deadband": LaunchConfiguration("linear_deadband"),
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "start_camera",
                default_value="false",
                description="Use the resident USB camera service by default.",
            ),
            DeclareLaunchArgument(
                "camera_package",
                default_value="omnifleet_bringup",
                description="Package that owns the USB camera launch file.",
            ),
            DeclareLaunchArgument(
                "camera_launch_file",
                default_value="usb_camera.launch.py",
                description="USB camera launch file.",
            ),
            DeclareLaunchArgument(
                "tracker_color_topic",
                default_value="/camera/color/image_raw",
                description="High-rate color image used to update the KCF tracker.",
            ),
            DeclareLaunchArgument(
                "aligned_color_topic",
                default_value="/camera/color/image_raw",
                description="Color image paired with aligned depth for distance updates.",
            ),
            DeclareLaunchArgument(
                "depth_topic",
                default_value="/camera/depth/image_raw",
                description="Depth image aligned to the color image.",
            ),
            DeclareLaunchArgument(
                "output_image_topic",
                default_value="/omnifleet_vision/kcf/image",
                description="Annotated KCF tracking image.",
            ),
            DeclareLaunchArgument(
                "cmd_vel_topic",
                default_value="/cmd_vel_vision",
                description="Motion candidate topic; must feed the safety mux, never final /cmd_vel.",
            ),
            DeclareLaunchArgument(
                "enable_motion",
                default_value="false",
                description="Publish motion candidates. Disabled by default for safety.",
            ),
            DeclareLaunchArgument(
                "use_gui",
                default_value="true",
                description="Use an OpenCV window for mouse ROI selection.",
            ),
            DeclareLaunchArgument(
                "roi_x", default_value="0", description="Headless initial ROI x coordinate."
            ),
            DeclareLaunchArgument(
                "roi_y", default_value="0", description="Headless initial ROI y coordinate."
            ),
            DeclareLaunchArgument(
                "roi_width", default_value="0", description="Headless initial ROI width."
            ),
            DeclareLaunchArgument(
                "roi_height", default_value="0", description="Headless initial ROI height."
            ),
            DeclareLaunchArgument(
                "target_distance",
                default_value="0.8",
                description="Desired target distance in metres when motion is enabled.",
            ),
            DeclareLaunchArgument(
                "max_pair_delta",
                default_value="0.8",
                description="Maximum accepted RGB-D timestamp delta in seconds.",
            ),
            DeclareLaunchArgument(
                "tracking_timeout",
                default_value="0.5",
                description="Stop motion when KCF updates are stale for this many seconds.",
            ),
            DeclareLaunchArgument(
                "depth_timeout",
                default_value="0.5",
                description="Stop motion when no valid aligned depth arrives within seconds.",
            ),
            DeclareLaunchArgument(
                "control_rate",
                default_value="10.0",
                description="Motion candidate publication rate in hertz.",
            ),
            DeclareLaunchArgument(
                "minimum_linear_speed",
                default_value="0.40",
                description="Non-zero chassis speed threshold in metres per second.",
            ),
            DeclareLaunchArgument(
                "max_linear_speed",
                default_value="0.40",
                description="Maximum visual-follow linear speed in metres per second.",
            ),
            DeclareLaunchArgument(
                "linear_deadband",
                default_value="0.15",
                description="Distance-error deadband in metres before linear motion starts.",
            ),
            DeclareLaunchArgument(
                "startup_delay",
                default_value="2.0",
                description="Delay before starting KCF after the camera action.",
            ),
            LogInfo(
                condition=UnlessCondition(enable_motion),
                msg="KCF tracking starts with motion disabled; output image remains active.",
            ),
            LogInfo(
                condition=IfCondition(enable_motion),
                msg=(
                    "KCF motion is enabled on /cmd_vel_vision; the production safety mux "
                    "and collision monitor must already own the final /cmd_vel."
                ),
            ),
            OpaqueFunction(function=reject_chassis_launch_args),
            camera,
            TimerAction(
                period=LaunchConfiguration("startup_delay"), actions=[vision]
            ),
        ]
    )
