import math
import struct, threading, time, serial

class Rosmaster:
    HEAD = 0xFF
    DEVICE_ID = 0xFC
    FUNC_MOTOR = 0x10
    FUNC_MOTION = 0x12
    FUNC_AKM_STEER_ANGLE = 0x31
    FUNC_AKM_DEADZONE_PWM = 0x32
    FUNC_AKM_STEER_CONFIG = 0x33
    FUNC_AKM_MOTOR_STATE = 0x34
    FUNC_REQUEST_DATA = 0x50
    FUNC_VERSION = 0x51
    FUNC_REPORT_SPEED = 0x0A
    FUNC_YAW_PID = 0x14
    FUNC_YAW_RATE_PI = 0x18
    FUNC_HEADING_TRIM = 0x19
    FUNC_TRACKED_STARTUP_PWM = 0x1A
    FUNC_REVERSE_HEADING_TRIM = 0x1B
    FUNC_TRACKED_PWM_COMP = 0x16
    FUNC_REPORT_MPU_RAW = 0x0B
    FUNC_REPORT_IMU_ATT = 0x0C
    FUNC_REPORT_ICM_RAW = 0x0E
    FUNC_FTSERVO = 0x28

    def __init__(self, car_type=1, com='/dev/omnifleet_t2_stm32', delay=0.002, debug=False):
        self.car_type = car_type
        self.delay = delay
        self.ser = serial.Serial(baudrate=115200, timeout=0.01, write_timeout=0.05, exclusive=True)
        self.ser.port = com
        self.ser.dtr = False
        self.ser.rts = False
        self.ser.open()
        self.ser.flushInput()
        self.lock = threading.Lock()
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
        self.voltage = 0.0
        self.imu_roll = 0.0
        self.imu_pitch = 0.0
        self.imu_yaw = 0.0
        self.gyro = (0.0, 0.0, 0.0)
        self.accel = (0.0, 0.0, 0.0)
        self.mag = (0.0, 0.0, 0.0)
        self._ftservo_condition = threading.Condition()
        self._ftservo_response = None
        self._control_condition = threading.Condition()
        self._control_state = None
        self._control_state_at = 0.0
        self._tracked_pwm_condition = threading.Condition()
        self._tracked_pwm_response = None
        self._yaw_pid_condition = threading.Condition()
        self._yaw_pid_response = None
        self._yaw_rate_pi_response = None
        self._heading_trim_response = None
        self._startup_pwm_response = None
        self.last_imu_frame_time = None

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
        if f[3] == 0x17 and len(f[4:-1]) == struct.calcsize('<BBBBBHI16H'):
            version, mode, result, failsafe, armed, age, frames, *channels = struct.unpack('<BBBBBHI16H', f[4:-1])
            if version != 1 or mode not in (0,1) or failsafe not in (0,1,3) or armed not in (0,1) or any(ch>2047 for ch in channels):
                return
            with self._control_condition:
                self._control_state = {'version':version,'mode':mode,'result':result,'failsafe':failsafe,
                    'armed':bool(armed),'age_ms':age,'frames':frames,'channels':channels}
                self._control_state_at = time.monotonic()
                self._control_condition.notify_all()
        elif f[3] == self.FUNC_FTSERVO and len(f) >= 14:
            values = struct.unpack('<hhh', f[7:13])
            with self._ftservo_condition:
                self._ftservo_response = (f[4], f[5], f[6], values[0], values[1], values[2])
                self._ftservo_condition.notify_all()
        elif f[3] == self.FUNC_TRACKED_PWM_COMP and len(f) >= 10:
            with self._tracked_pwm_condition:
                self._tracked_pwm_response = struct.unpack('<HHB', f[4:9])
                self._tracked_pwm_condition.notify_all()
        elif f[3] == self.FUNC_YAW_PID and len(f) == 12 and f[4] == 5:
            with self._yaw_pid_condition:
                self._yaw_pid_response = struct.unpack_from('<HHH', f, 5)
                self._yaw_pid_condition.notify_all()
        elif f[3] == self.FUNC_YAW_RATE_PI and len(f) == 9:
            with self._yaw_pid_condition:
                self._yaw_rate_pi_response = struct.unpack_from('<HH', f, 4)
                self._yaw_pid_condition.notify_all()
        elif f[3] in (self.FUNC_HEADING_TRIM, self.FUNC_REVERSE_HEADING_TRIM) and len(f) == 7:
            with self._yaw_pid_condition:
                self._heading_trim_response = (f[3], struct.unpack_from('<H', f, 4)[0])
                self._yaw_pid_condition.notify_all()
        elif f[3] == self.FUNC_TRACKED_STARTUP_PWM and len(f) == 13:
            with self._yaw_pid_condition:
                self._startup_pwm_response = struct.unpack_from('<4H', f, 4)
                self._yaw_pid_condition.notify_all()
        elif f[3] == self.FUNC_REPORT_SPEED and len(f) >= 12:
            vx_mm_s, vy_mm_s, wz_mrad_s = struct.unpack(
                '<hhh', f[4:10]
            )
            self.odom_vx = vx_mm_s / 1000.0
            self.odom_vy = vy_mm_s / 1000.0
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
            self.last_imu_frame_time = time.monotonic()
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

    def set_car_type(self, t):
        self.car_type = t

    def _tracked_pwm_request(self, command, payload, timeout):
        with self._tracked_pwm_condition:
            self._tracked_pwm_response = None
            self._send(command, payload)
            if not self._tracked_pwm_condition.wait_for(
                    lambda: self._tracked_pwm_response is not None, timeout):
                raise TimeoutError('STM32 PWM compensation readback timed out')
            m1, m2, status = self._tracked_pwm_response
            if status:
                raise RuntimeError('STM32 PWM compensation rejected: status=%d' % status)
            return m1, m2

    def get_tracked_pwm_compensation(self, timeout=.5):
        return self._tracked_pwm_request(
            self.FUNC_REQUEST_DATA, bytes([self.FUNC_TRACKED_PWM_COMP, 0]), timeout)

    def set_tracked_pwm_compensation(self, m1, m2, timeout=1.):
        if any(type(value) is not int or not 0 <= value <= 3300 for value in (m1, m2)):
            raise ValueError('PWM compensation must be integers in [0, 3300]')
        applied = self._tracked_pwm_request(
            self.FUNC_TRACKED_PWM_COMP, struct.pack('<HHB', m1, m2, 0x5F), timeout)
        actual = self.get_tracked_pwm_compensation(timeout)
        if applied != (m1, m2) or actual != (m1, m2):
            raise RuntimeError('STM32 PWM compensation readback mismatch')
        return actual

    def set_motion(self, vx, vy, vz, adjust=False):
        """Send tracked-body velocity; STM32 owns differential kinematics/PID.

        Units are Vx/Vy in mm/s and Vz in mrad/s. The tracked chassis uses
        Vy=0 and supports both moving turns and zero-radius rotation.
        """
        parm = 0x80 if adjust else 0
        data = struct.pack('<Bhhh', parm, int(vx), int(vy), int(vz))
        self._send(self.FUNC_MOTION, data)

    def get_yaw_pid(self, timeout=0.15):
        with self._yaw_pid_condition:
            self._yaw_pid_response = None
            self._send(self.FUNC_REQUEST_DATA, bytes((self.FUNC_YAW_PID, 5)))
            if not self._yaw_pid_condition.wait_for(
                    lambda: self._yaw_pid_response is not None, timeout):
                raise TimeoutError('STM32 yaw PID readback timed out')
            return tuple(value / 1000.0 for value in self._yaw_pid_response)

    @staticmethod
    def encode_yaw_gains(gains):
        if any(not math.isfinite(value) or not 0.0 <= value <= 65.535 for value in gains):
            raise ValueError('Yaw PID gains must be finite and in [0, 65.535]')
        encoded = tuple(round(value * 1000.0) for value in gains)
        if any(value != packed / 1000.0 for value, packed in zip(gains, encoded)):
            raise ValueError('Yaw PID gains support up to three decimal places')
        return encoded

    def set_yaw_pid(self, kp, ki, kd):
        gains = (kp, ki, kd)
        encoded = self.encode_yaw_gains(gains)
        with self._yaw_pid_condition:
            self._send(self.FUNC_YAW_PID, struct.pack('<HHHB', *encoded, 0))
            actual = self.get_yaw_pid()
        if actual != gains:
            raise RuntimeError(f'STM32 yaw PID readback mismatch: {actual}')
        return actual

    def get_yaw_rate_pi(self, timeout=0.15):
        with self._yaw_pid_condition:
            self._yaw_rate_pi_response = None
            self._send(self.FUNC_REQUEST_DATA, bytes((self.FUNC_YAW_RATE_PI, 0)))
            if not self._yaw_pid_condition.wait_for(
                    lambda: self._yaw_rate_pi_response is not None, timeout):
                raise TimeoutError('STM32 yaw rate PI readback timed out')
            return tuple(value / 1000.0 for value in self._yaw_rate_pi_response)

    def set_yaw_rate_pi(self, kp, ki):
        gains = (kp, ki)
        with self._yaw_pid_condition:
            self._send(self.FUNC_YAW_RATE_PI, struct.pack('<HH', *self.encode_yaw_gains(gains)))
            actual = self.get_yaw_rate_pi()
        if actual != gains:
            raise RuntimeError(f'STM32 yaw rate PI readback mismatch: {actual}')
        return actual

    def get_heading_trim(self, timeout=0.15, *, reverse=False):
        command = self.FUNC_REVERSE_HEADING_TRIM if reverse else self.FUNC_HEADING_TRIM
        with self._yaw_pid_condition:
            self._heading_trim_response = None
            self._send(self.FUNC_REQUEST_DATA, bytes((command, 0)))
            if not self._yaw_pid_condition.wait_for(
                    lambda: self._heading_trim_response is not None
                    and self._heading_trim_response[0] == command, timeout):
                raise TimeoutError('STM32 heading trim readback timed out')
            value = self._heading_trim_response[1]
            return -1.0 if reverse and value == 65535 else value / 1000.0

    @classmethod
    def encode_reverse_heading_trim(cls, values):
        if values[0] == -1.0:
            return 65535
        encoded = cls.encode_yaw_gains(values)[0]
        if encoded == 65535:
            raise ValueError('Reverse heading trim supports up to 65.534, or -1 to inherit')
        return encoded

    def set_heading_trim(self, trim, *, reverse=False):
        command = self.FUNC_REVERSE_HEADING_TRIM if reverse else self.FUNC_HEADING_TRIM
        encoded = self.encode_reverse_heading_trim((trim,)) if reverse else self.encode_yaw_gains((trim,))[0]
        with self._yaw_pid_condition:
            self._send(command, struct.pack('<H', encoded))
            actual = self.get_heading_trim(reverse=reverse)
        if actual != trim:
            raise RuntimeError(f'STM32 heading trim readback mismatch: {actual}')
        return actual

    @staticmethod
    def validate_startup_pwm(values):
        if any(type(value) is not int or not 0 <= value <= 3600 for value in values):
            raise ValueError('Startup PWM boosts must be integers in [0, 3600] timer counts')

    def get_startup_pwm(self, timeout=0.15):
        with self._yaw_pid_condition:
            self._startup_pwm_response = None
            self._send(self.FUNC_REQUEST_DATA, bytes((self.FUNC_TRACKED_STARTUP_PWM, 0)))
            if not self._yaw_pid_condition.wait_for(
                    lambda: self._startup_pwm_response is not None, timeout):
                raise TimeoutError('STM32 startup PWM readback timed out')
            return self._startup_pwm_response

    def set_startup_pwm(self, *values):
        self.validate_startup_pwm(values)
        with self._yaw_pid_condition:
            self._send(self.FUNC_TRACKED_STARTUP_PWM, struct.pack('<4H', *values))
            actual = self.get_startup_pwm()
        if actual != values:
            raise RuntimeError(f'STM32 startup PWM readback mismatch: {actual}')
        return actual

    def set_tank_motion(self, vx_mm_s, wz_mrad_s):
        """Drive M2 as the left track and M1 as the right track."""
        track_width_mm = 330.0
        max_track_speed_mm_s = 1000.0
        turn_speed_mm_s = (wz_mrad_s / 1000.0) * track_width_mm / 2.0
        left_speed_mm_s = vx_mm_s - turn_speed_mm_s
        right_speed_mm_s = vx_mm_s + turn_speed_mm_s

        scale = max(
            1.0,
            abs(left_speed_mm_s) / max_track_speed_mm_s,
            abs(right_speed_mm_s) / max_track_speed_mm_s,
        )
        motor_m1_right = int(round(
            right_speed_mm_s / scale / max_track_speed_mm_s * 100.0
        ))
        motor_m2_left = int(round(
            -left_speed_mm_s / scale / max_track_speed_mm_s * 100.0
        ))
        self._send(
            self.FUNC_MOTOR,
            struct.pack('<bbbb', motor_m1_right, motor_m2_left, 0, 0),
        )

    def set_ackermann_steering(self, angle_deg):
        """Set the steering servo while the drive wheels remain stopped."""
        angle_deg = int(round(max(-40.0, min(40.0, angle_deg))))
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
        if not 1 <= max_angle_deg <= 40:
            raise ValueError('maximum steering angle must be in [1, 40] degrees')
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

    def poll_control_state(self):
        self._send(self.FUNC_REQUEST_DATA, bytes([0x17, 0]))
        with self._control_condition:
            if self._control_state is not None and time.monotonic() - self._control_state_at < 0.15:
                return dict(self._control_state)
        return None

    def get_control_state(self, timeout=.5):
        """Query 0x17 through the existing receiver; never change control mode."""
        with self._control_condition:
            self._control_state = None
        self._send(self.FUNC_REQUEST_DATA, bytes([0x17,0]))
        deadline = time.monotonic()+timeout
        with self._control_condition:
            while self._control_state is None:
                remaining = deadline-time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Missing fresh STM32 control-mode response')
                self._control_condition.wait(remaining)
            return dict(self._control_state)

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
            # STM32 consumes its single command buffer on a 1 ms task tick.
            # Keep the next frame from replacing it before that task runs.
            time.sleep(self.delay)

    def ftservo_command(self, operation, servo_id, arg0=0, arg1=0, arg2=0, timeout=1.0):
        payload = bytes([operation & 0xFF, servo_id & 0xFF]) + struct.pack('<HHH', arg0 & 0xFFFF, arg1 & 0xFFFF, arg2 & 0xFFFF)
        with self._ftservo_condition:
            self._ftservo_response = None
        self._send(self.FUNC_FTSERVO, payload)
        deadline = time.monotonic() + timeout
        with self._ftservo_condition:
            while self._ftservo_response is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('FTServo response timeout')
                self._ftservo_condition.wait(remaining)
            op, response_id, status, value0, value1, value2 = self._ftservo_response
        if op != (operation & 0xFF) or response_id != (servo_id & 0xFF):
            raise RuntimeError('FTServo response mismatch')
        return status, value0, value1, value2

    def close(self):
        self.running = False
        self.set_motion(0, 0, 0)
        time.sleep(0.1)
        self.ser.close()
