from pathlib import Path

import yaml


PACKAGE = Path(__file__).resolve().parents[1]


def test_chassis_owns_the_single_permanent_command_mux():
    config = yaml.safe_load((PACKAGE / "config" / "safety_mux.yaml").read_text())
    collision = yaml.safe_load(
        (PACKAGE / "config" / "collision_monitor.yaml").read_text()
    )["collision_monitor"]["ros__parameters"]
    mux = config["rrc_command_mux"]["ros__parameters"]
    source = (PACKAGE / "launch" / "chassis_core.launch.py").read_text()

    assert mux["topics"]["teleop"]["topic"] == "/cmd_vel_teleop_repeated"
    assert mux["topics"]["keyboard"]["topic"] == "/cmd_vel_keyboard"
    assert mux["topics"]["keyboard"]["priority"] > mux["topics"]["teleop"]["priority"]
    assert mux["topics"]["keyboard"]["timeout"] == 0.5
    assert mux["topics"]["vision"]["topic"] == "/cmd_vel_vision"
    assert mux["topics"]["vision"]["timeout"] == 0.3
    assert mux["topics"]["navigation"]["priority"] < mux["topics"]["vision"]["priority"]
    assert mux["topics"]["vision"]["priority"] < mux["topics"]["teleop"]["priority"]
    assert mux["topics"]["navigation"]["topic"] == "/cmd_vel_nav_adjusted"
    assert mux["topics"]["navigation"]["timeout"] == 0.5
    assert mux["topics"]["zero"]["priority"] == 255
    assert "locks" not in mux
    assert source.count('package="twist_mux"') == 1
    assert 'name="rrc_command_mux"' in source
    assert 'name="teleop_command_repeater"' in source
    assert '"input_timeout": 0.60' in source
    assert 'remappings=[("/cmd_vel_out", "/cmd_vel_muxed")]' in source
    assert source.count('package="nav2_collision_monitor"') == 1
    assert 'name="lifecycle_manager_chassis_safety"' in source
    assert 'name="chassis_collision_lidar_filter"' not in source
    assert collision["cmd_vel_in_topic"] == "/cmd_vel_muxed"
    assert collision["cmd_vel_out_topic"] == "/cmd_vel"
    assert collision["lidar"]["topic"] == "/navigation/deskewed_points"
    assert collision["source_timeout"] == 1.0
    assert collision["base_shift_correction"] is False
    assert collision["polygons"] == ["EmergencyStop"]
    assert collision["EmergencyStop"]["action_type"] == "stop"
    assert collision["EmergencyStop"]["points"] == [0.85, 0.28, 0.85, -0.28, -0.22, -0.28, -0.22, 0.28]
    assert 'DeclareLaunchArgument("cmd_vel_timeout", default_value="0.35")' in source
    assert '"xlinear_limit": 0.40' in source
    assert '"minimum_linear_speed": 0.0' in source
    assert 'executable="base_node_R2"' not in source
    assert 'executable="stm32_feedback_adapter"' in source

    keyboard = (PACKAGE / "scripts" / "keyboard_teleop").read_text()
    assert "cmd_vel:=/cmd_vel_keyboard" in keyboard
    assert "speed:=0.20" in keyboard
    assert "turn:=0.20" in keyboard
    assert "repeat_rate:=0.0" in keyboard

    driver = (PACKAGE / "omnifleet_bringup" / "Ackman_driver_R2.py").read_text()
    assert "/rrc_safety/zero_lock" not in driver
    assert "_emergency_stop_active" not in driver
    assert 'self.create_publisher(Twist,"/motor_command_sent",20)' in driver
