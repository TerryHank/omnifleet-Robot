import struct, threading, time, serial

class Rosmaster:
    HEAD = 0xFF
    DEVICE_ID = 0xFC
    FUNC_MOTOR = 0x10
    FUNC_MOTION = 0x12
    FUNC_REPORT_SPEED = 0x0A
    FUNC_REPORT_MPU_RAW = 0x0B
    FUNC_REPORT_IMU_ATT = 0x0C
    FUNC_REPORT_ICM_RAW = 0x0E

    def __init__(self, car_type=1, com='/dev/myserial', delay=0.002, debug=False):
        self.car_type = car_type
        self.ser = serial.Serial(com, 115200, timeout=0.01)
        self.ser.flushInput()
        self.lock = threading.Lock()
        self.running = True
        self.odom_vx = 0.0
        self.odom_vy = 0.0
        self.odom_vz = 0.0
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
                        buf = buf[1:]
                        continue

                    self._parse(frame)
                    buf = buf[total:]
            except Exception:
                buf = b''
                time.sleep(0.01)

    def _parse(self, f):
        if f[3] == self.FUNC_REPORT_SPEED and len(f) >= 12:
            self.odom_vx = struct.unpack('<h', f[4:6])[0] / 1000.0
            self.odom_vy = struct.unpack('<h', f[6:8])[0] / 1000.0
            self.odom_vz = struct.unpack('<h', f[8:10])[0] / 1000.0
            self.voltage = f[10] / 10.0
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

    def set_car_type(self, t):
        self.car_type = t

    def set_car_motion(self, vx, vy, vz):
        m1 = max(-100, min(100, int(-vx * 100)))
        m2 = max(-100, min(100, int(-vx * 100)))
        m3 = max(-100, min(100, int(vy * 100)))
        m4 = max(-100, min(100, int(vz * 100)))
        data = struct.pack('<bbbb', m1, m2, m3, m4)
        self._send(self.FUNC_MOTOR, data)

    def set_motion(self, vx, vy, vz):
        """FUNC_MOTION: Vx(mm/s), Vy(steer deg), Vz(angular rate). STM32 handles Ackermann kinematics."""
        parm = 0
        data = struct.pack('<Bhhh', parm, int(vx), int(vy), int(vz))
        self._send(self.FUNC_MOTION, data)

    def set_colorful_effect(self, *a, **kw):
        pass
    def set_beep(self, v):
        pass
    def get_version(self):
        return 0
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
        self.set_car_motion(0, 0, 0)
        time.sleep(0.1)
        self.ser.close()
