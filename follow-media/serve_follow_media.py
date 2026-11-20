#!/usr/bin/env python3
"""Hardware AVC preview from the existing Gemini capture, over the GR01 DDS link."""

from collections import deque
import ctypes as ct
import json
from pathlib import Path
import struct
import time

import cv2
import gi
import numpy as np
import rclpy
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

gi.require_version('Gst', '1.0')
from gi.repository import Gst

from omnifleet_hikrobot_rgbd.local_frames import native_color_geometry


CAMERA = Path('/dev/shm/omnifleet-gemini-rgb1080.mjpeg')
BASE = Path(__file__).resolve().parent
WIDTH, HEIGHT = 640, 360
PERIOD_NS = 1_000_000_000 // 15
MAX_POSE_AGE_NS = 1_100_000_000
PIPELINE = (
    'appsrc name=input is-live=true format=time block=false max-buffers=1 leaky-type=downstream '
    'caps=image/jpeg,width=1920,height=1080,framerate=15/1 ! jpegparse ! nvjpegdec ! '
    'nvvidconv ! video/x-raw(memory:NVMM),format=NV12,width=640,height=360 ! '
    'nvv4l2h264enc bitrate=1200000 control-rate=1 preset-level=1 num-B-Frames=0 '
    'iframeinterval=8 idrinterval=8 insert-sps-pps=true copy-timestamp=true ! '
    'h264parse config-interval=-1 ! video/x-h264,stream-format=byte-stream,alignment=au ! '
    'appsink name=output sync=false max-buffers=6 drop=true'
)


class FramePose:
    def __init__(self):
        color = json.loads((Path.home() / 'orbbec345lg-v2.10.6/rgb1080-calibration.json').read_text())['color']
        self.original_k = np.asarray(color['k']).reshape(3, 3)
        self.distortion = np.asarray(color['d'])
        self.original_size = np.array([color['width'], color['height']])
        intrinsics, _ = native_color_geometry()
        self.inverse_k = np.linalg.inv(np.asarray(intrinsics['k']).reshape(3, 3))
        self.packets = deque(maxlen=20)
        self.notice = None
        self.anchor = 0
        self.last_gray = None
        self.tracks = []
        self.flow_stamp = 0

    def update(self, message):
        try:
            self.notice = json.loads(message.data)
        except ValueError:
            pass

    @staticmethod
    def gray(jpeg):
        return cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_REDUCED_GRAYSCALE_4)

    def project(self, pixels):
        rays = np.column_stack((pixels, np.ones(len(pixels)))) @ self.inverse_k.T
        uv, _ = cv2.projectPoints(rays, np.zeros(3), np.zeros(3), self.original_k, self.distortion)
        return ((uv.reshape(-1, 2) + .5) * np.array([WIDTH, HEIGHT]) / self.original_size - .5).astype(np.float32)

    def reseed(self, state, source_stamp, current_stamp):
        self.anchor = source_stamp
        self.tracks = []
        if not state.get('tracks') or current_stamp - source_stamp > MAX_POSE_AGE_NS:
            return
        stamp, jpeg = min(self.packets, key=lambda packet: abs(packet[0] - source_stamp))
        if abs(stamp - source_stamp) > 38_000_000:
            return
        self.last_gray = self.gray(jpeg)
        self.flow_stamp = stamp
        if self.last_gray is None:
            return
        for item in state['tracks'][:5]:
            pose = np.asarray(item.get('pose'), dtype=np.float32)
            if pose.shape != (33, 5) or not np.isfinite(pose).all():
                continue
            box = np.asarray(item.get('bbox'), dtype=np.float32)
            if box.shape != (4,) or not np.isfinite(box).all():
                continue
            pose[:, :2] = self.project(pose[:, :2])
            xyz = item.get('xyz')
            track = dict(id=item['id'], bbox=self.project(box.reshape(2, 2)).ravel(), pose=pose,
                         pose_action=item.get('pose_action', 'neutral'),
                         xyz=xyz if xyz and np.isfinite(xyz).all() else None)
            self.tracks.append(track)

    def flow(self, stamp, jpeg):
        next_gray = self.gray(jpeg)
        if next_gray is None:
            self.tracks = []
            return
        scale = np.array([next_gray.shape[1] / WIDTH, next_gray.shape[0] / HEIGHT], dtype=np.float32)
        tracked = []
        for track in self.tracks:
            pose = track['pose']
            visible = (pose[:, 3:5] >= .5).all(axis=1)
            previous = (pose[visible, :2] * scale).reshape(-1, 1, 2)
            if len(previous) < 4:
                continue
            next_points, ok, _ = cv2.calcOpticalFlowPyrLK(self.last_gray, next_gray, previous, None,
                                                         winSize=(17,17), maxLevel=2)
            if next_points is None:
                continue
            back, back_ok, _ = cv2.calcOpticalFlowPyrLK(next_gray, self.last_gray, next_points, None,
                                                       winSize=(17,17), maxLevel=2)
            if back is None:
                continue
            keep = (ok.ravel() == 1) & (back_ok.ravel() == 1)
            keep &= np.linalg.norm((back - previous).reshape(-1, 2), axis=1) < 2.0
            if np.count_nonzero(keep) < 4:
                continue
            joints = np.flatnonzero(visible)
            pose[joints[~keep], 3:5] = 0
            points = next_points[keep, 0] / scale
            displacement = np.median(points - pose[joints[keep], :2], axis=0)
            pose[joints[keep], :2] = points
            track['bbox'] += np.tile(displacement, 2)
            tracked.append(track)
        self.tracks = tracked
        self.last_gray = next_gray
        self.flow_stamp = stamp

    def for_frame(self, stamp, jpeg):
        self.packets.append((stamp, jpeg))
        if self.notice is not None:
            state = self.notice
            sec, nsec = state.get('source_stamp', (0, 0))
            source_stamp = sec * 1_000_000_000 + nsec
            if source_stamp <= stamp:
                self.notice = None
                if source_stamp > self.anchor:
                    self.reseed(state, source_stamp, stamp)
        if stamp - self.anchor > MAX_POSE_AGE_NS:
            self.tracks = []
        if not self.tracks:
            return b''
        # Catch up an inference result through the actual camera images. Do not
        # associate old joint positions with a new frame by timestamp alone.
        for frame_stamp, image in self.packets:
            if self.tracks and frame_stamp > self.flow_stamp and (
                    frame_stamp == stamp or frame_stamp - self.flow_stamp >= 95_000_000):
                self.flow(frame_stamp, image)
        if not self.tracks:
            return b''
        tracks = []
        for item in self.tracks:
            pose = item['pose']
            entry = {**item, 'pose': pose.round(2).tolist(), 'bbox': item['bbox'].round(2).tolist()}
            if (pose[[23, 24], 3:5] >= .5).all():
                entry['hip_center'] = pose[[23, 24], :2].mean(axis=0).round(2).tolist()
            tracks.append(entry)
        return json.dumps(tracks, separators=(',', ':')).encode()


def dds_writer():
    lib = ct.CDLL(str(BASE / 'build/libfollow_media.so'))
    lib.media_open.argtypes = [ct.c_char_p, ct.c_char_p, ct.c_bool]
    lib.media_open.restype = ct.c_void_p
    lib.media_matched.argtypes = [ct.c_void_p]
    lib.media_matched.restype = ct.c_int
    lib.media_close.argtypes = [ct.c_void_p]
    lib.media_write.argtypes = [ct.c_void_p, ct.c_uint64, ct.c_uint32, ct.c_bool,
                               ct.c_char_p, ct.c_uint32, ct.c_char_p, ct.c_uint32]
    lib.media_write.restype = ct.c_bool
    endpoint = lib.media_open(b'192.168.144.108', b'192.168.144.11', True)
    if not endpoint:
        raise RuntimeError('Fast DDS UDP writer could not bind to the GR01 LAN')
    return lib, endpoint


def main():
    cv2.setNumThreads(1)
    Gst.init(None)
    rclpy.init()
    node = rclpy.create_node('g20_h264_preview')
    overlay = FramePose()
    node.create_subscription(String, '/vision/body_tracking/status', overlay.update,
                             QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT))
    lib, endpoint = dds_writer()
    pipeline = Gst.parse_launch(PIPELINE)
    appsrc, sink = pipeline.get_by_name('input'), pipeline.get_by_name('output')
    bus = pipeline.get_bus()
    base = time.time_ns() - 1_000_000_000
    poses = {}
    previous_file, next_frame, sequence = 0, 0, 0
    sent, errors, report_at = 0, 0, time.monotonic()
    active = False
    print('Ready: Fast DDS UDP unicast 192.168.144.108 -> 192.168.144.11', flush=True)
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0)
            if lib.media_matched(endpoint) == 0:
                if active:
                    pipeline.set_state(Gst.State.NULL)
                    active = False
                    poses.clear()
                    overlay.packets.clear()
                    overlay.tracks = []
                time.sleep(.09)
                continue
            if not active:
                pipeline.set_state(Gst.State.PLAYING)
                active = True
            error = bus.pop_filtered(Gst.MessageType.ERROR)
            if error is not None:
                raise RuntimeError(str(error.parse_error()))
            sample = sink.emit('try-pull-sample', 0)
            while sample is not None:
                buffer = sample.get_buffer()
                segment = sample.get_segment()
                pts = segment.to_running_time(Gst.Format.TIME, buffer.pts)
                stamp = int(pts) + base
                seq, pose = poses.pop(stamp, (0, b''))
                if seq:
                    data = buffer.extract_dup(0, buffer.get_size())
                    keyframe = not buffer.has_flags(Gst.BufferFlags.DELTA_UNIT)
                    sent += bool(lib.media_write(endpoint, stamp, seq, keyframe, data, len(data), pose, len(pose)))
                else:
                    if errors == 0:
                        print(f'Unmatched timestamp: pts={buffer.pts} segment_start={segment.start} '
                              f'running={pts} expected={next(iter(poses), 0) - base}', flush=True)
                    errors += 1
                sample = sink.emit('try-pull-sample', 0)
            try:
                modified = CAMERA.stat().st_mtime_ns
                if modified != previous_file:
                    previous_file = modified
                    packet = CAMERA.read_bytes()
                    stamp = struct.unpack_from('<Q', packet)[0]
                    if stamp >= max(base, next_frame - 3_000_000):
                        next_frame = stamp + PERIOD_NS
                        sequence += 1
                        jpeg = packet[8:]
                        poses[stamp] = (sequence, overlay.for_frame(stamp, jpeg))
                        while len(poses) > 12:
                            del poses[next(iter(poses))]
                        buffer = Gst.Buffer.new_wrapped(jpeg)
                        buffer.pts = buffer.dts = stamp - base
                        buffer.duration = PERIOD_NS
                        if appsrc.emit('push-buffer', buffer) != Gst.FlowReturn.OK:
                            raise RuntimeError('Hardware encoder input rejected frame')
            except FileNotFoundError:
                pass
            now = time.monotonic()
            if now - report_at >= 5:
                print(f'NVENC sent_fps={sent / (now-report_at):.2f} sequence={sequence} unmatched_pts={errors}', flush=True)
                sent, errors, report_at = 0, 0, now
            time.sleep(.006)
    finally:
        pipeline.set_state(Gst.State.NULL)
        lib.media_close(endpoint)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
