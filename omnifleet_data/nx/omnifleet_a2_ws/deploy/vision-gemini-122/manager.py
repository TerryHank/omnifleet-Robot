#!/usr/bin/env python3
"""Connect the 122 vision page to the Gemini Pro and the existing follow nodes."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import String


ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / "vendor"
SOURCE = VENDOR / "home/iecme/omnifleet_ws"
DATA = VENDOR / "home/iecme/omnifleet_data"
MODELS = DATA / "ml_models/omnifleet_vision/vendor"
MOBILE = VENDOR / "opt/omnifleet-mobile-vision"
VISION = SOURCE / "src/perception/omnifleet_vision"
PERSON = SOURCE / "src/perception/omnifleet_person_follow"
PERSON_CASE = "04_09_body_tracking"
OBJECT_CASE = "02_07_kcf"
SERVICES = {
    OBJECT_CASE: "/kcf_follower/set_parameters",
    PERSON_CASE: "/body_tracking_104/horizon_tracking_RobotCmdVel/set_parameters",
}


def ros_command(command, config=None, params=None, remaps=None):
    args = [str(arg) for arg in command] + ["--ros-args"]
    if config:
        args += ["--params-file", str(config)]
    for key, value in (params or {}).items():
        if isinstance(value, bool):
            value = str(value).lower()
        args += ["-p", f"{key}:={value}"]
    for key, value in (remaps or {}).items():
        args += ["-r", f"{key}:={value}"]
    return args


class VisionManager(Node):
    def __init__(self):
        super().__init__("omnifleet_a2_vision_manager")
        self.env = dict(os.environ)
        paths = (ROOT / "python", PERSON, SOURCE / "src/sensing/omnifleet_hikrobot_rgbd",
                 self.env.get("PYTHONPATH", ""))
        self.env["PYTHONPATH"] = ":".join(str(path) for path in paths)
        self.env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                        OPENCV_FOR_THREADS_NUM="1", YOLO_AUTOINSTALL="false")
        self.processes = []
        self.case = self.request = None
        self.phase, self.message = "IDLE", ""
        self.started = 0.0
        self.status = self.create_publisher(String, "/vision/demo/status", 1)
        self.create_subscription(String, "/vision/demo/control", self.control, 10)
        self.mobile = self.spawn([sys.executable, str(MOBILE / "mobile_vision.py")])
        self.preview = self.create_publisher(
            CompressedImage, "/camera/color/vision_follow/compressed", qos_profile_sensor_data)
        self.create_subscription(Image, "/camera/color/image_raw", self.image, qos_profile_sensor_data)
        self.bridge, self.next_preview = CvBridge(), 0.0
        self.create_timer(0.25, self.update)

    def spawn(self, args):
        return subprocess.Popen(args, env=self.env)

    def image(self, frame):
        now = time.monotonic()
        if now < self.next_preview or not self.preview.get_subscription_count():
            return
        self.next_preview = now + 0.1
        image = self.bridge.imgmsg_to_cv2(frame, "bgr8")
        ok, jpeg = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 75])
        if ok:
            self.preview.publish(CompressedImage(header=frame.header, format="jpeg", data=jpeg.tobytes()))

    def commands(self, case):
        if case == OBJECT_CASE:
            return (
                ros_command([SOURCE / "build/omnifleet_vision/kcf_follower_node"],
                            VISION / "config/kcf_follower.yaml",
                            {"enable_motion": False, "use_gui": False, "sparse_depth": True,
                             "inline_sparse_depth": True, "remote_roi": True, "external_tracker": True,
                             "tracking_scale": 1.0, "minimum_linear_speed": 0.0,
                             "max_linear_speed": 0.2, "max_angular_speed": 0.3},
                            {"/cmd_vel_vision": "/cmd_vel"}),
                ros_command([sys.executable, VISION / "scripts/integration/nanotrack_node.py"], params={
                    "mode": "roi", "tracking_backend": "nanotrack", "model_root": str(MODELS / "nanotrack_v2"),
                    "output_topic": "/vision/nanotrack/selected", "debug_topic": "''",
                    "image_topic": "/camera/color/image_raw", "source_info_topic": "/camera/color/camera_info",
                }, remaps={"__node": "course_nanotrack"}),
            )
        return (
            ros_command([SOURCE / "build/body_tracking/body_tracking"], PERSON / "config/body_tracking_104.yaml",
                        {"enable_motion": False, "img_width": 640, "img_height": 480,
                         "steering_max_speed": 0.3, "reverse_max_speed": 0.2},
                        {"__ns": "/body_tracking_104", "body_tracking_cmd": "/vision/body_tracking/cmd_vel",
                         "body_tracking_state": "/vision/body_tracking/native_status",
                         "/cmd_vel_vision": "/cmd_vel"}) + ["--log-level", "error"],
            ros_command([sys.executable, "-c", "from omnifleet_person_follow.node import main; main()"],
                        PERSON / "config/person_follow.yaml",
                        {"controller_backend": "body_tracking", "auto_follow": False, "enable_motion": False,
                         "camera_backend": "orbbec", "use_local_frames": False, "depth_max_m": 6.0,
                         "engine_path": str(MODELS / "yolo26_person_follow/yolo26n-seg.engine"),
                         "zoo_root": str(DATA / "reference_sources/opencv_zoo_models"),
                         "model_root": str(MODELS), "tracker_config": str(PERSON / "config/botsort.yaml"),
                         "face_model_path": "''", "status_topic": "/vision/body_tracking/status",
                         "jpeg_quality": 60, "preview_interval_s": 0.125},
                        {"__node": "course_gesture_person_follow"}),
        )

    def stop_case(self):
        for process in self.processes:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
        for process in self.processes:
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        self.processes.clear()
        self.case = None

    def control(self, message):
        try:
            request = json.loads(message.data)
            op = request["op"]
            if op == "start" and request.get("case_id") in SERVICES:
                self.request = request.get("id")
                if self.case != request["case_id"] or self.phase not in ("STARTING", "RUNNING"):
                    self.stop_case()
                    self.case = request["case_id"]
                    self.started = time.monotonic()
                    self.phase, self.message = "STARTING", ""
                    for command in self.commands(self.case):
                        self.processes.append(self.spawn(command))
            elif op in ("stop", "navigation"):
                self.request = request.get("id")
                self.stop_case()
                self.phase = "NAVIGATION" if op == "navigation" else "STOPPED"
                self.message = ""
        except (ValueError, KeyError, TypeError, OSError) as error:
            self.stop_case()
            self.phase, self.message = "ERROR", str(error)
        self.publish()

    def update(self):
        if self.mobile.poll() is not None:
            raise RuntimeError("Mobile vision detection stopped")
        if self.case:
            exited = next((p for p in self.processes if p.poll() is not None), None)
            if exited:
                code = exited.returncode
                self.stop_case()
                self.phase, self.message = "ERROR", f"122 视觉跟随进程退出（{code}）"
            elif self.phase == "STARTING":
                names = dict(self.get_service_names_and_types())
                if SERVICES[self.case] in names:
                    self.phase = "RUNNING"
                elif time.monotonic() - self.started > 30:
                    self.stop_case()
                    self.phase, self.message = "ERROR", "122 视觉跟随控制服务启动超时"
        self.publish()

    def publish(self):
        self.status.publish(String(data=json.dumps({
            "phase": self.phase, "case_id": self.case,
            "request_id": self.request, "message": self.message,
        })))


def main():
    rclpy.init()
    node = VisionManager()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.stop_case()
        if node.mobile.poll() is None:
            node.mobile.send_signal(signal.SIGINT)
            node.mobile.wait(timeout=3)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
