from pathlib import Path

import yaml


PACKAGE = Path(__file__).resolve().parents[1]


def test_chassis_owns_the_single_permanent_command_mux():
    config = yaml.safe_load((PACKAGE / "config" / "safety_mux.yaml").read_text())
    mux = config["rrc_command_mux"]["ros__parameters"]
    source = (PACKAGE / "launch" / "chassis_core.launch.py").read_text()

    assert mux["topics"]["teleop"]["topic"] == "/cmd_vel_teleop"
    assert mux["topics"]["navigation"]["topic"] == "/cmd_vel_nav_safe"
    assert mux["topics"]["zero"]["priority"] == 255
    assert mux["locks"]["safety"]["topic"] == "/rrc_safety/zero_lock"
    assert source.count('package="twist_mux"') == 1
    assert 'name="rrc_command_mux"' in source
    assert '"base_footprint_frame": "base_link"' in source
    assert 'remappings=[("/cmd_vel_out", "/cmd_vel")]' in source
    assert '"xlinear_limit": 0.80' in source
    assert '"minimum_linear_speed": 0.45' in source
