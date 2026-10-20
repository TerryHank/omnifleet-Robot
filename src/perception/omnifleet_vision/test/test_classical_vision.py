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


def test_traffic_light_color_filter_finds_round_lamps_and_rejects_large_regions():
    image = np.zeros((240, 480, 3), dtype=np.uint8)
    cv2.circle(image, (80, 120), 18, (0, 0, 255), -1)
    cv2.circle(image, (180, 120), 18, (0, 255, 255), -1)
    cv2.circle(image, (280, 120), 18, (0, 255, 0), -1)
    cv2.rectangle(image, (360, 20), (479, 220), (0, 0, 255), -1)
    debug, result = ALGORITHMS.detect_traffic_light_colors(
        image, minimum_area=100.0, maximum_area_ratio=0.03
    )
    assert debug.shape == image.shape
    assert result["count"] == 3
    assert result["counts"] == {"red": 1, "yellow": 1, "green": 1}
    assert {item["branch"] for item in result["detections"]} == {"opencv_hsv"}


def test_traffic_light_color_filter_rejects_dim_unlit_lenses():
    image = np.zeros((160, 320, 3), dtype=np.uint8)
    cv2.circle(image, (80, 80), 16, (20, 75, 20), -1)
    cv2.circle(image, (160, 80), 16, (0, 0, 255), -1)
    _, result = ALGORITHMS.detect_traffic_light_colors(image, minimum_area=80.0)
    assert result["counts"] == {"red": 1, "yellow": 0, "green": 0}


def test_traffic_light_color_filter_scales_minimum_area_with_resolution():
    image = np.zeros((1024, 1920, 3), dtype=np.uint8)
    cv2.circle(image, (100, 100), 4, (0, 0, 255), -1)
    cv2.circle(image, (500, 500), 14, (0, 0, 255), -1)
    _, result = ALGORITHMS.detect_traffic_light_colors(image)
    assert result["counts"] == {"red": 1, "yellow": 0, "green": 0}


def test_traffic_light_cascade_checks_colors_only_inside_yolo_rois():
    image = np.zeros((220, 360, 3), dtype=np.uint8)
    cv2.circle(image, (100, 85), 18, (0, 0, 255), -1)
    cv2.circle(image, (300, 110), 20, (0, 255, 0), -1)
    yolo = [{"class": "traffic light", "confidence": 0.92, "bbox": [50, 25, 110, 150]}]
    debug, result = ALGORITHMS.detect_traffic_light_colors_in_yolo_rois(
        image, yolo, minimum_area=40.0, maximum_area_ratio=0.35,
        minimum_confidence=0.45,
    )
    assert debug.shape == image.shape
    assert result["roi_count"] == 1
    assert result["counts"] == {"red": 1, "yellow": 0, "green": 0}
    detection = result["detections"][0]
    assert detection["branch"] == "opencv_hsv_in_yolo_roi"
    assert detection["yolo_index"] == 0
    assert detection["yolo_bbox"] == [50, 25, 110, 150]
    assert detection["center"][0] < 160


def test_traffic_light_cascade_has_no_full_frame_hsv_fallback():
    image = np.zeros((160, 240, 3), dtype=np.uint8)
    cv2.circle(image, (120, 80), 20, (0, 255, 0), -1)
    _, result = ALGORITHMS.detect_traffic_light_colors_in_yolo_rois(image, [])
    assert result["roi_count"] == 0
    assert result["counts"] == {"red": 0, "yellow": 0, "green": 0}
    assert result["detections"] == []


def test_traffic_light_cascade_keeps_only_best_candidate_per_color_and_roi():
    image = np.zeros((240, 180, 3), dtype=np.uint8)
    cv2.circle(image, (90, 75), 24, (0, 0, 160), -1)
    cv2.circle(image, (45, 170), 5, (0, 0, 255), -1)
    cv2.circle(image, (135, 170), 6, (0, 0, 255), -1)
    yolo = [{"class": "traffic light", "confidence": 0.91, "bbox": [20, 20, 140, 200]}]
    _, result = ALGORITHMS.detect_traffic_light_colors_in_yolo_rois(
        image, yolo, minimum_area=20.0, maximum_area_ratio=0.35,
        minimum_confidence=0.45,
    )
    assert result["counts"] == {"red": 1, "yellow": 0, "green": 0}
    assert result["detections"][0]["bbox"][2] > 40


def test_qr_recognition_handles_empty_image():
    image = np.full((120, 120, 3), 255, dtype=np.uint8)
    debug, result = ALGORITHMS.recognize_qr_codes(image)
    assert debug.shape == image.shape
    assert result == {"detected": False, "count": 0, "detections": []}


def test_qr_decoded_text_can_be_drawn_on_debug_image():
    image = np.full((120, 360, 3), 255, dtype=np.uint8)
    debug = ALGORITHMS.draw_utf8_label(image, "QR: 课程内容 TEST-123", (10, 40))
    assert debug.shape == image.shape
    assert np.count_nonzero(cv2.absdiff(debug, image)) > 100


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


def test_target_depth_rejects_range_errors_and_flying_points():
    depth = np.full((31, 31), 1800, dtype=np.uint16)
    depth[10:13, 10:13] = 3200
    depth[14, 14] = 0
    depth[15, 15] = 250
    result = ALGORITHMS.measure_target_depth(
        depth,
        "16UC1",
        (15, 15),
        sample_radius=7,
        minimum_depth=0.3,
        maximum_depth=3.5,
    )
    assert result["detected"] is True
    assert result["depth_m"] == pytest.approx(1.8)
    assert result["range_rejected_count"] == 2
    assert result["outlier_rejected_count"] == 9
    assert result["filter"] == "range_then_median_mad"


def test_target_depth_requires_enough_filtered_samples():
    depth = np.zeros((15, 15), dtype=np.uint16)
    depth[7, 7] = 1200
    result = ALGORITHMS.measure_target_depth(
        depth, "16UC1", (7, 7), sample_radius=3, minimum_inlier_count=5,
    )
    assert result["detected"] is False
    assert result["depth_m"] is None


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
        assert '"/camera/color/image_raw"' in source
    depth_source = (scripts_dir / "depth_measurement_node.py").read_text(encoding="utf-8")
    assert '"/camera/color/image_raw"' in depth_source
    assert '"/camera/depth/image_raw"' in depth_source
    assert '"/vision/depth/yolo"' in depth_source
    assert "measure_target_depth" in depth_source
    assert '"range_then_median_mad"' in ALGORITHMS_FILE.read_text(encoding="utf-8")
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


def test_traffic_light_course_uses_yolo_then_opencv_cascade():
    package = ALGORITHMS_FILE.parents[2]
    launch = (package / "launch" / "course_function.launch.py").read_text(encoding="utf-8")
    cmake = (package / "CMakeLists.txt").read_text(encoding="utf-8")
    node = package / "scripts" / "classical" / "traffic_light_dual_node.py"
    assert 'class_ids="9"' in launch
    assert 'confidence=0.30' in launch
    assert 'result_topic="/vision/traffic_light/yolo"' in launch
    assert '"traffic_light_dual_node.py"' in launch
    assert "scripts/classical/traffic_light_dual_node.py" in cmake
    source = node.read_text(encoding="utf-8")
    assert "Stage 1 YOLO" in source
    assert "Stage 2 ROI OpenCV HSV" in source
    assert "detect_traffic_light_colors_in_yolo_rois" in source
    assert '"pipeline": "yolo_roi_then_opencv_hsv"' in source
    assert "latest_yolo_received_at" in source


def test_integrated_traffic_courses_use_coco_and_dual_lights():
    package = ALGORITHMS_FILE.parents[2]
    launch = (package / "launch" / "course_function.launch.py").read_text(encoding="utf-8")
    assert 'class_ids="0,2,3,5,7,9"' in launch
    assert 'class_ids="0,1,2,3,4,5,6,7,8,9"' not in launch
    assert "course_traffic_sign" not in launch
    assert '"/vision/detections/traffic_light"' in launch
    assert '"yolo_topic": "/vision/detections/coco"' in launch
