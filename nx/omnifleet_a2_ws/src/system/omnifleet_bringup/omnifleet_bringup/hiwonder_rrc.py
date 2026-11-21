"""Serial transport for the F407 Ackermann firmware on chassis 121."""

import math
import struct
import threading
import time

import serial


HEADER = b"\xaa\x55"
MOTOR_FUNCTION = 3
ACKERMANN_COMMAND = 4
SBUS_FUNCTION = 9
SBUS_REPORT = struct.Struct('<16H4B')
WHEELBASE_MM = 224.92
REAR_TRACK_M = 0.21333


def crc8(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x8C if crc & 1 else 0)
    return crc


def motion_frame(vx_mm_s, steering_deg, yaw_mrad_s):
    if vx_mm_s == 0.0:
        radius_mm = (
            WHEELBASE_MM / math.tan(math.radians(steering_deg))
            if steering_deg else 0.0
        )
    else:
        radius_mm = 1000.0 * vx_mm_s / yaw_mrad_s if yaw_mrad_s else 0.0

    payload = struct.pack("<Bff", ACKERMANN_COMMAND, vx_mm_s, radius_mm)
    body = bytes((MOTOR_FUNCTION, len(payload))) + payload
    ratio = WHEELBASE_MM / radius_mm if radius_mm else 0.0
    estimate_deg = math.degrees(math.atan(ratio))
    estimate_deg = max(-60.0, min(60.0, estimate_deg))
    return HEADER + body + bytes((crc8(body),)), estimate_deg


class HiwonderRRC:
    def __init__(self, port, *, wheel_radius_m=0.050):
        if not math.isfinite(wheel_radius_m) or wheel_radius_m <= 0.0:
            raise ValueError("wheel_radius_m must be finite and positive")
        self.port = port
        self.wheel_circumference_m = math.tau * wheel_radius_m
        self._serial = None
        self._lock = threading.Lock()
        self._stopping = threading.Event()
        self._thread = threading.Thread(target=self._receive, daemon=True)
        self._steering_deg = 0.0
        self._feedback = None
        self._sbus_frame = None
        self.steering_center_angle = None
        self._center_reply = threading.Event()
        self._center_status = None
        self.speed_frame_count = 0
        self.ack_count = 0
        self.checksum_error_count = 0
        self.receive_error_count = 0
        self.last_speed_frame_time = None

    def create_receive_threading(self):
        self._thread.start()

    def _receive(self):
        while not self._stopping.is_set():
            port = serial.Serial(baudrate=115200, timeout=0.1, write_timeout=0.1,
                                 exclusive=True)
            port.port = self.port
            port.dtr = False
            port.rts = False
            try:
                port.open()
                with self._lock:
                    self._serial = port
                buffer = bytearray()
                while not self._stopping.is_set():
                    buffer.extend(port.read(port.in_waiting or 1))
                    self._consume(buffer)
            except (OSError, serial.SerialException):
                self.receive_error_count += 1
            finally:
                with self._lock:
                    self._serial = None
                    self._feedback = None
                    self._sbus_frame = None
                    port.close()
            self._stopping.wait(0.5)

    def _consume(self, buffer):
        while len(buffer) >= len(HEADER):
            start = buffer.find(HEADER)
            if start < 0:
                buffer[:] = buffer[-1:] if buffer[-1] == HEADER[0] else b""
                return
            del buffer[:start]
            if len(buffer) < 5:
                return
            end = 5 + buffer[3]
            if len(buffer) < end:
                return
            if crc8(buffer[2:end - 1]) != buffer[end - 1]:
                self.checksum_error_count += 1
                del buffer[0]
                continue
            if buffer[2] == 0:
                self._report(buffer[4:end - 1])
            elif buffer[2] == SBUS_FUNCTION and buffer[3] == SBUS_REPORT.size:
                with self._lock:
                    self._sbus_frame = SBUS_REPORT.unpack_from(buffer, 4)
            del buffer[:end]

    def _report(self, data):
        if len(data) == 5 and data[:3] == b"CTR":
            self._center_status = data[3]
            self.steering_center_angle = data[4] if data[3] == 0 else None
            self._center_reply.set()
            return
        if data == b"ROS\x04":
            self.ack_count += 1
            return
        if len(data) != 88 or not data.startswith(b"RRC\x01"):
            return
        battery_mv = struct.unpack_from("<H", data, 6)[0]
        left = struct.unpack_from("<f", data, 12)[0] * self.wheel_circumference_m
        right = -struct.unpack_from("<f", data, 32)[0] * self.wheel_circumference_m
        if not (math.isfinite(left) and math.isfinite(right)):
            self.receive_error_count += 1
            return
        counts = tuple(struct.unpack_from("<i", data, offset)[0]
                       for offset in (24, 44, 64, 84))
        vx = (left + right) / 2.0
        wz = (right - left) / REAR_TRACK_M
        with self._lock:
            self._feedback = (vx, self._steering_deg, wz, counts, battery_mv / 1000.0)
            self.speed_frame_count += 1
            self.last_speed_frame_time = time.monotonic()

    def take_sbus_frame(self):
        with self._lock:
            frame = self._sbus_frame
            self._sbus_frame = None
            return frame

    def take_feedback(self):
        with self._lock:
            feedback = self._feedback
            self._feedback = None
            return feedback

    def get_transport_diagnostics(self):
        last = self.last_speed_frame_time
        age = time.monotonic() - last if last is not None else float("inf")
        return self.speed_frame_count, self.checksum_error_count, self.receive_error_count, age

    def set_motion(self, vx, vy, vz):
        frame, estimate_deg = motion_frame(vx, vy, vz)
        with self._lock:
            if self._serial is None:
                raise OSError(f"Chassis serial port is disconnected: {self.port}")
            self._serial.write(frame)
            self._steering_deg = estimate_deg

    def _center_command(self, command, angle=0):
        self._center_reply.clear()
        self._center_status = None
        self.steering_center_angle = None
        body = bytes((MOTOR_FUNCTION, 2, command, angle))
        frame = HEADER + body + bytes((crc8(body),))
        with self._lock:
            if self._serial is None:
                raise OSError(f"Chassis serial port is disconnected: {self.port}")
            self._serial.write(frame)

    def request_steering_center(self):
        self._center_command(6)

    def save_steering_center(self, angle):
        self._center_command(5, angle)
        if not self._center_reply.wait(0.25):
            raise TimeoutError("STM32 calibration save acknowledgment timed out")
        if self._center_status != 0 or self.steering_center_angle != angle:
            raise OSError("STM32 calibration flash save failed")

    def close(self):
        self._stopping.set()
        self._thread.join(timeout=1.0)

