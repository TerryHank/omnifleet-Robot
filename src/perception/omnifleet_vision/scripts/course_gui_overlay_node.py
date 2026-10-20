#!/usr/bin/env python3
"""把课程链路的 JSON、目标框和导航候选统一叠加到实时图像。"""

from __future__ import annotations

import json
import math
import time
from typing import Any, Iterable, Sequence

import cv2
import numpy as np


TOPIC_TITLES = {
    "/vision/camera/status": "Camera",
    "/vision/depth/result": "Depth ROI",
    "/vision/detections": "Detections",
    "/vision/faces": "Faces",
    "/vision/pose": "Pose",
    "/vision/license_plate": "License plate",
    "/vision/tracks": "Tracking",
    "/vision/targets_3d": "Target depth",
    "/vision/risk": "Risk",
    "/vision/events": "Events",
    "/vision/traffic_state": "Traffic state",
    "/vision/lane/result": "Lane",
    "/vision/lane_follow/status": "Lane control",
    "/vision/safe_behavior/status": "Safe control",
    "/vision/target_follow/status": "Target follow",
    "/vision/inference_status": "Inference",
}


def _number(value: Any, digits: int = 2) -> str | None:
    """把有限数值转成紧凑文本。"""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return f"{number:.{digits}f}"


def _short(value: Any, limit: int = 52) -> str:
    """清理用于单行 GUI 的文本。"""

    text = " ".join(str(value).replace("\r", " ").replace("\n", " ").split())
    return text if len(text) <= limit else text[: max(1, limit - 3)] + "..."


def topic_title(topic: str) -> str:
    """将 ROS 话题转换为短标题。"""

    if topic in TOPIC_TITLES:
        return TOPIC_TITLES[topic]
    parts = [part for part in str(topic).split("/") if part]
    return (parts[-1] if parts else "Result").replace("_", " ").title()


def detections_from_payload(payload: Any) -> list[dict]:
    """读取常见检测、跟踪、三维目标或候选数组。"""

    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("detections", "tracks", "candidates"):
        values = payload.get(key)
        if isinstance(values, list):
            return [item for item in values if isinstance(item, dict)]
    return []


def _bbox_xyxy(item: dict, payload: Any, width: int, height: int) -> tuple[int, int, int, int] | None:
    """把课程中的 xywh 与人脸/车牌 xyxy 框统一为绘图坐标。"""

    bbox = item.get("bbox")
    if not isinstance(bbox, Sequence) or isinstance(bbox, (str, bytes)) or len(bbox) < 4:
        return None
    try:
        a, b, c, d = (float(bbox[index]) for index in range(4))
    except (TypeError, ValueError):
        return None
    task = str(payload.get("task", "")) if isinstance(payload, dict) else ""
    is_xyxy = task == "face_detection" or (
        isinstance(payload, dict) and "candidates" in payload and "detections" not in payload
    )
    x1, y1 = a, b
    x2, y2 = (c, d) if is_xyxy else (a + c, b + d)
    x1 = int(np.clip(round(x1), 0, max(0, width - 1)))
    y1 = int(np.clip(round(y1), 0, max(0, height - 1)))
    x2 = int(np.clip(round(x2), 0, max(0, width - 1)))
    y2 = int(np.clip(round(y2), 0, max(0, height - 1)))
    return (x1, y1, x2, y2) if x2 > x1 and y2 > y1 else None


def detection_label(item: dict) -> str:
    """生成贴在目标框旁的类别、置信度、编号和距离。"""

    label = item.get("label", item.get("class", item.get("color", "target")))
    parts = [_short(label, 28)]
    if "id" in item:
        parts.append(f"ID={item['id']}")
    if "track_id" in item:
        parts.append(f"track={item['track_id']}")
    confidence = _number(item.get("confidence", item.get("score")), 2)
    if confidence is not None:
        parts.append(confidence)
    text = _short(item.get("text", ""), 28)
    if text:
        parts.append(text)
    depth = _number(item.get("depth_m"), 2)
    if depth is None and isinstance(item.get("position_3d"), dict):
        depth = _number(item["position_3d"].get("z"), 2)
    if depth is not None:
        parts.append(f"{depth}m")
    return " | ".join(parts)


def summarize_payload(topic: str, payload: Any) -> str:
    """把每个下游结果压缩成一行可见状态。"""

    title = topic_title(topic)
    if payload is None:
        return f"{title}: waiting"
    if isinstance(payload, dict) and payload.get("_overlay_status"):
        return f"{title}: {payload['_overlay_status']}"
    if not isinstance(payload, dict):
        count = len(payload) if isinstance(payload, list) else 0
        return f"{title}: count={count}"

    parts: list[str] = []
    values = detections_from_payload(payload)
    if values or any(key in payload for key in ("detections", "tracks", "candidates", "count")):
        parts.append(f"count={payload.get('count', len(values))}")

    status = payload.get("status")
    if status not in (None, ""):
        parts.append(f"status={_short(status, 24)}")
    if "fps" in payload and (value := _number(payload.get("fps"), 1)) is not None:
        parts.append(f"fps={value}")
    if "median_m" in payload:
        value = _number(payload.get("median_m"), 3)
        parts.append(f"median={value + 'm' if value else 'invalid'}")
    if "valid_ratio" in payload and (value := _number(100.0 * float(payload["valid_ratio"]), 1)) is not None:
        parts.append(f"valid={value}%")
    if "detected" in payload and "offset_normalized" in payload:
        offset = _number(payload.get("offset_normalized"), 3)
        parts.append("detected" if payload.get("detected") else "lost")
        if offset is not None:
            parts.append(f"offset={offset}")
    if "risk_level" in payload:
        parts.append(f"level={_short(payload.get('risk_level'), 16)}")
        if (value := _number(payload.get("nearest_distance_m"), 2)) is not None:
            parts.append(f"nearest={value}m")
        visual = _number(payload.get("visual_distance_m"), 2)
        cloud = _number(payload.get("point_cloud_distance_m"), 2)
        if visual is not None or cloud is not None:
            parts.append(f"vision={visual or '-'}m lidar={cloud or '-'}m")
    if "primary_event" in payload:
        event = payload.get("primary_event")
        event_name = event.get("event_type") if isinstance(event, dict) else event
        parts.append(f"primary={_short(event_name or 'none', 24)}")
    if "state" in payload:
        parts.append(f"state={_short(payload.get('state'), 24)}")
    if "reason" in payload:
        parts.append(f"reason={_short(payload.get('reason'), 24)}")
    if "linear_x" in payload or "angular_z" in payload:
        linear = _number(payload.get("linear_x"), 2) or "0.00"
        angular = _number(payload.get("angular_z"), 2) or "0.00"
        parts.append(f"cmd=({linear},{angular})")
    if "enable_motion" in payload:
        parts.append(f"motion={'ON' if payload.get('enable_motion') else 'OFF'}")
    if "inference_ms" in payload and (value := _number(payload.get("inference_ms"), 1)) is not None:
        parts.append(f"infer={value}ms")
    if "inference_mean_ms" in payload:
        mean = _number(payload.get("inference_mean_ms"), 1)
        p95 = _number(payload.get("inference_p95_ms"), 1)
        frequency = _number(payload.get("frequency_hz"), 1)
        parts.append(f"mean={mean or '-'}ms p95={p95 or '-'}ms hz={frequency or '-'}")
    if "text" in payload or "ocr_available" in payload:
        text = _short(payload.get("text", ""), 28)
        parts.append(f"text={text or '-'}")
    backend = payload.get("backend")
    if backend:
        parts.append(f"backend={_short(backend, 18)}")
    if not parts:
        parts.append("active")
    return f"{title}: " + " | ".join(parts)


def draw_detection_boxes(image: np.ndarray, payloads: Iterable[tuple[str, Any]]) -> np.ndarray:
    """把下游新增的跟踪编号、深度等信息画回对应目标框。"""

    debug = image.copy()
    height, width = debug.shape[:2]
    colors = ((0, 255, 255), (255, 180, 0), (0, 220, 0), (255, 0, 255))
    for payload_index, (_, payload) in enumerate(payloads):
        if not isinstance(payload, (dict, list)):
            continue
        color = colors[payload_index % len(colors)]
        for item in detections_from_payload(payload):
            box = _bbox_xyxy(item, payload, width, height)
            if box is None:
                continue
            x1, y1, x2, y2 = box
            label = detection_label(item)
            cv2.rectangle(debug, (x1, y1), (x2, y2), color, 2)
            text_y = max(20, y1 - 6)
            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.54, 2
            )
            cv2.rectangle(
                debug, (x1, max(0, text_y - text_height - 5)),
                (min(width - 1, x1 + text_width + 6), text_y + 4), (0, 0, 0), -1,
            )
            cv2.putText(
                debug, label, (x1 + 3, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                0.54, color, 2, cv2.LINE_AA,
            )
    return debug


def select_box_payloads(
    image_topic: str, payloads: Sequence[tuple[str, Any]]
) -> list[tuple[str, Any]]:
    """只选择信息最完整的框，避免检测、跟踪和深度框重复叠画。"""

    if not image_topic:
        return list(payloads)
    available = {
        topic: payload for topic, payload in payloads if detections_from_payload(payload)
    }
    for preferred in ("/vision/targets_3d", "/vision/tracks", "/vision/faces"):
        if preferred in available:
            return [(preferred, available[preferred])]
    if image_topic in {"/vision/lane/debug", "/vision/color/debug"}:
        payload = available.get("/vision/detections")
        return [("/vision/detections", payload)] if payload is not None else []
    return []


def render_course_gui(
    image: np.ndarray,
    title: str,
    payloads: Sequence[tuple[str, Any]],
    pose: dict[str, Any] | None = None,
    image_topic: str = "",
) -> np.ndarray:
    """绘制目标框、课程标题、各链路状态和导航候选。"""

    if image is None or image.size == 0:
        raise ValueError("输入图像不能为空")
    debug = draw_detection_boxes(image, select_box_payloads(image_topic, payloads))
    lines = [summarize_payload(topic, payload) for topic, payload in payloads]
    if pose is not None:
        x = _number(pose.get("x"), 2) or "-"
        y = _number(pose.get("y"), 2) or "-"
        yaw = _number(pose.get("yaw"), 2) or "-"
        lines.append(f"Nav candidate: frame={_short(pose.get('frame_id', '-'), 16)} x={x} y={y} yaw={yaw}")
    lines = lines[:9]

    height, width = debug.shape[:2]
    line_height = 24
    panel_height = min(height, 38 + line_height * len(lines) + 8)
    panel_width = min(width, 760)
    cv2.rectangle(debug, (0, 0), (panel_width - 1, panel_height - 1), (0, 0, 0), -1)
    cv2.putText(
        debug, _short(title, 58), (12, 27), cv2.FONT_HERSHEY_SIMPLEX,
        0.72, (255, 255, 255), 2, cv2.LINE_AA,
    )
    for index, line in enumerate(lines):
        color = (0, 255, 255) if "waiting" in line or "stale" in line else (120, 255, 120)
        cv2.putText(
            debug, _short(line, 112), (12, 54 + index * line_height),
            cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 1, cv2.LINE_AA,
        )
    return debug


def main(args=None) -> None:
    """启动 ROS2 课程 GUI 叠加节点。"""

    import rclpy
    from cv_bridge import CvBridge
    from geometry_msgs.msg import PoseStamped
    from rclpy.executors import ExternalShutdownException
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image
    from std_msgs.msg import String

    class CourseGuiOverlayNode(Node):
        """缓存各结果话题，并在每帧基础调试图上形成最终可见证据。"""

        def __init__(self) -> None:
            super().__init__("course_gui_overlay")
            image_topic = str(self.declare_parameter("image_topic", "/vision/detections/debug").value)
            self.image_topic = image_topic
            self.json_topics = [
                str(item) for item in self.declare_parameter("json_topics", [""]).value
                if str(item)
            ]
            pose_topic = str(self.declare_parameter("pose_topic", "").value)
            output_topic = str(self.declare_parameter("output_topic", "/vision/course_gui/debug").value)
            self.title = str(self.declare_parameter("title", "OmniFleet Vision Course").value)
            self.stale_timeout = float(self.declare_parameter("stale_timeout", 2.0).value)
            self.bridge = CvBridge()
            self.latest: dict[str, tuple[Any, float]] = {}
            self.pose: tuple[dict[str, Any], float] | None = None
            self.publisher = self.create_publisher(Image, output_topic, 10)
            self.image_subscription = self.create_subscription(
                Image, image_topic, self.on_image, qos_profile_sensor_data
            )
            self.json_subscriptions = [
                self.create_subscription(
                    String, topic,
                    lambda message, source=topic: self.on_json(source, message), 10,
                )
                for topic in self.json_topics
            ]
            self.pose_subscription = None
            if pose_topic:
                self.pose_subscription = self.create_subscription(
                    PoseStamped, pose_topic, self.on_pose, 10
                )
            self.get_logger().info(
                f"课程 GUI 叠加：图像={image_topic}，结果={','.join(self.json_topics) or '无'}，输出={output_topic}"
            )

        def on_json(self, topic: str, message: String) -> None:
            try:
                payload = json.loads(message.data)
            except json.JSONDecodeError:
                payload = {"_overlay_status": "invalid JSON"}
            self.latest[topic] = (payload, time.monotonic())

        def on_pose(self, message: PoseStamped) -> None:
            orientation = message.pose.orientation
            yaw = math.atan2(
                2.0 * (orientation.w * orientation.z + orientation.x * orientation.y),
                1.0 - 2.0 * (orientation.y * orientation.y + orientation.z * orientation.z),
            )
            self.pose = ({
                "frame_id": message.header.frame_id,
                "x": message.pose.position.x,
                "y": message.pose.position.y,
                "yaw": yaw,
            }, time.monotonic())

        def on_image(self, message: Image) -> None:
            try:
                image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
                now = time.monotonic()
                payloads = []
                for topic in self.json_topics:
                    cached = self.latest.get(topic)
                    if cached is None:
                        payload = None
                    elif now - cached[1] > self.stale_timeout:
                        payload = {"_overlay_status": "stale"}
                    else:
                        payload = cached[0]
                    payloads.append((topic, payload))
                pose = None
                if self.pose is not None and now - self.pose[1] <= self.stale_timeout:
                    pose = self.pose[0]
                debug = render_course_gui(
                    image, self.title, payloads, pose, self.image_topic
                )
                output = self.bridge.cv2_to_imgmsg(debug, encoding="bgr8")
                output.header = message.header
                self.publisher.publish(output)
            except Exception as error:
                self.get_logger().error(f"课程 GUI 叠加失败：{error}")

    rclpy.init(args=args)
    node = CourseGuiOverlayNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
