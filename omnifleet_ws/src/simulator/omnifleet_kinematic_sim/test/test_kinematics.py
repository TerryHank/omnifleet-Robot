import math

from omnifleet_kinematic_sim.ackermann_sim_driver import solve_ackermann


GEOMETRY = dict(
    wheel_base=0.362295943,
    front_track=0.264956799,
    rear_track=0.245400019,
    max_steering=0.523599,
)


def test_straight_motion_has_equal_wheel_speeds():
    result = solve_ackermann(0.2, 0.0, **GEOMETRY)
    assert result.yaw_rate == 0.0
    assert result.left_steering == 0.0
    assert result.right_steering == 0.0
    assert result.front_left_speed == result.front_right_speed == 0.2
    assert result.rear_left_speed == result.rear_right_speed == 0.2


def test_left_arc_has_ackermann_inner_outer_geometry():
    result = solve_ackermann(0.2, 0.15, **GEOMETRY)
    assert result.yaw_rate > 0.0
    assert result.left_steering > result.right_steering > 0.0
    assert result.rear_left_speed < result.rear_right_speed


def test_right_arc_is_symmetric():
    left = solve_ackermann(0.2, 0.15, **GEOMETRY)
    right = solve_ackermann(0.2, -0.15, **GEOMETRY)
    assert math.isclose(left.yaw_rate, -right.yaw_rate, rel_tol=1e-9)
    assert math.isclose(left.left_steering, -right.right_steering, rel_tol=1e-9)
    assert math.isclose(left.right_steering, -right.left_steering, rel_tol=1e-9)


def test_reverse_preserves_requested_yaw_direction():
    result = solve_ackermann(-0.2, 0.1, **GEOMETRY)
    assert result.velocity < 0.0
    assert result.yaw_rate > 0.0
    assert result.center_steering < 0.0


def test_zero_speed_cannot_create_in_place_rotation():
    result = solve_ackermann(0.0, 0.3, stationary_steering=0.4, **GEOMETRY)
    assert result.velocity == 0.0
    assert result.yaw_rate == 0.0
    assert result.center_steering == 0.4
    assert result.front_left_speed == result.rear_right_speed == 0.0


def test_steering_limit_reduces_unreachable_yaw_rate():
    result = solve_ackermann(0.2, 10.0, **GEOMETRY)
    assert math.isclose(result.center_steering, GEOMETRY["max_steering"])
    assert result.yaw_rate < 1.0
