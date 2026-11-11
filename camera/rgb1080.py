"""Publish the Gemini's native MJPEG frames, with on-demand raw compatibility."""
import fcntl
import json
import os
from pathlib import Path
from queue import Empty, Full, Queue
import struct
import threading
import time

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, CompressedImage, Image
from std_msgs.msg import Header
from orbbec_camera_msgs.msg import Extrinsics
from omnifleet_hikrobot_rgbd.local_frames import native_color_geometry, rectify_native_color


def supports_mjpeg(device):
    try:
        with device.open('rb', buffering=0) as handle:
            index = 0
            while True:
                entry = bytearray(64)
                struct.pack_into('II', entry, 0, index, 1)  # V4L2_BUF_TYPE_VIDEO_CAPTURE
                fcntl.ioctl(handle, 0xc0405602, entry, True)  # VIDIOC_ENUM_FMT
                if entry[44:48] == b'MJPG':
                    return True
                index += 1
    except OSError:
        return False


def find_rgb_device(configured, serial):
    video_class = Path('/sys/class/video4linux')
    devices = [Path(configured), *[Path('/dev') / path.name for path in sorted(video_class.glob('video*'))]]
    for device in devices:
        try:
            name = device.resolve(strict=True).name
            interface = (video_class / name / 'device').resolve(strict=True)
            serial_file = next((p / 'serial' for p in (interface, *interface.parents)
                                if (p / 'serial').is_file()), None)
            if serial_file and serial_file.read_text().strip() == serial and supports_mjpeg(device):
                return device
        except OSError:
            continue
    raise RuntimeError(f'No MJPEG capture interface found for Gemini serial {serial}')


def watch_streams(closed, progress):
    while not closed.wait(1.0):
        now = time.monotonic()
        stale = [name for name, timestamp in progress.items() if now - timestamp > 8.0]
        if stale:
            print('Gemini RGB watchdog: no frame progress on ' + ', '.join(stale), flush=True)
            os._exit(1)  # The ROS launch respawns this RGB child; depth stays up.


def capture_stamp(camera, node):
    source_ms = camera.get(cv2.CAP_PROP_POS_MSEC)
    delay_ms = time.monotonic_ns() / 1e6 - source_ms
    now = node.get_clock().now().nanoseconds
    if 0 <= delay_ms < 1000:
        return now - int(delay_ms * 1e6), 'V4L2 monotonic timestamp'
    if abs(now / 1e6 - source_ms) < 1000:
        return int(source_ms * 1e6), 'V4L2 wall timestamp'
    return now, 'timestamp at capture dequeue'


def preview_worker(jobs, closed, compressed, raw, color, progress):
    raw_next = 0.
    while not closed.is_set():
        try:
            header, jpeg = jobs.get(timeout=.2)
        except Empty:
            continue
        data = np.frombuffer(jpeg, np.uint8)
        small = cv2.imdecode(data, cv2.IMREAD_REDUCED_COLOR_2)
        if small is not None:
            small = rectify_native_color(small, (640, 360))
            ok, output = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, 65])
            if ok:
                compressed.publish(CompressedImage(header=header, format='jpeg', data=output.tobytes()))
                progress['JPEG preview'] = time.monotonic()
        now = time.monotonic()
        if now >= raw_next and raw.get_subscription_count():
            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if frame is not None:
                frame = rectify_native_color(frame)
                raw.publish(Image(header=header, height=color['height'], width=color['width'],
                                  encoding='bgr8', step=color['width'] * 3, data=frame.tobytes()))
            raw_next = now + .1



def main():
    cv2.setNumThreads(1)
    config = json.loads(Path(__file__).with_name('rgb1080-calibration.json').read_text())
    color, _ = native_color_geometry()
    rclpy.init()
    node = Node('gemini345lg_native_color')
    compressed = node.create_publisher(CompressedImage, '/camera/color/image_raw/compressed', 1)
    raw = node.create_publisher(Image, '/camera/color/image_raw', qos_profile_sensor_data)
    info = node.create_publisher(CameraInfo, '/camera/color/camera_info', qos_profile_sensor_data)
    notices = node.create_publisher(Header, '/camera/color/native1080', qos_profile_sensor_data)
    transforms = StaticTransformBroadcaster(node)
    extrinsics = node.create_publisher(Extrinsics, '/camera/depth_to_color',
        QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    frame_file = Path('/dev/shm/omnifleet-gemini-rgb1080.mjpeg')
    pending_file = frame_file.with_suffix('.part')
    frame_file.unlink(missing_ok=True)
    pending_file.unlink(missing_ok=True)
    jobs = Queue(maxsize=1)
    closed = threading.Event()
    progress = dict.fromkeys(('native capture', 'JPEG preview'), time.monotonic())
    worker = threading.Thread(target=preview_worker,
                              args=(jobs, closed, compressed, raw, color, progress), daemon=True)
    watchdog = threading.Thread(target=watch_streams, args=(closed, progress), daemon=True)
    worker.start()
    watchdog.start()
    camera = None
    try:
        device = find_rgb_device(config['device'], config['device_serial'])
        camera = cv2.VideoCapture(str(device), cv2.CAP_V4L2)
        if not camera.isOpened():
            raise RuntimeError(f'Unable to open Gemini RGB device {device}')
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, color['width'])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, color['height'])
        camera.set(cv2.CAP_PROP_FPS, 30)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not camera.set(cv2.CAP_PROP_CONVERT_RGB, 0):
            raise RuntimeError("Unable to request native MJPEG packets")
        reported = False
        while rclpy.ok():
            ok, data = camera.read()
            if not ok:
                raise RuntimeError('Gemini stopped delivering native MJPEG frames')
            if data.ndim != 2 or data.shape[0] != 1 or data[0, 0] != 0xff or data[0, 1] != 0xd8:
                raise RuntimeError('Gemini did not negotiate raw MJPEG packets')
            stamp, clock = capture_stamp(camera, node)
            header = Header(frame_id=color['frame_id'])
            header.stamp.sec, header.stamp.nanosec = divmod(stamp, 1_000_000_000)
            jpeg = data.tobytes()
            end = jpeg.rfind(b'\xff\xd9')
            if end < 0:
                continue
            jpeg = jpeg[:end + 2]
            if not reported:
                frame = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
                if frame is None or frame.shape[:2] != (color['height'], color['width']):
                    raise RuntimeError('Gemini MJPEG did not match its 1080p calibration')
                node.get_logger().info(f"Native MJPEG {color['width']}x{color['height']} at {camera.get(cv2.CAP_PROP_FPS):.0f} FPS; {clock}")
                transform = config['extrinsics']
                extrinsics.publish(Extrinsics(header=Header(frame_id=transform['frame_id'], stamp=header.stamp),
                    rotation=transform['rotation'], translation=transform['translation']))
                optical = config['color_tf']
                tf = TransformStamped(header=Header(frame_id=optical['parent'], stamp=header.stamp),
                                      child_frame_id=optical['child'])
                tf.transform.translation.x, tf.transform.translation.y, tf.transform.translation.z = optical['translation']
                tf.transform.rotation.x, tf.transform.rotation.y, tf.transform.rotation.z, tf.transform.rotation.w = optical['quaternion']
                transforms.sendTransform(tf)
                reported = True
            with pending_file.open('wb') as out:
                out.write(struct.pack('<Q', stamp))
                out.write(jpeg)
            pending_file.replace(frame_file)
            info.publish(CameraInfo(header=header, **{key: value for key, value in color.items() if key != 'frame_id'}))
            notices.publish(header)
            progress['native capture'] = time.monotonic()
            try:
                jobs.put_nowait((header, jpeg))
            except Full:
                try:
                    jobs.get_nowait()
                except Empty:
                    pass
                jobs.put_nowait((header, jpeg))
    finally:
        closed.set()
        watchdog.join(timeout=2.)
        worker.join(timeout=2.)
        if camera is not None:
            camera.release()
        frame_file.unlink(missing_ok=True)
        pending_file.unlink(missing_ok=True)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
