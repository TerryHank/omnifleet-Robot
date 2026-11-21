from argparse import ArgumentTypeError
from math import pi

from omnifleet_multi_robot_sim.core import (
    Pose2D,
    ackermann_command,
    nearest_available_robot,
    nearest_robot_for_route,
    normalize_angle,
    normalize_waypoints,
    safety_speed_scale,
)
import pytest

from omnifleet_multi_robot_sim.multi_waypoint_verifier import parse_waypoints_json


def test_angle_normalization():
    assert normalize_angle(3 * pi) == -pi
    assert abs(normalize_angle(-0.2) + 0.2) < 1e-9


def test_forward_reverse_and_no_in_place_rotation():
    forward = ackermann_command(Pose2D(0, 0, 0), (1, 0))
    reverse = ackermann_command(Pose2D(0, 0, pi), (1, 0))
    stopped = ackermann_command(Pose2D(0, 0, 0), (0.1, 0))
    assert forward[0] > 0 and forward[1] == 0
    assert reverse[0] < 0
    assert stopped == (0.0, 0.0)


def test_nearest_available_assignment():
    poses = {"robot1": Pose2D(0, 0), "robot2": Pose2D(3, 0)}
    assert nearest_available_robot((2.5, 0), poses, ["robot1", "robot2"]) == "robot2"
    assert nearest_available_robot((0, 0), poses, []) is None


def test_safety_scaling_contract():
    assert safety_speed_scale(0.5) == 0.0
    assert safety_speed_scale(0.8) == 1.0
    assert 0.0 < safety_speed_scale(0.65) < 1.0


def test_waypoint_validation_rejects_empty_and_non_finite_routes():
    assert normalize_waypoints([(0, 1), (2.5, -3)]) == ((0.0, 1.0), (2.5, -3.0))
    with pytest.raises(ValueError, match="empty"):
        normalize_waypoints([])
    with pytest.raises(ValueError, match="finite"):
        normalize_waypoints([(float("nan"), 0)])


@pytest.mark.parametrize("count", [1, 3, 5, 8, 32])
def test_waypoint_validation_preserves_arbitrary_route_length(count):
    route = [(index * 0.25, index * -0.1) for index in range(count)]
    assert len(normalize_waypoints(route)) == count


def test_waypoint_cli_json_accepts_variable_lengths_and_rejects_bad_shapes():
    assert len(parse_waypoints_json("[[0,0]]")) == 1
    assert len(parse_waypoints_json("[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0]]")) == 8
    with pytest.raises(ArgumentTypeError, match="array of"):
        parse_waypoints_json('{"x": 1}')


def test_route_assignment_uses_only_the_first_waypoint():
    poses = {"robot1": Pose2D(0, 0), "robot2": Pose2D(5, 0)}
    route = [(4.5, 0), (-10, 0)]
    assert nearest_robot_for_route(route, poses, poses) == "robot2"
