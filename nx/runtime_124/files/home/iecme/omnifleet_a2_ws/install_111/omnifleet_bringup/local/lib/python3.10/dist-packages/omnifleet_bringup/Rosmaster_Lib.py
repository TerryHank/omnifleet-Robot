import struct, threading, time, serial

class Rosmaster:
    HEAD = 0xFF
    DEVICE_ID = 0xFC
    FUNC_MOTION = 0x12
    FUNC_AKM_DEF_ANGLE = 0x30
    FUNC_AKM_STEER_ANGLE = 0x31
    FUNC_FTSERVO = 0x28
    FUNC_REQUEST_DATA = 0x50
    FUNC_VERSION = 0x51
    FUNC_REPORT_SPEED = 0x0A
    FUNC_REPORT_MPU_RAW = 0x0B
    FUNC_REPORT_IMU_ATT = 0x0C
    FUNC_REPORT_ENCODER = 0x0D
    FUNC_REPORT_ICM_RAW = 0x0E

    def __init__(self, car_type=1, com='/dev/myserial', delay=0.002, debug=False):
        self.car_type = car_type
        self.ser = serial.Serial(com, 115200, timeout=0.01)
        self.ser.flushInput()
        self.lock = threading.Lock()
        self.running = True
        self.servo_reply = threading.Event()
        self.servo_request = None
        self.servo_response = None
        self.steering_center_angle = None
        self.odom_vx = 0.0
        self.odom_vy = 0.0
        self.odom_vz = 0.0
        self.speed_frame_count = 0
        self.checksum_error_count = 0
        self.receive_error_count = 0
        self.last_speed_frame_time = None
        self.encoder_counts = (0, 0, 0, 0)
        self.encoder_frame_count = 0
        self.last_encoder_frame_time = None
        self.firmware_version = None
        self.last_version_request_time = 0.0
        self.voltage = 0.0
        self.imu_roll = 0.0
        self.imu_pitch = 0.0
        self.imu_yaw = 0.0
        self.gyro = (0.0, 0.0, 0.0)
        self.accel = (0.0, 0.0, 0.0)
        self.mag = (0.0, 0.0, 0.0)

    def create_receive_threading(self):
        t = threading.Thread(target=self._recv, daemon=True)
        t.start()

    def _recv(self):
        max_frame = 64
        max_buffer = 256
        head = bytes([self.HEAD])
        buf = b''
        while self.running:
            try:
                with self.lock:
                    n = self.ser.in_waiting or 1
                    r = self.ser.read(n)
                if not r:
                    time.sleep(0.01)
                    continue

                buf += r
                if len(buf) > max_buffer:
                    last_head = buf.rfind(head, max(0, len(buf) - max_frame))
                    buf = buf[last_head:] if last_head >= 0 else b''

                while len(buf) >= 5:
                    head_index = buf.find(head)
                    if head_index < 0:
                        buf = b''
                        break
                    if head_index > 0:
                        buf = buf[head_index:]

                    total = buf[2] + 2
                    if total < 5 or total > max_frame:
                        buf = buf[1:]
                        continue
                    if len(buf) < total:
                        break

                    frame = buf[:total]
                    if (sum(frame[2:-1]) & 0xFF) != frame[-1]:
                        self.checksum_error_count += 1
                        buf = buf[1:]
                        continue

                    self._parse(frame)
                    buf = buf[total:]
            except Exception:
                self.receive_error_count += 1
                buf = b''
                time.sleep(0.01)

    def _parse(self, f):
        if f[3] == self.FUNC_REPORT_SPEED and len(f) >= 12:
            vx_mm_s, steering_deg, wz_mrad_s = struct.unpack('<hhh', f[4:10])
            self.odom_vx = vx_mm_s / 1000.0
            self.odom_vy = float(steering_deg)
            self.odom_vz = wz_mrad_s / 1000.0
            self.voltage = f[10] / 10.0
            self.speed_frame_count += 1
            self.last_speed_frame_time = time.monotonic()
        elif f[3] == self.FUNC_REPORT_IMU_ATT and len(f) >= 11:
            roll, pitch, yaw = struct.unpack('<hhh', f[4:10])
            self.imu_roll = roll / 10000.0
            self.imu_pitch = pitch / 10000.0
            self.imu_yaw = yaw / 10000.0
        elif f[3] == self.FUNC_REPORT_ENCODER and len(f) >= 21:
            # Firmware reports cumulative M1..M4 encoder counts as four
            # little-endian signed int32 values. Assign one tuple atomically so
            # ROS publishers never combine channels from different frames.
            self.encoder_counts = struct.unpack('<iiii', f[4:20])
            self.encoder_frame_count += 1
            self.last_encoder_frame_time = time.monotonic()
        elif f[3] in (self.FUNC_REPORT_MPU_RAW, self.FUNC_REPORT_ICM_RAW) and len(f) >= 23:
            raw = struct.unpack('<hhhhhhhhh', f[4:22])
            self.gyro = tuple(float(v) for v in raw[0:3])
            self.accel = tuple(float(v) for v in raw[3:6])
            self.mag = tuple(float(v) for v in raw[6:9])
        elif f[3] == self.FUNC_AKM_DEF_ANGLE and len(f) == 7 and f[4] == 4:
            if f[5] <= 180:
                self.steering_center_angle = f[5]
        elif f[3] == self.FUNC_VERSION and len(f) >= 7:
            self.firmware_version = '%d.%d' % (f[4], f[5])

        elif f[3] == self.FUNC_FTSERVO and len(f) == 15:
            op, servo_id, status, position, speed, load = struct.unpack_from('<BBBhhh', f, 4)
            if (op, servo_id) == self.servo_request:
                self.servo_response = status, position, speed, load
                self.servo_reply.set()

    def ftservo_command(self, operation, servo_id, arg0, arg1, arg2):
        payload = struct.pack('<BBHHH', operation, servo_id,
                              arg0 & 0xffff, arg1 & 0xffff, arg2 & 0xffff)
        self.servo_reply.clear()
        self.servo_request = operation, servo_id
        try:
            self._send(self.FUNC_FTSERVO, payload)
            if not self.servo_reply.wait(0.25):
                raise TimeoutError(f'No STM32 FTServo response for ID {servo_id}')
            return self.servo_response
        finally:
            self.servo_request = None

    def request_steering_center(self):
        self.steering_center_angle = None
        self._send(self.FUNC_REQUEST_DATA, bytes([self.FUNC_AKM_DEF_ANGLE, 0]))

    def save_steering_center(self, angle):
        # The Ackermann protocol takes logical ID 1 and responds with physical S4.
        self._send(self.FUNC_AKM_DEF_ANGLE, bytes([1, angle, 0x5F]))

    def set_car_type(self, t):
        self.car_type = t

    def set_motion(self, vx, vy, vz):
        """Send body command; STM32 exclusively computes Ackermann actuator targets.

        Units are Vx in mm/s, Vy fixed at zero, and Vz in mrad/s.
        """
        parm = 0
        data = struct.pack('<Bhhh', parm, int(vx), int(vy), int(vz))
        self._send(self.FUNC_MOTION, data)

    def set_ackermann_steering(self, angle_deg):
        """Set the steering servo while the drive wheels remain stopped."""
        angle_deg = int(round(max(-45.0, min(45.0, angle_deg))))
        self._send(
            self.FUNC_AKM_STEER_ANGLE,
            struct.pack('<Bb', 1, angle_deg),
        )

    def set_colorful_effect(self, *a, **kw):
        pass
    def set_beep(self, v):
        pass
    def get_version(self):
        now = time.monotonic()
        if self.firmware_version is None and now - self.last_version_request_time >= 1.0:
            self.last_version_request_time = now
            self._send(
                self.FUNC_REQUEST_DATA,
                bytes([self.FUNC_VERSION, 0]),
            )
        return self.firmware_version
    def get_battery_voltage(self):
        return self.voltage
    def get_accelerometer_data(self):
        return self.accel
    def get_gyroscope_data(self):
        return self.gyro
    def get_magnetometer_data(self):
        return self.mag
    def get_imu_attitude_data(self):
        return (self.imu_roll, self.imu_pitch, self.imu_yaw)
    def get_motion_data(self):
        return (self.odom_vx, self.odom_vy, self.odom_vz)
    def get_encoder_counts(self):
        return self.encoder_counts

    def get_transport_diagnostics(self):
        frame_age = (
            time.monotonic() - self.last_speed_frame_time
            if self.last_speed_frame_time is not None
            else float('inf')
        )
        return (
            self.speed_frame_count,
            self.checksum_error_count,
            self.receive_error_count,
            frame_age,
        )

    def _send(self, cmd, data):
        dlen = len(data) + 3
        frame = bytes([self.HEAD, self.DEVICE_ID, dlen, cmd]) + data
        chk = sum(frame[2:]) & 0xFF
        frame += bytes([chk])
        with self.lock:
            self.ser.write(frame)
            self.ser.flush()

    def close(self):
        self.running = False
        self.set_motion(0, 0, 0)
        time.sleep(0.1)
        self.ser.close()
