from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ROOT = PACKAGE_ROOT.parents[2]


def test_kinematic_launch_is_serial_free_and_namespaced():
    text = (PACKAGE_ROOT / "launch" / "multi_robot_kinematic.launch.py").read_text()
    assert "omnifleet_kinematic_sim" in text
    assert "ackermann_sim_driver" in text
    assert "initial_x" in text
    assert "initial_y" in text
    assert '"/cmd_vel", f"/{name}/cmd_vel"' in text
    assert '"/odom", f"/{name}/odom"' in text
    assert '"startup_settle_time": 5.0' in text
    assert "gazebo_ros" not in text
    assert "/dev/myserial" not in text


def test_remote_kinematic_smoke_scripts_exist():
    scripts = DELIVERY_ROOT / "scripts"
    for name in (
        "smoke_test_multi_robot_kinematic.sh",
        "smoke_test_multi_waypoint_kinematic.sh",
    ):
        script = (scripts / name).read_text()
        assert "--kinematic" in script
