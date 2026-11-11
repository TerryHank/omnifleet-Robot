import math

import pytest

from omnifleet_localization.vector_math import normalize_quaternion, rotate_vector_inverse


def test_normalize_quaternion_rejects_zero_length():
    with pytest.raises(ValueError):
        normalize_quaternion((0.0, 0.0, 0.0, 0.0))


def test_inverse_rotation_converts_odom_velocity_to_base_frame():
    half = math.sqrt(0.5)
    velocity = rotate_vector_inverse((1.0, 0.0, 0.0), (0.0, 0.0, half, half))
    assert velocity == pytest.approx((0.0, -1.0, 0.0), abs=1.0e-9)
