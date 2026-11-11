from pathlib import Path


ROOT = Path(__file__).parents[1]
LAUNCH = (ROOT / "launch" / "multi_robot_classic.launch.py").read_text(encoding="utf-8")
WORLD = (ROOT / "worlds" / "multi_robot_open.world").read_text(encoding="utf-8")
RVIZ = (ROOT / "rviz" / "multi_robot.rviz").read_text(encoding="utf-8")


def test_three_robot_launch_contract():
    for name, x, y in (("robot1", "-1.5", "0.0"), ("robot2", "-2.5", "1.2"), ("robot3", "-2.5", "-1.2")):
        assert f'("{name}", "{x}", "{y}")' in LAUNCH
    assert 'f"{name}/odom"' in LAUNCH
    assert '"gui", default_value="true"' in LAUNCH
    assert '"rviz", default_value="true"' in LAUNCH
    assert '"foxglove", default_value="true"' in LAUNCH
    assert '"foxglove_port", default_value="8796"' in LAUNCH
    assert '"auto_demo", default_value="true"' in LAUNCH
    assert "mapping_sensors:=false stable_drive:=true" in LAUNCH
    assert '"-robot_namespace"' not in LAUNCH


def test_global_tf_and_world_connectivity_contract():
    assert '("tf", "/tf")' in LAUNCH
    assert '("tf_static", "/tf_static")' in LAUNCH
    assert '"--frame-id", "world"' in LAUNCH
    assert 'f"{name}/odom"' in LAUNCH
    assert "$(arg frame_prefix)imu_link" in (Path(__file__).parents[3] / "vehicle" / "omnifleet_description" / "urdf" / "lunshi_ackermann_lite_gazebo_classic.urdf.xacro").read_text(encoding="utf-8")
    for name in ("robot1", "robot2", "robot3"):
        assert f"TF Prefix: {name}\n" in RVIZ
        assert f"TF Prefix: {name}/" not in RVIZ
        assert f"{name}//" not in RVIZ
        assert f"Value: /{name}/robot_description" in RVIZ


def test_world_keeps_three_corridors_open():
    assert 'filename="libgazebo_ros_state.so"' in WORLD
    assert "north_boundary" in WORLD and "south_boundary" in WORLD
    assert "target_robot1" in WORLD and "target_robot2" in WORLD and "target_robot3" in WORLD
    assert "<collision" not in WORLD.split('name="target_robot1"', 1)[1].split("</model>", 1)[0]
