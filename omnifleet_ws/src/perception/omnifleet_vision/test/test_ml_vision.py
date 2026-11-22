"""机器学习视觉核心函数测试，不加载大模型、不依赖 ROS 运行时。"""

import ast
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
import yaml


ML_DIR = Path(__file__).resolve().parents[1] / "scripts" / "ml"
sys.path.insert(0, str(ML_DIR))

import face_detection_node as FACE
import inference_status_node as STATUS
import license_plate_node as PLATE
import model_training as TRAINING
import onnx_detector_node as DETECTOR_NODE
import onnx_yolo_core as YOLO
import pose_node as POSE
import tensorrt_tools as TENSORRT


def test_labels_support_file_and_comma_separated_text(tmp_path):
    labels_file = tmp_path / "labels.txt"
    labels_file.write_text("行人\n红灯\n", encoding="utf-8")
    assert YOLO.load_labels(str(labels_file)) == ["行人", "红灯"]
    assert YOLO.load_labels("person, car") == ["person", "car"]


def test_letterbox_and_blob_keep_aspect_ratio():
    image = np.zeros((320, 640, 3), dtype=np.uint8)
    padded, ratio, padding = YOLO.letterbox(image, (640, 640))
    blob, blob_ratio, blob_padding = YOLO.preprocess_image(image, (640, 640))
    assert padded.shape == (640, 640, 3)
    assert ratio == pytest.approx(1.0)
    assert padding == (0.0, 160.0)
    assert blob.shape == (1, 3, 640, 640)
    assert blob_ratio == ratio
    assert blob_padding == padding


@pytest.mark.parametrize(
    ("shape", "expected"),
    [
        ((1, 84, 8400), (8400, 84)),
        ((1, 7, 8400), (8400, 7)),
        ((1, 17, 8400), (8400, 17)),
        ((1, 56, 8400), (8400, 56)),
    ],
)
def test_four_course_onnx_output_shape_contracts(shape, expected):
    # 只验证静态形状合同，不读取课程中的大模型权重。
    output = np.zeros(shape, dtype=np.float32)
    assert YOLO.normalize_output(output).shape == expected


def test_yolo_decode_filters_classes_and_applies_nms():
    output = np.zeros((1, 6, 20), dtype=np.float32)
    # 两个人框高度重叠，NMS 应只保留置信度更高的一个。
    output[:, :, 0] = [100, 100, 80, 80, 0.90, 0.10]
    output[:, :, 1] = [102, 102, 80, 80, 0.80, 0.20]
    # 单独的车辆框用于验证类别过滤。
    output[:, :, 2] = [300, 200, 100, 60, 0.10, 0.95]
    detections = YOLO.decode_yolo_output(
        output,
        (480, 640),
        1.0,
        (0.0, 0.0),
        ["person", "car"],
        confidence_threshold=0.4,
        nms_threshold=0.45,
        allowed_class_ids=[0],
    )
    assert len(detections) == 1
    assert detections[0]["label"] == "person"
    assert detections[0]["bbox"] == [60, 60, 140, 140]


def test_yolo_decode_accepts_end_to_end_six_column_output():
    output = np.asarray([[[10, 20, 110, 120, 0.8, 1]]], dtype=np.float32)
    detections = YOLO.decode_yolo_output(
        output, (200, 200), 1.0, (0.0, 0.0), ["person", "car"]
    )
    assert detections[0]["class_id"] == 1
    assert detections[0]["bbox"] == [10, 20, 110, 120]


def test_detector_result_schema_is_stable():
    detections = [{"class_id": 0, "label": "person", "confidence": 0.9, "bbox": [1, 2, 3, 4]}]
    result = DETECTOR_NODE.make_result("pedestrian", detections, 12.3456, 1.25)
    assert result == {
        "task": "pedestrian",
        "stamp": 1.25,
        "inference_ms": 12.346,
        "count": 1,
        "detections": detections,
    }


def test_pose_decoder_restores_keypoints_and_visibility():
    output = np.zeros((1, 56, 20), dtype=np.float32)
    output[0, :5, 0] = [100, 120, 80, 100, 0.9]
    for keypoint_index in range(17):
        start = 5 + keypoint_index * 3
        output[0, start : start + 3, 0] = [80 + keypoint_index, 90, 0.8]
    poses = POSE.decode_pose_output(
        output, (240, 320), 1.0, (0.0, 0.0), confidence_threshold=0.4
    )
    assert len(poses) == 1
    assert poses[0]["bbox"] == [60, 70, 140, 170]
    assert len(poses[0]["keypoints"]) == 17
    assert poses[0]["keypoints"][0]["visible"] is True


def test_face_detector_handles_blank_image():
    class EmptyClassifier:
        """模拟未检测到人脸的分类器，避免测试依赖外部分类器数据文件。"""

        @staticmethod
        def detectMultiScale(*_args, **_kwargs):
            return []

    classifier = EmptyClassifier()
    detections = FACE.detect_faces(np.zeros((120, 160, 3), dtype=np.uint8), classifier)
    assert detections == []


def test_plate_rectangle_filter_and_injected_ocr(monkeypatch):
    rectangles = [((100.0, 60.0), (120.0, 30.0), 0.0), ((20.0, 20.0), (10.0, 10.0), 0.0)]
    candidates = PLATE.filter_plate_rectangles(rectangles, (150, 240), minimum_area=500.0)
    assert len(candidates) == 1
    monkeypatch.setattr(PLATE, "detect_plate_candidates", lambda *_args, **_kwargs: candidates)
    image = np.zeros((150, 240, 3), dtype=np.uint8)
    _, result = PLATE.recognize_license_plate(
        image, enable_ocr=True, ocr_function=lambda _image: " 粤 B-12345 "
    )
    assert result["status"] == "recognized"
    assert result["ocr_backend"] == "custom"
    assert result["text"] == "粤B12345"


def test_plate_ocr_preprocessing_enlarges_and_binarizes():
    image = np.full((30, 120, 3), 255, dtype=np.uint8)
    prepared = PLATE.prepare_plate_for_ocr(image)
    assert prepared.ndim == 2
    assert prepared.shape[0] > image.shape[0]
    assert set(np.unique(prepared)).issubset({0, 255})


def test_plate_ocr_reports_unavailable_backend(monkeypatch):
    monkeypatch.setattr(PLATE, "detect_plate_candidates", lambda *_args, **_kwargs: [[10, 10, 110, 40]])
    monkeypatch.setattr(PLATE, "_pytesseract_ocr", lambda *_args: ("", "", "Python OCR 不可用"))
    monkeypatch.setattr(PLATE, "_system_tesseract_ocr", lambda *_args: ("", "", "系统 OCR 不可用"))
    _, result = PLATE.recognize_license_plate(np.zeros((80, 160, 3), dtype=np.uint8))
    assert result["status"] == "ocr_unavailable"
    assert result["ocr_available"] is False
    assert "不可用" in result["message"]


def test_training_arguments_have_no_hardcoded_workspace(tmp_path):
    data = tmp_path / "dataset.yaml"
    data.write_text("path: .\n", encoding="utf-8")
    arguments = TRAINING.build_training_arguments(
        str(data), str(tmp_path / "runs"), "traffic", epochs=2, image_size=320, device="cpu"
    )
    assert arguments["data"] == str(data.resolve())
    assert arguments["device"] == "cpu"
    assert arguments["epochs"] == 2
    assert arguments["amp"] is False


def test_training_dataset_path_is_resolved_from_yaml_location(tmp_path):
    """数据集相对路径必须相对 YAML 文件，而不是启动命令工作目录。"""

    dataset = tmp_path / "dataset"
    dataset.mkdir()
    data_yaml = dataset / "data.yaml"
    data_yaml.write_text("path: .\ntrain: train/images\nval: val/images\n", encoding="utf-8")
    output = tmp_path / "resolved"
    output.mkdir()
    resolved = TRAINING.write_resolved_dataset_yaml(data_yaml, output)
    payload = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    assert payload["path"] == str(dataset.resolve())


def test_tensorrt_commands_are_argument_lists_and_metrics_parse(tmp_path):
    executable = tmp_path / "trtexec"
    executable.write_text("", encoding="utf-8")
    model = tmp_path / "model.onnx"
    model.write_bytes(b"contract only")
    command = TENSORRT.build_export_command(
        str(model), str(tmp_path / "model.engine"), str(executable), fp16=True
    )
    assert isinstance(command, list)
    assert "--fp16" in command
    assert any(item.startswith("--onnx=") for item in command)
    assert any(item == "--memPoolSize=workspace:2048" for item in command)
    metrics = TENSORRT.parse_trtexec_metrics(
        "Throughput: 25.5 qps\nLatency: min = 1 ms, max = 8 ms, mean = 4.2 ms, median = 4.0 ms\n"
        "GPU Compute Time: min = 1 ms, max = 5 ms, mean = 3.1 ms"
    )
    assert metrics["throughput_qps"] == pytest.approx(25.5)
    assert metrics["latency_mean_ms"] == pytest.approx(4.2)
    assert metrics["gpu_compute_mean_ms"] == pytest.approx(3.1)


def test_inference_statistics_calculates_latency_and_frequency():
    statistics = STATUS.InferenceStatistics(window_size=4)
    statistics.update(10.0, 1.0)
    statistics.update(20.0, 1.1)
    statistics.update(30.0, 1.2)
    snapshot = statistics.snapshot()
    assert snapshot["sample_count"] == 3
    assert snapshot["frequency_hz"] == pytest.approx(10.0)
    assert snapshot["inference_mean_ms"] == pytest.approx(20.0)
    assert STATUS.extract_inference_ms({"inference_ms": "12.5"}) == pytest.approx(12.5)


def test_ml_scripts_are_valid_chinese_commented_and_never_publish_velocity():
    sources = []
    for path in ML_DIR.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
        sources.append(source)
        assert any("\u4e00" <= character <= "\u9fff" for character in source)
    combined = "\n".join(sources)
    forbidden_topic = "cmd" + "_vel"
    assert forbidden_topic not in combined
    # 分段写出检查词，避免测试文件自身被品牌残留扫描误报。
    for watermark in ("轮" + "趣", "亚" + "博", "WHEEL" + "TEC", "Yah" + "boom"):
        assert watermark not in combined


def test_requested_detector_parameters_exist_in_node_source():
    source = (ML_DIR / "onnx_detector_node.py").read_text(encoding="utf-8")
    for parameter in ("model_path", "labels", "task", "input", "result", "debug"):
        assert f'"{parameter}"' in source


def test_ultralytics_cuda_adapter_uses_course_detection_contract():
    """远端 PyTorch 后端必须输出左上宽高框且不发布速度。"""

    path = ML_DIR / "ultralytics_detector_node.py"
    source = path.read_text(encoding="utf-8")
    ast.parse(source)
    assert '"bbox":' in source
    assert '"backend": "pytorch_cuda"' in source
    assert "torch.cuda.is_available" in source
    assert "/cmd_vel" not in source
