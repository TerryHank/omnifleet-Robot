#!/usr/bin/env python3
"""基于 OpenCV DNN 的 YOLOv8/YOLO11 ONNX 推理核心。"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Sequence

import cv2
import numpy as np


def load_labels(value: str | Sequence[str] | None) -> list[str]:
    """从文本文件、逗号分隔字符串或字符串序列读取类别名称。"""

    if value is None:
        return []
    if not isinstance(value, str):
        return [str(item).strip() for item in value if str(item).strip()]
    text = value.strip()
    if not text:
        return []
    path = Path(text).expanduser()
    if path.is_file():
        return [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    return [item.strip() for item in text.split(",") if item.strip()]


def letterbox(
    image: np.ndarray,
    size: tuple[int, int] = (640, 640),
    color: tuple[int, int, int] = (114, 114, 114),
) -> tuple[np.ndarray, float, tuple[float, float]]:
    """等比例缩放并补边，返回图像、缩放比例和左上补边量。"""

    if image is None or image.size == 0:
        raise ValueError("输入图像不能为空")
    input_width, input_height = int(size[0]), int(size[1])
    if input_width <= 0 or input_height <= 0:
        raise ValueError("输入尺寸必须大于零")
    height, width = image.shape[:2]
    ratio = min(input_width / width, input_height / height)
    resized_width = max(1, int(round(width * ratio)))
    resized_height = max(1, int(round(height * ratio)))
    resized = cv2.resize(image, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)
    pad_width = input_width - resized_width
    pad_height = input_height - resized_height
    left = pad_width // 2
    right = pad_width - left
    top = pad_height // 2
    bottom = pad_height - top
    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return padded, ratio, (float(left), float(top))


def preprocess_image(
    image: np.ndarray,
    size: tuple[int, int] = (640, 640),
) -> tuple[np.ndarray, float, tuple[float, float]]:
    """执行 YOLO 常用的 BGR 到 RGB、归一化和 NCHW 预处理。"""

    padded, ratio, padding = letterbox(image, size)
    blob = cv2.dnn.blobFromImage(
        padded,
        scalefactor=1.0 / 255.0,
        size=size,
        swapRB=True,
        crop=False,
    )
    return blob, ratio, padding


def normalize_output(output: np.ndarray | Sequence[np.ndarray]) -> np.ndarray:
    """把 ONNX 输出统一整理为“候选数量 × 属性数量”的二维矩阵。"""

    if isinstance(output, (list, tuple)):
        arrays = [np.asarray(item) for item in output if np.asarray(item).size]
        if not arrays:
            return np.empty((0, 0), dtype=np.float32)
        output_array = max(arrays, key=lambda item: item.size)
    else:
        output_array = np.asarray(output)
    # 保留三维输出的原始轴信息，便于小规模单元测试和动态候选数模型正确判断方向。
    if output_array.ndim == 3 and output_array.shape[0] == 1:
        matrix = output_array[0]
        if matrix.ndim == 2:
            is_end_to_end_layout = matrix.shape[1] == 6 and matrix.shape[0] != 6
            if not is_end_to_end_layout and matrix.shape[0] <= 256:
                matrix = matrix.T
    else:
        matrix = np.squeeze(output_array)
    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)
    if matrix.ndim != 2:
        raise ValueError(f"不支持的 ONNX 输出形状：{output_array.shape}")
    # YOLOv8/11 常见输出为 [属性, 候选]，需转为 [候选, 属性]。
    if output_array.ndim != 3 and matrix.shape[0] <= 256 and matrix.shape[1] > matrix.shape[0]:
        matrix = matrix.T
    return np.ascontiguousarray(matrix, dtype=np.float32)


def _clip_box(
    box: Sequence[float], original_shape: tuple[int, int]
) -> tuple[int, int, int, int]:
    """把浮点坐标裁剪到原图范围并转换为整数坐标。"""

    height, width = original_shape
    x1 = int(round(max(0.0, min(float(width - 1), float(box[0])))))
    y1 = int(round(max(0.0, min(float(height - 1), float(box[1])))))
    x2 = int(round(max(0.0, min(float(width), float(box[2])))))
    y2 = int(round(max(0.0, min(float(height), float(box[3])))))
    return x1, y1, max(x1 + 1, x2), max(y1 + 1, y2)


def _restore_xyxy(
    xyxy: Sequence[float],
    ratio: float,
    padding: tuple[float, float],
    original_shape: tuple[int, int],
) -> tuple[int, int, int, int]:
    """把补边图坐标还原到原图坐标。"""

    if ratio <= 0.0:
        raise ValueError("缩放比例必须大于零")
    pad_x, pad_y = padding
    restored = (
        (float(xyxy[0]) - pad_x) / ratio,
        (float(xyxy[1]) - pad_y) / ratio,
        (float(xyxy[2]) - pad_x) / ratio,
        (float(xyxy[3]) - pad_y) / ratio,
    )
    return _clip_box(restored, original_shape)


def non_max_suppression(
    boxes: Sequence[Sequence[int]],
    scores: Sequence[float],
    class_ids: Sequence[int],
    score_threshold: float,
    nms_threshold: float,
) -> list[int]:
    """按类别分别做 NMS，避免不同类别之间相互抑制。"""

    selected: list[int] = []
    for class_id in sorted(set(int(item) for item in class_ids)):
        indices = [index for index, item in enumerate(class_ids) if int(item) == class_id]
        xywh = []
        class_scores = []
        for index in indices:
            x1, y1, x2, y2 = boxes[index]
            xywh.append([x1, y1, x2 - x1, y2 - y1])
            class_scores.append(float(scores[index]))
        kept = cv2.dnn.NMSBoxes(xywh, class_scores, score_threshold, nms_threshold)
        if len(kept):
            for local_index in np.asarray(kept).reshape(-1):
                selected.append(indices[int(local_index)])
    return sorted(selected, key=lambda index: float(scores[index]), reverse=True)


def decode_yolo_output(
    output: np.ndarray | Sequence[np.ndarray],
    original_shape: tuple[int, int],
    ratio: float,
    padding: tuple[float, float],
    labels: Sequence[str] | None = None,
    confidence_threshold: float = 0.4,
    nms_threshold: float = 0.45,
    allowed_class_ids: Optional[Iterable[int]] = None,
) -> list[dict]:
    """解码 YOLOv8/11 检测输出，并执行置信度过滤与 NMS。"""

    matrix = normalize_output(output)
    if matrix.size == 0:
        return []
    label_list = list(labels or [])
    allowed = None if allowed_class_ids is None else {int(item) for item in allowed_class_ids}
    boxes: list[tuple[int, int, int, int]] = []
    scores: list[float] = []
    class_ids: list[int] = []

    # 部分端到端导出模型直接给出 [x1, y1, x2, y2, score, class_id]。
    active_rows = matrix[matrix[:, 4] > 0.0] if matrix.shape[1] == 6 else np.empty((0, 6))
    end_to_end = bool(
        active_rows.size
        and np.all(active_rows[:, 2] > active_rows[:, 0])
        and np.all(active_rows[:, 3] > active_rows[:, 1])
        and np.allclose(active_rows[:, 5], np.rint(active_rows[:, 5]), atol=1.0e-4)
    )
    for row in matrix:
        if end_to_end:
            score = float(row[4])
            class_id = int(round(float(row[5])))
            xyxy = row[:4]
        else:
            class_count = len(label_list) if label_list else matrix.shape[1] - 4
            if class_count <= 0 or matrix.shape[1] < 4 + class_count:
                continue
            class_scores = row[4 : 4 + class_count]
            class_id = int(np.argmax(class_scores))
            score = float(class_scores[class_id])
            center_x, center_y, width, height = (float(item) for item in row[:4])
            xyxy = (
                center_x - width / 2.0,
                center_y - height / 2.0,
                center_x + width / 2.0,
                center_y + height / 2.0,
            )
        if score < confidence_threshold or (allowed is not None and class_id not in allowed):
            continue
        boxes.append(_restore_xyxy(xyxy, ratio, padding, original_shape))
        scores.append(score)
        class_ids.append(class_id)

    kept = non_max_suppression(
        boxes, scores, class_ids, confidence_threshold, nms_threshold
    )
    detections = []
    for index in kept:
        class_id = class_ids[index]
        x1, y1, x2, y2 = boxes[index]
        detections.append(
            {
                "class_id": class_id,
                "label": label_list[class_id] if class_id < len(label_list) else str(class_id),
                "confidence": round(float(scores[index]), 6),
                "bbox": [x1, y1, x2, y2],
            }
        )
    return detections


def draw_detections(image: np.ndarray, detections: Sequence[dict]) -> np.ndarray:
    """绘制检测框、类别和置信度，保持原图不被修改。"""

    debug = image.copy()
    for item in detections:
        x1, y1, x2, y2 = (int(value) for value in item["bbox"])
        label = f"{item['label']} {float(item['confidence']):.2f}"
        cv2.rectangle(debug, (x1, y1), (x2, y2), (0, 220, 0), 2)
        cv2.putText(debug, label, (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 0), 2)
    return debug


class OnnxYoloDetector:
    """加载一次 ONNX 网络并重复执行目标检测。"""

    def __init__(
        self,
        model_path: str,
        labels: str | Sequence[str] | None = None,
        input_size: tuple[int, int] = (640, 640),
        confidence_threshold: float = 0.4,
        nms_threshold: float = 0.45,
        allowed_class_ids: Optional[Iterable[int]] = None,
    ) -> None:
        path = Path(model_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"找不到 ONNX 模型：{path}")
        self.labels = load_labels(labels)
        self.input_size = (int(input_size[0]), int(input_size[1]))
        self.confidence_threshold = float(confidence_threshold)
        self.nms_threshold = float(nms_threshold)
        self.allowed_class_ids = None if allowed_class_ids is None else list(allowed_class_ids)
        self.network = cv2.dnn.readNetFromONNX(str(path))
        self.network.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.network.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def detect(self, image: np.ndarray) -> list[dict]:
        """对单帧 BGR 图像执行推理并返回结构化检测结果。"""

        blob, ratio, padding = preprocess_image(image, self.input_size)
        self.network.setInput(blob)
        output_names = self.network.getUnconnectedOutLayersNames()
        output = self.network.forward(output_names) if output_names else self.network.forward()
        return decode_yolo_output(
            output,
            image.shape[:2],
            ratio,
            padding,
            self.labels,
            self.confidence_threshold,
            self.nms_threshold,
            self.allowed_class_ids,
        )
