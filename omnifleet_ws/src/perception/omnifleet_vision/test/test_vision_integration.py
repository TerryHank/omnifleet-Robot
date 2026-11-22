"""视觉联调纯算法与安全契约测试。"""

import ast
from pathlib import Path
import struct
import sys

import pytest


PACKAGE = Path(__file__).resolve().parents[1]
INTEGRATION = PACKAGE / "scripts" / "integration"
sys.path.insert(0, str(INTEGRATION))

from vision_integration_core import (
    EventDebouncer,
    IoUTracker,
    TrafficCourseStateMachine,
    bbox_iou,
    depth_at_pixel,
    fuse_detections_with_depth,
    multimodal_risk,
    navigation_candidate,
    point_cloud_min_distance,
    safe_velocity_command,
)


def detection(label: str, bbox: list[float], confidence: float = 0.9) -> dict:
    """构造测试检测结果。"""

    return {"class": label, "bbox": bbox, "confidence": confidence}


def test_bbox_iou_handles_overlap_and_separation():
    """交并比同时覆盖重叠和完全分离。"""

    assert bbox_iou([0, 0, 10, 10], [5, 5, 10, 10]) == pytest.approx(25 / 175)
    assert bbox_iou([0, 0, 2, 2], [3, 3, 2, 2]) == 0.0


def test_iou_tracker_keeps_ids_and_reallocates_after_timeout():
    """相邻帧保持编号，超时后重新分配编号。"""

    tracker = IoUTracker(iou_threshold=0.2, timeout=1.0)
    first = tracker.update([detection("person", [10, 10, 30, 40])], now=0.0)
    second = tracker.update([detection("person", [12, 11, 30, 40])], now=0.2)
    third = tracker.update([detection("person", [12, 11, 30, 40])], now=1.3)
    assert first[0]["track_id"] == second[0]["track_id"] == 1
    assert second[0]["hits"] == 2
    assert third[0]["track_id"] == 2


def test_iou_tracker_supports_multiple_targets_and_class_isolation():
    """多目标贪心匹配不会跨类别串号。"""

    tracker = IoUTracker(iou_threshold=0.1, timeout=1.0)
    first = tracker.update(
        [detection("person", [0, 0, 10, 10]), detection("car", [20, 0, 10, 10])],
        now=0.0,
    )
    second = tracker.update(
        [detection("car", [21, 0, 10, 10]), detection("person", [1, 0, 10, 10])],
        now=0.1,
    )
    assert [item["track_id"] for item in first] == [1, 2]
    assert {item["class"]: item["track_id"] for item in second} == {
        "person": 1,
        "car": 2,
    }


def test_depth_reader_supports_16u_and_32f():
    """两种课程深度编码都换算为米。"""

    depth_16u = struct.pack("<4H", 1000, 2000, 3000, 4000)
    depth_32f = struct.pack("<4f", 1.0, 2.0, 3.0, 4.0)
    assert depth_at_pixel(depth_16u, 2, 2, 4, "16UC1", False, 1, 0) == 2.0
    assert depth_at_pixel(depth_32f, 2, 2, 8, "32FC1", False, 0, 1) == 3.0
    assert depth_at_pixel(depth_16u, 2, 2, 4, "8UC1", False, 0, 0) is None


def test_depth_fusion_node_scales_color_coordinates_to_depth_image():
    """彩色检测框和低分辨率深度图不能直接使用同一像素坐标。"""

    source = (
        Path(__file__).parents[1]
        / "scripts"
        / "integration"
        / "target_depth_fusion_node.py"
    ).read_text(encoding="utf-8")
    assert "x * image.width / self.color_width" in source
    assert "y * image.height / self.color_height" in source
    assert '"color_width", 1536.0' in source
    assert '"color_height", 1280.0' in source


def test_depth_fusion_outputs_approximate_3d_position():
    """检测框中心深度能够生成相机坐标近似值。"""

    payload = {"tracks": [detection("person", [300, 220, 40, 40])]}
    fused = fuse_detections_with_depth(
        payload,
        lambda _x, _y: 2.0,
        fx=500.0,
        fy=500.0,
        cx=320.0,
        cy=240.0,
        sample_grid=3,
    )
    assert len(fused) == 1
    assert fused[0]["depth_m"] == 2.0
    assert fused[0]["position_3d"] == {"x": 0.0, "y": 0.0, "z": 2.0}


def test_traffic_event_debounce_and_priority():
    """行人需要连续出现，并且优先级高于红灯。"""

    debouncer = EventDebouncer(activate_frames=2, release_frames=2)
    frame = [
        detection("red_light", [0, 0, 10, 10]),
        detection("person", [20, 0, 10, 20]),
    ]
    assert debouncer.update(frame) == []
    active = debouncer.update(frame)
    assert [item["event_type"] for item in active] == ["pedestrian", "red_light"]
    assert len(debouncer.update([])) == 2
    assert debouncer.update([]) == []


def test_traffic_light_color_attribute_is_understood():
    """通用信号灯类别可通过颜色属性转为红灯事件。"""

    debouncer = EventDebouncer(activate_frames=1, release_frames=1)
    item = detection("traffic_light", [0, 0, 10, 10])
    item["color"] = "red"
    assert debouncer.update([item])[0]["event_type"] == "red_light"


def test_safe_behavior_controller_is_closed_and_fail_safe_by_default():
    """运动关闭、消息超时和停车事件都必须输出零速。"""

    green = {
        "primary_event": {"event_type": "green_light", "priority": 10}
    }
    red = {"primary_event": {"event_type": "red_light", "priority": 90}}
    disabled = safe_velocity_command(green, False, 1.0, 1.0, 0.5, 0.4, 0.2, 0.6)
    stale = safe_velocity_command(green, True, 2.0, 1.0, 0.5, 0.4, 0.2, 0.6)
    stopped = safe_velocity_command(red, True, 1.1, 1.0, 0.5, 0.4, 0.2, 0.6)
    waiting = safe_velocity_command(green, True, 1.1, 1.0, 0.5, 0.4, 0.2, 0.6)
    green["cruise_allowed"] = True
    moving = safe_velocity_command(green, True, 1.1, 1.0, 0.5, 0.4, 0.2, 0.6)
    assert disabled[:2] == stale[:2] == stopped[:2] == waiting[:2] == (0.0, 0.0)
    assert moving[:2] == (0.4, 0.0)


def test_navigation_candidate_uses_pixel_and_depth_without_action_call():
    """目标像素仅生成候选位姿数据。"""

    center = navigation_candidate({"pixel_x": 320, "depth_m": 2.0}, 500.0, 320.0)
    right = navigation_candidate({"pixel_x": 420, "depth_m": 2.0}, 500.0, 320.0)
    assert center == {"x": 2.0, "y": 0.0, "yaw": 0.0}
    assert right is not None and right["y"] < 0.0 and right["yaw"] < 0.0


def test_point_cloud_distance_and_multimodal_risk_use_nearest_source():
    """点云解析和多模态融合都采用最保守距离。"""

    cloud = b"".join(
        [
            struct.pack("<fff", 2.0, 0.0, 0.0),
            struct.pack("<fff", 0.5, 0.0, 0.0),
            struct.pack("<fff", -0.1, 0.0, 0.0),
        ]
    )
    fields = {"x": (0, 7), "y": (4, 7), "z": (8, 7)}
    nearest = point_cloud_min_distance(
        cloud, 3, 1, 12, 36, fields, False, -1.0, 1.0, True
    )
    assert nearest == pytest.approx(0.5)
    risk = multimodal_risk(1.5, nearest, 0.6, 1.0, 2.0)
    assert risk["risk_level"] == "stop"
    assert risk["nearest_distance_m"] == pytest.approx(0.5)


def test_unknown_multimodal_input_is_fail_safe():
    """两路输入都无效时发布未知高优先级状态。"""

    risk = multimodal_risk(None, None)
    assert risk["risk_level"] == "unknown"
    assert risk["priority"] == 100


def test_course_state_machine_prioritizes_pedestrian_over_red_light():
    """阶段项目状态机固定执行行人高于红灯。"""

    machine = TrafficCourseStateMachine()
    result = machine.update(
        {
            "active_events": [
                {"event_type": "red_light", "priority": 90},
                {"event_type": "pedestrian", "priority": 100},
            ]
        }
    )
    assert result == {"state": "PEDESTRIAN_STOP", "reason": "pedestrian"}
    assert machine.update({"active_events": []})["state"] == "WAIT_FOR_EVENT"


def test_all_nodes_parse_and_keep_output_safety_contract():
    """联调节点均可解析，且控制节点只允许视觉速度候选话题。"""

    expected = {
        "detection_tracker_node.py",
        "detection_aggregator_node.py",
        "lane_follow_controller_node.py",
        "target_follow_controller_node.py",
        "target_depth_fusion_node.py",
        "traffic_event_node.py",
        "safe_behavior_controller_node.py",
        "vision_nav_target_node.py",
        "multimodal_risk_node.py",
        "traffic_course_state_node.py",
    }
    for filename in expected:
        source = (INTEGRATION / filename).read_text(encoding="utf-8")
        ast.parse(source)
        assert "轮趣" not in source
        assert "亚博" not in source
    controller = (INTEGRATION / "safe_behavior_controller_node.py").read_text(
        encoding="utf-8"
    )
    nav_target = (INTEGRATION / "vision_nav_target_node.py").read_text(
        encoding="utf-8"
    )
    assert '"/cmd_vel"' not in controller
    assert '"cmd_vel"' not in controller
    assert '"/cmd_vel_vision"' in controller
    assert "NavigateToPose" not in nav_target
    assert "ActionClient" not in nav_target


def test_detection_aggregator_keeps_detector_topics_separate_before_merge():
    source = (INTEGRATION / "detection_aggregator_node.py").read_text(encoding="utf-8")
    assert "/vision/detections/coco" in source
    assert "/vision/detections/traffic_light" in source
    assert 'item["source"] = source' in source
