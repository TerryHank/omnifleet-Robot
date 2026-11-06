#!/usr/bin/env python3
"""Publish synchronized MV-DT01SNU RGB, native depth and registered depth."""

from __future__ import annotations

import array
import ctypes
import json
import os
import re
import signal
import struct
import sys
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import cv2
import numpy as np
cv2.setNumThreads(1)


def planar_rgb_to_bgr(data: bytes, width: int, height: int) -> np.ndarray:
    pixels = width * height
    planes = np.frombuffer(data, dtype=np.uint8, count=pixels * 3).reshape(3, height, width)
    return np.stack((planes[2], planes[1], planes[0]), axis=-1)


def depth_c16(data: bytes, width: int, height: int) -> np.ndarray:
    """Coord3D_C16; the caller applies the device's millimetres-per-count."""
    return np.frombuffer(data, dtype="<u2", count=width * height).reshape(height, width)


def scaled_intrinsics(fx, fy, cx, cy, source_width, source_height, width, height):
    sx, sy = width / source_width, height / source_height
    return fx * sx, fy * sy, cx * sx, cy * sy


def rgb_chunk(data: bytes):
    """The DT01 RGB chunk has a 32-byte header followed by RGB8Planar."""
    if len(data) < 32:
        raise ValueError("truncated RGB chunk header")
    pixel, width, height, length = struct.unpack_from("<4I", data)
    if pixel != 0x02180021 or length != width * height * 3 or len(data) != length + 32:
        raise ValueError("unexpected RGB8Planar chunk format or length")
    return memoryview(data)[32:], width, height


def load_calibration(path, serial):
    """Read camera-exported factory XML, using rectified DepthMode intrinsics."""
    root = ET.parse(path).getroot()
    if root.find("MatchCamSN").get("value") != serial:
        raise ValueError("factory calibration serial differs from camera serial")
    entry = root.find("RGBD_MAX")

    def matrix(name):
        v = entry.find(name + "/Intrins").attrib
        return np.array([[float(v["fx"]), 0., float(v["cx"])],
                         [0., float(v["fy"]), float(v["cy"])], [0., 0., 1.]])

    transform = np.eye(4)
    rotation = entry.find("Left_correct_2_RGB/RotMat").attrib
    translation = entry.find("Left_correct_2_RGB/TVec").attrib
    for row in range(3):
        for col in range(3):
            transform[row, col] = float(rotation[f"r{row}{col}"])
        transform[row, 3] = float(translation[f"t{row}"]) * 0.001
    color = entry.find("RGB_Camera")
    depth = entry.find("Camera")
    return (matrix("Left_correct"), matrix("RGB_correct"), transform,
            (int(depth.get("img_w")), int(depth.get("img_h"))),
            (int(color.get("img_w")), int(color.get("img_h"))))


def register_depth(depth, depth_k, color_k, depth_to_color, color_size):
    # Keep holes/occlusions invalid instead of inventing distances.
    valid_depth = depth.copy()
    valid_depth[valid_depth == 65535] = 0
    return cv2.rgbd.registerDepth(depth_k, color_k, None, depth_to_color,
                                  valid_depth, color_size, depthDilation=False)


def colorize_depth(depth):
    """Display 0-1.5 m using JET; leave invalid samples black, without changing depth."""
    scaled = cv2.convertScaleAbs(np.minimum(depth, 1500), alpha=255. / 1500.)
    color = cv2.applyColorMap(scaled, cv2.COLORMAP_JET)
    color[(depth == 0) | (depth == 65535)] = 0
    return color


class HikrobotCamera:
    """Fetch a DepthMode frame with its matching RGBImage chunk via MVS U3V."""

    def __init__(self, vendor_python_path, serial_number, timeout_ms, exposure, gain, depth_exposure=0., color_exposure_mode="DynamicMode", depth_exposure_mode="SingleMode", gap_fill_class=None, range_filter_class=None, depth_auto_exposure_max_us=500):
        os.environ.setdefault("MVCAM_COMMON_RUNENV", "/opt/MVS/lib")
        sys.path.insert(0, str(Path(vendor_python_path) / "MvImport"))
        import MvCameraControl_class as mvs

        self.mvs = mvs
        self.camera = mvs.MvCamera()
        self.running = False
        self.timeout_ms = timeout_ms
        mvs.MvCamera.MV_CC_Initialize()
        devices = mvs.MV_CC_DEVICE_INFO_LIST()
        self.check(mvs.MvCamera.MV_CC_EnumDevices(mvs.MV_USB_DEVICE, devices), "enumerate")
        selected = None
        for index in range(devices.nDeviceNum):
            info = ctypes.cast(devices.pDeviceInfo[index], ctypes.POINTER(mvs.MV_CC_DEVICE_INFO)).contents
            found = bytes(info.SpecialInfo.stUsb3VInfo.chSerialNumber).split(b"\0", 1)[0].decode()
            if not serial_number or found == serial_number:
                selected = info
                break
        if selected is None:
            raise RuntimeError(f"MV-DT01SNU {serial_number!r} was not found")
        self.check(self.camera.MV_CC_CreateHandle(selected), "create handle")
        self.check(self.camera.MV_CC_OpenDevice(mvs.MV_ACCESS_Exclusive, 0), "open")
        for key, value in [("CameraWorkingMode", "DepthMode"), ("ImageMode", "Depth"),
                           ("RGBDAlignCoord", "UnAlign"), ("TriggerMode", "Off")]:
            self.check(self.camera.MV_CC_SetEnumValueByString(key, value), key)
        self.check(self.camera.MV_CC_SetBoolValue("DepthRectifyEnable", True), "depth rectify")
        self.check(self.camera.MV_CC_SetBoolValue("ChunkModeActive", True), "chunks")
        for name in ["TimeStamp", "RGBImage"]:
            self.check(self.camera.MV_CC_SetEnumValueByString("ChunkSelector", name), name)
            self.check(self.camera.MV_CC_SetBoolValue("ChunkEnable", True), name + " enable")
        self.check(self.camera.MV_CC_SetEnumValueByString("ColorExposureModeSelector", color_exposure_mode), "RGB exposure mode")
        if color_exposure_mode == "SingleMode":
            for key, value in [("ColorExposureTime", exposure), ("ColorGain", gain)]:
                self.check(self.camera.MV_CC_SetFloatValue(key, value), key)
        self.check(self.camera.MV_CC_SetEnumValueByString("ExposureModeSelector", depth_exposure_mode), "depth exposure mode")
        if depth_exposure_mode == 'DynamicMode':
            self.check(self.camera.MV_CC_SetIntValueEx('StereoAutoExposureTimeUpperLimit',int(depth_auto_exposure_max_us)), 'depth auto exposure limit')
        elif depth_exposure > 0:
            self.check(self.camera.MV_CC_SetFloatValue("ExposureTime", depth_exposure), "depth exposure")
        for key, value in [('GapFillClass',gap_fill_class),('RangeFilterClass',range_filter_class)]:
            if value is not None:
                self.check(self.camera.MV_CC_SetEnumValueByString(key,value),key)
        rate = mvs.MVCC_FLOATVALUE()
        if self.camera.MV_CC_GetFloatValue("AcquisitionFrameRate", rate) == 0:
            self.camera.MV_CC_SetBoolValue("AcquisitionFrameRateEnable", True)
            requested_rate = float(int(rate.fMax))
            rc = self.camera.MV_CC_SetFloatValue("AcquisitionFrameRate", requested_rate)
            print(f"MV-DT01SNU maximum frame-rate request={requested_rate} rc=0x{rc & 0xffffffff:08x}", flush=True)
        unit = mvs.MVCC_FLOATVALUE()
        self.check(self.camera.MV_CC_GetFloatValue("LSLProfileCoordZUnit", unit), "depth unit")
        self.depth_unit_mm = float(unit.fCurValue)
        features = {}
        for kind, names in [
            ("bool", ["LaserEnable", "DepthRectifyEnable", "NoiseFilterEnable", "RangeFilterEnable"]),
            ("float", ["ExposureTime", "Gain", "ColorExposureTime", "ColorGain", "AcquisitionFrameRate", "ResultingFrameRate"]),
            ("enum", ["CameraWorkingMode", "ImageMode", "DepthType", "ColorExposureModeSelector", "ExposureModeSelector", "ExposureAuto", "DepthFilterMode", "NoiseFilterType"]),
        ]:
            for name in names:
                value = {"bool": ctypes.c_bool, "float": mvs.MVCC_FLOATVALUE,
                         "enum": mvs.MVCC_ENUMVALUE}[kind]()
                getter = {"bool": self.camera.MV_CC_GetBoolValue,
                          "float": self.camera.MV_CC_GetFloatValue,
                          "enum": self.camera.MV_CC_GetEnumValue}[kind]
                rc = getter(name, value)
                features[name] = {"rc": hex(rc & 0xffffffff)}
                if rc == 0:
                    features[name]["value"] = (value.value if kind == "bool" else
                                               float(value.fCurValue) if kind == "float" else
                                               int(value.nCurValue))
                    if kind == "float":
                        features[name].update(min=float(value.fMin), max=float(value.fMax))
        diagnostic = Path("/home/iecme/omnifleet_data/camera_validation/mv_dt01snu_20261020/foxglove_3d/device_features.json")
        diagnostic.parent.mkdir(exist_ok=True)
        diagnostic.write_text(json.dumps(features, indent=2))
        print("MV-DT01SNU depth feature readback: " + json.dumps(features), flush=True)
        self.check(self.camera.MV_CC_SetGrabStrategy(mvs.MV_GrabStrategy_LatestImagesOnly), "latest frame strategy")
        self.check(self.camera.MV_CC_StartGrabbing(), "start grabbing")
        self.running = True

    @staticmethod
    def check(rc, operation):
        if rc:
            raise RuntimeError(f"{operation} failed: 0x{rc & 0xffffffff:08x}")

    def depth_settings(self):
        exposure, rate = self.mvs.MVCC_FLOATVALUE(), self.mvs.MVCC_FLOATVALUE()
        mode = self.mvs.MVCC_ENUMVALUE()
        self.check(self.camera.MV_CC_GetEnumValue('ExposureModeSelector',mode), 'read depth exposure mode')
        automatic = int(mode.nCurValue)==1
        if automatic:
            upper = self.mvs.MVCC_INTVALUE_EX()
            self.check(self.camera.MV_CC_GetIntValueEx('StereoAutoExposureTimeUpperLimit',upper), 'read depth auto exposure limit')
            current, minimum, maximum = None, float(upper.nMin), float(upper.nMax)
        else:
            self.check(self.camera.MV_CC_GetFloatValue('ExposureTime', exposure), 'read depth exposure')
            current, minimum, maximum = float(exposure.fCurValue),float(exposure.fMin),float(exposure.fMax)
        self.check(self.camera.MV_CC_GetFloatValue('AcquisitionFrameRate', rate), 'read frame rate')
        color_mode = self.mvs.MVCC_ENUMVALUE()
        self.check(self.camera.MV_CC_GetEnumValue('ColorExposureModeSelector', color_mode), 'read RGB exposure mode')
        result = dict(depth_exposure_time_us=current,depth_auto_exposure=automatic,
                    depth_exposure_mode='DynamicMode' if automatic else 'SingleMode',
                    depth_auto_exposure_max_us=int(upper.nCurValue) if automatic else None,
                    depth_exposure_min_us=minimum,depth_exposure_max_us=maximum,
                    acquisition_frame_rate=float(rate.fCurValue),max_frame_rate=float(rate.fMax),
                    rgb_auto_exposure=int(color_mode.nCurValue)==1)
        for key in ('GapFillEnable','RangeFilterEnable'):
            value = ctypes.c_bool()
            self.check(self.camera.MV_CC_GetBoolValue(key,value),key)
            result[key] = value.value
        for key in ('GapFillClass','RangeFilterClass'):
            value = self.mvs.MVCC_ENUMVALUE()
            self.check(self.camera.MV_CC_GetEnumValue(key,value),key)
            result[key] = int(value.nCurValue)
        return result

    def set_depth_exposure(self, value, mode='SingleMode'):
        old = self.depth_settings()
        old_mode = old.get('depth_exposure_mode','SingleMode')
        # The firmware locks the automatic limit while grabbing, even when
        # the exposure mode itself stays DynamicMode.
        restart = (mode != old_mode or mode == 'DynamicMode') and self.running
        if restart:
            self.check(self.camera.MV_CC_StopGrabbing(),'pause stream for exposure mode switch')
            self.running = False
        try:
            if mode != old_mode:
                self.check(self.camera.MV_CC_SetEnumValueByString('ExposureModeSelector',mode),'set depth exposure mode')
            if mode == 'DynamicMode':
                self.check(self.camera.MV_CC_SetIntValueEx('StereoAutoExposureTimeUpperLimit',int(value)), 'set depth auto exposure limit')
            else:
                self.check(self.camera.MV_CC_SetFloatValue('ExposureTime', value), 'set depth exposure')
            rate = self.mvs.MVCC_FLOATVALUE()
            self.check(self.camera.MV_CC_GetFloatValue('AcquisitionFrameRate', rate), 'read new frame rate range')
            self.check(self.camera.MV_CC_SetFloatValue('AcquisitionFrameRate', float(min(30,int(rate.fMax)))), 'set frame rate')
            return self.depth_settings()
        except Exception:
            if mode != old_mode:
                self.camera.MV_CC_SetEnumValueByString('ExposureModeSelector',old_mode)
            if old_mode == 'DynamicMode':
                self.camera.MV_CC_SetIntValueEx('StereoAutoExposureTimeUpperLimit',old['depth_auto_exposure_max_us'])
            else:
                self.camera.MV_CC_SetFloatValue('ExposureTime',old['depth_exposure_time_us'])
            self.camera.MV_CC_SetFloatValue('AcquisitionFrameRate',old['acquisition_frame_rate'])
            raise
        finally:
            if restart:
                self.check(self.camera.MV_CC_StartGrabbing(),'resume stream after exposure mode switch')
                self.running = True

    def fetch(self):
        frame = self.mvs.MV_FRAME_OUT()
        self.check(self.camera.MV_CC_GetImageBuffer(frame, self.timeout_ms), "fetch RGB-D")
        try:
            info = frame.stFrameInfo
            if info.enPixelType != 0x011000b8:
                raise ValueError("expected Coord3D_C16 primary depth image")
            depth = ctypes.string_at(frame.pBufAddr, int(info.nWidth)*int(info.nHeight)*2)
            color = None
            for index in range(info.nUnparsedChunkNum):
                chunk = info.UnparsedChunkList.pUnparsedChunkContent[index]
                if chunk.nChunkID == 0xa5a53d0b:
                    color = rgb_chunk(ctypes.string_at(chunk.pChunkData, chunk.nChunkLen))
                    break
            if color is None:
                raise ValueError("RGBImage chunk absent from depth frame")
            return (depth, int(info.nWidth), int(info.nHeight), color, int(info.nFrameNum),
                    (int(info.nDevTimeStampHigh) << 32) | int(info.nDevTimeStampLow))
        finally:
            self.camera.MV_CC_FreeImageBuffer(frame)

    def close(self):
        if self.camera is not None:
            if self.running:
                self.camera.MV_CC_StopGrabbing()
                self.running = False
            self.camera.MV_CC_CloseDevice()
            self.camera.MV_CC_DestroyHandle()
            self.camera = None


def main(args=None):
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from rclpy.signals import SignalHandlerOptions
    from sensor_msgs.msg import CameraInfo, CompressedImage, Image
    from std_msgs.msg import String
    from omnifleet_hikrobot_rgbd.local_frames import LocalFrameWriter

    class CameraNode(Node):
        def __init__(self):
            super().__init__("mv_dt01snu_camera")
            p = lambda name, default: self.declare_parameter(name, default).value
            serial = str(p("serial_number", "DB0993529"))
            calibration = str(p("calibration_file", ""))
            self.dk, self.ck, self.rt, self.depth_size, self.color_size = load_calibration(calibration, serial)
            self.output_size = (int(p("output_color_width", self.color_size[0])), int(p("output_color_height", self.color_size[1])))
            self.ck[0, :] *= self.output_size[0] / self.color_size[0]
            self.ck[1, :] *= self.output_size[1] / self.color_size[1]
            self.color_frame = str(p("color_frame_id", "camera_color_optical_frame"))
            self.depth_frame = str(p("depth_frame_id", "camera_depth_optical_frame"))
            self.stream_publishers = {}
            for key, topic, sdk_topic in [
                ("color", "/camera/color/image_raw", "rgb/image_raw"),
                ("depth", "/camera/depth/image_raw", "depth/image_raw"),
                ("aligned_depth", "/camera/aligned_depth_to_color/image_raw", "aligned_depth_to_color/image_raw"),
                ("color_info", "/camera/color/camera_info", "rgb/camera_info"),
                ("depth_info", "/camera/depth/camera_info", "depth/camera_info"),
                ("aligned_depth_info", "/camera/aligned_depth_to_color/camera_info", "aligned_depth_to_color/camera_info")]:
                message_type = CameraInfo if key.endswith("info") else Image
                self.stream_publishers[key] = [
                    self.create_publisher(message_type, str(p(key + "_topic", topic)), qos_profile_sensor_data),
                    self.create_publisher(message_type, sdk_topic, qos_profile_sensor_data)]
            self.stream_publishers["depth_color"] = [
                self.create_publisher(Image, "depth/image_color", qos_profile_sensor_data)]
            self.color_compressed = self.create_publisher(
                CompressedImage, str(self.get_parameter("color_topic").value) + "/compressed", qos_profile_sensor_data)
            self.status = self.create_publisher(String, "/camera/rgbd/status", 10)
            self.local_frame_pub = self.create_publisher(String,'/camera/rgbd/local_frame',qos_profile_sensor_data)
            self.local_frame_writer = None
            self.device_args = (str(p("vendor_python_path", "/opt/MVS/Samples/aarch64/Python")),
                                serial, int(p("grab_timeout_ms", 2000)),
                                float(p("color_exposure_time_us", 16500.)), float(p("color_gain", 23.7)),
                                float(p("depth_exposure_time_us", 0.)),
                                str(p("color_exposure_mode", "DynamicMode")),
                                str(p("depth_exposure_mode", "SingleMode")),
                                str(p("depth_gap_fill_class", "Normal")),
                                str(p("depth_range_filter_class", "Normal")),
                                int(p("depth_auto_exposure_max_us",500)))
            self.device = HikrobotCamera(*self.device_args)
            self.camera_settings = self.device.depth_settings()
            self.control_lock, self.pending_control = threading.Lock(), None
            self.last_control = None
            self.create_subscription(String,'/camera/rgbd/control',self.camera_control,10)
            self.stop_event = threading.Event()
            self.worker = threading.Thread(target=self.run, name="mv_dt01snu_capture", daemon=True)
            self.worker.start()
            self.get_logger().info(f"MV-DT01SNU {serial}: same-frame RGB + depth; calibration={calibration}")

        def camera_control(self, message):
            try:
                request = json.loads(message.data)
                mode = str(request.get('depth_exposure_mode','SingleMode'))
                value = float(request['depth_auto_exposure_max_us' if mode=='DynamicMode' else 'depth_exposure_time_us'])
                if not np.isfinite(value):
                    raise ValueError('Depth exposure must be finite')
                with self.control_lock:
                    self.pending_control = dict(id=request.get('id'),value=value,mode=mode,persist=bool(request.get('persist',False)))
            except Exception as error:
                self.last_control = dict(id=None,success=False,error=str(error))

        def apply_camera_control(self):
            with self.control_lock:
                request, self.pending_control = self.pending_control, None
            if request is None:
                return
            try:
                self.camera_settings = self.device.set_depth_exposure(request['value'],request['mode'])
                args = list(self.device_args)
                if request['mode']=='SingleMode':
                    args[5] = self.camera_settings['depth_exposure_time_us']
                else:
                    args[10] = self.camera_settings['depth_auto_exposure_max_us']
                args[7] = request['mode']
                self.device_args = tuple(args)
                if request['persist']:
                    from ament_index_python.packages import get_package_share_directory
                    config = (Path(get_package_share_directory('omnifleet_hikrobot_rgbd'))/'config/mv_dt01snu.yaml').resolve()
                    text = config.read_text()
                    value_key = 'depth_auto_exposure_max_us' if request['mode']=='DynamicMode' else 'depth_exposure_time_us'
                    for key,value in [('depth_exposure_mode',request['mode']),(value_key,self.camera_settings[value_key])]:
                        text, count = re.subn(r'(?m)^(\s*'+key+r':)\s*[^\n]*',lambda match:match[1]+' '+str(value),text)
                        if count != 1:
                            raise ValueError('Depth exposure configuration entry missing: '+key)
                    temporary = config.with_suffix('.yaml.tmp')
                    temporary.write_text(text)
                    temporary.replace(config)
                self.last_control = dict(id=request['id'],success=True,persisted=request['persist'],**self.camera_settings)
            except Exception as error:
                self.last_control = dict(id=request['id'],success=False,error=str(error))

        def publish_image(self, key, data, stamp, frame):
            publishers = [publisher for publisher in self.stream_publishers[key]
                          if publisher.get_subscription_count() > 0]
            if not publishers:
                return
            msg = Image()
            msg.header.stamp, msg.header.frame_id = stamp, frame
            msg.height, msg.width = data.shape[:2]
            msg.encoding = "bgr8" if data.ndim == 3 else "16UC1"
            msg.step = msg.width * (3 if data.ndim == 3 else 2)
            msg.data = array.array("B")
            msg.data.frombytes(memoryview(np.ascontiguousarray(data)).cast("B"))
            for publisher in publishers:
                publisher.publish(msg)

        def publish_info(self, key, stamp, frame, size, k):
            msg = CameraInfo()
            msg.header.stamp, msg.header.frame_id = stamp, frame
            msg.width, msg.height = size
            msg.k = k.ravel().tolist()
            msg.r = np.eye(3).ravel().tolist()
            msg.p = np.column_stack((k, np.zeros(3))).ravel().tolist()
            msg.distortion_model, msg.d = "plumb_bob", [0.] * 5
            for publisher in self.stream_publishers[key]:
                publisher.publish(msg)

        def run(self):
            failures = 0
            last_status = 0.
            while not self.stop_event.is_set() and rclpy.ok():
                try:
                    if self.device is None:
                        self.device = HikrobotCamera(*self.device_args)
                        self.camera_settings = self.device.depth_settings()
                    self.apply_camera_control()
                    payload, width, height, rgb, frame_number, device_ticks = self.device.fetch()
                    stamp = self.get_clock().now().to_msg()
                    color_payload, cw, ch = rgb
                    if (width, height) != self.depth_size or (cw, ch) != self.color_size:
                        raise ValueError("capture resolution differs from factory calibration")
                    depth = depth_c16(payload, width, height)
                    if self.device.depth_unit_mm != 1.:
                        depth = np.where(depth == 65535, 0, depth)
                        depth = np.clip(np.rint(depth * self.device.depth_unit_mm), 0, 65534).astype(np.uint16)
                    color = None
                    local_requested = self.local_frame_pub.get_subscription_count()
                    if local_requested or any(publisher.get_subscription_count() for publisher in self.stream_publishers['color']) or self.color_compressed.get_subscription_count():
                        color = planar_rgb_to_bgr(color_payload, cw, ch)
                        if self.output_size != (cw, ch):
                            color = cv2.resize(color, self.output_size, interpolation=cv2.INTER_AREA)
                    if local_requested:
                        if self.local_frame_writer is None:
                            self.local_frame_writer = LocalFrameWriter(color.shape,depth.shape)
                        notification = self.local_frame_writer.write(color,depth,stamp,frame_number)
                        notification['color_frame_id'] = self.color_frame
                        notification['depth_frame_id'] = self.depth_frame
                        self.local_frame_pub.publish(String(data=json.dumps(notification)))
                    aligned = None
                    if any(publisher.get_subscription_count() for publisher in self.stream_publishers["aligned_depth"]):
                        aligned = register_depth(depth, self.dk, self.ck, self.rt, self.output_size)
                    if color is not None:
                        self.publish_image("color", color, stamp, self.color_frame)
                    if color is not None and self.color_compressed.get_subscription_count():
                        ok, encoded = cv2.imencode('.jpg', color, [cv2.IMWRITE_JPEG_QUALITY, 90])
                        if ok:
                            compressed = CompressedImage()
                            compressed.header.stamp, compressed.header.frame_id = stamp, self.color_frame
                            compressed.format = 'jpeg'
                            compressed.data = array.array('B')
                            compressed.data.frombytes(memoryview(encoded).cast('B'))
                            self.color_compressed.publish(compressed)
                    self.publish_image("depth", depth, stamp, self.depth_frame)
                    if aligned is not None:
                        self.publish_image("aligned_depth", aligned, stamp, self.color_frame)
                    if any(publisher.get_subscription_count() for publisher in self.stream_publishers["depth_color"]):
                        self.publish_image("depth_color", colorize_depth(depth), stamp, self.depth_frame)
                    self.publish_info("color_info", stamp, self.color_frame, self.output_size, self.ck)
                    self.publish_info("depth_info", stamp, self.depth_frame, self.depth_size, self.dk)
                    self.publish_info("aligned_depth_info", stamp, self.color_frame, self.output_size, self.ck)
                    if time.monotonic() - last_status >= 1.:
                        self.status.publish(String(data=json.dumps({"frame_number": frame_number,
                            "device_timestamp_ticks": device_ticks, "synchronized_rgb_depth": True,
                            "depth_unit_mm": self.device.depth_unit_mm, "registration": "factory_depth_to_rgb",
                            **self.camera_settings,"last_control":self.last_control})))
                        last_status = time.monotonic()
                    failures = 0
                except Exception as error:
                    if not rclpy.ok() or self.stop_event.is_set():
                        return
                    self.get_logger().error(str(error))
                    failures += 1
                    if failures >= 3:
                        if self.device is not None:
                            self.device.close()
                        self.device = None
                        time.sleep(1.)
                        failures = 0
                    time.sleep(.2)

        def destroy_node(self):
            self.stop_event.set()
            if self.worker.is_alive():
                self.worker.join(timeout=4.)
            if self.device is not None:
                self.device.close()
            if self.local_frame_writer is not None:
                self.local_frame_writer.close()
            return super().destroy_node()

    # Stop acquisition before rclpy closes the transport used by its publishing thread.
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    node = CameraNode()
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
