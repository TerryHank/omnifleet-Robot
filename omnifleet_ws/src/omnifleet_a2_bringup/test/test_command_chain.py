from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]


def test_chassis_is_a_direct_single_point_command_bridge():
    source = (PACKAGE / "launch" / "chassis_core.launch.py").read_text()

    assert not (PACKAGE / "config" / "safety_mux.yaml").exists()
    assert not (PACKAGE / "scripts" / "keyboard_teleop").exists()
    assert not (PACKAGE / "scripts" / "teleop_command_repeater").exists()
    assert not (PACKAGE / "omnifleet_a2_bringup" / "teleop_command_repeater.py").exists()
    assert 'package="twist_mux"' not in source
    assert 'name="omnifleet_command_mux"' not in source
    assert 'name="teleop_command_repeater"' not in source
    assert 'package="nav2_collision_monitor"' not in source
    assert 'name="lifecycle_manager_chassis_safety"' not in source
    assert 'name="chassis_collision_lidar_filter"' not in source
    assert "cmd_vel_timeout" not in source
    assert '"steering_angle_target_topic"' in source
    assert '"/omnifleet_a2/chassis/steering_angle_cmd"' in source
    assert "xlinear_limit" not in source
    assert "minimum_linear_speed" not in source
    assert 'executable="base_node_R2"' not in source
    assert 'executable="stm32_feedback_adapter"' not in source
    assert 'executable="voltage_display_node.py"' not in source

    driver = (PACKAGE / "omnifleet_a2_bringup" / "omnifleet_ackermann_driver.py").read_text()
    assert 'self.create_subscription(Twist,"cmd_vel",self.cmd_vel_callback,1)' in driver
    assert "emergency_stop_callback" not in driver
    assert "cmd_vel_timeout" not in driver
    assert "math.copysign" not in driver
    assert "steering_angle_target_callback" in driver
    assert "angular = 0.0" in driver
    assert "motor_command.linear.y" not in driver
    assert "twist.linear.y" not in driver
    assert "SteeringAngleCommand" in driver
    assert "steering_angle_rad" in driver
    assert "steering_angle_feedback_deg" not in driver
    assert "self.motion_timer" not in driver
    assert "minimum_linear_speed" not in driver
    assert "xlinear_limit" not in driver
    assert 'self.create_publisher(Twist,"/omnifleet_a2/chassis/motor_command_sent",20)' in driver
    assert 'Float32MultiArray,"/omnifleet_a2/chassis/motor_state_raw",20' in driver
    for parameter in (
        "motor_deadzone_pwm_m1_forward",
        "motor_deadzone_pwm_m2_forward",
        "motor_deadzone_pwm_m1_reverse",
        "motor_deadzone_pwm_m2_reverse",
    ):
        assert parameter in source
    assert '"motor_deadzone_pwm_m1_forward": 2050' in source
    assert '"motor_deadzone_pwm_m2_forward": 2250' in source
    assert '"motor_deadzone_pwm_m1_reverse": 2000' in source
    assert '"motor_deadzone_pwm_m2_reverse": 2200' in source
    assert "motor_start_pwm" not in source
    assert "motor_run_pwm" not in source


def test_boot_selfcheck_audits_the_single_final_cmd_vel_owner():
    source = (PACKAGE / "omnifleet_a2_bringup" / "boot_selfcheck.py").read_text()

    assert '["ros2", "topic", "info", "/cmd_vel", "-v"]' in source
    assert 'publisher_count in (0, 1)' in source
    assert "expected_publishers" not in source
    assert '"Subscription count: 1"' not in source
