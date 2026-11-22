"""不依赖 ROS 的经典视觉算法，便于单元测试和教学复用。"""

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np


def _check_bgr(image: np.ndarray) -> np.ndarray:
    """检查并统一为三通道彩色图像。"""
    if image is None or image.size == 0:
        raise ValueError("图像不能为空")
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.ndim == 3 and image.shape[2] == 3:
        return image
    if image.ndim == 3 and image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    raise ValueError("仅支持灰度、BGR 或 BGRA 图像")


def _find_contours(mask: np.ndarray) -> List[np.ndarray]:
    """兼容不同版本 OpenCV 的轮廓返回值。"""
    result = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return list(result[-2])


@dataclass
class CameraHealthMonitor:
    """根据帧时间和帧差判断相机频率、冻结与健康状态。"""

    minimum_fps: float = 10.0
    freeze_frame_count: int = 5
    freeze_difference: float = 0.5
    window_size: int = 30
    timestamps: Deque[float] = field(default_factory=deque)
    repeated_frames: int = 0
    previous_gray: Optional[np.ndarray] = None

    def update(self, image: np.ndarray, timestamp: float) -> Dict[str, object]:
        """送入一帧并返回当前监测结果。"""
        bgr = _check_bgr(image)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        thumbnail = cv2.resize(gray, (64, 48), interpolation=cv2.INTER_AREA)

        difference = None
        if self.previous_gray is not None:
            difference = float(cv2.absdiff(thumbnail, self.previous_gray).mean())
            if difference <= self.freeze_difference:
                self.repeated_frames += 1
            else:
                self.repeated_frames = 0
        self.previous_gray = thumbnail

        if not self.timestamps or timestamp > self.timestamps[-1]:
            self.timestamps.append(float(timestamp))
        while len(self.timestamps) > max(2, self.window_size):
            self.timestamps.popleft()

        fps = 0.0
        if len(self.timestamps) >= 2:
            duration = self.timestamps[-1] - self.timestamps[0]
            if duration > 0.0:
                fps = (len(self.timestamps) - 1) / duration

        frozen = self.repeated_frames >= max(1, self.freeze_frame_count)
        if frozen:
            status = "frozen"
        elif len(self.timestamps) < 2:
            status = "warming_up"
        elif fps < self.minimum_fps:
            status = "low_frequency"
        else:
            status = "ok"

        return {
            "status": status,
            "fps": round(float(fps), 3),
            "frozen": bool(frozen),
            "repeated_frames": int(self.repeated_frames),
            "frame_difference": None if difference is None else round(difference, 3),
            "width": int(bgr.shape[1]),
            "height": int(bgr.shape[0]),
        }


def process_opencv_image(
    image: np.ndarray,
    operation: str = "canny",
    blur_size: int = 5,
    canny_low: int = 50,
    canny_high: int = 150,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """执行灰度、模糊或边缘处理并返回可发布的彩色调试图。"""
    bgr = _check_bgr(image)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    kernel = max(1, int(blur_size))
    if kernel % 2 == 0:
        kernel += 1
    blurred = cv2.GaussianBlur(gray, (kernel, kernel), 0)
    edges = cv2.Canny(blurred, int(canny_low), int(canny_high))

    selected = operation.lower()
    if selected == "gray":
        output = gray
    elif selected == "blur":
        output = blurred
    elif selected == "canny":
        output = edges
    else:
        raise ValueError("operation 仅支持 gray、blur 或 canny")

    result = {
        "operation": selected,
        "mean_gray": round(float(gray.mean()), 3),
        "edge_pixels": int(np.count_nonzero(edges)),
        "edge_ratio": round(float(np.count_nonzero(edges) / edges.size), 6),
    }
    debug = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)
    label = (
        f"OpenCV {selected.upper()} | mean={result['mean_gray']:.1f} | "
        f"edges={result['edge_pixels']} ({100.0 * result['edge_ratio']:.1f}%)"
    )
    cv2.rectangle(debug, (6, 6), (min(debug.shape[1] - 1, 650), 38), (0, 0, 0), -1)
    cv2.putText(
        debug, label, (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.62,
        (0, 255, 255), 2, cv2.LINE_AA,
    )
    return debug, result


COLOR_RANGES: Dict[str, Sequence[Tuple[Tuple[int, int, int], Tuple[int, int, int]]]] = {
    "red": (((0, 90, 60), (10, 255, 255)), ((170, 90, 60), (179, 255, 255))),
    "yellow": (((18, 80, 80), (38, 255, 255)),),
    "green": (((38, 60, 50), (88, 255, 255)),),
    "blue": (((90, 70, 50), (135, 255, 255)),),
}


def recognize_colors(
    image: np.ndarray, minimum_area: float = 200.0
) -> Tuple[np.ndarray, Dict[str, object]]:
    """识别红、黄、绿、蓝色区域并返回面积最大的目标。"""
    bgr = _check_bgr(image)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    debug = bgr.copy()
    detections: List[Dict[str, object]] = []
    drawing_colors = {
        "red": (0, 0, 255),
        "yellow": (0, 255, 255),
        "green": (0, 255, 0),
        "blue": (255, 0, 0),
    }

    kernel = np.ones((3, 3), np.uint8)
    for name, ranges in COLOR_RANGES.items():
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in ranges:
            mask = cv2.bitwise_or(
                mask,
                cv2.inRange(hsv, np.array(lower, np.uint8), np.array(upper, np.uint8)),
            )
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours = _find_contours(mask)
        if not contours:
            continue
        contour = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(contour))
        if area < float(minimum_area):
            continue
        x, y, width, height = cv2.boundingRect(contour)
        detection = {
            "class": name,
            "confidence": 1.0,
            "color": name,
            "area": round(area, 2),
            "area_ratio": round(area / (bgr.shape[0] * bgr.shape[1]), 6),
            "bbox": [int(x), int(y), int(width), int(height)],
            "center": [int(x + width / 2), int(y + height / 2)],
        }
        detections.append(detection)
        cv2.rectangle(debug, (x, y), (x + width, y + height), drawing_colors[name], 2)
        label = f"{name} | area={area:.0f}"
        cv2.putText(
            debug, label, (x, max(18, y - 5)), cv2.FONT_HERSHEY_SIMPLEX,
            0.55, drawing_colors[name], 2, cv2.LINE_AA,
        )

    detections.sort(key=lambda item: float(item["area"]), reverse=True)
    return debug, {
        "detected": bool(detections),
        "count": len(detections),
        "detections": detections,
    }


TRAFFIC_LIGHT_COLOR_RANGES: Dict[
    str, Sequence[Tuple[Tuple[int, int, int], Tuple[int, int, int]]]
] = {
    "red": (((0, 70, 70), (25, 255, 255)), ((168, 70, 70), (179, 255, 255))),
    "yellow": (((15, 20, 160), (38, 255, 255)),),
    "green": (((40, 70, 60), (100, 255, 255)),),
}


def detect_traffic_light_colors(
    image: np.ndarray,
    minimum_area: float = 25.0,
    maximum_area_ratio: float = 0.03,
    minimum_circularity: float = 0.35,
    minimum_confidence: float = 0.48,
    minimum_mean_value: float = 100.0,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """独立使用 HSV、面积和圆度筛选红黄绿灯色候选。"""

    bgr = _check_bgr(image)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    debug = bgr.copy()
    image_area = float(bgr.shape[0] * bgr.shape[1])
    effective_minimum_area = max(float(minimum_area), image_area * 0.00015)
    drawing_colors = {
        "red": (0, 0, 255),
        "yellow": (0, 255, 255),
        "green": (0, 255, 0),
    }
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    detections: List[Dict[str, object]] = []

    for color, ranges in TRAFFIC_LIGHT_COLOR_RANGES.items():
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in ranges:
            mask = cv2.bitwise_or(
                mask,
                cv2.inRange(hsv, np.array(lower, np.uint8), np.array(upper, np.uint8)),
            )
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        color_detections: List[Dict[str, object]] = []
        for contour in _find_contours(mask):
            area = float(cv2.contourArea(contour))
            area_ratio = area / image_area
            if area < effective_minimum_area or area_ratio > float(maximum_area_ratio):
                continue
            x, y, width, height = cv2.boundingRect(contour)
            if width <= 0 or height <= 0:
                continue
            aspect_ratio = width / float(height)
            fill_ratio = area / float(width * height)
            perimeter = float(cv2.arcLength(contour, True))
            circularity = (
                0.0
                if perimeter <= 0.0
                else float(4.0 * np.pi * area / (perimeter * perimeter))
            )
            if not 0.4 <= aspect_ratio <= 2.5:
                continue
            if fill_ratio < 0.25 or circularity < float(minimum_circularity):
                continue

            contour_mask = np.zeros(mask.shape, dtype=np.uint8)
            cv2.drawContours(contour_mask, [contour], -1, 255, -1)
            _, mean_saturation, mean_value, _ = cv2.mean(hsv, mask=contour_mask)
            if mean_value < float(minimum_mean_value):
                continue
            confidence = min(
                1.0,
                0.45 * (mean_saturation / 255.0)
                + 0.35 * (mean_value / 255.0)
                + 0.20 * min(1.0, circularity),
            )
            if confidence < float(minimum_confidence):
                continue
            color_detections.append(
                {
                    "class": f"{color}_light",
                    "label": color,
                    "color": color,
                    "branch": "opencv_hsv",
                    "confidence": round(float(confidence), 6),
                    "area": round(area, 2),
                    "area_ratio": round(area_ratio, 6),
                    "circularity": round(circularity, 6),
                    "bbox": [int(x), int(y), int(width), int(height)],
                    "center": [int(x + width / 2), int(y + height / 2)],
                }
            )

        color_detections.sort(
            key=lambda item: (float(item["area"]), float(item["confidence"])),
            reverse=True,
        )
        detections.extend(color_detections[:6])

    detections.sort(key=lambda item: float(item["confidence"]), reverse=True)
    for detection in detections:
        x, y, width, height = (int(value) for value in detection["bbox"])
        color = str(detection["color"])
        drawing_color = drawing_colors[color]
        cv2.rectangle(debug, (x, y), (x + width, y + height), drawing_color, 2)
        cv2.putText(
            debug,
            f"OpenCV: {color.upper()} {float(detection['confidence']):.2f}",
            (x, max(20, y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            drawing_color,
            2,
            cv2.LINE_AA,
        )

    counts = {
        color: sum(1 for item in detections if item["color"] == color)
        for color in TRAFFIC_LIGHT_COLOR_RANGES
    }
    return debug, {
        "detected": bool(detections),
        "count": len(detections),
        "counts": counts,
        "detections": detections,
    }


def detect_traffic_light_colors_in_yolo_rois(
    image: np.ndarray,
    yolo_detections: Sequence[Dict[str, object]],
    minimum_area: float = 9.0,
    maximum_area_ratio: float = 0.35,
    minimum_circularity: float = 0.35,
    minimum_confidence: float = 0.60,
    minimum_mean_value: float = 100.0,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """仅在 YOLO 红绿灯框内执行 HSV 判色，并把坐标还原到整幅图。"""

    bgr = _check_bgr(image)
    debug = bgr.copy()
    image_height, image_width = bgr.shape[:2]
    detections: List[Dict[str, object]] = []
    rois: List[Dict[str, object]] = []

    for yolo_index, yolo_detection in enumerate(yolo_detections):
        bbox = yolo_detection.get("bbox")
        if not isinstance(bbox, Sequence) or isinstance(bbox, (str, bytes)) or len(bbox) < 4:
            continue
        try:
            x, y, width, height = (float(bbox[index]) for index in range(4))
        except (TypeError, ValueError):
            continue
        x1 = int(np.clip(np.floor(x), 0, image_width - 1))
        y1 = int(np.clip(np.floor(y), 0, image_height - 1))
        x2 = int(np.clip(np.ceil(x + width), 0, image_width))
        y2 = int(np.clip(np.ceil(y + height), 0, image_height))
        if x2 <= x1 or y2 <= y1:
            continue

        _, roi_result = detect_traffic_light_colors(
            bgr[y1:y2, x1:x2],
            minimum_area=minimum_area,
            maximum_area_ratio=maximum_area_ratio,
            minimum_circularity=minimum_circularity,
            minimum_confidence=minimum_confidence,
            minimum_mean_value=minimum_mean_value,
        )
        best_by_color: Dict[str, Dict[str, object]] = {}
        for item in roi_result["detections"]:
            color = str(item["color"])
            current = best_by_color.get(color)
            if current is None or float(item["area"]) > float(current["area"]):
                best_by_color[color] = item

        translated = []
        for item in best_by_color.values():
            translated_item = dict(item)
            item_x, item_y, item_width, item_height = (
                int(value) for value in item["bbox"]
            )
            center_x, center_y = (int(value) for value in item["center"])
            translated_item.update(
                {
                    "bbox": [x1 + item_x, y1 + item_y, item_width, item_height],
                    "center": [x1 + center_x, y1 + center_y],
                    "branch": "opencv_hsv_in_yolo_roi",
                    "yolo_index": yolo_index,
                    "yolo_confidence": yolo_detection.get("confidence"),
                    "yolo_bbox": [x1, y1, x2 - x1, y2 - y1],
                }
            )
            translated.append(translated_item)
        detections.extend(translated)
        rois.append(
            {
                "yolo_index": yolo_index,
                "bbox": [x1, y1, x2 - x1, y2 - y1],
                "yolo_confidence": yolo_detection.get("confidence"),
                "color_count": len(translated),
            }
        )

    detections.sort(key=lambda item: float(item["confidence"]), reverse=True)
    drawing_colors = {
        "red": (0, 0, 255),
        "yellow": (0, 255, 255),
        "green": (0, 255, 0),
    }
    for detection in detections:
        x, y, width, height = (int(value) for value in detection["bbox"])
        color = str(detection["color"])
        drawing_color = drawing_colors[color]
        cv2.rectangle(debug, (x, y), (x + width, y + height), drawing_color, 2)
        cv2.putText(
            debug,
            f"OpenCV: {color.upper()} {float(detection['confidence']):.2f}",
            (x, max(20, y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            drawing_color,
            2,
            cv2.LINE_AA,
        )
    counts = {
        color: sum(1 for item in detections if item["color"] == color)
        for color in TRAFFIC_LIGHT_COLOR_RANGES
    }
    return debug, {
        "detected": bool(detections),
        "count": len(detections),
        "counts": counts,
        "detections": detections,
        "roi_count": len(rois),
        "rois": rois,
    }


def recognize_qr_codes(image: np.ndarray) -> Tuple[np.ndarray, Dict[str, object]]:
    """使用二维码检测器识别一个或多个二维码。"""
    bgr = _check_bgr(image)
    debug = bgr.copy()
    detector = cv2.QRCodeDetector()
    detections: List[Dict[str, object]] = []

    try:
        found, values, points, _ = detector.detectAndDecodeMulti(bgr)
    except (AttributeError, cv2.error):
        found, values, points = False, (), None

    if found and points is not None:
        for value, polygon in zip(values, points):
            polygon_int = np.round(polygon).astype(np.int32)
            cv2.polylines(debug, [polygon_int], True, (0, 255, 0), 2)
            detections.append({
                "text": str(value),
                "corners": polygon_int.reshape(-1, 2).tolist(),
            })
    else:
        value, polygon, _ = detector.detectAndDecode(bgr)
        if value and polygon is not None:
            polygon_int = np.round(polygon).astype(np.int32).reshape(-1, 2)
            cv2.polylines(debug, [polygon_int], True, (0, 255, 0), 2)
            detections.append({"text": str(value), "corners": polygon_int.tolist()})

    # 部分 Ubuntu OpenCV 没有链接 QUIRC，只能定位二维码而不能解码；此时回退到 zbar。
    if not any(item.get("text") for item in detections):
        try:
            from pyzbar.pyzbar import ZBarSymbol, decode

            decoded = decode(bgr, symbols=[ZBarSymbol.QRCODE])
            fallback = []
            for item in decoded:
                text = item.data.decode("utf-8", errors="replace")
                if item.polygon:
                    corners = [[int(point.x), int(point.y)] for point in item.polygon]
                else:
                    rectangle = item.rect
                    corners = [
                        [rectangle.left, rectangle.top],
                        [rectangle.left + rectangle.width, rectangle.top],
                        [rectangle.left + rectangle.width, rectangle.top + rectangle.height],
                        [rectangle.left, rectangle.top + rectangle.height],
                    ]
                fallback.append({"text": text, "corners": corners, "backend": "pyzbar"})
                cv2.polylines(debug, [np.asarray(corners, dtype=np.int32)], True, (0, 255, 0), 2)
            if fallback:
                detections = fallback
        except (ImportError, OSError):
            pass

    # 无论使用 OpenCV 还是 pyzbar，都把实际解码内容直接叠加到实时调试图。
    for index, item in enumerate(detections):
        corners = np.asarray(item.get("corners", []), dtype=np.int32).reshape(-1, 2)
        if corners.size:
            x = int(np.min(corners[:, 0]))
            y = int(np.min(corners[:, 1]))
        else:
            x, y = 12, 38 + index * 42
        text = str(item.get("text", "")).strip()
        label = f"QR: {text}" if text else "QR detected (not decoded)"
        debug = draw_utf8_label(debug, label, (x, max(32, y - 8)))

    return debug, {
        "detected": bool(detections),
        "count": len(detections),
        "detections": detections,
    }


def draw_utf8_label(
    image: np.ndarray,
    text: str,
    origin: Tuple[int, int],
    color: Tuple[int, int, int] = (0, 255, 0),
) -> np.ndarray:
    """在 BGR 图像上绘制 UTF-8 标签；无 Pillow 时退回 OpenCV ASCII。"""
    debug = _check_bgr(image).copy()
    cleaned = " ".join(str(text).replace("\r", " ").replace("\n", " ").split())[:120]
    x = max(0, int(origin[0]))
    y = max(30, int(origin[1]))
    try:
        from PIL import Image as PillowImage, ImageDraw, ImageFont

        font_paths = (
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        )
        font = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 26)
                break
            except OSError:
                continue
        font = font or ImageFont.load_default()
        rgb = cv2.cvtColor(debug, cv2.COLOR_BGR2RGB)
        canvas = PillowImage.fromarray(rgb)
        drawing = ImageDraw.Draw(canvas)
        bounds = drawing.textbbox((x, y - 28), cleaned, font=font)
        drawing.rectangle(
            (max(0, bounds[0] - 5), max(0, bounds[1] - 3), bounds[2] + 5, bounds[3] + 3),
            fill=(0, 0, 0),
        )
        drawing.text((x, y - 28), cleaned, font=font, fill=(color[2], color[1], color[0]))
        return cv2.cvtColor(np.asarray(canvas), cv2.COLOR_RGB2BGR)
    except (ImportError, OSError, ValueError):
        ascii_text = cleaned.encode("ascii", errors="replace").decode("ascii")
        cv2.putText(
            debug, ascii_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2,
            cv2.LINE_AA,
        )
        return debug


def recognize_apriltags(image: np.ndarray) -> Tuple[np.ndarray, Dict[str, object]]:
    """使用 36h11 字典识别标签并返回编号和角点。"""
    bgr = _check_bgr(image)
    debug = bgr.copy()
    if not hasattr(cv2, "aruco"):
        return debug, {"available": False, "detected": False, "count": 0, "detections": []}

    aruco = cv2.aruco
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_APRILTAG_36h11)
    if hasattr(aruco, "ArucoDetector"):
        detector = aruco.ArucoDetector(dictionary, aruco.DetectorParameters())
        corners, identifiers, _ = detector.detectMarkers(bgr)
    else:
        parameters = aruco.DetectorParameters_create()
        corners, identifiers, _ = aruco.detectMarkers(bgr, dictionary, parameters=parameters)

    detections: List[Dict[str, object]] = []
    if identifiers is not None:
        aruco.drawDetectedMarkers(debug, corners, identifiers)
        for identifier, polygon in zip(identifiers.flatten(), corners):
            points = np.round(polygon.reshape(-1, 2)).astype(np.int32)
            center = points.mean(axis=0).astype(int)
            detections.append({
                "id": int(identifier),
                "corners": points.tolist(),
                "center": center.tolist(),
            })
            x = int(np.min(points[:, 0]))
            y = int(np.min(points[:, 1]))
            debug = draw_utf8_label(
                debug, f"AprilTag ID={int(identifier)}", (x, max(32, y - 8)),
                (0, 255, 0),
            )

    return debug, {
        "available": True,
        "detected": bool(detections),
        "count": len(detections),
        "detections": detections,
    }


def measure_depth(
    depth: np.ndarray,
    encoding: str,
    roi: Optional[Tuple[int, int, int, int]] = None,
    depth_scale_16u: float = 0.001,
    minimum_depth: float = 0.1,
    maximum_depth: float = 3.5,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """在指定区域统计深度中位数、有效率和范围，距离单位为米。"""
    if depth is None or depth.size == 0 or depth.ndim != 2:
        raise ValueError("深度图必须是非空单通道图像")
    normalized_encoding = encoding.upper()
    if normalized_encoding in ("16UC1", "MONO16"):
        depth_m = depth.astype(np.float32) * float(depth_scale_16u)
    elif normalized_encoding == "32FC1":
        depth_m = depth.astype(np.float32)
    else:
        raise ValueError("仅支持 16UC1、MONO16 或 32FC1 深度编码")

    height, width = depth_m.shape
    if roi is None:
        roi_width = max(1, width // 5)
        roi_height = max(1, height // 5)
        x = (width - roi_width) // 2
        y = (height - roi_height) // 2
    else:
        x, y, roi_width, roi_height = (int(value) for value in roi)
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        roi_width = max(1, min(roi_width, width - x))
        roi_height = max(1, min(roi_height, height - y))

    region = depth_m[y : y + roi_height, x : x + roi_width]
    valid = np.isfinite(region) & (region >= minimum_depth) & (region <= maximum_depth)
    values = region[valid]
    valid_ratio = float(values.size / region.size)
    detected = values.size > 0

    clipped = np.nan_to_num(depth_m, nan=0.0, posinf=maximum_depth, neginf=0.0)
    clipped = np.clip(clipped, minimum_depth, maximum_depth)
    normalized = ((clipped - minimum_depth) * (255.0 / max(1e-6, maximum_depth - minimum_depth))).astype(np.uint8)
    debug = cv2.applyColorMap(255 - normalized, cv2.COLORMAP_TURBO)
    cv2.rectangle(debug, (x, y), (x + roi_width, y + roi_height), (255, 255, 255), 2)

    result: Dict[str, object] = {
        "detected": bool(detected),
        "encoding": normalized_encoding,
        "roi": [x, y, roi_width, roi_height],
        "sample_count": int(region.size),
        "valid_count": int(values.size),
        "valid_ratio": round(valid_ratio, 6),
        "median_m": None,
        "minimum_m": None,
        "maximum_m": None,
    }
    if detected:
        result.update({
            "median_m": round(float(np.median(values)), 4),
            "minimum_m": round(float(np.min(values)), 4),
            "maximum_m": round(float(np.max(values)), 4),
        })
    depth_label = (
        f"Depth: {result['median_m']:.3f} m | valid={100.0 * valid_ratio:.1f}%"
        if detected else f"Depth: no valid sample | valid={100.0 * valid_ratio:.1f}%"
    )
    cv2.rectangle(debug, (6, 6), (min(debug.shape[1] - 1, 560), 38), (0, 0, 0), -1)
    cv2.putText(
        debug, depth_label, (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.62,
        (255, 255, 255), 2, cv2.LINE_AA,
    )
    return debug, result


def measure_target_depth(
    depth: np.ndarray,
    encoding: str,
    center: Tuple[int, int],
    sample_radius: int = 7,
    depth_scale_16u: float = 0.001,
    minimum_depth: float = 0.1,
    maximum_depth: float = 3.5,
    minimum_inlier_count: int = 9,
    absolute_outlier_tolerance: float = 0.08,
    mad_scale: float = 3.5,
) -> Dict[str, object]:
    """在目标中心邻域用距离范围和 MAD 中值滤波抑制飞点。"""

    if depth is None or depth.size == 0 or depth.ndim != 2:
        raise ValueError("深度图必须是非空单通道图像")
    if minimum_depth >= maximum_depth:
        raise ValueError("最小深度必须小于最大深度")
    normalized_encoding = encoding.upper()
    if normalized_encoding in ("16UC1", "MONO16"):
        depth_m = depth.astype(np.float32) * float(depth_scale_16u)
    elif normalized_encoding == "32FC1":
        depth_m = depth.astype(np.float32)
    else:
        raise ValueError("仅支持 16UC1、MONO16 或 32FC1 深度编码")

    height, width = depth_m.shape
    center_x = int(np.clip(int(center[0]), 0, width - 1))
    center_y = int(np.clip(int(center[1]), 0, height - 1))
    radius = max(0, int(sample_radius))
    x1 = max(0, center_x - radius)
    y1 = max(0, center_y - radius)
    x2 = min(width, center_x + radius + 1)
    y2 = min(height, center_y + radius + 1)
    region = depth_m[y1:y2, x1:x2]
    valid_mask = (
        np.isfinite(region)
        & (region >= float(minimum_depth))
        & (region <= float(maximum_depth))
    )
    values = region[valid_mask]
    required = max(1, int(minimum_inlier_count))
    result: Dict[str, object] = {
        "detected": False,
        "encoding": normalized_encoding,
        "filter": "range_then_median_mad",
        "center_depth": [center_x, center_y],
        "sample_roi_depth": [x1, y1, x2 - x1, y2 - y1],
        "sample_count": int(region.size),
        "range_valid_count": int(values.size),
        "inlier_count": 0,
        "range_rejected_count": int(region.size - values.size),
        "outlier_rejected_count": 0,
        "valid_ratio": round(float(values.size / max(1, region.size)), 6),
        "raw_median_m": None,
        "mad_m": None,
        "outlier_tolerance_m": None,
        "depth_m": None,
    }
    if values.size < required:
        return result

    raw_median = float(np.median(values))
    deviations = np.abs(values - raw_median)
    mad = float(np.median(deviations))
    tolerance = max(
        float(absolute_outlier_tolerance),
        float(mad_scale) * 1.4826 * mad,
    )
    inliers = values[deviations <= tolerance]
    result.update(
        {
            "raw_median_m": round(raw_median, 4),
            "mad_m": round(mad, 6),
            "outlier_tolerance_m": round(tolerance, 4),
            "inlier_count": int(inliers.size),
            "outlier_rejected_count": int(values.size - inliers.size),
        }
    )
    if inliers.size < required:
        return result
    result.update(
        {
            "detected": True,
            "depth_m": round(float(np.median(inliers)), 4),
        }
    )
    return result


def detect_lane(
    image: np.ndarray,
    roi_start_ratio: float = 0.55,
    white_threshold: int = 180,
    minimum_area: float = 100.0,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """融合灰度白线与 HSV 黄线，在下方感兴趣区域计算车道中心。"""
    bgr = _check_bgr(image)
    height, width = bgr.shape[:2]
    start_y = int(np.clip(roi_start_ratio, 0.0, 0.95) * height)
    roi = bgr[start_y:, :]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    white_mask = cv2.inRange(gray, int(white_threshold), 255)
    yellow_mask = cv2.inRange(hsv, np.array((15, 70, 70), np.uint8), np.array((40, 255, 255), np.uint8))
    mask = cv2.bitwise_or(white_mask, yellow_mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours = [contour for contour in _find_contours(mask) if cv2.contourArea(contour) >= minimum_area]
    lane_center = None
    total_area = 0.0
    if contours:
        moments_x = 0.0
        for contour in contours:
            area = float(cv2.contourArea(contour))
            moments = cv2.moments(contour)
            if moments["m00"] > 0.0:
                moments_x += (moments["m10"] / moments["m00"]) * area
                total_area += area
        if total_area > 0.0:
            lane_center = int(round(moments_x / total_area))

    debug = bgr.copy()
    overlay = np.zeros_like(roi)
    overlay[mask > 0] = (0, 255, 255)
    debug[start_y:, :] = cv2.addWeighted(roi, 0.7, overlay, 0.3, 0.0)
    image_center = width // 2
    cv2.line(debug, (image_center, start_y), (image_center, height - 1), (255, 0, 0), 2)
    if lane_center is not None:
        cv2.line(debug, (lane_center, start_y), (lane_center, height - 1), (0, 255, 0), 2)
        offset_pixels = lane_center - image_center
        offset_normalized = offset_pixels / max(1.0, width / 2.0)
    else:
        offset_pixels = None
        offset_normalized = None

    lane_label = (
        f"Lane: detected | offset={offset_pixels:+d}px ({offset_normalized:+.3f})"
        if lane_center is not None else "Lane: not detected"
    )
    cv2.rectangle(debug, (6, 6), (min(width - 1, 590), 38), (0, 0, 0), -1)
    cv2.putText(
        debug, lane_label, (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.62,
        (0, 255, 0) if lane_center is not None else (0, 0, 255),
        2, cv2.LINE_AA,
    )

    return debug, {
        "detected": lane_center is not None,
        "lane_center_x": lane_center,
        "image_center_x": image_center,
        "offset_pixels": offset_pixels,
        "offset_normalized": None if offset_normalized is None else round(float(offset_normalized), 6),
        "roi_start_y": start_y,
        "contour_count": len(contours),
        "lane_area": round(total_area, 2),
    }
