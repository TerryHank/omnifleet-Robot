"""视觉课程学生入口的静态契约测试。"""

import ast
import re
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PACKAGE_ROOT.parents[1]
TUTORIAL_LAUNCH = PACKAGE_ROOT / "launch"
INNER_LAUNCH = (
    WORKSPACE_ROOT
    / "perception"
    / "omnifleet_vision"
    / "launch"
    / "course_function.launch.py"
)

COURSE_FUNCTIONS = {
    "02_01_camera_monitor",
    "02_03_opencv",
    "02_04_color",
    "02_05_qr",
    "02_06_apriltag",
    "02_07_kcf",
    "02_08_human_perception",
    "02_09_yolo",
    "02_10_depth",
    "02_11_model_training",
    "02_12_tensorrt",
    "02_13_pedestrian",
    "02_14_traffic_light",
    "02_16_vehicle",
    "02_17_license_plate",
    "03_01_camera_topics",
    "03_02_detection_tracking",
    "03_03_target_depth",
    "03_04_vision_lidar",
    "03_05_traffic_events",
    "03_06_chassis_control",
    "03_07_lane_integration",
    "03_08_vision_nav",
    "03_09_edge_deployment",
    "04_01_color_follow",
    "04_02_human_object_follow",
    "04_03_lane_project",
    "04_04_object_navigation",
    "04_05_multimodal_avoidance",
    "04_06_edge_detection",
    "04_07_traffic_safety",
}


def _read(path: Path) -> str:
    """以 UTF-8 读取并先验证 Python 语法。"""

    text = path.read_text(encoding="utf-8")
    ast.parse(text, filename=str(path))
    return text


def test_exactly_31_student_wrappers_exist():
    """课程定义中的 31 个学生入口必须全部存在且没有多余入口。"""

    actual = {path.stem.removeprefix("vision_").removesuffix(".launch") for path in TUTORIAL_LAUNCH.glob("vision_*.launch.py")}
    assert actual == COURSE_FUNCTIONS


def test_each_wrapper_uses_inner_launch_and_safe_motion_default():
    """所有学生入口必须复用内部 Launch，并默认关闭运动。"""

    for course_function in COURSE_FUNCTIONS:
        path = TUTORIAL_LAUNCH / f"vision_{course_function}.launch.py"
        text = _read(path)
        assert f'COURSE_FUNCTION = "{course_function}"' in text
        assert 'FindPackageShare("omnifleet_vision")' in text
        assert '"course_function.launch.py"' in text
        assert re.search(
            r'DeclareLaunchArgument\(\s*"enable_motion",\s*default_value="false"',
            text,
        )
        assert re.search(r'description="[^"\n]*[\u4e00-\u9fff][^"\n]*"', text)


def test_inner_launch_covers_every_function_and_actual_topics():
    """内部 Launch 必须覆盖课程编号、真实传感器话题和包内模型路径。"""

    text = _read(INNER_LAUNCH)
    for course_function in COURSE_FUNCTIONS:
        assert f'"{course_function}"' in text
    assert 'FindPackageShare("omnifleet_vision")' in text
    assert '[share, "models", "vendor", filename]' in text
    assert '"/camera/color/image_raw"' in text
    assert '"/camera/depth/image_raw"' in text
    assert '"/rslidar_points"' in text
    assert '"kcf_follower.launch.py"' in text


def test_motion_never_targets_final_chassis_topic():
    """课程入口只能输出视觉速度候选，不得绕过安全仲裁。"""

    files = [INNER_LAUNCH, *TUTORIAL_LAUNCH.glob("vision_*.launch.py")]
    for path in files:
        text = _read(path)
        assert 'VISION_COMMAND_TOPIC = "/cmd_vel_vision"' in text or path != INNER_LAUNCH
        assert not re.search(r'["\']/cmd_vel["\']', text)


def test_depth_course_uses_aligned_rgb_yolo_and_filtered_depth():
    """02_10 必须在对齐 RGB 上检测，并把框中心映射到对齐深度。"""

    text = _read(INNER_LAUNCH)
    depth_mapping = text.split('"02_10_depth": lambda:', 1)[1].split(
        '"02_13_pedestrian": lambda:', 1
    )[0]
    assert '"ultralytics_detector_node.py"' in depth_mapping
    assert '"input": ALIGNED_COLOR_TOPIC' in depth_mapping
    assert '"input_topic": ALIGNED_COLOR_TOPIC' in depth_mapping
    assert '"depth_topic": DEPTH_TOPIC' in depth_mapping
    assert '"detection_topic": "/vision/depth/yolo"' in depth_mapping


def test_offline_tools_require_explicit_paths_and_safe_shutdown():
    """训练和 TensorRT 缺少路径时必须说明原因并安全结束。"""

    text = _read(INNER_LAUNCH)
    assert 'dataset_yaml 和 training_output' in text
    assert 'engine_path 和 report_path' in text
    assert "EmitEvent(event=Shutdown" in text
    assert '"02_11_model_training"' in text
    assert '"02_12_tensorrt"' in text


def test_kcf_student_entry_forwards_gui_and_headless_roi_arguments():
    """KCF 学生入口必须同时支持鼠标选框和无界面坐标选框。"""

    wrapper = _read(TUTORIAL_LAUNCH / "vision_02_07_kcf.launch.py")
    inner = _read(INNER_LAUNCH)
    for argument in (
        "use_gui", "tracking_scale", "roi_x", "roi_y", "roi_width", "roi_height"
    ):
        assert re.search(rf'DeclareLaunchArgument\(\s*"{argument}"', wrapper)
        assert f'"{argument}": LaunchConfiguration("{argument}")' in wrapper
        assert re.search(rf'DeclareLaunchArgument\(\s*"{argument}"', inner)
        assert f'"{argument}": LaunchConfiguration("{argument}")' in inner


def test_all_realtime_visual_courses_have_a_gui_path():
    """除训练和 TensorRT 外，29 个实时视觉课程都必须具备窗口路径。"""

    text = _read(INNER_LAUNCH)
    tree = ast.parse(text)
    display_assignment = next(
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(getattr(target, "id", "") == "DISPLAY_TOPICS" for target in node.targets)
    )
    display_keys = {item.value for item in display_assignment.value.keys}
    self_displayed = {
        "02_01_camera_monitor", "02_03_opencv", "02_04_color", "02_05_qr",
        "02_06_apriltag", "02_07_kcf", "02_10_depth",
    }
    non_realtime = {"02_11_model_training", "02_12_tensorrt"}
    assert display_keys | self_displayed | non_realtime == COURSE_FUNCTIONS
    assert len(display_keys) == 22
    assert '"image_display_node.py"' in text
    assert 'ParameterValue(LaunchConfiguration("use_gui"), value_type=bool)' in text
