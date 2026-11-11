#!/usr/bin/env python3
"""车牌矩形候选检测与可选 OCR 的 ROS2 节点。"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Sequence

import cv2
import numpy as np


def draw_plate_label(
    image: np.ndarray, text: str, origin: tuple[int, int], color=(0, 220, 220)
) -> np.ndarray:
    """绘制支持中文车牌字符的标签，无 Pillow 时退回 OpenCV。"""

    debug = image.copy()
    cleaned = " ".join(str(text).replace("\r", " ").replace("\n", " ").split())[:80]
    x, y = max(0, int(origin[0])), max(28, int(origin[1]))
    try:
        from PIL import Image as PillowImage, ImageDraw, ImageFont

        font_paths = (
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        )
        font = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 24)
                break
            except OSError:
                continue
        font = font or ImageFont.load_default()
        canvas = PillowImage.fromarray(cv2.cvtColor(debug, cv2.COLOR_BGR2RGB))
        drawing = ImageDraw.Draw(canvas)
        bounds = drawing.textbbox((x, y - 26), cleaned, font=font)
        drawing.rectangle(
            (max(0, bounds[0] - 4), max(0, bounds[1] - 3), bounds[2] + 4, bounds[3] + 3),
            fill=(0, 0, 0),
        )
        drawing.text((x, y - 26), cleaned, font=font, fill=(color[2], color[1], color[0]))
        return cv2.cvtColor(np.asarray(canvas), cv2.COLOR_RGB2BGR)
    except (ImportError, OSError, ValueError):
        ascii_text = cleaned.encode("ascii", errors="replace").decode("ascii")
        cv2.putText(
            debug, ascii_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
            0.6, color, 2, cv2.LINE_AA,
        )
        return debug


def filter_plate_rectangles(
    rectangles: Sequence[tuple],
    image_shape: tuple[int, int],
    minimum_area: float = 800.0,
    aspect_range: tuple[float, float] = (2.0, 6.5),
) -> list[list[int]]:
    """按面积、宽高比和图像边界过滤旋转矩形候选。"""

    height, width = image_shape
    candidates = []
    for rectangle in rectangles:
        (_, _), (box_width, box_height), _ = rectangle
        long_side = max(float(box_width), float(box_height))
        short_side = min(float(box_width), float(box_height))
        if short_side <= 0.0:
            continue
        area = long_side * short_side
        aspect = long_side / short_side
        if area < minimum_area or not aspect_range[0] <= aspect <= aspect_range[1]:
            continue
        points = cv2.boxPoints(rectangle)
        x, y, candidate_width, candidate_height = cv2.boundingRect(points.astype(np.float32))
        x1 = max(0, int(x))
        y1 = max(0, int(y))
        x2 = min(width, int(x + candidate_width))
        y2 = min(height, int(y + candidate_height))
        if x2 > x1 and y2 > y1:
            candidates.append([x1, y1, x2, y2])
    candidates.sort(key=lambda item: (item[2] - item[0]) * (item[3] - item[1]), reverse=True)
    return candidates


def detect_plate_candidates(
    image: np.ndarray,
    minimum_area: float = 800.0,
    aspect_range: tuple[float, float] = (2.0, 6.5),
) -> list[list[int]]:
    """利用水平梯度和闭运算定位可能的车牌矩形区域。"""

    if image is None or image.size == 0:
        raise ValueError("输入图像不能为空")
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    blue_mask = cv2.inRange(hsv, np.array((90, 60, 40), np.uint8), np.array((140, 255, 255), np.uint8))
    blue_mask = cv2.morphologyEx(
        blue_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 5)), iterations=2
    )
    blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gradient = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gradient = cv2.convertScaleAbs(gradient)
    _, binary = cv2.threshold(gradient, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 5))
    connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rectangles = [cv2.minAreaRect(contour) for contour in blue_contours]
    rectangles.extend(cv2.minAreaRect(contour) for contour in contours)
    return filter_plate_rectangles(rectangles, image.shape[:2], minimum_area, aspect_range)


def clean_plate_text(text: str) -> str:
    """清除 OCR 中的空格、标点，只保留字母、数字和汉字。"""

    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]", "", text).upper()


def prepare_plate_for_ocr(image: np.ndarray) -> np.ndarray:
    """放大并二值化车牌区域，提高小字号课程假牌的识别稳定性。"""

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    scale = max(2.0, 120.0 / max(1, gray.shape[0]))
    enlarged = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(enlarged, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if float(binary.mean()) < 127.0:
        binary = 255 - binary
    return cv2.copyMakeBorder(binary, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)


def _pytesseract_ocr(image: np.ndarray, language: str) -> tuple[str, str, str]:
    """尝试使用 Python OCR 接口，失败时返回错误原因。"""

    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        prepared = prepare_plate_for_ocr(image)
        text = pytesseract.image_to_string(
            prepared,
            lang=language,
            config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        )
        return clean_plate_text(text), "pytesseract", ""
    except Exception as error:
        return "", "", str(error)


def _system_tesseract_ocr(image: np.ndarray, language: str) -> tuple[str, str, str]:
    """通过参数列表调用系统 tesseract，禁止 shell 字符串拼接。"""

    executable = shutil.which("tesseract")
    if not executable:
        return "", "", "系统中找不到 tesseract 可执行程序"
    with tempfile.TemporaryDirectory(prefix="omnifleet_plate_") as directory:
        image_path = Path(directory) / "plate.png"
        if not cv2.imwrite(str(image_path), prepare_plate_for_ocr(image)):
            return "", "", "临时车牌图像写入失败"
        try:
            completed = subprocess.run(
                [
                    executable, str(image_path), "stdout", "-l", language, "--psm", "7",
                    "-c", "tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            return "", "", str(error)
    if completed.returncode != 0:
        return "", "", completed.stderr.strip() or f"返回码 {completed.returncode}"
    return clean_plate_text(completed.stdout), "tesseract", ""


def run_plate_ocr(
    image: np.ndarray,
    language: str = "eng",
    ocr_function: Callable[[np.ndarray], str] | None = None,
) -> tuple[str, str, str]:
    """按注入函数、Python 接口、系统程序的顺序执行 OCR。"""

    if ocr_function is not None:
        try:
            return clean_plate_text(ocr_function(image)), "custom", ""
        except Exception as error:
            return "", "", str(error)
    text, backend, error_python = _pytesseract_ocr(image, language)
    if backend:
        return text, backend, ""
    text, backend, error_system = _system_tesseract_ocr(image, language)
    if backend:
        return text, backend, ""
    errors = "; ".join(item for item in (error_python, error_system) if item)
    return "", "", errors or "没有可用的 OCR 后端"


def annotate_plate_candidates(
    image: np.ndarray, candidates: Sequence[Sequence[int]], result: dict
) -> np.ndarray:
    """把每个车牌候选和首个候选的 OCR 内容直接画到调试图。"""

    debug = image.copy()
    for index, (x1, y1, x2, y2) in enumerate(candidates):
        cv2.rectangle(debug, (x1, y1), (x2, y2), (0, 220, 220), 2)
        if index == 0:
            text = str(result.get("text", "")).strip()
            status = str(result.get("status", "plate_detected"))
            if text:
                label = f"Plate: {text}"
            elif status == "ocr_unavailable":
                label = "Plate: OCR unavailable"
            elif status == "ocr_disabled":
                label = "Plate: OCR disabled"
            elif status == "plate_found_text_empty":
                label = "Plate: text empty"
            else:
                label = "Plate candidate"
        else:
            label = f"Plate candidate {index + 1}"
        debug = draw_plate_label(debug, label, (x1, max(28, y1 - 7)))
    return debug


def recognize_license_plate(
    image: np.ndarray,
    enable_ocr: bool = True,
    language: str = "eng",
    minimum_area: float = 800.0,
    ocr_function: Callable[[np.ndarray], str] | None = None,
) -> tuple[np.ndarray, dict]:
    """检测车牌候选，按配置执行 OCR，并明确返回能力状态。"""

    candidates = detect_plate_candidates(image, minimum_area)
    result = {
        "detected": bool(candidates),
        "count": len(candidates),
        "candidates": [{"bbox": item} for item in candidates],
        "ocr_requested": bool(enable_ocr),
        "ocr_available": False,
        "ocr_backend": None,
        "text": "",
        "status": "no_plate_candidate" if not candidates else "plate_detected",
    }
    if not candidates or not enable_ocr:
        if candidates and not enable_ocr:
            result["status"] = "ocr_disabled"
        return annotate_plate_candidates(image, candidates, result), result
    x1, y1, x2, y2 = candidates[0]
    # 梯度候选通常只包住字符笔画，OCR 前向四周扩展到完整牌面。
    horizontal_padding = x2 - x1
    vertical_padding = 2 * (y2 - y1)
    ocr_x1 = max(0, x1 - horizontal_padding)
    ocr_y1 = max(0, y1 - vertical_padding)
    ocr_x2 = min(image.shape[1], x2 + horizontal_padding)
    ocr_y2 = min(image.shape[0], y2 + vertical_padding)
    crop = image[ocr_y1:ocr_y2, ocr_x1:ocr_x2]
    result["ocr_bbox"] = [ocr_x1, ocr_y1, ocr_x2, ocr_y2]
    text, backend, error = run_plate_ocr(crop, language, ocr_function)
    result["ocr_available"] = bool(backend)
    result["ocr_backend"] = backend or None
    result["text"] = text
    if not backend:
        result["status"] = "ocr_unavailable"
        result["message"] = error
    elif text:
        result["status"] = "recognized"
    else:
        result["status"] = "plate_found_text_empty"
    return annotate_plate_candidates(image, candidates, result), result


def main(args=None) -> None:
    """启动车牌检测与识别节点。"""

    import rclpy
    from cv_bridge import CvBridge
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image
    from std_msgs.msg import String

    class LicensePlateNode(Node):
        """发布车牌候选、OCR 状态和调试图。"""

        def __init__(self) -> None:
            super().__init__("license_plate")
            input_topic = str(self.declare_parameter("input", "/camera/color/image_raw").value)
            result_topic = str(self.declare_parameter("result", "/vision/license_plate").value)
            debug_topic = str(self.declare_parameter("debug", "/vision/license_plate/debug").value)
            self.enable_ocr = bool(self.declare_parameter("enable_ocr", True).value)
            self.language = str(self.declare_parameter("ocr_language", "eng").value)
            self.minimum_area = float(self.declare_parameter("minimum_area", 800.0).value)
            self.bridge = CvBridge()
            self.result_publisher = self.create_publisher(String, result_topic, 10)
            self.debug_publisher = self.create_publisher(Image, debug_topic, 10)
            self.subscription = self.create_subscription(
                Image, input_topic, self.on_image, qos_profile_sensor_data
            )

        def on_image(self, message: Image) -> None:
            """处理一帧图像并发布车牌识别状态。"""

            try:
                image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
                debug, result = recognize_license_plate(
                    image, self.enable_ocr, self.language, self.minimum_area
                )
                result["stamp"] = message.header.stamp.sec + message.header.stamp.nanosec / 1.0e9
                output = String()
                output.data = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
                self.result_publisher.publish(output)
                debug_message = self.bridge.cv2_to_imgmsg(debug, encoding="bgr8")
                debug_message.header = message.header
                self.debug_publisher.publish(debug_message)
            except Exception as error:
                self.get_logger().error(f"车牌识别失败：{error}")

    rclpy.init(args=args)
    node = LicensePlateNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
