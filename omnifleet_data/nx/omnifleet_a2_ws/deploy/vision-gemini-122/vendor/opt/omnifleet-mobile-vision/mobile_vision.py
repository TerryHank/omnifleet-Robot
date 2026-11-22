#!/usr/bin/env python3
"""Detection and target selection; existing NanoTrack and depth controller execute follow."""
import json
import threading
import time
from collections import OrderedDict
from uuid import uuid4
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import String
from detection import LABELS, detect, select_detection

REACQUIRE_SECONDS = 3.
TRACK_FRESH_SECONDS = .5


class MobileVision(Node):
    def __init__(self):
        super().__init__('mobile_vision_detection')
        self.mode = 'off'
        self.labels = ()
        self.latest = None
        self.lock = threading.Lock()
        self.frames = OrderedDict()
        self.serial = 0
        self.target = None
        self.session_id = None
        self.last_seen = None
        self.source_stamp = float('-inf')
        self.tracking_state = 'recognizing'
        self.orphan_session = None
        self.bridge = CvBridge()
        self.status = self.create_publisher(String, '/vision/mobile/detections', 1)
        self.tracking_control = self.create_publisher(String, '/vision/mobile/tracking_control', 10)
        self.create_subscription(Image, '/camera/color/image_raw', self.image, qos_profile_sensor_data)
        self.create_subscription(String, '/vision/mobile/control', self.control, 10)
        self.create_subscription(String, '/vision/nanotrack/selected', self.track, 1)
        self.create_timer(.2, self.process)

    def image(self, message):
        if self.mode != 'off' and self.session_id is None:
            with self.lock:
                self.latest = message

    def publish_state(self):
        remaining = (max(0., REACQUIRE_SECONDS - (time.monotonic() - self.last_seen))
                     if self.tracking_state == 'searching' else None)
        self.status.publish(String(data=json.dumps({
            'op': 'state', 'mode': self.mode, 'labels': self.labels,
            'tracking_state': self.tracking_state, 'session_id': self.session_id,
            'target': self.target, 'remaining_s': remaining,
        })))

    def tracker_command(self, op, **fields):
        self.tracking_control.publish(String(data=json.dumps({
            'op': op, 'session_id': self.session_id, **fields,
        })))

    def clear_frames(self):
        self.frames.clear()
        with self.lock:
            self.latest = None

    def cancel(self):
        if self.session_id is not None:
            self.tracker_command('cancel')
            self.orphan_session = self.session_id
        self.session_id = self.target = self.last_seen = None
        self.tracking_state = 'recognizing'
        self.clear_frames()

    def track(self, message):
        try:
            payload = json.loads(message.data)
            if self.session_id is None:
                orphan = payload.get('session_id')
                if orphan and orphan != self.orphan_session:
                    self.orphan_session = orphan
                    self.tracking_control.publish(String(data=json.dumps({
                        'op': 'cancel', 'session_id': orphan,
                    })))
                    self.publish_state()
                return
            if payload.get('session_id') != self.session_id:
                return
            stamp = float(payload['source_stamp'])
            if not stamp > self.source_stamp:
                return
            self.source_stamp = stamp
            now = time.monotonic()
            previous_state = self.tracking_state
            if now - self.last_seen >= REACQUIRE_SECONDS:
                self.cancel()
            elif payload.get('tracks'):
                self.last_seen = now
                self.tracking_state = 'tracking'
            elif self.tracking_state != 'locking':
                self.tracking_state = 'searching'
            if previous_state != self.tracking_state:
                self.publish_state()
        except (ValueError, KeyError, TypeError) as error:
            self.get_logger().warning(f'Invalid tracker status: {error}', throttle_duration_sec=5.)

    def control(self, message):
        try:
            request = json.loads(message.data)
            op = request.get('op')
            if op == 'status':
                self.publish_state()
            elif op == 'cancel':
                if request.get('session_id') == self.session_id:
                    self.cancel()
                self.publish_state()
            elif op == 'mode' and request.get('mode') in LABELS:
                mode = request['mode']
                labels = request.get('labels', LABELS[mode])
                if not isinstance(labels, (list, tuple)) or any(label not in LABELS[mode] for label in labels):
                    raise ValueError('识别项与当前模式不匹配')
                if mode != self.mode:
                    self.cancel()
                self.mode, self.labels = mode, tuple(labels)
                self.clear_frames()
                self.publish_state()
            elif op == 'select':
                if self.session_id is not None:
                    self.publish_state()
                    return
                frame = self.frames.get(request.get('frame_id'))
                if frame is None or time.monotonic() - frame['received'] > 1.5:
                    raise ValueError('检测结果已更新，请再次点击目标')
                target = select_detection(self.frames, request.get('frame_id'), request.get('index'))
                self.session_id = str(uuid4())
                self.target = target
                self.last_seen = time.monotonic()
                self.source_stamp = float('-inf')
                self.tracking_state = 'locking'
                self.clear_frames()
                self.tracker_command('select', bbox=target['bbox'])
                self.status.publish(String(data=json.dumps({'selection': target, 'request_id': request.get('id')})))
                self.publish_state()
        except (ValueError, TypeError, KeyError) as error:
            self.status.publish(String(data=json.dumps({'error': str(error)})))

    def process(self):
        if self.session_id is not None:
            elapsed = time.monotonic() - self.last_seen
            if elapsed >= REACQUIRE_SECONDS:
                self.cancel()
            elif self.tracking_state == 'tracking' and elapsed > TRACK_FRESH_SECONDS:
                self.tracking_state = 'searching'
            self.publish_state()
            return
        if self.mode == 'off':
            self.publish_state()
            return
        with self.lock:
            message, self.latest = self.latest, None
        if message is None:
            return
        try:
            image = self.bridge.imgmsg_to_cv2(message, desired_encoding='bgr8')
            self.serial += 1
            result = {'frame_id': self.serial, 'mode': self.mode, 'width': message.width, 'height': message.height,
                      'stamp': [message.header.stamp.sec, message.header.stamp.nanosec],
                      'detections': detect(image, self.mode, self.labels)}
            self.frames[self.serial] = {**result, 'received': time.monotonic()}
            while len(self.frames) > 8:
                self.frames.popitem(last=False)
            self.status.publish(String(data=json.dumps(result)))
        except Exception as error:
            self.get_logger().error(str(error))
            self.status.publish(String(data=json.dumps({'error': '识别失败：' + str(error)})))


def main():
    rclpy.init()
    node = MobileVision()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
