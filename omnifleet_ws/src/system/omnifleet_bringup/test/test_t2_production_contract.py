from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
DRIVER = (PACKAGE.parents[1] / "vehicle" / "omnifleet_chassis_driver" / "omnifleet_chassis_driver" / "omnifleet_t2_driver.py").read_text()
ROSMASTER = (PACKAGE.parents[1] / "vehicle" / "omnifleet_chassis_driver" / "omnifleet_chassis_driver" / "Rosmaster_Lib.py").read_text()
RAW_PWM = (PACKAGE.parents[1] / "vehicle" / "omnifleet_chassis_driver" / "omnifleet_chassis_driver" / "raw_pwm_cli.py").read_text()
CHASSIS = (PACKAGE / "launch" / "chassis_core.launch.py").read_text()
ROBOT = (PACKAGE / "launch" / "robot.launch.py").read_text()
PRODUCTION = (PACKAGE / "launch" / "production.launch.py").read_text()
PRODUCTION_MOLA = (PACKAGE / "launch" / "production_mola.launch.py").read_text()
KCF = (PACKAGE.parents[1] / "perception" / "omnifleet_tutorials" / "launch" / "robot_kcf.launch.py").read_text()


def test_driver_owns_standard_odometry_and_tf():
    assert 'self.create_publisher(Odometry, "/odom", 50)' in DRIVER
    assert "TransformBroadcaster(self)" in DRIVER
    assert 'self.declare_parameter("publish_odom_tf", True)' in DRIVER
    assert 'self.get_parameter("publish_odom_tf").value' in DRIVER
    assert "transform.header.frame_id = self.odom_frame" in DRIVER
    assert "transform.child_frame_id = self.base_frame" in DRIVER
    assert 'track_separation_m", 0.33' in DRIVER
    assert 'DeclareLaunchArgument("publish_odom_tf", default_value="true")' in CHASSIS
    assert 'LaunchConfiguration("publish_odom_tf"), value_type=bool' in CHASSIS


def test_all_host_side_tracked_kinematics_use_330_mm_separation():
    assert "track_width_mm = 330.0" in ROSMASTER
    assert "track_width_mm = 369.0" not in ROSMASTER


def test_chassis_transport_preserves_requested_linear_speed():
    assert 'vx = float(linear_x)' in DRIVER
    assert 'max_linear_speed_mps' not in DRIVER
    assert 'max_linear_speed_mps' not in CHASSIS


def test_tracked_pwm_compensation_is_stm32_owned_and_read_back():
    assert "FUNC_TRACKED_PWM_COMP = 0x16" in ROSMASTER
    assert "def get_tracked_pwm_compensation" in ROSMASTER
    assert "def set_tracked_pwm_compensation" in ROSMASTER
    assert "struct.pack('<HHB', values[0], values[1], 0x5F)" in ROSMASTER
    assert 'self.declare_parameter("pwm_compensation_m1", 2736)' in DRIVER
    assert 'self.declare_parameter("pwm_compensation_m2", 2772)' in DRIVER
    assert "self.add_on_set_parameters_callback(self.set_runtime_parameters)" in DRIVER
    assert "底盘存在非零运动指令" in DRIVER


def test_raw_pwm_is_nx_adjustable_and_separate_from_navigation():
    assert 'for name in ("start", "set")' in RAW_PWM
    assert 'if not -100 <= value <= 100' in RAW_PWM
    assert 'packet(0x10' in RAW_PWM
    assert 'Refusing raw PWM while navigation is active' in RAW_PWM
    assert 'systemctl", "start", CHASSIS_SERVICE' in RAW_PWM


def test_driver_publishes_human_readable_voltage_for_foxglove():
    assert 'String, "/voltage/display", 20' in DRIVER
    assert 'voltage_display.data = f"{voltage.data:.1f} V"' in DRIVER


def test_production_chain_has_no_adapter_or_mux():
    assert "stm32_feedback_adapter" not in CHASSIS
    assert "/cmd_vel_nav_raw" not in ROBOT
    assert "nav_steering_adapter" not in ROBOT
    assert 'localization_backend", default_value="mola"' in ROBOT
    assert 'planner_mode", default_value="smac_2d"' in ROBOT
    assert 'controller_mode", default_value="dwb"' in ROBOT


def test_upper_launches_never_manage_the_chassis_service():
    for source in (ROBOT, PRODUCTION, PRODUCTION_MOLA, KCF):
        assert "chassis_core.launch.py" not in source
        assert 'DeclareLaunchArgument("start_chassis"' not in source
        assert 'DeclareLaunchArgument("start_chassis_core"' not in source
        assert 'executable="t2_driver"' not in source


def test_t2_serial_alias_is_the_only_default():
    assert "/dev/omnifleet_t2_stm32" in DRIVER
    assert "/dev/omnifleet_t2_stm32" in CHASSIS
