"""Ranger Mini 3.0 manual section 3.2 and the Linux classic CAN frame."""

import math
import socket
import struct

MOTION = 0x111
LIGHT = 0x121
MOTION_MODE = 0x141
CONTROL_MODE = 0x421
DRIVE_MODE = 0x423
CLEAR_FAULT = 0x441
ACKERMANN, CRAB, SPIN, PARK = range(4)
STANDBY, CAN, REMOTE = 0, 1, 3
COMMAND_LENGTHS = {
    MOTION: 8, LIGHT: 8, MOTION_MODE: 1,
    CONTROL_MODE: 1, DRIVE_MODE: 1, CLEAR_FAULT: 1,
}
HALF_WHEELBASE = 0.494 / 2
HALF_TRACK = 0.370 / 2
WHEEL_RADIUS_FROM_CENTER = math.hypot(HALF_WHEELBASE, HALF_TRACK)

FEEDBACK = {
    0x211: (20, ">BBHI", "body_state control_mode voltage_dV faults"),
    0x221: (20, ">hh2xh", "speed_mm_s spin_mrad_s steering_mrad"),
    0x231: (20, ">BB5xB", "enabled mode count"),
    # Live firmware reports 0x7E at neutral. Preserve the raw stick bytes.
    0x241: (20, ">6BxB", "switches right_x_raw right_y_raw left_y_raw left_x_raw knob_raw count"),
    0x271: (20, ">4h", "rf_mrad rr_mrad lr_mrad lf_mrad"),
    0x281: (20, ">4h", "rf_mm_s rr_mm_s lr_mm_s lf_mm_s"),
    0x291: (20, ">BBB", "motion_mode switching drive_mode"),
    0x311: (20, ">ii", "lf_mm rf_mm"),
    0x312: (20, ">ii", "lr_mm rr_mm"),
    # On 104 this field is 4960 while the system frame reports 49.7 V.
    0x361: (500, ">BBHhh", "soc soh voltage_raw current_dA temperature_dC"),
    0x362: (500, ">BBBB", "alarm1 alarm2 warning1 warning2"),
}
for motor in range(1, 9):
    FEEDBACK[0x250 + motor] = (20, ">hhi", "rpm current_dA position_pulses")
    FEEDBACK[0x260 + motor] = (100, ">HhbB2x", "voltage_dV driver_degC motor_degC status")

CAN_FRAME = struct.Struct("=IB3x8s")


def open_can(interface):
    bus = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    try:
        bus.bind((interface,))
    except OSError:
        bus.close()
        raise
    return bus


def unpack_frame(raw):
    can_id, length, data = CAN_FRAME.unpack(raw)
    if can_id > 0x7FF or length > 8:
        return None  # Extended, RTR, error or malformed frame.
    return can_id, data[:length]


def pack_frame(can_id, data):
    if not 0 <= can_id <= 0x7FF or len(data) > 8:
        raise ValueError("Expected a classic CAN standard data frame")
    return CAN_FRAME.pack(can_id, len(data), data)


def motion_command(speed, spin, steering):
    """Encode SI units. Reserved bytes are zero."""
    return struct.pack(">hh2xh", round(speed * 1000), round(spin * 1000),
                       round(steering * 1000))


def decode_feedback(can_id, data):
    _, fmt, names = FEEDBACK[can_id]
    extension = b""
    if can_id == 0x362 and len(data) == 8:
        data, extension = data[:4], data[4:]
    decoded = dict(zip(names.split(), struct.unpack(fmt, data)))
    if extension:
        decoded["extension_raw"] = extension.hex()
    return decoded


def ackermann_radii(radius):
    inner = math.hypot(radius - HALF_TRACK, HALF_WHEELBASE)
    outer = math.hypot(radius + HALF_TRACK, HALF_WHEELBASE)
    return inner, outer


def body_twist(mode, motion):
    speed = motion["speed_mm_s"] / 1000
    angle = motion["steering_mrad"] / 1000
    if mode == PARK:
        return 0.0, 0.0, 0.0
    if mode == SPIN:
        return 0.0, 0.0, motion["spin_mrad_s"] / 1000
    if mode == CRAB:
        return speed * math.cos(angle), speed * math.sin(angle), 0.0
    if not angle:
        return speed, 0.0, 0.0
    # 0x221 is the mean of the inner and outer angles in Ackermann mode.
    # The manual defines right-positive feedback for this mode only.
    sine, cosine = math.sin(2 * abs(angle)), math.cos(2 * angle)
    radius = (HALF_WHEELBASE * cosine +
              math.hypot(HALF_WHEELBASE, HALF_TRACK * sine)) / sine
    inner, outer = ackermann_radii(radius)
    yaw_rate = speed / ((inner + outer) / 2)
    return yaw_rate * radius, 0.0, yaw_rate * math.copysign(1, -angle)
