"""视觉联调节点共享的纯算法。

本文件不依赖 ROS 运行时，便于在没有相机和底盘时对数据契约、状态机与
安全逻辑做单元测试。
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import struct
from typing import Any, Callable, Iterable


STOP_EVENT_TYPES = {
    "pedestrian",
    "red_light",
    "stop_sign",
    "emergency",
    "danger",
}


def clamp(value: float, lower: float, upper: float) -> float:
    """把数值限制在指定闭区间内。"""

    return max(lower, min(upper, value))


def message_stamp(payload: dict[str, Any], fallback: float) -> float:
    """从 JSON 对象读取秒时间戳，缺失或非法时使用接收时间。"""

    try:
        stamp = float(payload.get("stamp", fallback))
    except (TypeError, ValueError):
        return fallback
    return stamp if math.isfinite(stamp) else fallback


def normalize_bbox(raw_bbox: Any) -> list[float] | None:
    """把常见检测框格式统一为 [左, 上, 宽, 高]。"""

    try:
        if isinstance(raw_bbox, dict):
            if all(key in raw_bbox for key in ("x", "y", "width", "height")):
                values = [
                    raw_bbox["x"],
                    raw_bbox["y"],
                    raw_bbox["width"],
                    raw_bbox["height"],
                ]
            elif all(key in raw_bbox for key in ("x1", "y1", "x2", "y2")):
                values = [
                    raw_bbox["x1"],
                    raw_bbox["y1"],
                    float(raw_bbox["x2"]) - float(raw_bbox["x1"]),
                    float(raw_bbox["y2"]) - float(raw_bbox["y1"]),
                ]
            else:
                return None
        elif isinstance(raw_bbox, (list, tuple)) and len(raw_bbox) == 4:
            values = list(raw_bbox)
        else:
            return None
        bbox = [float(item) for item in values]
    except (TypeError, ValueError):
        return None
    if not all(math.isfinite(item) for item in bbox) or bbox[2] <= 0 or bbox[3] <= 0:
        return None
    return bbox


def normalize_detection(raw_detection: Any) -> dict[str, Any] | None:
    """清洗一条检测结果，并保留上游提供的扩展字段。"""

    if not isinstance(raw_detection, dict):
        return None
    label = raw_detection.get(
        "class", raw_detection.get("label", raw_detection.get("class_name", ""))
    )
    label = str(label).strip().lower()
    bbox = normalize_bbox(raw_detection.get("bbox", raw_detection.get("box")))
    try:
        confidence = float(raw_detection.get("confidence", raw_detection.get("score", 1.0)))
    except (TypeError, ValueError):
        return None
    if not label or bbox is None or not math.isfinite(confidence):
        return None
    detection = dict(raw_detection)
    detection["class"] = label
    detection["confidence"] = clamp(confidence, 0.0, 1.0)
    detection["bbox"] = bbox
    detection.pop("box", None)
    return detection


def detections_from_payload(payload: Any) -> list[dict[str, Any]]:
    """从 JSON 根对象或数组中提取有效检测结果。"""

    if isinstance(payload, dict):
        raw_detections = payload.get("detections", payload.get("tracks", []))
    else:
        raw_detections = payload
    if not isinstance(raw_detections, list):
        return []
    normalized = [normalize_detection(item) for item in raw_detections]
    return [item for item in normalized if item is not None]


def bbox_iou(first: Iterable[float], second: Iterable[float]) -> float:
    """计算两个 [左, 上, 宽, 高] 检测框的交并比。"""

    ax, ay, aw, ah = (float(value) for value in first)
    bx, by, bw, bh = (float(value) for value in second)
    left = max(ax, bx)
    top = max(ay, by)
    right = min(ax + aw, bx + bw)
    bottom = min(ay + ah, by + bh)
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    union = aw * ah + bw * bh - intersection
    return intersection / union if union > 0.0 else 0.0


@dataclass
class TrackRecord:
    """单个目标的短时跟踪记录。"""

    track_id: int
    detection: dict[str, Any]
    first_seen: float
    last_seen: float
    hits: int = 1


class IoUTracker:
    """用类别一致和 IoU 贪心匹配维护多目标编号。"""

    def __init__(self, iou_threshold: float = 0.3, timeout: float = 1.0) -> None:
        if not 0.0 <= iou_threshold <= 1.0:
            raise ValueError("交并比阈值必须位于 0 到 1 之间")
        if timeout <= 0.0:
            raise ValueError("跟踪超时时间必须大于零")
        self.iou_threshold = float(iou_threshold)
        self.timeout = float(timeout)
        self._next_id = 1
        self._tracks: dict[int, TrackRecord] = {}

    def _expire(self, now: float) -> None:
        expired = [
            track_id
            for track_id, track in self._tracks.items()
            if now - track.last_seen > self.timeout
        ]
        for track_id in expired:
            del self._tracks[track_id]

    def update(self, detections: Any, now: float) -> list[dict[str, Any]]:
        """输入当前检测结果，返回带稳定编号的当前帧目标。"""

        now = float(now)
        current = detections_from_payload(detections)
        self._expire(now)
        candidates: list[tuple[float, int, int]] = []
        for detection_index, detection in enumerate(current):
            for track_id, track in self._tracks.items():
                if detection["class"] != track.detection["class"]:
                    continue
                score = bbox_iou(detection["bbox"], track.detection["bbox"])
                if score >= self.iou_threshold:
                    candidates.append((score, detection_index, track_id))
        candidates.sort(reverse=True)

        used_detections: set[int] = set()
        used_tracks: set[int] = set()
        assignments: dict[int, int] = {}
        for _, detection_index, track_id in candidates:
            if detection_index in used_detections or track_id in used_tracks:
                continue
            assignments[detection_index] = track_id
            used_detections.add(detection_index)
            used_tracks.add(track_id)

        output: list[dict[str, Any]] = []
        for detection_index, detection in enumerate(current):
            track_id = assignments.get(detection_index)
            if track_id is None:
                track_id = self._next_id
                self._next_id += 1
                record = TrackRecord(track_id, dict(detection), now, now)
                self._tracks[track_id] = record
            else:
                record = self._tracks[track_id]
                record.detection = dict(detection)
                record.last_seen = now
                record.hits += 1
            tracked = dict(record.detection)
            tracked.update(
                {
                    "track_id": record.track_id,
                    "hits": record.hits,
                    "age": max(0.0, now - record.first_seen),
                }
            )
            output.append(tracked)
        return sorted(output, key=lambda item: int(item["track_id"]))


def depth_at_pixel(
    data: bytes,
    width: int,
    height: int,
    step: int,
    encoding: str,
    is_bigendian: bool,
    x: int,
    y: int,
    scale_16u: float = 0.001,
    scale_32f: float = 1.0,
) -> float | None:
    """读取一个深度像素并统一换算为米。"""

    if x < 0 or x >= width or y < 0 or y >= height:
        return None
    normalized_encoding = encoding.upper()
    if normalized_encoding in {"16UC1", "MONO16"}:
        byte_count, code, scale = 2, "H", scale_16u
    elif normalized_encoding == "32FC1":
        byte_count, code, scale = 4, "f", scale_32f
    else:
        return None
    offset = y * step + x * byte_count
    if offset < 0 or offset + byte_count > len(data):
        return None
    endian = ">" if is_bigendian else "<"
    value = float(struct.unpack_from(endian + code, data, offset)[0]) * scale
    if not math.isfinite(value) or value <= 0.0:
        return None
    return value


def median_depth_in_bbox(
    bbox: Iterable[float],
    depth_reader: Callable[[int, int], float | None],
    sample_grid: int = 5,
) -> tuple[float, float, float] | None:
    """在检测框中心区域采样，返回中心像素与中值深度。"""

    x, y, width, height = (float(value) for value in bbox)
    grid = max(1, int(sample_grid))
    center_x = x + width * 0.5
    center_y = y + height * 0.5
    radius_x = width * 0.2
    radius_y = height * 0.2
    values: list[float] = []
    for row in range(grid):
        ratio_y = 0.5 if grid == 1 else row / (grid - 1)
        sample_y = round(center_y - radius_y + 2.0 * radius_y * ratio_y)
        for column in range(grid):
            ratio_x = 0.5 if grid == 1 else column / (grid - 1)
            sample_x = round(center_x - radius_x + 2.0 * radius_x * ratio_x)
            value = depth_reader(sample_x, sample_y)
            if value is not None and math.isfinite(value) and value > 0.0:
                values.append(value)
    if not values:
        return None
    values.sort()
    middle = len(values) // 2
    depth = (
        values[middle]
        if len(values) % 2 == 1
        else (values[middle - 1] + values[middle]) * 0.5
    )
    return center_x, center_y, depth


def fuse_detections_with_depth(
    detections: Any,
    depth_reader: Callable[[int, int], float | None],
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    sample_grid: int = 5,
    min_depth: float = 0.1,
    max_depth: float = 20.0,
) -> list[dict[str, Any]]:
    """为检测框补充相机坐标系近似三维位置。"""

    if fx <= 0.0 or fy <= 0.0:
        raise ValueError("相机焦距必须大于零")
    fused: list[dict[str, Any]] = []
    for detection in detections_from_payload(detections):
        sample = median_depth_in_bbox(detection["bbox"], depth_reader, sample_grid)
        if sample is None:
            continue
        pixel_x, pixel_y, depth = sample
        if depth < min_depth or depth > max_depth:
            continue
        item = dict(detection)
        item.update(
            {
                "pixel_center": [pixel_x, pixel_y],
                "depth_m": depth,
                "position_3d": {
                    "x": (pixel_x - cx) * depth / fx,
                    "y": (pixel_y - cy) * depth / fy,
                    "z": depth,
                },
            }
        )
        fused.append(item)
    return fused


def canonical_event_type(label: str, attributes: dict[str, Any] | None = None) -> str | None:
    """把常见检测类别映射为课程统一事件名称。"""

    normalized = str(label).strip().lower().replace("-", "_").replace(" ", "_")
    attributes = attributes or {}
    state = str(attributes.get("state", attributes.get("color", ""))).strip().lower()
    aliases = {
        "person": "pedestrian",
        "pedestrian": "pedestrian",
        "行人": "pedestrian",
        "red_light": "red_light",
        "traffic_light_red": "red_light",
        "红灯": "red_light",
        "green_light": "green_light",
        "traffic_light_green": "green_light",
        "绿灯": "green_light",
        "yellow_light": "yellow_light",
        "traffic_light_yellow": "yellow_light",
        "黄灯": "yellow_light",
        "stop_sign": "stop_sign",
        "stop": "stop_sign",
        "停车标志": "stop_sign",
        "traffic_sign": "traffic_sign",
        "road_sign": "traffic_sign",
        "school": "traffic_sign",
        "turn": "traffic_sign",
        "slow": "traffic_sign",
        "straight": "traffic_sign",
        "parking": "traffic_sign",
        "crossing_sign": "traffic_sign",
        "construction": "traffic_sign",
        "crossing": "traffic_sign",
        "路标": "traffic_sign",
        "car": "vehicle",
        "vehicle": "vehicle",
        "truck": "vehicle",
        "bus": "vehicle",
        "motorcycle": "vehicle",
        "车辆": "vehicle",
    }
    if normalized in {"traffic_light", "交通灯", "红绿灯"}:
        return {
            "red": "red_light",
            "红": "red_light",
            "green": "green_light",
            "绿": "green_light",
            "yellow": "yellow_light",
            "黄": "yellow_light",
        }.get(state)
    return aliases.get(normalized)


EVENT_PRIORITIES = {
    "pedestrian": 100,
    "red_light": 90,
    "stop_sign": 80,
    "yellow_light": 70,
    "traffic_sign": 50,
    "vehicle": 40,
    "green_light": 10,
}


class EventDebouncer:
    """对连续视觉结果做出现和消失防抖。"""

    def __init__(self, activate_frames: int = 3, release_frames: int = 2) -> None:
        if activate_frames <= 0 or release_frames <= 0:
            raise ValueError("防抖帧数必须大于零")
        self.activate_frames = int(activate_frames)
        self.release_frames = int(release_frames)
        self._present_count: dict[str, int] = {}
        self._missing_count: dict[str, int] = {}
        self._active: set[str] = set()

    def update(self, detections: Any) -> list[dict[str, Any]]:
        """返回当前已经通过防抖的事件，按优先级从高到低排列。"""

        best_by_type: dict[str, dict[str, Any]] = {}
        for detection in detections_from_payload(detections):
            event_type = canonical_event_type(detection["class"], detection)
            if event_type is None:
                continue
            candidate = {
                "event_type": event_type,
                "priority": EVENT_PRIORITIES[event_type],
                "confidence": detection["confidence"],
            }
            if "track_id" in detection:
                candidate["track_id"] = detection["track_id"]
            if "depth_m" in detection:
                candidate["depth_m"] = detection["depth_m"]
            existing = best_by_type.get(event_type)
            if existing is None or candidate["confidence"] > existing["confidence"]:
                best_by_type[event_type] = candidate

        observed = set(best_by_type)
        all_types = set(self._present_count) | set(self._active) | observed
        for event_type in all_types:
            if event_type in observed:
                self._present_count[event_type] = self._present_count.get(event_type, 0) + 1
                self._missing_count[event_type] = 0
                if self._present_count[event_type] >= self.activate_frames:
                    self._active.add(event_type)
            else:
                self._present_count[event_type] = 0
                self._missing_count[event_type] = self._missing_count.get(event_type, 0) + 1
                if self._missing_count[event_type] >= self.release_frames:
                    self._active.discard(event_type)

        active_events: list[dict[str, Any]] = []
        for event_type in self._active:
            event = best_by_type.get(
                event_type,
                {
                    "event_type": event_type,
                    "priority": EVENT_PRIORITIES[event_type],
                    "confidence": 0.0,
                    "held_by_debounce": True,
                },
            )
            active_events.append(event)
        return sorted(
            active_events,
            key=lambda item: (-int(item["priority"]), -float(item["confidence"])),
        )


def primary_event(payload: Any) -> dict[str, Any] | None:
    """从事件消息中选择最高优先级事件。"""

    if not isinstance(payload, dict):
        return None
    direct = payload.get("primary_event")
    if isinstance(direct, dict) and direct.get("event_type"):
        return direct
    events = payload.get("active_events", [])
    if not isinstance(events, list):
        return None
    valid = [item for item in events if isinstance(item, dict) and item.get("event_type")]
    if not valid:
        return None
    return max(valid, key=lambda item: int(item.get("priority", 0)))


def safe_velocity_command(
    event_payload: Any,
    enable_motion: bool,
    now: float,
    last_message_time: float | None,
    timeout: float,
    cruise_speed: float,
    caution_speed: float,
    max_angular_speed: float,
) -> tuple[float, float, str]:
    """根据事件计算安全速度候选，并给出决策原因。"""

    if not enable_motion:
        return 0.0, 0.0, "motion_disabled"
    if last_message_time is None or now - last_message_time > timeout:
        return 0.0, 0.0, "event_timeout"
    event = primary_event(event_payload)
    if event is None:
        return 0.0, 0.0, "no_event"
    event_type = str(event.get("event_type", ""))
    if event_type in STOP_EVENT_TYPES or event_type == "yellow_light":
        return 0.0, 0.0, event_type
    try:
        offset = float(event.get("target_offset", 0.0))
    except (TypeError, ValueError):
        offset = 0.0
    angular = clamp(-offset * max_angular_speed, -max_angular_speed, max_angular_speed)
    if event_type in {"vehicle", "traffic_sign"}:
        return max(0.0, caution_speed), angular, event_type
    if event_type == "green_light":
        # 绿灯只解除红灯约束，不能单独证明车道和前方区域安全。
        if isinstance(event_payload, dict) and bool(event_payload.get("cruise_allowed", False)):
            return max(0.0, cruise_speed), angular, "green_light_cruise_allowed"
        return 0.0, 0.0, "green_light_wait_for_lane"
    return 0.0, 0.0, "unsupported_event"


def navigation_candidate(
    target: dict[str, Any],
    fx: float,
    cx: float,
    min_depth: float = 0.2,
    max_depth: float = 10.0,
) -> dict[str, float] | None:
    """把目标像素和深度近似换算为底盘平面候选位姿。"""

    try:
        pixel_x = float(target.get("pixel_x", target.get("u")))
        depth = float(target.get("depth_m", target.get("depth")))
    except (TypeError, ValueError):
        return None
    if fx <= 0.0 or not all(math.isfinite(value) for value in (pixel_x, depth)):
        return None
    if depth < min_depth or depth > max_depth:
        return None
    lateral = -(pixel_x - cx) * depth / fx
    yaw = math.atan2(lateral, depth)
    return {"x": depth, "y": lateral, "yaw": yaw}


def point_cloud_min_distance(
    data: bytes,
    width: int,
    height: int,
    point_step: int,
    row_step: int,
    fields: dict[str, tuple[int, int]],
    is_bigendian: bool,
    min_height: float = -1.0,
    max_height: float = 1.5,
    forward_only: bool = True,
) -> float | None:
    """从点云字节流中提取最近有效点距离。"""

    if point_step <= 0 or row_step <= 0:
        return None
    endian = ">" if is_bigendian else "<"
    format_by_datatype = {7: "f", 8: "d"}
    descriptors: dict[str, tuple[int, str]] = {}
    for axis in ("x", "y", "z"):
        descriptor = fields.get(axis)
        if descriptor is None or descriptor[1] not in format_by_datatype:
            return None
        descriptors[axis] = (descriptor[0], format_by_datatype[descriptor[1]])
    nearest: float | None = None
    for row in range(height):
        row_base = row * row_step
        for column in range(width):
            point_base = row_base + column * point_step
            coordinates: dict[str, float] = {}
            valid = True
            for axis, (offset, code) in descriptors.items():
                byte_count = 4 if code == "f" else 8
                absolute = point_base + offset
                if absolute < 0 or absolute + byte_count > len(data):
                    valid = False
                    break
                coordinates[axis] = float(struct.unpack_from(endian + code, data, absolute)[0])
            if not valid or not all(math.isfinite(value) for value in coordinates.values()):
                continue
            if forward_only and coordinates["x"] <= 0.0:
                continue
            if coordinates["z"] < min_height or coordinates["z"] > max_height:
                continue
            distance = math.hypot(coordinates["x"], coordinates["y"])
            if distance <= 0.0:
                continue
            nearest = distance if nearest is None else min(nearest, distance)
    return nearest


def minimum_visual_distance(payload: Any) -> float | None:
    """提取视觉检测结果中的最近有效深度。"""

    values: list[float] = []
    for detection in detections_from_payload(payload):
        try:
            value = float(detection.get("depth_m"))
        except (TypeError, ValueError):
            continue
        if math.isfinite(value) and value > 0.0:
            values.append(value)
    return min(values) if values else None


def multimodal_risk(
    visual_distance: float | None,
    point_cloud_distance: float | None,
    stop_distance: float = 0.6,
    danger_distance: float = 1.0,
    caution_distance: float = 2.0,
) -> dict[str, Any]:
    """融合视觉和点云最近距离，输出统一风险等级。"""

    if not 0.0 < stop_distance < danger_distance < caution_distance:
        raise ValueError("风险距离阈值必须严格递增")
    valid = [
        float(value)
        for value in (visual_distance, point_cloud_distance)
        if value is not None and math.isfinite(float(value)) and float(value) > 0.0
    ]
    nearest = min(valid) if valid else None
    if nearest is None:
        level, priority = "unknown", 100
    elif nearest <= stop_distance:
        level, priority = "stop", 100
    elif nearest <= danger_distance:
        level, priority = "danger", 90
    elif nearest <= caution_distance:
        level, priority = "caution", 50
    else:
        level, priority = "clear", 0
    return {
        "risk_level": level,
        "priority": priority,
        "nearest_distance_m": nearest,
        "visual_distance_m": visual_distance,
        "point_cloud_distance_m": point_cloud_distance,
    }


class TrafficCourseStateMachine:
    """阶段项目状态机，固定执行行人优先于红灯的规则。"""

    def __init__(self) -> None:
        self.state = "WAIT_FOR_EVENT"

    def update(self, event_payload: Any) -> dict[str, Any]:
        """根据活动事件更新课程状态并返回状态与原因。"""

        events = []
        if isinstance(event_payload, dict):
            raw_events = event_payload.get("active_events", [])
            if isinstance(raw_events, list):
                events = [item for item in raw_events if isinstance(item, dict)]
        event_types = {str(item.get("event_type", "")) for item in events}
        if "pedestrian" in event_types:
            self.state, reason = "PEDESTRIAN_STOP", "pedestrian"
        elif "red_light" in event_types:
            self.state, reason = "RED_LIGHT_STOP", "red_light"
        elif "stop_sign" in event_types:
            self.state, reason = "SIGN_STOP", "stop_sign"
        elif "yellow_light" in event_types:
            self.state, reason = "CAUTION", "yellow_light"
        elif "green_light" in event_types:
            self.state, reason = "GO", "green_light"
        elif self.state in {"PEDESTRIAN_STOP", "RED_LIGHT_STOP", "SIGN_STOP", "CAUTION"}:
            self.state, reason = "WAIT_FOR_EVENT", "event_released"
        else:
            self.state, reason = "WAIT_FOR_EVENT", "no_actionable_event"
        return {"state": self.state, "reason": reason}
