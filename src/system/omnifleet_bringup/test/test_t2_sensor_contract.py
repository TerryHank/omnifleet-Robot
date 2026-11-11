from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[3]
    / "vehicle"
    / "omnifleet_chassis_driver"
    / "omnifleet_chassis_driver"
    / "omnifleet_t2_driver.py"
).read_text(encoding="utf-8")


def test_raw_imu_declares_missing_orientation_and_covariances():
    assert "imu.orientation_covariance[0] = -1.0" in SOURCE
    assert "imu.angular_velocity_covariance[index]" in SOURCE
    assert "imu.linear_acceleration_covariance[index]" in SOURCE


def test_magnetometer_is_converted_to_tesla():
    assert '"magnetic_field_tesla_per_raw_unit", 1.0e-9' in SOURCE
    assert "mx * self.mag_scale" in SOURCE
    assert "mag.magnetic_field_covariance[index]" in SOURCE


def test_standard_status_and_feedback_topics_are_kept():
    for topic in (
        '"/firmware/version"', '"/voltage"', '"/vel_raw"',
        '"/imu/data_raw"', '"/imu/mag"', '"/motor_command_sent"',
    ):
        assert topic in SOURCE


def test_planar_odometry_has_nonzero_six_dof_covariance():
    for covariance in ("pose.covariance", "twist.covariance"):
        assert f"odometry.{covariance}[14] = 1.0" in SOURCE
        assert f"odometry.{covariance}[21] = 0.01" in SOURCE
        assert f"odometry.{covariance}[28] = 0.01" in SOURCE
