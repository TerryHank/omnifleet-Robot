import struct, threading, time, serial

class Rosmaster:
    HEAD = 0xFF
    DEVICE_ID = 0xFC
    FUNC_MOTION = 0x12
    FUNC_AKM_STEER_ANGLE = 0x31
    FUNC_AKM_DEADZONE_PWM = 0x32
    FUNC_AKM_STEER_CONFIG = 0x33
    FUNC_AKM_MOTOR_STATE = 0x34
    FUNC_AKM_WATCHDOG = 0x35
    FUNC_REQUEST_DATA = 0x50
    FUNC_VERSION = 0x51
    FUNC_REPORT_SPEED = 0x0A
    FUNC_REPORT_MPU_RAW = 0x0B
    FUNC_REPORT_IMU_ATT = 0x0C
    FUNC_REPORT_ICM_RAW = 0x0E

    def __init__(self, car_type=1, com='/dev/myserial', delay=0.003, debug=False):
        self.car_type = car_type
        self.ser = serial.Serial(com, 115200, timeout=0.01)
        self.ser.flushInput()
        self.lock = threading.Lock()
        self.delay = max(0.0, float(delay))
        self.last_send_finished_time = 0.0
        self.running = True
        self.odom_vx = 0.0
        self.odom_vy = 0.0
        self.odom_vz = 0.0
        self.speed_frame_count = 0
        self.checksum_error_count = 0
        self.receive_error_count = 0
        self.last_speed_frame_time = None
        self.firmware_version = None
        self.last_version_request_time = 0.0
        self.ackermann_deadzone_pwm = None
        self.ackermann_steering_config = None
        self.ackermann_motor_state = None
        self.motor_state_frame_count = 0
        self.last_motor_state_time = None
        self.motion_watchdog_status = None
        self.last_motion_watchdog_status_time = None
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
            vx_mm_s, commanded_steering_deg, wz_mrad_s = struct.unpack(
                '<hhh', f[4:10]
            )
            self.odom_vx = vx_mm_s / 1000.0
            self.odom_vy = float(commanded_steering_deg)
            self.odom_vz = wz_mrad_s / 1000.0
            self.voltage = f[10] / 10.0
            self.speed_frame_count += 1
            self.last_speed_frame_time = time.monotonic()
        elif f[3] == self.FUNC_REPORT_IMU_ATT and len(f) >= 11:
            roll, pitch, yaw = struct.unpack('<hhh', f[4:10])
            self.imu_roll = roll / 10000.0
            self.imu_pitch = pitch / 10000.0
            self.imu_yaw = yaw / 10000.0
        elif f[3] in (self.FUNC_REPORT_MPU_RAW, self.FUNC_REPORT_ICM_RAW) and len(f) >= 23:
            raw = struct.unpack('<hhhhhhhhh', f[4:22])
            self.gyro = tuple(float(v) for v in raw[0:3])
            self.accel = tuple(float(v) for v in raw[3:6])
            self.mag = tuple(float(v) for v in raw[6:9])
        elif f[3] == self.FUNC_VERSION and len(f) >= 7:
            self.firmware_version = '%d.%d' % (f[4], f[5])
        elif f[3] == self.FUNC_AKM_DEADZONE_PWM and len(f) >= 13:
            self.ackermann_deadzone_pwm = struct.unpack('<HHHH', f[4:12])
        elif f[3] == self.FUNC_AKM_STEER_CONFIG and len(f) >= 7:
            self.ackermann_steering_config = struct.unpack('<Bb', f[4:6])
        elif f[3] == self.FUNC_AKM_MOTOR_STATE and len(f) >= 19:
            values = struct.unpack('<hhhhhhH', f[4:18])
            self.ackermann_motor_state = values[:6] + (
                values[6] & 0xff,
                (values[6] >> 8) & 0xff,
            )
            self.motor_state_frame_count += 1
            self.last_motor_state_time = time.monotonic()
        elif f[3] == self.FUNC_AKM_WATCHDOG and len(f) >= 12:
            timeout_ms, elapsed_ms, flags, trigger_count = struct.unpack(
                '<HHBH', f[4:11]
            )
            self.motion_watchdog_status = (
                timeout_ms,
                elapsed_ms,
                bool(flags & 0x01),
                bool(flags & 0x02),
                trigger_count,
            )
            self.last_motion_watchdog_status_time = time.monotonic()

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
        angle_deg = int(round(angle_deg))
        if not -128 <= angle_deg <= 127:
            raise ValueError('steering target is outside the signed-byte protocol range')
        self._send(
            self.FUNC_AKM_STEER_ANGLE,
            struct.pack('<Bb', 1, angle_deg),
        )

    def set_ackermann_deadzone_pwm(self, m1_forward, m2_forward, m1_reverse, m2_reverse):
        """Set volatile Ackermann motor dead-zone PWM offsets."""
        values = tuple(int(v) for v in (m1_forward, m2_forward, m1_reverse, m2_reverse))
        if any(v < 0 or v > 3000 for v in values):
            raise ValueError('Ackermann dead-zone PWM values must be in [0, 3000]')
        self.ackermann_deadzone_pwm = None
        self._send(self.FUNC_AKM_DEADZONE_PWM, struct.pack('<HHHH', *values))

    def get_ackermann_deadzone_pwm(self):
        return self.ackermann_deadzone_pwm

    def set_ackermann_steering_config(self, max_angle_deg, center_offset_deg):
        """Set volatile STM32 steering limits and receive the applied values."""
        max_angle_deg = int(max_angle_deg)
        center_offset_deg = int(center_offset_deg)
        if not 1 <= max_angle_deg <= 25:
            raise ValueError('maximum steering angle must be in [1, 25] degrees')
        if not -40 <= center_offset_deg <= 40:
            raise ValueError('steering centre offset must be in [-40, 40] degrees')
        self.ackermann_steering_config = None
        self._send(
            self.FUNC_AKM_STEER_CONFIG,
            struct.pack('<Bb', max_angle_deg, center_offset_deg),
        )

    def get_ackermann_steering_config(self):
        return self.ackermann_steering_config

    def get_ackermann_motor_state(self):
        return self.ackermann_motor_state

    def send_motion_watchdog_heartbeat(self):
        """Tell STM32 that the NX chassis process is alive."""
        self._send(self.FUNC_AKM_WATCHDOG, bytes([0]))

    def set_motion_watchdog_timeout(self, timeout_ms):
        """Set the volatile STM32 communication-loss timeout in milliseconds."""
        timeout_ms = int(timeout_ms)
        if not 100 <= timeout_ms <= 5000:
            raise ValueError('motion watchdog timeout must be in [100, 5000] ms')
        self.motion_watchdog_status = None
        self._send(
            self.FUNC_AKM_WATCHDOG,
            struct.pack('<BH', 1, timeout_ms),
        )

    def request_motion_watchdog_status(self):
        self._send(
            self.FUNC_REQUEST_DATA,
            bytes([self.FUNC_AKM_WATCHDOG, 0]),
        )

    def get_motion_watchdog_status(self):
        return self.motion_watchdog_status

    def get_motion_watchdog_status_age(self):
        if self.last_motion_watchdog_status_time is None:
            return float('inf')
        return time.monotonic() - self.last_motion_watchdog_status_time

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
            remaining = self.delay - (time.monotonic() - self.last_send_finished_time)
            if remaining > 0.0:
                time.sleep(remaining)
            self.ser.write(frame)
            self.ser.flush()
            self.last_send_finished_time = time.monotonic()

    def close(self):
        self.running = False
        self.set_motion(0, 0, 0)
        time.sleep(0.1)
        self.ser.close()
