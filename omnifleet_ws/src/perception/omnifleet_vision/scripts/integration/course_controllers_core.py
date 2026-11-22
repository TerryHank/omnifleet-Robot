"""课程闭环控制器的纯算法，便于在不连接底盘时做安全测试。"""

from __future__ import annotations

import math
from typing import Any


def _clamp(value: float, lower: float, upper: float) -> float:
    """把数值限制到闭区间。"""

    return max(lower, min(upper, value))


def lane_follow_command(
    lane_payload: Any,
    risk_payload: Any,
    enable_motion: bool,
    now: float,
    last_lane_time: float | None,
    timeout: float = 0.6,
    linear_speed: float = 0.4,
    angular_gain: float = 0.6,
    max_angular_speed: float = 0.3,
    event_payload: Any = None,
) -> tuple[float, float, str]:
    """根据线路中心和风险状态生成候选速度；任何缺失或超时都停车。"""

    if not enable_motion:
        return 0.0, 0.0, "motion_disabled"
    if last_lane_time is None or now - last_lane_time > timeout:
        return 0.0, 0.0, "lane_timeout"
    if not isinstance(lane_payload, dict) or not bool(lane_payload.get("detected", False)):
        return 0.0, 0.0, "lane_lost"
    if isinstance(risk_payload, dict):
        level = str(risk_payload.get("risk_level", "unknown"))
        if level in {"unknown", "stop", "danger"}:
            return 0.0, 0.0, f"risk_{level}"
    if isinstance(event_payload, dict):
        event = event_payload.get("primary_event")
        if isinstance(event, dict):
            event_type = str(event.get("event_type", ""))
            if event_type in {"pedestrian", "red_light", "yellow_light", "stop_sign", "emergency"}:
                return 0.0, 0.0, f"event_{event_type}"
    try:
        offset = float(lane_payload.get("offset_normalized"))
    except (TypeError, ValueError):
        return 0.0, 0.0, "invalid_lane_offset"
    if not math.isfinite(offset):
        return 0.0, 0.0, "invalid_lane_offset"
    angular = _clamp(-angular_gain * offset, -max_angular_speed, max_angular_speed)
    return max(0.0, linear_speed), angular, "lane_follow"


def _candidate_targets(payload: Any) -> list[dict[str, Any]]:
    """兼容 detections、tracks 两种课程 JSON 容器。"""

    if not isinstance(payload, dict):
        return []
    for key in ("detections", "tracks"):
        values = payload.get(key)
        if isinstance(values, list):
            return [item for item in values if isinstance(item, dict)]
    return []


def target_follow_command(
    payload: Any,
    enable_motion: bool,
    now: float,
    last_target_time: float | None,
    timeout: float = 0.8,
    image_width: float = 1536.0,
    target_distance: float = 0.8,
    distance_deadband: float = 0.15,
    linear_speed: float = 0.4,
    angular_gain: float = 0.6,
    max_angular_speed: float = 0.3,
    class_filter: str = "",
) -> tuple[float, float, str]:
    """依据目标框中心和深度生成跟随候选，目标丢失或无深度时停车。"""

    if not enable_motion:
        return 0.0, 0.0, "motion_disabled"
    if last_target_time is None or now - last_target_time > timeout:
        return 0.0, 0.0, "target_timeout"
    targets = _candidate_targets(payload)
    wanted = class_filter.strip().lower()
    if wanted:
        targets = [
            item
            for item in targets
            if str(item.get("class", item.get("label", item.get("color", "")))).lower()
            == wanted
        ]
    if not targets:
        return 0.0, 0.0, "target_lost"
    target = max(targets, key=lambda item: float(item.get("confidence", 1.0)))
    bbox = target.get("bbox")
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4 or image_width <= 0.0:
        return 0.0, 0.0, "invalid_bbox"
    try:
        x, _, width, _ = (float(value) for value in bbox)
        distance = float(target.get("depth_m"))
    except (TypeError, ValueError):
        return 0.0, 0.0, "depth_unavailable"
    if not all(math.isfinite(value) for value in (x, width, distance)) or distance <= 0.0:
        return 0.0, 0.0, "depth_unavailable"
    offset = ((x + width * 0.5) - image_width * 0.5) / (image_width * 0.5)
    angular = _clamp(-angular_gain * offset, -max_angular_speed, max_angular_speed)
    distance_error = distance - target_distance
    linear = 0.0
    if abs(distance_error) > distance_deadband:
        linear = math.copysign(max(0.0, linear_speed), distance_error)
    return linear, angular, "target_follow"
