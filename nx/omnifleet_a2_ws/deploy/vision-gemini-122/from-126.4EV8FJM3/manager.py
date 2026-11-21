#!/usr/bin/env python3
"""Connect the 122 vision page to the Gemini Pro and the existing follow nodes."""

import json
import os
from pathlib import Path
from queue import Empty, Queue
import signal
import subprocess
import sys
import threading
import time

import cv2
from cv_bridge import CvBridge
import rclpy
from rcl_interfaces.msg import Parameter, ParameterType, ParameterValue
from rcl_interfaces.srv import SetParameters
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
CASES = (OBJECT_CASE, PERSON_CASE)
BODY_CONTROL = "/body_tracking_104/horizon_tracking_RobotCmdVel"
os.environ['OMNIFLEET_COLOR_CALIBRATION'] = str(ROOT.parent/'split1080/rgb1080-calibration.yaml')
sys.path.insert(0,str(SOURCE/'src/sensing/omnifleet_hikrobot_rgbd'))


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
        self.processes = {}
        self.active_case = None
        self.state = {"phase": "IDLE", "case_id": None, "request_id": None, "message": ""}
        self.requests = Queue()
        self.parameter_clients = {}
        self.closing = threading.Event()
        self.status = self.create_publisher(String, "/vision/demo/status", 1)
        self.create_subscription(String, "/vision/demo/control", self.control, 10)
        self.mobile = self.spawn([sys.executable, str(MOBILE / "mobile_vision.py")])
        self.preview = self.create_publisher(
            CompressedImage, "/camera/color/receiver_follow/compressed", qos_profile_sensor_data)
        self.create_subscription(Image, "/camera/color/image_raw", self.image, qos_profile_sensor_data)
        self.bridge, self.next_preview = CvBridge(), 0.0
        self.create_timer(0.25, self.publish)
        self.worker = threading.Thread(target=self.work, name="vision-cases")
        self.worker.start()

    def spawn(self, args, warm=False):
        env = dict(self.env, OMNIFLEET_WARM_CASE="1") if warm else self.env
        return subprocess.Popen(args, env=env)

    def image(self, frame):
        now = time.monotonic()
        if now < self.next_preview or not self.preview.get_subscription_count():
            return
        self.next_preview = now + 1 / 15
        image = self.bridge.imgmsg_to_cv2(frame, "bgr8")
        height, width = image.shape[:2]
        scale = min(1, 640 / width, 480 / height)
        if self.active_case == PERSON_CASE:
            from omnifleet_hikrobot_rgbd.local_frames import rectify_native_color
            image = rectify_native_color(image,(round(width*scale),round(height*scale)))
        elif scale < 1:
            image = cv2.resize(image, (round(width * scale), round(height * scale)),
                               interpolation=cv2.INTER_AREA)
        for quality in (65, 55, 45, 35):
            ok, jpeg = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
            if ok and jpeg.nbytes <= 24 * 1024:
                self.preview.publish(CompressedImage(header=frame.header, format="jpeg", data=jpeg.tobytes()))
                return

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
                        {"enable_motion": False, "img_width": 1920, "img_height": 1080,
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
                         "jpeg_quality": 60, "preview_interval_s": 0.125,
                         "steering_max_speed": 0.3, "reverse_max_speed": 0.2},
                        {"__node": "course_gesture_person_follow"}),
        )

    @staticmethod
    def stop_processes(processes):
        for process in processes:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
        for process in processes:
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

    def stop_all(self):
        for processes in self.processes.values():
            self.stop_processes(processes)
        self.processes.clear()
        self.active_case = None

    def ensure_warm(self, case):
        processes = self.processes.get(case)
        if processes and all(process.poll() is None for process in processes):
            return
        if processes:
            self.stop_processes(processes)
        self.processes[case] = []
        for command in self.commands(case):
            self.processes[case].append(self.spawn(command, warm=True))

    def switch(self, node, **values):
        client = self.parameter_clients.get(node)
        if client is None:
            client = self.create_client(SetParameters, node + "/set_parameters")
            self.parameter_clients[node] = client
        deadline = time.monotonic() + 24
        while not self.closing.is_set() and not client.wait_for_service(timeout_sec=0.25):
            if time.monotonic() >= deadline:
                raise RuntimeError(f"{node} 启动超时")
        request = SetParameters.Request(parameters=[
            Parameter(name=key, value=ParameterValue(type=ParameterType.PARAMETER_BOOL, bool_value=value))
            for key, value in values.items()
        ])
        future = client.call_async(request)
        while not self.closing.wait(0.05):
            if future.done():
                replies = future.result().results
                if len(replies) != len(values) or any(not reply.successful for reply in replies):
                    raise RuntimeError(f"{node} 切换失败: " + "; ".join(reply.reason for reply in replies))
                return
            if time.monotonic() >= deadline:
                break
        client.remove_pending_request(future)
        raise RuntimeError(f"{node} 切换响应超时")

    def set_active(self, case, active):
        if case == PERSON_CASE:
            self.switch(BODY_CONTROL, enable_motion=False)
            self.switch("/course_gesture_person_follow", vision_active=active)
        elif active:
            self.switch("/course_nanotrack", vision_active=True)
            self.switch("/kcf_follower", vision_active=True, enable_motion=False)
        else:
            self.switch("/kcf_follower", vision_active=False, enable_motion=False)
            self.switch("/course_nanotrack", vision_active=False)

    def update(self, phase, case=None, request=None, message=""):
        self.state = {"phase": phase, "case_id": case, "request_id": request, "message": message}

    def control(self, message):
        try:
            request = json.loads(message.data)
            op, case = request.get("op"), request.get("case_id")
            if op in ("stop", "navigation") or (op in ("start", "preload") and case in CASES):
                self.requests.put((op, case, request.get("id")))
        except (ValueError, AttributeError):
            self.get_logger().warning("无效的视觉请求")

    def work(self):
        try:
            while not self.closing.is_set():
                try:
                    op, case, request = self.requests.get(timeout=0.25)
                except Empty:
                    if self.active_case and any(p.poll() is not None for p in self.processes[self.active_case]):
                        case = self.active_case
                        self.stop_all()
                        self.update("ERROR", case, self.state["request_id"], "122 视觉进程已退出")
                    continue
                try:
                    if op == "preload":
                        if case == self.active_case:
                            self.ensure_warm(next(other for other in CASES if other != case))
                    elif op in ("stop", "navigation"):
                        self.stop_all()
                        self.update("NAVIGATION" if op == "navigation" else "STOPPED", request=request)
                    else:
                        if self.active_case != case:
                            self.update("STARTING", case, request)
                            if self.active_case:
                                self.set_active(self.active_case, False)
                            self.ensure_warm(case)
                            self.set_active(case, True)
                            self.active_case = case
                        self.update("RUNNING", case, request)
                except (RuntimeError, OSError) as error:
                    if op == "preload":
                        self.get_logger().warning(f"视觉预加载失败: {error}")
                    else:
                        self.stop_all()
                        self.update("ERROR", case, request, str(error))
        finally:
            self.stop_all()

    def publish(self):
        if self.mobile.poll() is not None:
            raise RuntimeError("Mobile vision detection stopped")
        self.status.publish(String(data=json.dumps(self.state)))


def main():
    rclpy.init()
    node = VisionManager()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.closing.set()
        node.worker.join()
        node.stop_processes([node.mobile])
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
