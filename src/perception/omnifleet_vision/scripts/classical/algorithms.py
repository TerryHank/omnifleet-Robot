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
    return cv2.cvtColor(output, cv2.COLOR_GRAY2BGR), result


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
        cv2.putText(debug, name, (x, max(15, y - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, drawing_colors[name], 2)

    detections.sort(key=lambda item: float(item["area"]), reverse=True)
    return debug, {
        "detected": bool(detections),
        "count": len(detections),
        "detections": detections,
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

    return debug, {
        "detected": bool(detections),
        "count": len(detections),
        "detections": detections,
    }


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
    return debug, result


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
