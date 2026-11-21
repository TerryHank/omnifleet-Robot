from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]


def test_chassis_follow_programs_are_safe_and_mutually_exclusive():
    for filename in ("human_follow_chassis.launch.py", "kcf_follow_chassis.launch.py"):
        source = (PACKAGE / "launch" / filename).read_text()
        assert 'default_value="false"' in source
        assert "Nav2 must be stopped" in source
        assert "visual_follow_steering_adapter" not in source
        assert '"angular_scale"' not in source
        assert '"presteer_settle_sec"' not in source
        assert '"command_input_timeout_sec"' not in source
        assert '"reject_parallel_publishers"' not in source


def test_human_and_kcf_follow_programs_select_the_expected_rgbd_functions():
    human = (PACKAGE / "launch" / "human_follow_chassis.launch.py").read_text()
    kcf = (PACKAGE / "launch" / "kcf_follow_chassis.launch.py").read_text()
    assert '"course_function": "04_02_human_object_follow"' in human
    assert '"course_function": "02_07_kcf"' in kcf
    assert '"tracking_scale": LaunchConfiguration("tracking_scale")' in kcf
