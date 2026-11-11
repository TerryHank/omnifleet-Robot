from pathlib import Path
import math
import struct
import sys
import threading
import types

import pytest
from geometry_msgs.msg import Twist
from omnifleet_a2_interfaces.msg import SteeringAngleCommand


PACKAGE = Path(__file__).resolve().parents[1]
FIRMWARE_CANDIDATES = (
    PACKAGE.parents[1] / "firmware" / "V3.5.1",
    Path.home() / "stm32_driver_ws" / "src" / "robot_stm32" / "V3.5.1",
)
FIRMWARE = next(
    (candidate for candidate in FIRMWARE_CANDIDATES if candidate.is_dir()),
    FIRMWARE_CANDIDATES[0],
)
sys.path.insert(0, str(PACKAGE))
try:
    import serial  # noqa: F401
except ModuleNotFoundError:
    sys.modules["serial"] = types.SimpleNamespace(Serial=object)

from omnifleet_a2_bringup.Rosmaster_Lib import Rosmaster
from omnifleet_a2_bringup import Rosmaster_Lib as rosmaster_transport
from omnifleet_a2_bringup.omnifleet_ackermann_driver import omnifleet_ackermann_driver
DRIVER = (PACKAGE / "omnifleet_a2_bringup" / "omnifleet_ackermann_driver.py").read_text(
    encoding="utf-8"
)
TRANSPORT = (PACKAGE / "omnifleet_a2_bringup" / "Rosmaster_Lib.py").read_text(
    encoding="utf-8"
)
LAUNCH = (PACKAGE / "launch" / "chassis_core.launch.py").read_text(
    encoding="utf-8"
)
ROBOT_LAUNCH = (PACKAGE / "launch" / "robot.launch.py").read_text(
    encoding="utf-8"
)
PRODUCTION_MOLA = (PACKAGE / "launch" / "production_mola.launch.py").read_text(
    encoding="utf-8"
)
PRODUCTION_NAV2 = (PACKAGE / "launch" / "production_nav2.launch.py").read_text(
    encoding="utf-8"
)
CMAKE = (PACKAGE / "CMakeLists.txt").read_text(encoding="utf-8")
FIRMWARE_PROTOCOL = (FIRMWARE / "Source" / "APP" / "protocol.c").read_text(
    encoding="utf-8"
)
FIRMWARE_ACKERMANN = (
    FIRMWARE / "Source" / "APP" / "app_ackerman.c"
).read_text(encoding="utf-8")
FIRMWARE_APP = (FIRMWARE / "Source" / "APP" / "app.c").read_text(
    encoding="utf-8"
)
FIRMWARE_APP_HEADER = (FIRMWARE / "Source" / "APP" / "app.h").read_text(
    encoding="utf-8"
)
FIRMWARE_MOTION = (FIRMWARE / "Source" / "APP" / "app_motion.c").read_text(
    encoding="utf-8"
)


def test_nx_forwards_driving_twist_to_stm32_without_inverse_kinematics():
    callback = DRIVER.split("def cmd_vel_callback", 1)[1].split(
        "def steering_angle_target_callback", 1
    )[0]
    assert "motion_cmd = (vx * 1000.0, 0.0, angular * 1000.0)" in DRIVER
    assert "angular = msg.angular.z * 1.0" in DRIVER
    assert "angular_limit" not in DRIVER
    assert '"angular_limit"' not in LAUNCH
    assert "math.atan" not in callback
    assert "nav_use_rotvel" not in DRIVER
    assert "cmd_angular_to_steering" not in DRIVER
    assert "declare_parameter('wheelbase'" not in DRIVER
    assert "declare_parameter('steering_limit'" not in DRIVER


def test_explicit_steering_uses_only_the_dedicated_angle_topic():
    assert "math.copysign(" not in DRIVER
    assert "msg.linear.y" not in DRIVER
    assert "steering_angle_target_callback" in DRIVER
    assert "/omnifleet_a2/chassis/steering_angle_cmd" in DRIVER
    assert "SteeringAngleCommand" in DRIVER
    assert "steering_angle_rad" in DRIVER
    assert "self.car.set_motion(0.0, 0.0, 0.0)" in DRIVER
    assert "math.degrees(steering_angle_target_rad)" in DRIVER
    assert "steering_angle_limit_deg" not in DRIVER
    assert "max(-25.0, min(25.0, angle_deg))" not in TRANSPORT
    assert '"max_steering_angle_deg"' in LAUNCH
    assert '"steering_center_offset_deg"' in LAUNCH
    assert (
        'DeclareLaunchArgument("max_steering_angle_deg", default_value="15")'
        in LAUNCH
    )
    assert '"max_steering_angle_deg", default_value="15"' in ROBOT_LAUNCH


def test_existing_chassis_driver_owns_standard_rep105_odometry():
    assert "FUNC_MOTOR" not in TRANSPORT
    assert "def set_car_motion" not in TRANSPORT
    assert 'executable="base_node_R2"' not in LAUNCH
    assert "add_executable(base_node_R2" not in CMAKE
    assert not (PACKAGE / "config" / "ackermann_steering_controller.yaml").exists()
    assert 'self.create_publisher(Odometry,"/odom",50)' in DRIVER
    assert "TransformBroadcaster(self)" in DRIVER
    assert 'odom.header.frame_id = "odom"' in DRIVER
    assert 'odom.child_frame_id = "base_link"' in DRIVER
    assert 'transform.child_frame_id = "base_link"' in DRIVER


def test_real_robot_production_entries_split_mola_from_nav2():
    assert '"operation": "mapping"' in PRODUCTION_MOLA
    assert '"use_sim_time": "false"' in PRODUCTION_MOLA
    assert "production_common_navigation.launch.py" not in PRODUCTION_MOLA
    assert "production_common_navigation.launch.py" in PRODUCTION_NAV2
    assert '"use_sim_time": "false"' in PRODUCTION_NAV2
    assert "mola_backend.launch.py" not in PRODUCTION_NAV2


def test_chassis_odometry_integrates_encoder_feedback_in_rep103_axes():
    x, y, yaw = omnifleet_ackermann_driver._integrate_planar_pose(
        0.0, 0.0, 0.0, 0.4, 0.0, 1.0
    )
    assert x == pytest.approx(0.4)
    assert y == pytest.approx(0.0)
    assert yaw == pytest.approx(0.0)

    x, y, yaw = omnifleet_ackermann_driver._integrate_planar_pose(
        x, y, yaw, 0.0, 0.5, 1.0
    )
    assert x == pytest.approx(0.4)
    assert y == pytest.approx(0.0)
    assert yaw == pytest.approx(0.5)


def test_stm32_feedback_keeps_firmware_units_explicit():
    assert "vx_mm_s, commanded_steering_deg, wz_mrad_s" in TRANSPORT
    assert "self.odom_vx = vx_mm_s / 1000.0" in TRANSPORT
    assert "self.odom_vy = float(commanded_steering_deg)" in TRANSPORT
    assert "self.odom_vz = wz_mrad_s / 1000.0" in TRANSPORT
    assert "get_transport_diagnostics" in TRANSPORT


def test_motion_packet_contains_body_velocity_not_actuator_targets():
    transport = Rosmaster.__new__(Rosmaster)
    sent = {}
    transport._send = lambda command, payload: sent.update(
        command=command, payload=payload
    )

    transport.set_motion(420.0, 0.0, -350.0)

    assert sent["command"] == Rosmaster.FUNC_MOTION
    assert struct.unpack("<Bhhh", sent["payload"]) == (0, 420, 0, -350)


def test_serial_transport_keeps_three_milliseconds_between_frames(monkeypatch):
    clock = types.SimpleNamespace(now=10.0, sleeps=[])
    monkeypatch.setattr(rosmaster_transport.time, "monotonic", lambda: clock.now)

    def advance(seconds):
        clock.sleeps.append(seconds)
        clock.now += seconds

    monkeypatch.setattr(rosmaster_transport.time, "sleep", advance)
    transport = Rosmaster.__new__(Rosmaster)
    transport.delay = 0.003
    transport.last_send_finished_time = clock.now
    transport.lock = threading.Lock()
    transport.ser = types.SimpleNamespace(write=lambda _frame: None, flush=lambda: None)

    transport._send(Rosmaster.FUNC_AKM_WATCHDOG, bytes([0]))
    transport._send(Rosmaster.FUNC_MOTION, struct.pack("<Bhhh", 0, 1000, 0, 0))

    assert clock.sleeps == pytest.approx([0.003, 0.003])


def test_stm32_motion_decoders_forward_body_velocity_without_nx_mapping():
    assert "Motion_Ctrl(Vx_recv, Vy_recv, Vz_recv" in FIRMWARE_PROTOCOL
    assert "Motion_Ctrl(Vx_recv*10, Vy_recv*10, Vz_recv*10" in FIRMWARE_PROTOCOL
    assert "Motion_Ctrl(-Vx_recv" not in FIRMWARE_PROTOCOL
    assert "Motion_Ctrl(-Vx_recv*10" not in FIRMWARE_PROTOCOL


def test_stm32_directly_applies_the_final_clamped_steering_target():
    assert "akm_servo_angle = akm_servo_target_angle;" in FIRMWARE_ACKERMANN
    assert "AKM_STEER_RATE_STEP" not in FIRMWARE_ACKERMANN
    assert "akm_servo_angle++" not in FIRMWARE_ACKERMANN
    assert "akm_servo_angle--" not in FIRMWARE_ACKERMANN


def test_servo_direction_is_flipped_once_at_the_stm32_pwm_boundary():
    assert "Ackerman_Get_Default_Angle() - akm_servo_angle" in FIRMWARE_ACKERMANN
    assert "Ackerman_Get_Default_Angle() + akm_servo_angle" not in FIRMWARE_ACKERMANN
    assert "angular = msg.angular.z * 1.0" in DRIVER


def test_stm32_runtime_steering_limit_interface_is_preserved():
    assert "FUNC_AKM_STEER_CONFIG" in FIRMWARE_PROTOCOL
    assert "Ackerman_Set_Steering_Config" in FIRMWARE_PROTOCOL
    assert "set_ackermann_steering_config" in TRANSPORT
    assert '"max_steering_angle_deg"' in LAUNCH


def test_stm32_owns_the_motion_command_watchdog():
    assert "#define MOTION_WATCHDOG_DEFAULT_TIMEOUT_MS 1000" in FIRMWARE_APP_HEADER
    assert "App_Set_Motion_Command_Watchdog_Timeout" in FIRMWARE_APP
    assert "App_Motion_Command_Watchdog_Handle();" in FIRMWARE_APP
    assert "Motion_Stop(STOP_BRAKE);" in FIRMWARE_APP
    assert "g_motion_watchdog_trigger_count++" in FIRMWARE_APP
    assert "FUNC_AKM_WATCHDOG" in FIRMWARE_PROTOCOL
    assert "cmd_vel_timeout" not in DRIVER


def test_nx_watchdog_parameters_are_exposed_without_a_linux_motion_timeout():
    assert 'DeclareLaunchArgument("motion_watchdog_timeout_ms", default_value="1000")' in LAUNCH
    assert 'DeclareLaunchArgument("watchdog_heartbeat_rate_hz", default_value="10.0")' in LAUNCH
    assert '"motion_watchdog_timeout_ms", default_value="1000"' in ROBOT_LAUNCH
    assert '"watchdog_heartbeat_rate_hz", default_value="10.0"' in ROBOT_LAUNCH
    assert "/omnifleet_a2/chassis/watchdog_status" in DRIVER
    assert "send_motion_watchdog_heartbeat" in DRIVER


def test_ackermann_m1_encoder_is_normalized_before_odometry_and_pid():
    assert "g_car_type == CAR_ACKERMAN && i == MOTOR_ID_M1" in FIRMWARE_MOTION
    assert "g_Encoder_All_Offset[i] = -g_Encoder_All_Offset[i];" in FIRMWARE_MOTION
    assert "car->Vx = (speed_mm[0] + speed_mm[1]) / 2;" in FIRMWARE_MOTION
    assert "car->Vz = (speed_mm[0] - speed_mm[1]) * 1000 / robot_APB;" in FIRMWARE_MOTION


def test_watchdog_settings_require_three_heartbeat_periods():
    omnifleet_ackermann_driver._validate_watchdog_settings(350, 10.0)
    with pytest.raises(ValueError):
        omnifleet_ackermann_driver._validate_watchdog_settings(250, 10.0)
    with pytest.raises(ValueError):
        omnifleet_ackermann_driver._validate_watchdog_settings(350, 0.5)


def test_watchdog_transport_config_heartbeat_and_status_round_trip():
    transport = Rosmaster.__new__(Rosmaster)
    transport.motion_watchdog_status = None
    transport.last_motion_watchdog_status_time = None
    sent = []
    transport._send = lambda command, payload: sent.append((command, payload))

    transport.set_motion_watchdog_timeout(350)
    transport.send_motion_watchdog_heartbeat()
    transport.request_motion_watchdog_status()

    assert sent[0][0] == Rosmaster.FUNC_AKM_WATCHDOG
    assert struct.unpack("<BH", sent[0][1]) == (1, 350)
    assert sent[1] == (Rosmaster.FUNC_AKM_WATCHDOG, bytes([0]))
    assert sent[2] == (
        Rosmaster.FUNC_REQUEST_DATA,
        bytes([Rosmaster.FUNC_AKM_WATCHDOG, 0]),
    )

    frame = bytearray(12)
    frame[3] = Rosmaster.FUNC_AKM_WATCHDOG
    frame[4:11] = struct.pack("<HHBH", 350, 42, 0x03, 7)
    transport._parse(frame)
    assert transport.get_motion_watchdog_status() == (350, 42, True, True, 7)
    assert transport.get_motion_watchdog_status_age() < 1.0


def make_cmd_vel_driver():
    driver = object.__new__(omnifleet_ackermann_driver)
    driver._motion_cmd_lock = threading.Lock()
    driver._last_cmd_log_time = float("inf")
    driver._serial_error_reported = False
    driver.motorCommandPublisher = types.SimpleNamespace(publish=lambda message: None)
    driver.car = types.SimpleNamespace(set_motion=lambda vx, vy, vz: None)
    return driver


@pytest.mark.parametrize(
    ("requested", "expected_mm_s"),
    [(0.0, 0.0), (0.05, 50.0), (-0.05, -50.0),
     (0.10, 100.0), (-0.10, -100.0), (0.75, 750.0), (-0.75, -750.0)],
)
def test_driver_preserves_linear_commands_without_floor_or_ceiling(requested, expected_mm_s):
    driver = make_cmd_vel_driver()

    message = Twist()
    message.linear.x = requested
    driver.cmd_vel_callback(message)

    assert driver._motion_cmd[0] == pytest.approx(expected_mm_s)


@pytest.mark.parametrize(
    ("requested", "expected_mrad_s"),
    [(0.0, 0.0), (0.05, 50.0), (-0.05, -50.0),
     (0.64, 640.0), (-0.64, -640.0), (1.25, 1250.0), (-1.25, -1250.0)],
)
def test_driver_preserves_angular_commands_without_nx_ceiling(requested, expected_mrad_s):
    driver = make_cmd_vel_driver()

    message = Twist()
    message.linear.x = 0.25
    message.angular.z = requested
    driver.cmd_vel_callback(message)

    assert driver._motion_cmd[2] == pytest.approx(expected_mrad_s)


def test_zero_linear_velocity_cannot_implicitly_command_steering():
    driver = make_cmd_vel_driver()

    message = Twist()
    message.linear.x = 0.0
    message.angular.z = 1.25
    driver.cmd_vel_callback(message)

    assert driver._motion_cmd == (0.0, 0.0, 0.0)


def test_manual_steering_packet_keeps_drive_control_inside_stm32():
    transport = Rosmaster.__new__(Rosmaster)
    sent = {}
    transport._send = lambda command, payload: sent.update(
        command=command, payload=payload
    )

    transport.set_ackermann_steering(-20)

    assert sent["command"] == Rosmaster.FUNC_AKM_STEER_ANGLE
    assert struct.unpack("<Bb", sent["payload"]) == (1, -20)


@pytest.mark.parametrize("requested", [-45, 45])
def test_manual_steering_packet_forwards_target_without_nx_clamp(requested):
    transport = Rosmaster.__new__(Rosmaster)
    sent = {}
    transport._send = lambda command, payload: sent.update(
        command=command, payload=payload
    )

    transport.set_ackermann_steering(requested)

    assert sent["command"] == Rosmaster.FUNC_AKM_STEER_ANGLE
    assert struct.unpack("<Bb", sent["payload"]) == (1, requested)


def test_ackermann_deadzone_pwm_packet_is_runtime_transport_parameter():
    transport = Rosmaster.__new__(Rosmaster)
    transport.ackermann_deadzone_pwm = None
    sent = {}
    transport._send = lambda command, payload: sent.update(
        command=command, payload=payload
    )

    transport.set_ackermann_deadzone_pwm(1600, 1700, 1550, 1650)

    assert sent["command"] == Rosmaster.FUNC_AKM_DEADZONE_PWM
    assert struct.unpack("<HHHH", sent["payload"]) == (1600, 1700, 1550, 1650)
    frame = bytearray(13)
    frame[3] = Rosmaster.FUNC_AKM_DEADZONE_PWM
    frame[4:12] = struct.pack("<HHHH", 1600, 1700, 1550, 1650)
    transport._parse(frame)
    assert transport.get_ackermann_deadzone_pwm() == (1600, 1700, 1550, 1650)


@pytest.mark.parametrize("center_offset", [-40, 40])
def test_ackermann_steering_config_packet_round_trips_applied_values(center_offset):
    transport = Rosmaster.__new__(Rosmaster)
    transport.ackermann_steering_config = None
    sent = {}
    transport._send = lambda command, payload: sent.update(
        command=command, payload=payload
    )

    transport.set_ackermann_steering_config(25, center_offset)

    assert sent["command"] == Rosmaster.FUNC_AKM_STEER_CONFIG
    assert struct.unpack("<Bb", sent["payload"]) == (25, center_offset)
    frame = bytearray(7)
    frame[3] = Rosmaster.FUNC_AKM_STEER_CONFIG
    frame[4:6] = struct.pack("<Bb", 25, center_offset)
    transport._parse(frame)
    assert transport.get_ackermann_steering_config() == (25, center_offset)


@pytest.mark.parametrize(
    ("max_angle", "center_offset"),
    [(0, 0), (26, 0), (25, -41), (25, 41)],
)
def test_ackermann_steering_config_rejects_unsafe_values(max_angle, center_offset):
    transport = Rosmaster.__new__(Rosmaster)
    transport.ackermann_steering_config = None
    transport._send = lambda command, payload: None

    with pytest.raises(ValueError):
        transport.set_ackermann_steering_config(max_angle, center_offset)


def test_ackermann_motor_state_packet_exposes_wheel_level_closed_loop_data():
    transport = Rosmaster.__new__(Rosmaster)
    transport.ackermann_motor_state = None
    transport.motor_state_frame_count = 0
    transport.last_motor_state_time = None
    frame = bytearray(19)
    frame[3] = Rosmaster.FUNC_AKM_MOTOR_STATE
    frame[4:18] = struct.pack("<hhhhhhH", -90, -110, -88, -105, -1810, -1920, 0x0101)

    transport._parse(frame)

    assert transport.get_ackermann_motor_state() == (
        -90, -110, -88, -105, -1810, -1920, 1, 1
    )
    assert transport.motor_state_frame_count == 1
    assert transport.last_motor_state_time is not None


def test_ros_does_not_use_a_timer_to_repeat_an_old_motion_command():
    assert "self.motion_timer" not in DRIVER
    assert "self.create_timer(self.send_motion_period" not in DRIVER
    callback = DRIVER.split("def cmd_vel_callback", 1)[1].split(
        "def steering_angle_target_callback", 1
    )[0]
    assert callback.count("self.send_motion_command()") == 1


def test_explicit_steering_is_converted_to_degrees_only_at_firmware_boundary():
    driver = object.__new__(omnifleet_ackermann_driver)
    driver._motion_cmd_lock = threading.Lock()
    driver._motion_cmd = (0.0, 0.0, 640.0)
    driver._steering_angle_target_rad = math.radians(25.0)
    driver._serial_error_reported = False
    driver._steering_stop_sent = False
    driver.motorCommandPublisher = types.SimpleNamespace(publish=lambda message: None)
    calls = []
    driver.car = types.SimpleNamespace(
        set_motion=lambda vx, vy, vz: calls.append(("motion", vx, vy, vz)),
        set_ackermann_steering=lambda angle: calls.append(("steer", angle)),
    )

    driver.send_motion_command()

    assert calls == [
        ("motion", 0.0, 0.0, 0.0),
        ("steer", 25.0),
    ]


def test_dedicated_steering_topic_forwards_target_and_stops_motion():
    driver = object.__new__(omnifleet_ackermann_driver)
    driver._motion_cmd_lock = threading.Lock()
    driver._motion_cmd = (420.0, 0.0, 350.0)
    driver._steering_angle_target_rad = None
    driver._steering_stop_sent = True
    driver.get_logger = lambda: types.SimpleNamespace(
        info=lambda message: None,
        warning=lambda message: None,
        error=lambda message: None,
    )
    driver._serial_error_reported = False
    driver.motorCommandPublisher = types.SimpleNamespace(publish=lambda message: None)
    calls = []
    driver.car = types.SimpleNamespace(
        set_motion=lambda vx, vy, vz: calls.append(("motion", vx, vy, vz)),
        set_ackermann_steering=lambda angle: calls.append(("steer", angle)),
    )

    message = SteeringAngleCommand()
    message.steering_angle_rad = math.radians(40.0)
    driver.steering_angle_target_callback(message)

    assert driver._motion_cmd == (0.0, 0.0, 0.0)
    assert driver._steering_angle_target_rad == pytest.approx(math.radians(40.0))
    assert driver._steering_stop_sent is True
    assert calls[-1] == ("steer", pytest.approx(40.0))

    driver._steering_stop_sent = True
    message.steering_angle_rad = math.radians(-25.0)
    driver.steering_angle_target_callback(message)

    assert driver._steering_angle_target_rad == pytest.approx(math.radians(-25.0))
    assert driver._steering_stop_sent is True


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
