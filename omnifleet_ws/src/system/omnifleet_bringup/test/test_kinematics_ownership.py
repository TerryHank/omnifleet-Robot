from pathlib import Path
import struct
import sys
import types


PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
try:
    import serial  # noqa: F401
except ModuleNotFoundError:
    sys.modules["serial"] = types.SimpleNamespace(Serial=object)

from omnifleet_bringup.Rosmaster_Lib import Rosmaster


DRIVER = (PACKAGE / "omnifleet_bringup" / "Ackman_driver_R2.py").read_text(
    encoding="utf-8"
)
TRANSPORT = (PACKAGE / "omnifleet_bringup" / "Rosmaster_Lib.py").read_text(
    encoding="utf-8"
)
LAUNCH = (PACKAGE / "launch" / "chassis_core.launch.py").read_text(
    encoding="utf-8"
)
CMAKE = (PACKAGE / "CMakeLists.txt").read_text(encoding="utf-8")


def test_nx_forwards_driving_twist_to_stm32_without_inverse_kinematics():
    assert "motion_cmd = (vx * 1000.0, 0.0, angular * 1000.0)" in DRIVER
    assert "math.atan" not in DRIVER
    assert "nav_use_rotvel" not in DRIVER
    assert "cmd_angular_to_steering" not in DRIVER
    assert "declare_parameter('wheelbase'" not in DRIVER
    assert "declare_parameter('steering_limit'" not in DRIVER


def test_stationary_teleop_uses_only_the_firmware_manual_steering_command():
    assert "if vx == 0.0 and not deadbanded_motion:" in DRIVER
    assert "abs(msg.linear.y) > 1e-6" in DRIVER
    assert "math.copysign(" in DRIVER
    assert "deadbanded_motion = 1e-6 < abs(vx) < self.minimum_linear_speed" in DRIVER
    assert "angular = 0.0" in DRIVER
    assert "self.car.set_motion(0.0, 0.0, 0.0)" in DRIVER
    assert "self.car.set_ackermann_steering(stationary_steering_deg)" in DRIVER
    assert '"stationary_steering_angle_deg": 30.0' in LAUNCH


def test_raw_motor_and_nx_wheel_odometry_paths_are_not_available():
    assert "FUNC_MOTOR" not in TRANSPORT
    assert "def set_car_motion" not in TRANSPORT
    assert 'executable="base_node_R2"' not in LAUNCH
    assert "add_executable(base_node_R2" not in CMAKE
    assert not (PACKAGE / "config" / "ackermann_steering_controller.yaml").exists()


def test_stm32_feedback_keeps_firmware_units_explicit():
    assert "vx_mm_s, steering_deg, wz_mrad_s" in TRANSPORT
    assert "self.odom_vx = vx_mm_s / 1000.0" in TRANSPORT
    assert "self.odom_vy = float(steering_deg)" in TRANSPORT
    assert "self.odom_vz = wz_mrad_s / 1000.0" in TRANSPORT
    assert "get_transport_diagnostics" in TRANSPORT
    assert '"/stm32/encoder_counts"' in DRIVER


def test_motion_packet_contains_body_velocity_not_actuator_targets():
    transport = Rosmaster.__new__(Rosmaster)
    sent = {}
    transport._send = lambda command, payload: sent.update(
        command=command, payload=payload
    )

    transport.set_motion(420.0, 0.0, -350.0)

    assert sent["command"] == Rosmaster.FUNC_MOTION
    assert struct.unpack("<Bhhh", sent["payload"]) == (0, 420, 0, -350)


def test_manual_steering_packet_keeps_drive_control_inside_stm32():
    transport = Rosmaster.__new__(Rosmaster)
    sent = {}
    transport._send = lambda command, payload: sent.update(
        command=command, payload=payload
    )

    transport.set_ackermann_steering(-30)

    assert sent["command"] == Rosmaster.FUNC_AKM_STEER_ANGLE
    assert struct.unpack("<Bb", sent["payload"]) == (1, -30)


def test_speed_feedback_exposes_stm32_steering_and_body_velocity_units():
    transport = Rosmaster.__new__(Rosmaster)
    transport.odom_vx = 0.0
    transport.odom_vy = 0.0
    transport.odom_vz = 0.0
    transport.voltage = 0.0
    transport.speed_frame_count = 0
    transport.last_speed_frame_time = None
    frame = bytearray(12)
    frame[3] = Rosmaster.FUNC_REPORT_SPEED
    frame[4:10] = struct.pack("<hhh", 420, 12, -350)
    frame[10] = 123

    transport._parse(frame)

    assert transport.get_motion_data() == (0.42, 12.0, -0.35)
    assert transport.voltage == 12.3
    assert transport.speed_frame_count == 1


def test_encoder_feedback_exposes_atomic_m1_to_m4_counts():
    transport = Rosmaster.__new__(Rosmaster)
    transport.encoder_counts = (0, 0, 0, 0)
    transport.encoder_frame_count = 0
    transport.last_encoder_frame_time = None
    frame = bytearray(21)
    frame[3] = Rosmaster.FUNC_REPORT_ENCODER
    frame[4:20] = struct.pack("<iiii", 101, -202, 303, -404)

    transport._parse(frame)

    assert transport.get_encoder_counts() == (101, -202, 303, -404)
    assert transport.encoder_frame_count == 1
    assert transport.last_encoder_frame_time is not None


def test_firmware_version_is_queried_from_stm32_instead_of_faked():
    transport = Rosmaster.__new__(Rosmaster)
    transport.firmware_version = None
    transport.last_version_request_time = 0.0
    sent = {}
    transport._send = lambda command, payload: sent.update(
        command=command, payload=payload
    )

    assert transport.get_version() is None
    assert sent == {
        "command": Rosmaster.FUNC_REQUEST_DATA,
        "payload": bytes([Rosmaster.FUNC_VERSION, 0]),
    }

    frame = bytearray(7)
    frame[3] = Rosmaster.FUNC_VERSION
    frame[4] = 3
    frame[5] = 5
    transport._parse(frame)
    assert transport.get_version() == "3.5"
