from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "omnifleet_a2_bringup"
    / "omnifleet_ackermann_driver.py"
).read_text(encoding="utf-8")


def test_raw_imu_declares_missing_orientation_and_covariances():
    assert "imu.orientation_covariance[0] = -1.0" in SOURCE
    assert "imu.angular_velocity_covariance[index]" in SOURCE
    assert "imu.linear_acceleration_covariance[index]" in SOURCE


def test_magnetometer_is_converted_from_firmware_units_to_tesla():
    assert "magnetic_field_tesla_per_raw_unit', 1.0e-9" in SOURCE
    assert "mx * self.magnetic_field_tesla_per_raw_unit" in SOURCE
    assert "mag.magnetic_field_covariance[index]" in SOURCE


def test_firmware_version_topics_use_the_omnifleet_a2_namespace():
    assert 'Float32,"/omnifleet_a2/chassis/edition"' in SOURCE
    assert 'String,"/omnifleet_a2/chassis/firmware_version"' in SOURCE
    assert 'Float32,"edition"' not in SOURCE


def test_joint_state_does_not_fake_motion_with_random_positions():
    assert "random.uniform" not in SOURCE
