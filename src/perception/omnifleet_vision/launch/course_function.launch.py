"""视觉课程 31 个功能共用的内部 Launch。

学生只启动 ``omnifleet_tutorials`` 中对应的 ``vision_*.launch.py``。
本文件负责按课程编号组合现有节点；所有运动候选默认关闭，并且只允许发布到
``/cmd_vel_vision``，最终底盘速度必须继续经过安全仲裁链。
"""

import os
from pathlib import Path

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    ExecuteProcess,
    IncludeLaunchDescription,
    LogInfo,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


COLOR_TOPIC = os.environ.get("OMNIFLEET_CAMERA_COLOR_TOPIC", "/camera/color/image_raw")
ALIGNED_COLOR_TOPIC = COLOR_TOPIC
# Orbbec keeps the image topic name unchanged when depth_registration is on;
# the frame_id switches to the color optical frame.
DEPTH_TOPIC = os.environ.get("OMNIFLEET_CAMERA_DEPTH_TOPIC", "/camera/depth/image_raw")
LIDAR_TOPIC = os.environ.get("OMNIFLEET_LIDAR_POINTS_TOPIC", "/rslidar_points")
VISION_COMMAND_TOPIC = "/cmd_vel_vision"
VISION_VENV = "/home/iecme/omnifleet_ws/.env/vision"

# 经典视觉节点和 KCF 已自行画框/显示；其余 22 个实时链路把下游结果叠加到最终窗口。
DISPLAY_TOPICS = {
    "02_08_human_perception": {
        "image": "/vision/pose/debug", "title": "OmniFleet Human Perception",
        "json": ["/vision/faces", "/vision/pose"],
    },
    "02_09_yolo": {
        "image": "/vision/detections/debug", "title": "OmniFleet YOLO Detection",
        "json": ["/vision/detections"],
    },
    "02_13_pedestrian": {
        "image": "/vision/detections/debug", "title": "OmniFleet Pedestrian Detection",
        "json": ["/vision/detections"],
    },
    "02_14_traffic_light": {
        "image": "/vision/detections/debug", "title": "OmniFleet Traffic Light",
        "json": ["/vision/detections"],
    },
    "02_16_vehicle": {
        "image": "/vision/detections/debug", "title": "OmniFleet Vehicle Detection",
        "json": ["/vision/detections"],
    },
    "02_17_license_plate": {
        "image": "/vision/license_plate/debug", "title": "OmniFleet License Plate",
        "json": ["/vision/license_plate"],
    },
    "03_01_camera_topics": {
        "image": "/vision/camera/debug", "title": "OmniFleet Camera Topics",
        "json": ["/vision/camera/status", "/vision/depth/result"],
    },
    "03_02_detection_tracking": {
        "image": "/vision/detections/debug", "title": "OmniFleet Detection Tracking",
        "json": ["/vision/detections", "/vision/tracks"],
    },
    "03_03_target_depth": {
        "image": "/vision/detections/debug", "title": "OmniFleet Target Depth",
        "json": ["/vision/tracks", "/vision/targets_3d"],
    },
    "03_04_vision_lidar": {
        "image": "/vision/detections/debug", "title": "OmniFleet Vision Lidar",
        "json": ["/vision/targets_3d", "/vision/risk"],
    },
    "03_05_traffic_events": {
        "image": "/vision/detections/traffic_light/debug", "title": "OmniFleet Traffic Events",
        "json": ["/vision/detections", "/vision/targets_3d", "/vision/events", "/vision/traffic_state"],
    },
    "03_06_chassis_control": {
        "image": "/vision/detections/debug", "title": "OmniFleet Chassis Control",
        "json": ["/vision/targets_3d", "/vision/events", "/vision/safe_behavior/status"],
    },
    "03_07_lane_integration": {
        "image": "/vision/lane/debug", "title": "OmniFleet Lane Integration",
        "json": ["/vision/lane/result", "/vision/targets_3d", "/vision/risk", "/vision/lane_follow/status"],
    },
    "03_08_vision_nav": {
        "image": "/vision/detections/debug", "title": "OmniFleet Vision Navigation",
        "json": ["/vision/targets_3d"], "pose": "/vision/nav_goal",
    },
    "03_09_edge_deployment": {
        "image": "/vision/detections/debug", "title": "OmniFleet Edge Deployment",
        "json": ["/vision/detections", "/vision/inference_status"],
    },
    "04_01_color_follow": {
        "image": "/vision/color/debug", "title": "OmniFleet Color Follow",
        "json": ["/vision/detections", "/vision/targets_3d", "/vision/target_follow/status"],
    },
    "04_02_human_object_follow": {
        "image": "/vision/detections/debug", "title": "OmniFleet Human Follow",
        "json": ["/vision/targets_3d", "/vision/target_follow/status"],
    },
    "04_03_lane_project": {
        "image": "/vision/lane/debug", "title": "OmniFleet Lane Project",
        "json": ["/vision/lane/result", "/vision/targets_3d", "/vision/risk", "/vision/lane_follow/status"],
    },
    "04_04_object_navigation": {
        "image": "/vision/detections/debug", "title": "OmniFleet Object Navigation",
        "json": ["/vision/targets_3d"], "pose": "/vision/nav_goal",
    },
    "04_05_multimodal_avoidance": {
        "image": "/vision/lane/debug", "title": "OmniFleet Multimodal Avoidance",
        "json": ["/vision/lane/result", "/vision/targets_3d", "/vision/risk", "/vision/lane_follow/status"],
    },
    "04_06_edge_detection": {
        "image": "/vision/detections/debug", "title": "OmniFleet Edge Detection",
        "json": ["/vision/detections", "/vision/inference_status"],
    },
    "04_07_traffic_safety": {
        "image": "/vision/lane/debug", "title": "OmniFleet Traffic Safety",
        "json": [
            "/vision/lane/result", "/vision/detections", "/vision/targets_3d",
            "/vision/events", "/vision/traffic_state", "/vision/risk",
            "/vision/lane_follow/status",
        ],
    },
}


def _vision_node(executable, name, parameters=None):
    """创建课程节点，并统一终端输出格式。"""

    return Node(
        package="omnifleet_vision",
        executable=executable,
        name=name,
        output="screen",
        parameters=[parameters or {}],
        additional_env={
            "VIRTUAL_ENV": VISION_VENV,
            "PATH": f"{VISION_VENV}/bin:{os.environ.get('PATH', '')}",
        },
    )


def _classical_node(executable, name, result_topic, debug_topic, extra=None):
    """创建传统视觉节点，并统一相机输入及结果话题。"""

    parameters = {
        "input_topic": COLOR_TOPIC,
        "result_topic": result_topic,
        "debug_topic": debug_topic,
        "use_gui": LaunchConfiguration("use_gui"),
    }
    parameters.update(extra or {})
    return _vision_node(executable, name, parameters)


def _display_nodes(course_function):
    """创建课程结果叠加节点和最终实时窗口。"""

    config = DISPLAY_TOPICS.get(course_function)
    if config is None:
        return []
    output_topic = f"/vision/course_gui/course_{course_function}/debug"
    overlay = _vision_node(
        "course_gui_overlay_node.py",
        f"course_overlay_{course_function}",
        {
            "image_topic": config["image"],
            "json_topics": config.get("json", []),
            "pose_topic": config.get("pose", ""),
            "output_topic": output_topic,
            "title": config["title"],
        },
    )
    display = _vision_node(
        "image_display_node.py",
        f"course_display_{course_function}",
        {
            "input_topic": output_topic,
            "window_name": config["title"],
            "use_gui": ParameterValue(LaunchConfiguration("use_gui"), value_type=bool),
        },
    )
    return [overlay, display]


def _detector(
    name, model, labels, result_topic="/vision/detections", class_ids="", confidence=0.4
):
    """创建 Jetson PyTorch CUDA 检测节点，模型始终来自包内 vendor 目录。"""

    return _vision_node(
        "ultralytics_detector_node.py",
        name,
        {
            "model_path": model,
            "input": COLOR_TOPIC,
            "result": result_topic,
            "debug": f"{result_topic}/debug",
            "class_ids": class_ids,
            "confidence": confidence,
        },
    )


def _tracker(input_topic="/vision/detections", output_topic="/vision/tracks"):
    """创建检测到跟踪的轻量级联调节点。"""

    return _vision_node(
        "detection_tracker_node.py",
        "course_detection_tracker",
        {"input_topic": input_topic, "output_topic": output_topic},
    )


def _depth_fusion(input_topic="/vision/tracks", output_topic="/vision/targets_3d"):
    """创建目标与对齐深度融合节点。"""

    return _vision_node(
        "target_depth_fusion_node.py",
        "course_target_depth_fusion",
        {
            "detection_topic": input_topic,
            "depth_topic": DEPTH_TOPIC,
            "output_topic": output_topic,
        },
    )


def _risk_node():
    """创建视觉与 RoboSense Airy 点云风险融合节点。"""

    return _vision_node(
        "multimodal_risk_node.py",
        "course_multimodal_risk",
        {
            "visual_topic": "/vision/targets_3d",
            "cloud_topic": LIDAR_TOPIC,
            "output_topic": "/vision/risk",
        },
    )


def _target_follow(enable_motion, class_filter=""):
    """创建目标跟随控制器；速度只进入视觉候选话题。"""

    return _vision_node(
        "target_follow_controller_node.py",
        "course_target_follow",
        {
            "target_topic": "/vision/targets_3d",
            "command_topic": VISION_COMMAND_TOPIC,
            "enable_motion": ParameterValue(enable_motion, value_type=bool),
            "class_filter": class_filter,
        },
    )


def _safe_behavior(enable_motion):
    """创建交通事件安全控制器；默认只发布零速候选。"""

    return _vision_node(
        "safe_behavior_controller_node.py",
        "course_safe_behavior",
        {
            "event_topic": "/vision/events",
            "command_topic": VISION_COMMAND_TOPIC,
            "enable_motion": ParameterValue(enable_motion, value_type=bool),
        },
    )


def _lane_controller(enable_motion):
    """创建车道控制器；默认禁止运动。"""

    return _vision_node(
        "lane_follow_controller_node.py",
        "course_lane_controller",
        {
            "lane_topic": "/vision/lane/result",
            "risk_topic": "/vision/risk",
            "command_topic": VISION_COMMAND_TOPIC,
            "enable_motion": ParameterValue(enable_motion, value_type=bool),
        },
    )


def _traffic_detectors(coco_model, coco_labels):
    """运行通用与双路红绿灯检测，再合并为统一结果。"""

    return [
        _detector(
            "course_traffic_coco", coco_model, coco_labels,
            result_topic="/vision/detections/coco", class_ids="0,2,3,5,7,9",
        ),
        _vision_node(
            "traffic_light_dual_node.py", "course_traffic_light_dual",
            {
                "input_topic": COLOR_TOPIC,
                "yolo_topic": "/vision/detections/coco",
                "result_topic": "/vision/detections/traffic_light",
                "debug_topic": "/vision/detections/traffic_light/debug",
            },
        ),
        _vision_node(
            "detection_aggregator_node.py", "course_detection_aggregator",
            {
                "input_topics": [
                    "/vision/detections/coco",
                    "/vision/detections/traffic_light",
                ],
                "output_topic": "/vision/detections",
            },
        ),
    ]


def _traffic_events():
    """创建检测、深度和交通事件联调链。"""

    return [
        _tracker(),
        _depth_fusion(),
        _vision_node(
            "traffic_event_node.py",
            "course_traffic_event",
            {"input_topic": "/vision/targets_3d", "output_topic": "/vision/events"},
        ),
        _vision_node(
            "traffic_course_state_node.py",
            "course_traffic_state",
            {"input_topic": "/vision/events", "output_topic": "/vision/traffic_state"},
        ),
    ]


def _camera_action(params_file):
    """按开关和课程配置启动板载相机。"""

    # The tutorials use the attached USB camera.  MVS is intentionally not
    # launched here; its daemon and driver are disabled on this robot.
    return Node(
        package="omnifleet_bringup",
        executable="usb_camera_publisher",
        name="tutorial_usb_camera",
        output="screen",
        parameters=[{"device": "/dev/video0",
                     "topic": "/camera/color/image_raw/compressed",
                     "frame_id": "camera_link",
                     "fps": 15.0}],
        condition=IfCondition(LaunchConfiguration("start_camera")),
    )


def _offline_failure(message):
    """离线工具缺少必需路径时只给出说明并安全结束。"""

    return [LogInfo(msg=message), EmitEvent(event=Shutdown(reason=message))]


def _build_course_actions(context):
    """根据课程功能编号装配节点，避免复制 32 套运行逻辑。"""

    course_function = LaunchConfiguration("course_function").perform(context)
    enable_motion = LaunchConfiguration("enable_motion")
    share = FindPackageShare("omnifleet_vision")
    vendor = lambda filename: PathJoinSubstitution([share, "models", "vendor", filename])
    coco_model = vendor("yolo11n_coco.pt")
    coco_labels = vendor("coco80_labels.txt")
    pose_model = vendor("yolov8s_pose.pt")

    # 模型训练和 TensorRT 是离线工具，不需要也不会默认启动相机。
    if course_function == "02_11_model_training":
        model = LaunchConfiguration("training_model").perform(context)
        dataset = LaunchConfiguration("dataset_yaml").perform(context)
        output = LaunchConfiguration("training_output").perform(context)
        if not dataset or not output:
            return _offline_failure("模型训练未启动：请显式提供 dataset_yaml 和 training_output。")
        if not Path(model).is_file() or not Path(dataset).is_file() or not Path(output).is_dir():
            return _offline_failure("模型训练未启动：模型、数据集文件或输出目录不存在。")
        return [
            ExecuteProcess(
                cmd=[
                    "ros2", "run", "omnifleet_vision", "model_training.py",
                    "--model", model, "--data", dataset, "--project", output,
                    "--name", LaunchConfiguration("training_name"),
                ],
                output="screen",
                additional_env={
                    "VIRTUAL_ENV": VISION_VENV,
                    "PATH": f"{VISION_VENV}/bin:{os.environ.get('PATH', '')}",
                },
            )
        ]

    if course_function == "02_12_tensorrt":
        mode = LaunchConfiguration("tensorrt_mode").perform(context)
        onnx_path = LaunchConfiguration("onnx_path").perform(context)
        engine_path = LaunchConfiguration("engine_path").perform(context)
        report_path = LaunchConfiguration("report_path").perform(context)
        if mode not in {"export", "benchmark"}:
            return _offline_failure("TensorRT 未启动：tensorrt_mode 只能是 export 或 benchmark。")
        required_file = onnx_path if mode == "export" else engine_path
        if not required_file or not Path(required_file).is_file() or not engine_path or not report_path:
            return _offline_failure("TensorRT 未启动：请提供存在的输入文件、engine_path 和 report_path。")
        if not Path(engine_path).parent.is_dir() or not Path(report_path).parent.is_dir():
            return _offline_failure("TensorRT 未启动：引擎或报告的父目录不存在。")
        command = ["ros2", "run", "omnifleet_vision", "tensorrt_tools.py", mode]
        if mode == "export":
            command += ["--onnx", onnx_path, "--engine", engine_path, "--report", report_path]
        else:
            command += ["--engine", engine_path, "--report", report_path]
        return [
            ExecuteProcess(
                cmd=command,
                output="screen",
                additional_env={
                    "VIRTUAL_ENV": VISION_VENV,
                    "PATH": f"{VISION_VENV}/bin:{os.environ.get('PATH', '')}",
                },
            )
        ]

    rgbd_functions = {
        "02_07_kcf", "02_10_depth", "03_01_camera_topics", "03_03_target_depth",
        "03_04_vision_lidar", "03_05_traffic_events", "03_06_chassis_control",
        "03_07_lane_integration", "03_08_vision_nav", "04_01_color_follow",
        "04_02_human_object_follow", "04_03_lane_project", "04_04_object_navigation",
        "04_05_multimodal_avoidance", "04_07_traffic_safety",
    }
    camera_profile = "mvs_rgbd_course.yaml" if course_function in rgbd_functions else "mvs_rgb_fast.yaml"
    actions = [_camera_action(PathJoinSubstitution([share, "config", camera_profile]))]
    mapping = {
        "02_01_camera_monitor": lambda: [
            _classical_node(
                "camera_monitor_node.py", "course_camera_monitor",
                "/vision/camera/status", "/vision/camera/debug",
            )
        ],
        "02_03_opencv": lambda: [
            _classical_node(
                "opencv_processor_node.py", "course_opencv",
                "/vision/opencv/result", "/vision/opencv/debug",
            )
        ],
        "02_04_color": lambda: [
            _classical_node(
                "color_recognition_node.py", "course_color",
                "/vision/color/result", "/vision/color/debug",
            )
        ],
        "02_05_qr": lambda: [
            _classical_node(
                "qr_recognition_node.py", "course_qr",
                "/vision/qr/result", "/vision/qr/debug",
            )
        ],
        "02_06_apriltag": lambda: [
            _classical_node(
                "apriltag_recognition_node.py", "course_apriltag",
                "/vision/apriltag/result", "/vision/apriltag/debug",
            )
        ],
        "02_07_kcf": lambda: [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([share, "launch", "kcf_follower.launch.py"])
                ),
                launch_arguments={
                    "tracker_color_topic": COLOR_TOPIC,
                    "aligned_color_topic": ALIGNED_COLOR_TOPIC,
                    "depth_topic": DEPTH_TOPIC,
                    "cmd_vel_topic": VISION_COMMAND_TOPIC,
                    "enable_motion": enable_motion,
                    "use_gui": LaunchConfiguration("use_gui"),
                    "tracking_scale": LaunchConfiguration("tracking_scale"),
                    "roi_x": LaunchConfiguration("roi_x"),
                    "roi_y": LaunchConfiguration("roi_y"),
                    "roi_width": LaunchConfiguration("roi_width"),
                    "roi_height": LaunchConfiguration("roi_height"),
                }.items(),
            )
        ],
        "02_08_human_perception": lambda: [
            _vision_node(
                "face_detection_node.py", "course_face",
                {"input": COLOR_TOPIC, "result": "/vision/faces", "debug": "/vision/faces/debug"},
            ),
            _vision_node(
                "ultralytics_detector_node.py", "course_pose",
                {"model_path": pose_model, "task": "human_pose", "input": COLOR_TOPIC,
                 "result": "/vision/pose", "debug": "/vision/pose/debug"},
            ),
        ],
        "02_09_yolo": lambda: [_detector("course_yolo", coco_model, coco_labels)],
        "02_10_depth": lambda: [
            _vision_node(
                "ultralytics_detector_node.py",
                "course_depth_yolo",
                {
                    "model_path": coco_model,
                    "task": "object_detection",
                    "input": ALIGNED_COLOR_TOPIC,
                    "result": "/vision/depth/yolo",
                    "debug": "/vision/depth/yolo/debug",
                    "confidence": 0.4,
                },
            ),
            _classical_node(
                "depth_measurement_node.py", "course_depth",
                "/vision/depth/result", "/vision/depth/debug",
                {
                    "input_topic": ALIGNED_COLOR_TOPIC,
                    "depth_topic": DEPTH_TOPIC,
                    "detection_topic": "/vision/depth/yolo",
                },
            )
        ],
        "02_13_pedestrian": lambda: [
            _detector("course_pedestrian", coco_model, coco_labels, class_ids="0")
        ],
        "02_14_traffic_light": lambda: [
            _detector(
                "course_traffic_light_yolo", coco_model, coco_labels,
                result_topic="/vision/traffic_light/yolo", class_ids="9", confidence=0.30,
            ),
            _vision_node(
                "traffic_light_dual_node.py", "course_traffic_light_dual",
                {
                    "input_topic": COLOR_TOPIC,
                    "yolo_topic": "/vision/traffic_light/yolo",
                    "result_topic": "/vision/detections",
                    "debug_topic": "/vision/detections/debug",
                },
            ),
        ],
        "02_16_vehicle": lambda: [
            _detector("course_vehicle", coco_model, coco_labels, class_ids="2,3,5,7")
        ],
        "02_17_license_plate": lambda: [
            _vision_node(
                "license_plate_node.py", "course_license_plate",
                {"input": COLOR_TOPIC, "result": "/vision/license_plate", "debug": "/vision/license_plate/debug"},
            )
        ],
        "03_01_camera_topics": lambda: [
            _classical_node(
                "camera_monitor_node.py", "course_camera_topics",
                "/vision/camera/status", "/vision/camera/debug",
            ),
            _classical_node(
                "depth_measurement_node.py", "course_depth_topics",
                "/vision/depth/result", "/vision/depth/debug", {"input_topic": DEPTH_TOPIC},
            ),
        ],
        "03_02_detection_tracking": lambda: [
            _detector("course_yolo", coco_model, coco_labels), _tracker()
        ],
        "03_03_target_depth": lambda: [
            _detector("course_yolo", coco_model, coco_labels), _tracker(), _depth_fusion()
        ],
        "03_04_vision_lidar": lambda: [
            _detector("course_yolo", coco_model, coco_labels), _tracker(), _depth_fusion(), _risk_node()
        ],
        "03_05_traffic_events": lambda: (
            _traffic_detectors(coco_model, coco_labels) + _traffic_events()
        ),
        "03_06_chassis_control": lambda: [
            _detector("course_yolo", coco_model, coco_labels), _tracker(), _depth_fusion(),
            _vision_node(
                "traffic_event_node.py", "course_traffic_event",
                {"input_topic": "/vision/targets_3d", "output_topic": "/vision/events"},
            ),
            _safe_behavior(enable_motion),
        ],
        "03_07_lane_integration": lambda: [
            _detector("course_yolo", coco_model, coco_labels), _tracker(), _depth_fusion(), _risk_node(),
            _classical_node(
                "lane_detection_node.py", "course_lane",
                "/vision/lane/result", "/vision/lane/debug",
            ),
            _lane_controller(enable_motion),
        ],
        "03_08_vision_nav": lambda: [
            _detector("course_yolo", coco_model, coco_labels), _tracker(), _depth_fusion(),
            _vision_node(
                "vision_nav_target_node.py", "course_vision_nav",
                {"input_topic": "/vision/targets_3d", "output_topic": "/vision/nav_goal"},
            ),
        ],
        "03_09_edge_deployment": lambda: [
            _detector("course_edge_yolo", coco_model, coco_labels),
            _vision_node(
                "inference_status_node.py", "course_inference_status",
                {"input": "/vision/detections", "result": "/vision/inference_status"},
            ),
        ],
        "04_01_color_follow": lambda: [
            _classical_node(
                "color_recognition_node.py", "course_color",
                "/vision/detections", "/vision/color/debug",
            ),
            _tracker(), _depth_fusion(), _target_follow(enable_motion),
        ],
        "04_02_human_object_follow": lambda: [
            _detector("course_pedestrian", coco_model, coco_labels, class_ids="0"),
            _tracker(), _depth_fusion(), _target_follow(enable_motion, "person"),
        ],
        "04_03_lane_project": lambda: [
            _detector("course_yolo", coco_model, coco_labels), _tracker(), _depth_fusion(), _risk_node(),
            _classical_node(
                "lane_detection_node.py", "course_lane",
                "/vision/lane/result", "/vision/lane/debug",
            ),
            _lane_controller(enable_motion),
        ],
        "04_04_object_navigation": lambda: [
            _detector("course_yolo", coco_model, coco_labels), _tracker(), _depth_fusion(),
            _vision_node(
                "vision_nav_target_node.py", "course_object_navigation",
                {"input_topic": "/vision/targets_3d", "output_topic": "/vision/nav_goal"},
            ),
        ],
        "04_05_multimodal_avoidance": lambda: [
            _detector("course_yolo", coco_model, coco_labels), _tracker(), _depth_fusion(), _risk_node(),
            _classical_node(
                "lane_detection_node.py", "course_lane",
                "/vision/lane/result", "/vision/lane/debug",
            ),
            _lane_controller(enable_motion),
        ],
        "04_06_edge_detection": lambda: [
            _detector("course_edge_yolo", coco_model, coco_labels),
            _vision_node(
                "inference_status_node.py", "course_edge_status",
                {"input": "/vision/detections", "result": "/vision/inference_status"},
            ),
        ],
        "04_07_traffic_safety": lambda: (
            _traffic_detectors(coco_model, coco_labels)
            + _traffic_events()
            + [
                _risk_node(),
                _classical_node(
                    "lane_detection_node.py", "course_lane",
                    "/vision/lane/result", "/vision/lane/debug",
                ),
                _lane_controller(enable_motion),
            ]
        ),
    }
    builder = mapping.get(course_function)
    if builder is None:
        return _offline_failure(f"未知视觉课程功能：{course_function}")
    course_actions = builder()
    course_actions.extend(_display_nodes(course_function))
    return actions + course_actions


def generate_launch_description():
    """声明统一参数并在运行时装配选定课程功能。"""

    share = FindPackageShare("omnifleet_vision")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "course_function", description="课程功能编号，由学生入口固定传入。"
            ),
            DeclareLaunchArgument(
                "start_camera", default_value="false", description="是否另行启动相机；远端常驻相机已运行时保持关闭。"
            ),
            DeclareLaunchArgument(
                "enable_motion", default_value="false",
                description="是否发布运动候选；默认关闭，输出仅限视觉安全候选话题。",
            ),
            DeclareLaunchArgument(
                "use_gui", default_value="true", description="是否打开课程图形窗口。"
            ),
            DeclareLaunchArgument(
                "tracking_scale", default_value="0.4",
                description="KCF 内部跟踪缩放比例；0.4 对应约 614×512。",
            ),
            DeclareLaunchArgument("roi_x", default_value="0", description="无界面模式初始框左上角 x。"),
            DeclareLaunchArgument("roi_y", default_value="0", description="无界面模式初始框左上角 y。"),
            DeclareLaunchArgument("roi_width", default_value="0", description="无界面模式初始框宽度。"),
            DeclareLaunchArgument("roi_height", default_value="0", description="无界面模式初始框高度。"),
            DeclareLaunchArgument(
                "training_model", default_value=PathJoinSubstitution(
                    [share, "models", "vendor", "yolo11n_coco.pt"]
                ), description="训练使用的初始模型文件。",
            ),
            DeclareLaunchArgument(
                "dataset_yaml", default_value="", description="训练数据集 YAML 文件，必须显式提供。"
            ),
            DeclareLaunchArgument(
                "training_output", default_value="", description="训练输出目录，必须显式提供且已存在。"
            ),
            DeclareLaunchArgument(
                "training_name", default_value="omnifleet_course", description="本次训练实验名称。"
            ),
            DeclareLaunchArgument(
                "tensorrt_mode", default_value="export", description="TensorRT 工具模式：export 或 benchmark。"
            ),
            DeclareLaunchArgument(
                "onnx_path", default_value=PathJoinSubstitution(
                    [share, "models", "vendor", "yolo11n_coco.onnx"]
                ), description="TensorRT 导出使用的 ONNX 文件。",
            ),
            DeclareLaunchArgument(
                "engine_path", default_value="", description="TensorRT 引擎路径，必须显式提供。"
            ),
            DeclareLaunchArgument(
                "report_path", default_value="", description="TensorRT 报告路径，必须显式提供。"
            ),
            OpaqueFunction(function=_build_course_actions),
        ]
    )
