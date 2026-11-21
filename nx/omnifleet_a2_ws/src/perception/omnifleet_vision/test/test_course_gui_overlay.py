import importlib.util
from pathlib import Path

import cv2
import numpy as np


PACKAGE = Path(__file__).resolve().parents[1]
OVERLAY_PATH = PACKAGE / "scripts" / "course_gui_overlay_node.py"
SPEC = importlib.util.spec_from_file_location("course_gui_overlay_node", OVERLAY_PATH)
OVERLAY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(OVERLAY)


def test_detection_label_contains_class_track_confidence_and_depth():
    label = OVERLAY.detection_label({
        "label": "person", "track_id": 7, "confidence": 0.91, "depth_m": 1.25,
    })
    assert "person" in label
    assert "track=7" in label
    assert "0.91" in label
    assert "1.25m" in label


def test_render_course_gui_draws_boxes_status_and_navigation_candidate():
    image = np.full((480, 640, 3), 48, dtype=np.uint8)
    payloads = [
        ("/vision/tracks", {
            "tracks": [{
                "label": "car", "confidence": 0.88, "track_id": 3,
                "bbox": [220, 190, 160, 100],
            }],
        }),
        ("/vision/targets_3d", {
            "detections": [{
                "label": "car", "confidence": 0.88, "track_id": 3,
                "bbox": [220, 190, 160, 100], "depth_m": 2.4,
            }],
        }),
        ("/vision/risk", {"risk_level": "caution", "nearest_distance_m": 1.4}),
    ]
    debug = OVERLAY.render_course_gui(
        image, "GUI overlay test", payloads,
        {"frame_id": "base_link", "x": 2.4, "y": 0.2, "yaw": 0.08},
    )
    assert debug.shape == image.shape
    assert np.count_nonzero(cv2.absdiff(debug, image)) > 5000
    assert np.count_nonzero(debug[188:294, 218:384] != image[188:294, 218:384]) > 500


def test_only_most_enriched_boxes_are_selected_for_integrated_window():
    detections = ("/vision/detections", {"detections": [{"bbox": [1, 2, 3, 4]}]})
    tracks = ("/vision/tracks", {"tracks": [{"bbox": [1, 2, 3, 4], "track_id": 8}]})
    targets = (
        "/vision/targets_3d",
        {"detections": [{"bbox": [1, 2, 3, 4], "track_id": 8, "depth_m": 1.2}]},
    )
    assert OVERLAY.select_box_payloads("/vision/detections/debug", [detections, tracks]) == [tracks]
    assert OVERLAY.select_box_payloads("/vision/detections/debug", [detections, tracks, targets]) == [targets]
    assert OVERLAY.select_box_payloads("/vision/license_plate/debug", [detections]) == []


def test_summaries_expose_lane_risk_event_control_and_inference_values():
    assert "offset=0.125" in OVERLAY.summarize_payload(
        "/vision/lane/result", {"detected": True, "offset_normalized": 0.125}
    )
    assert "nearest=0.75m" in OVERLAY.summarize_payload(
        "/vision/risk", {"risk_level": "danger", "nearest_distance_m": 0.75}
    )
    assert "primary=red_light" in OVERLAY.summarize_payload(
        "/vision/events", {"primary_event": {"event_type": "red_light"}}
    )
    assert "cmd=(0.00,-0.20)" in OVERLAY.summarize_payload(
        "/vision/safe_behavior/status",
        {"enable_motion": False, "linear_x": 0.0, "angular_z": -0.2, "reason": "motion_disabled"},
    )
    assert "mean=12.3ms" in OVERLAY.summarize_payload(
        "/vision/inference_status",
        {"inference_mean_ms": 12.3, "inference_p95_ms": 15.0, "frequency_hz": 28.5},
    )


def test_all_integrated_gui_entries_use_overlay_before_display():
    launch = (PACKAGE / "launch" / "course_function.launch.py").read_text(encoding="utf-8")
    cmake = (PACKAGE / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "DISPLAY_TOPICS" in launch
    assert "course_gui_overlay_node.py" in launch
    assert '"json_topics": config.get("json", [])' in launch
    assert '"pose_topic": config.get("pose", "")' in launch
    assert 'f"/vision/course_gui/course_{course_function}/debug"' in launch
    assert "course_actions.extend(_display_nodes(course_function))" in launch
    assert "scripts/course_gui_overlay_node.py" in cmake


def test_ros_string_array_default_is_not_inferred_as_byte_array():
    source = OVERLAY_PATH.read_text(encoding="utf-8")
    assert 'declare_parameter("json_topics", [""])' in source
