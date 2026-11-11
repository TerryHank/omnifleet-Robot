from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
SOURCE = (
    PACKAGE / "omnifleet_bringup" / "stm32_feedback_adapter.py"
).read_text(encoding="utf-8")


def test_feedback_adapter_wraps_stm32_twist_without_kinematics():
    assert 'Twist, "/vel_raw"' in SOURCE
    assert 'Odometry, "/wheel/odometry"' in SOURCE
    assert "feedback.linear.x" in SOURCE
    assert "feedback.angular.z" in SOURCE
    assert "wheelbase" not in SOURCE
    assert "tan(" not in SOURCE
    assert "cos(" not in SOURCE
    assert "sin(" not in SOURCE
    assert "delta_heading" not in SOURCE
