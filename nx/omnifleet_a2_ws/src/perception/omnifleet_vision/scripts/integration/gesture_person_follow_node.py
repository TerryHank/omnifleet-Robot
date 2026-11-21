#!/usr/bin/env python3
"""Single-pass whole-body gesture driven person-following course node."""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


FINGER_CHAINS = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12),
                 (13, 14, 15, 16), (17, 18, 19, 20))


def classify_hand(landmarks: np.ndarray) -> tuple[str, int]:
    """Use the OpenCV Zoo demo geometry to classify fist, palm, and 1-3."""
    points = np.asarray(landmarks, dtype=np.float32).reshape(21, -1)[:, :2]

    def angle(first, second):
        first_norm = np.linalg.norm(first)
        second_norm = np.linalg.norm(second)
        if first_norm < 1e-6 or second_norm < 1e-6:
            return 180.0
        cosine = float(np.dot(first / first_norm, second / second_norm))
        return float(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))))

    angles = [
        angle(points[0] - points[2], points[3] - points[4]),
        angle(points[0] - points[6], points[7] - points[8]),
        angle(points[0] - points[10], points[11] - points[12]),
        angle(points[0] - points[14], points[15] - points[16]),
        angle(points[0] - points[18], points[19] - points[20]),
    ]
    open_status = []
    for base, tip in ((5, 4), (6, 8), (10, 12), (14, 16), (18, 20)):
        open_status.append(
            np.linalg.norm(points[tip] - points[0]) > np.linalg.norm(points[base] - points[0])
        )
    large, straight = 65.0, 49.0
    extended = [angles[index] < straight and open_status[index] for index in range(1, 5)]
    if all(value > large for value in angles[1:]) and not any(extended):
        return "fist", 0
    if extended == [True, False, False, False]:
        return "1", 1
    if extended == [True, True, False, False]:
        return "2", 2
    if extended == [True, True, True, False]:
        return "3", 3
    if all(extended):
        return "open_palm", 4 + int(open_status[0])
    return "unknown", int(sum(extended)) + int(open_status[0])


@dataclass
class GestureState:
    mode: str = "idle"
    candidate: str = "unknown"
    candidate_frames: int = 0
    last_confirmed: str = "unknown"

    def update(self, gesture: str, required_frames: int = 1) -> str | None:
        """Debounce a gesture and apply the user-visible command state machine."""
        if gesture != self.candidate:
            self.candidate = gesture
            self.candidate_frames = 1
        else:
            self.candidate_frames += 1
        if self.candidate_frames < required_frames or gesture == self.last_confirmed:
            return None
        self.last_confirmed = gesture
        if gesture == "open_palm":
            self.mode = "follow"
            return "follow_started"
        if gesture == "fist":
            event = "follow_cancelled" if self.mode == "follow" else "stopped"
            self.mode = "idle"
            return event
        if gesture == "1":
            self.mode = "forward"
            return "forward"
        if gesture == "2":
            self.mode = "reverse"
            return "reverse"
        if gesture == "3":
            self.mode = "rotate"
            return "rotate"
        return None


def median_depth_m(depth: np.ndarray, x: float, y: float, color_size: tuple[int, int], radius=5):
    """Return median valid depth at a color-image coordinate."""
    color_width, color_height = color_size
    px = int(round(x * depth.shape[1] / color_width))
    py = int(round(y * depth.shape[0] / color_height))
    x0, x1 = max(0, px - radius), min(depth.shape[1], px + radius + 1)
    y0, y1 = max(0, py - radius), min(depth.shape[0], py + radius + 1)
    values = depth[y0:y1, x0:x1]
    values = values[(values >= 200) & (values <= 1500)]
    return None if values.size == 0 else float(np.median(values)) * 0.001


def manual_velocity(mode: str, forward=0.20, reverse=-0.15, rotate=0.50):
    """Map confirmed numeric gestures to linear-x and angular-z commands."""
    if mode == "forward":
        return forward, 0.0
    if mode == "reverse":
        return reverse, 0.0
    if mode == "rotate":
        return 0.0, rotate
    return 0.0, 0.0


class SingleWholebodyPipeline:
    """RTMW-m: one full-image inference for body and both 21-point hands.

    Uses the official COCO-WholeBody SimCC output order. No detector, second
    hand network, flip-test or per-person inference loop is loaded or run.
    This full-image top-down model is intended for one main person in view.
    """

    def __init__(self, model_path: str):
        import onnxruntime as ort
        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        providers = [name for name in ("CUDAExecutionProvider", "CPUExecutionProvider")
                     if name in ort.get_available_providers()]
        self.session = ort.InferenceSession(str(Path(model_path)), options, providers=providers)
        self.provider = self.session.get_providers()[0]
        self.input_name = self.session.get_inputs()[0].name
        self.timings = {}
        self.calls_last_frame = 0

    @staticmethod
    def preprocess(image):
        # Match model pipeline.json: aspect-correct bbox padding 1.25,
        # affine directly to 192x256, then RGB normalization at that size.
        height, width = image.shape[:2]
        center = np.array([width / 2., height / 2.], dtype=np.float32)
        scale = np.array([width, height], dtype=np.float32)
        aspect = 192. / 256.
        if scale[0] > scale[1] * aspect:
            scale[1] = scale[0] / aspect
        else:
            scale[0] = scale[1] * aspect
        scale *= 1.25
        matrix = np.array([[192. / scale[0], 0., 96. - center[0] * 192. / scale[0]],
                           [0., 256. / scale[1], 128. - center[1] * 256. / scale[1]]], np.float32)
        small = cv2.warpAffine(image, matrix, (192, 256), flags=cv2.INTER_LINEAR)
        small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).astype(np.float32)
        small -= np.array([123.675, 116.28, 103.53], np.float32)
        small /= np.array([58.395, 57.12, 57.375], np.float32)
        return np.ascontiguousarray(small.transpose(2, 0, 1)[None]), center, scale

    @staticmethod
    def decode(outputs, center, scale):
        simcc_x, simcc_y = outputs
        x = simcc_x[0].argmax(axis=1)
        y = simcc_y[0].argmax(axis=1)
        scores = np.minimum(simcc_x[0].max(axis=1), simcc_y[0].max(axis=1))
        points = np.stack([x, y], axis=1).astype(np.float32) / 2.
        points = points / np.array([192., 256.], np.float32) * scale + center - scale / 2.
        return points, scores

    def infer(self, image: np.ndarray):
        started = time.perf_counter()
        blob, center, scale = self.preprocess(image)
        prepared = time.perf_counter()
        self.calls_last_frame = 0
        outputs = self.session.run(None, {self.input_name: blob})
        self.calls_last_frame += 1
        forwarded = time.perf_counter()
        points, scores = self.decode(outputs, center, scale)
        person, pose, hands = None, None, []
        # Whole-body models predict coordinates even on an empty image; use
        # the returned joint confidence to distinguish a recognized body/hand.
        if float(scores[[5, 6, 11, 12]].mean()) >= .3:
            body = points[:17]
            visible = body[scores[:17] >= .3]
            person = np.r_[visible.min(axis=0), visible.max(axis=0)]
            pose = (person, np.c_[body, np.zeros(17), scores[:17], scores[:17]])
            for offset in (91, 112):
                hand_scores = scores[offset:offset + 21]
                if float(hand_scores.mean()) >= .3:
                    hand = points[offset:offset + 21]
                    hands.append(np.r_[hand.min(axis=0), hand.max(axis=0),
                                       np.c_[hand, np.zeros(21)].reshape(-1)])
        hand = max(hands, key=lambda item: (item[2] - item[0]) * (item[3] - item[1])) if hands else None
        self.timings = dict(preprocess_ms=round((prepared - started) * 1000., 2),
                            forward_ms=round((forwarded - prepared) * 1000., 2),
                            postprocess_ms=round((time.perf_counter() - forwarded) * 1000., 2))
        return person, pose, hand


def main(args=None) -> None:
    import rclpy
    from cv_bridge import CvBridge
    from geometry_msgs.msg import Twist
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy
    from sensor_msgs.msg import Image
    from std_msgs.msg import String

    class GesturePersonFollowNode(Node):
        def __init__(self):
            super().__init__("gesture_person_follow")
            p = lambda name, default: self.declare_parameter(name, default).value
            self.image_topic = str(p("image_topic", "/camera/color/image_raw"))
            self.depth_topic = str(p("depth_topic", "/camera/aligned_depth_to_color/image_raw"))
            self.command_topic = str(p("command_topic", "/cmd_vel"))
            self.enable_motion = bool(p("enable_motion", False))
            self.stable_frames = int(p("stable_frames", 1))
            self.gesture_timeout = float(p("gesture_timeout", 0.8))
            self.target_timeout = float(p("target_timeout", 0.7))
            self.depth_timeout = float(p("depth_timeout", 2.5))
            self.follow_min = float(p("follow_distance_min", 0.8))
            self.follow_max = float(p("follow_distance_max", 1.0))
            self.forward_speed = float(p("forward_speed", 0.20))
            self.reverse_speed = float(p("reverse_speed", -0.15))
            self.rotate_speed = float(p("rotate_speed", 0.50))
            model_path = str(p("model_path",
                "/home/iecme/omnifleet_data/ml_models/omnifleet_vision/vendor/rtmw/end2end.onnx"))
            self.pipeline = SingleWholebodyPipeline(model_path)
            self.bridge = CvBridge()
            self.state = GestureState()
            self.depth = None
            self.depth_time = 0.0
            self.last_gesture_time = 0.0
            self.last_target_time = 0.0
            self.last_command = Twist()
            self.processing = False
            self.status_pub = self.create_publisher(String, "/vision/gesture_follow/status", 10)
            self.debug_pub = self.create_publisher(Image, "/vision/gesture_follow/debug", 10)
            self.cmd_pub = self.create_publisher(Twist, self.command_topic, 10)
            latest_image_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
            self.create_subscription(Image, self.depth_topic, self.on_depth, latest_image_qos)
            self.create_subscription(Image, self.image_topic, self.on_image, latest_image_qos)
            self.create_timer(0.1, self.on_control)
            self.get_logger().info(
                f"RTMW-m single model; provider={self.pipeline.provider}; motion={self.enable_motion}"
            )

        def now(self):
            return self.get_clock().now().nanoseconds / 1e9

        def on_depth(self, message: Image):
            if message.encoding not in ("16UC1", "mono16"):
                return
            self.depth = np.frombuffer(message.data, dtype="<u2").reshape(message.height, message.width).copy()
            self.depth_time = self.now()

        def on_image(self, message: Image):
            if self.processing:
                return
            self.processing = True
            started = time.perf_counter()
            try:
                image = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
                person, pose, hand = self.pipeline.infer(image)
                gesture = "unknown"
                fingers = None
                if hand is not None:
                    gesture, fingers = classify_hand(np.asarray(hand[4:67]).reshape(21, 3))
                    self.last_gesture_time = self.now()
                    event = self.state.update(gesture, self.stable_frames)
                    if event:
                        self.get_logger().info(f"gesture={gesture} event={event} mode={self.state.mode}")
                target_depth = None
                target_center = None
                if person is not None:
                    x1, y1, x2, y2 = (float(value) for value in person[:4])
                    target_center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
                    if self.depth is not None:
                        target_depth = median_depth_m(
                            self.depth, *target_center, (image.shape[1], image.shape[0])
                        )
                    self.last_target_time = self.now()
                    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 160, 0), 3)
                if pose is not None:
                    for x, y, _, visibility, presence in pose[1][:33]:
                        if visibility > 0.5 and presence > 0.5:
                            cv2.circle(image, (int(x), int(y)), 3, (0, 200, 255), -1)
                if hand is not None:
                    landmarks = np.asarray(hand[4:67]).reshape(21, 3)
                    for x, y, _ in landmarks:
                        cv2.circle(image, (int(x), int(y)), 4, (0, 255, 0), -1)
                self.update_command(image.shape[1], target_center, target_depth)
                latency = (time.perf_counter() - started) * 1000.0
                status = {
                    "mode": self.state.mode, "gesture": gesture, "fingers": fingers,
                    "person": person is not None, "target_depth_m": target_depth,
                    "inference_ms": round(latency, 1), "cuda_target": None,
                    "model_name": "RTMW-m", "model_count": 1,
                    "inference_calls": self.pipeline.calls_last_frame,
                    "inference_backend": "onnxruntime", "execution_provider": self.pipeline.provider,
                    **self.pipeline.timings,
                    "motion_enabled": self.enable_motion,
                    "depth_received": self.depth is not None,
                    "depth_topic": self.depth_topic,
                }
                text = f"{self.state.mode} | {gesture} | {target_depth or 0:.2f}m | {latency:.0f}ms"
                cv2.putText(image, text, (24, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                out = String(); out.data = json.dumps(status, ensure_ascii=False)
                self.status_pub.publish(out)
                debug = self.bridge.cv2_to_imgmsg(image, encoding="bgr8")
                debug.header = message.header
                self.debug_pub.publish(debug)
            except Exception as error:
                self.get_logger().error(f"gesture person following inference failed: {error}")
            finally:
                self.processing = False

        def update_command(self, width, center, depth):
            command = Twist()
            now = self.now()
            mode = self.state.mode
            if mode == "follow":
                if (center is None or depth is None or
                        now - self.last_target_time > self.target_timeout or
                        now - self.depth_time > self.depth_timeout):
                    self.last_command = command
                    return
                horizontal_error = (center[0] - width / 2.0) / (width / 2.0)
                command.angular.z = float(np.clip(-horizontal_error * 0.7, -0.6, 0.6))
                if depth > self.follow_max:
                    command.linear.x = float(np.clip((depth - self.follow_max) * 0.5, 0.0, 0.25))
                elif depth < self.follow_min:
                    command.linear.x = 0.0
            elif now - self.last_gesture_time <= self.gesture_timeout:
                command.linear.x, command.angular.z = manual_velocity(
                    mode, self.forward_speed, self.reverse_speed, self.rotate_speed
                )
            else:
                self.state.mode = "idle"
                self.state.last_confirmed = "unknown"
            self.last_command = command

        def on_control(self):
            now = self.now()
            if self.state.mode == "follow":
                if now - self.last_target_time > self.target_timeout or now - self.depth_time > self.depth_timeout:
                    self.last_command = Twist()
            elif now - self.last_gesture_time > self.gesture_timeout:
                self.last_command = Twist()
                self.state.mode = "idle"
                self.state.last_confirmed = "unknown"
            if self.enable_motion:
                self.cmd_pub.publish(self.last_command)

        def destroy_node(self):
            if self.enable_motion and rclpy.ok():
                self.cmd_pub.publish(Twist())
            return super().destroy_node()

    rclpy.init(args=args)
    node = GesturePersonFollowNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
