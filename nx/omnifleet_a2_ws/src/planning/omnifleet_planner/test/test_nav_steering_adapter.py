from geometry_msgs.msg import Twist

from omnifleet_planner.nav_steering_adapter import (
    adapt_navigation_twist,
    scale_angular_z,
)


def test_navigation_adapter_only_reverses_yaw_command():
    source = Twist()
    source.linear.x = 0.2
    source.linear.y = 0.03
    source.angular.x = 0.01
    source.angular.z = -0.17

    output = scale_angular_z(source, -1.0)

    assert output.linear.x == 0.2
    assert output.linear.y == 0.03
    assert output.angular.x == 0.01
    assert output.angular.z == 0.17
    assert source.angular.z == -0.17


def test_navigation_adapter_maps_subdeadband_speed_before_collision_monitor():
    source = Twist()
    source.linear.x = 0.10
    source.angular.z = -0.05

    output = adapt_navigation_twist(source, -1.0, 0.31, 0.30)

    assert output.linear.x == 0.31
    assert abs(output.angular.z - 0.155) < 1.0e-12
    assert source.linear.x == 0.10
    assert source.angular.z == -0.05


def test_navigation_adapter_preserves_reverse_and_caps_scaled_yaw():
    source = Twist()
    source.linear.x = -0.05
    source.angular.z = -0.20

    output = adapt_navigation_twist(source, -1.0, 0.31, 0.30)

    assert output.linear.x == -0.31
    assert output.angular.z == 0.30


def test_navigation_adapter_rejects_in_place_nav_rotation():
    source = Twist()
    source.angular.z = 0.20

    output = adapt_navigation_twist(source, -1.0, 0.31, 0.30)

    assert output.linear.x == 0.0
    assert output.angular.z == 0.0
