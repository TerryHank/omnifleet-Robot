"""经典视觉纯函数测试，不需要 ROS 图像消息或相机。"""

import importlib.util
from pathlib import Path

import cv2
import numpy as np
import pytest


ALGORITHMS_FILE = Path(__file__).resolve().parents[1] / "scripts" / "classical" / "algorithms.py"
SPEC = importlib.util.spec_from_file_location("classical_algorithms", ALGORITHMS_FILE)
ALGORITHMS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ALGORITHMS)


def test_camera_monitor_detects_frequency_and_frozen_frame():
    monitor = ALGORITHMS.CameraHealthMonitor(
        minimum_fps=5.0, freeze_frame_count=2, freeze_difference=0.0
    )
    image = np.zeros((60, 80, 3), dtype=np.uint8)
    monitor.update(image, 0.0)
    monitor.update(image, 0.1)
    result = monitor.update(image, 0.2)
    assert result["fps"] == pytest.approx(10.0)
    assert result["frozen"] is True
    assert result["status"] == "frozen"


@pytest.mark.parametrize("operation", ["gray", "blur", "canny"])
def test_opencv_processing_returns_bgr_debug_image(operation):
    image = np.zeros((100, 120, 3), dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (80, 80), (255, 255, 255), -1)
    debug, result = ALGORITHMS.process_opencv_image(image, operation)
    assert debug.shape == image.shape
    assert result["operation"] == operation
    assert result["edge_pixels"] > 0


def test_hsv_color_recognition_finds_four_colors():
    image = np.zeros((120, 240, 3), dtype=np.uint8)
    colors = [(0, 0, 255), (0, 255, 255), (0, 255, 0), (255, 0, 0)]
    for index, color in enumerate(colors):
        cv2.rectangle(image, (index * 60 + 5, 20), (index * 60 + 50, 100), color, -1)
    _, result = ALGORITHMS.recognize_colors(image, minimum_area=100.0)
    assert result["count"] == 4
    assert {item["color"] for item in result["detections"]} == {"red", "yellow", "green", "blue"}


def test_qr_recognition_handles_empty_image():
    image = np.full((120, 120, 3), 255, dtype=np.uint8)
    debug, result = ALGORITHMS.recognize_qr_codes(image)
    assert debug.shape == image.shape
    assert result == {"detected": False, "count": 0, "detections": []}


def test_apriltag_recognition_reports_capability():
    image = np.full((120, 120, 3), 255, dtype=np.uint8)
    debug, result = ALGORITHMS.recognize_apriltags(image)
    assert debug.shape == image.shape
    assert isinstance(result["available"], bool)
    assert result["count"] == 0


def test_qr_source_has_pyzbar_fallback_for_opencv_without_quirc():
    source = ALGORITHMS_FILE.read_text(encoding="utf-8")
    assert "from pyzbar.pyzbar import ZBarSymbol, decode" in source
    assert '"backend": "pyzbar"' in source


def test_depth_measurement_supports_16u_and_32f():
    depth_16u = np.full((20, 30), 1500, dtype=np.uint16)
    depth_16u[0, 0] = 0
    _, result_16u = ALGORITHMS.measure_depth(depth_16u, "16UC1", (0, 0, 30, 20))
    assert result_16u["median_m"] == pytest.approx(1.5)
    assert result_16u["valid_count"] == 599

    depth_32f = np.full((20, 30), 2.25, dtype=np.float32)
    depth_32f[0, 0] = np.nan
    _, result_32f = ALGORITHMS.measure_depth(depth_32f, "32FC1", (0, 0, 30, 20))
    assert result_32f["median_m"] == pytest.approx(2.25)
    assert result_32f["valid_count"] == 599


def test_lane_detection_returns_center_and_offset():
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    cv2.line(image, (120, 239), (145, 130), (255, 255, 255), 14)
    cv2.line(image, (220, 239), (195, 130), (0, 255, 255), 14)
    debug, result = ALGORITHMS.detect_lane(image, roi_start_ratio=0.5, minimum_area=50.0)
    assert debug.shape == image.shape
    assert result["detected"] is True
    assert abs(result["offset_pixels"]) < 20


def test_classical_nodes_do_not_publish_velocity_commands():
    scripts_dir = ALGORITHMS_FILE.parent
    source = "\n".join(path.read_text(encoding="utf-8") for path in scripts_dir.glob("*.py"))
    forbidden = "cmd" + "_vel"
    assert forbidden not in source


def test_classical_nodes_use_uniform_topics_and_actual_camera_defaults():
    scripts_dir = ALGORITHMS_FILE.parent
    color_nodes = [
        "camera_monitor_node.py",
        "opencv_processor_node.py",
        "color_recognition_node.py",
        "qr_recognition_node.py",
        "apriltag_recognition_node.py",
        "lane_detection_node.py",
    ]
    for filename in color_nodes:
        source = (scripts_dir / filename).read_text(encoding="utf-8")
        assert '"/tof/color/image_raw"' in source
    depth_source = (scripts_dir / "depth_measurement_node.py").read_text(encoding="utf-8")
    assert '"/tof/aligned_depth_to_color/image_raw"' in depth_source
    support_source = (scripts_dir / "ros_support.py").read_text(encoding="utf-8")
    for parameter in (
        "input_topic", "debug_topic", "result_topic", "qos_depth", "use_gui", "window_name"
    ):
        assert f'"{parameter}"' in support_source
    assert "cv2.imshow" in support_source
    assert "cv2.waitKey" in support_source
    assert "cv2.destroyWindow" in support_source
    assert 'os.environ.get("DISPLAY")' in support_source


def test_synthetic_scenes_are_brand_free_and_detectable():
    """课程测试图像必须由代码生成，不包含厂商截图或真实隐私素材。"""

    path = ALGORITHMS_FILE.parent / "synthetic_scene_publisher.py"
    spec = importlib.util.spec_from_file_location("synthetic_scene_publisher", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    color = module.build_scene("color")
    lane = module.build_scene("lane")
    tag = module.build_scene("apriltag")
    assert color.shape == lane.shape == tag.shape == (480, 640, 3)
    assert "wheeltec" not in path.read_text(encoding="utf-8").lower()


def test_unified_image_display_is_gui_optional_and_installed():
    package = ALGORITHMS_FILE.parents[2]
    display_source = (package / "scripts" / "image_display_node.py").read_text(encoding="utf-8")
    cmake = (package / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'os.environ.get("DISPLAY")' in display_source
    assert "cv2.imshow" in display_source
    assert "cv2.waitKey" in display_source
    assert "cv2.destroyWindow" in display_source
    assert "scripts/image_display_node.py" in cmake
