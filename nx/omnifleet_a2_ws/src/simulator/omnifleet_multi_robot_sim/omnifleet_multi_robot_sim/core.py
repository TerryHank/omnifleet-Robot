"""ROS-independent fleet assignment and Ackermann control helpers."""

from dataclasses import dataclass
from math import atan2, cos, hypot, isfinite, pi, sin
from typing import Iterable, Mapping, Optional, Tuple


@dataclass(frozen=True)
class Pose2D:
    x: float
    y: float
    yaw: float = 0.0


def normalize_angle(angle: float) -> float:
    """Return an angle in [-pi, pi)."""
    return (angle + pi) % (2.0 * pi) - pi


def ackermann_command(
    pose: Pose2D,
    goal: Tuple[float, float],
    max_speed: float = 0.32,
    max_yaw_rate: float = 0.75,
    goal_tolerance: float = 0.15,
) -> Tuple[float, float]:
    """Return (linear speed, yaw rate) without commanding an in-place turn."""
    dx, dy = goal[0] - pose.x, goal[1] - pose.y
    distance = hypot(dx, dy)
    if distance <= goal_tolerance:
        return 0.0, 0.0

    heading_error = normalize_angle(atan2(dy, dx) - pose.yaw)
    reverse = abs(heading_error) > pi / 2.0
    if reverse:
        heading_error = normalize_angle(heading_error - (pi if heading_error > 0 else -pi))

    speed = min(max_speed, max(0.08, 0.65 * distance))
    speed *= max(0.25, cos(heading_error))
    if reverse:
        speed = -speed
    yaw_rate = max(-max_yaw_rate, min(max_yaw_rate, 1.8 * heading_error))
    return speed, yaw_rate


def nearest_available_robot(
    goal: Tuple[float, float],
    poses: Mapping[str, Pose2D],
    available: Iterable[str],
) -> Optional[str]:
    candidates = [name for name in available if name in poses]
    if not candidates:
        return None
    return min(candidates, key=lambda name: hypot(poses[name].x - goal[0], poses[name].y - goal[1]))


def normalize_waypoints(points: Iterable[Tuple[float, float]]) -> Tuple[Tuple[float, float], ...]:
    """Validate and freeze a non-empty finite waypoint sequence."""
    waypoints = tuple((float(x), float(y)) for x, y in points)
    if not waypoints:
        raise ValueError("waypoint path is empty")
    if not all(isfinite(x) and isfinite(y) for x, y in waypoints):
        raise ValueError("waypoints must contain finite coordinates")
    return waypoints


def nearest_robot_for_route(
    waypoints: Iterable[Tuple[float, float]],
    poses: Mapping[str, Pose2D],
    available: Iterable[str],
) -> Optional[str]:
    """Choose a route owner using distance to its first waypoint."""
    route = normalize_waypoints(waypoints)
    return nearest_available_robot(route[0], poses, available)


def safety_speed_scale(distance: float, stop_distance: float = 0.55, slow_distance: float = 0.8) -> float:
    """Linearly reduce speed inside the slow zone and stop at the hard limit."""
    if distance <= stop_distance:
        return 0.0
    if distance >= slow_distance:
        return 1.0
    return (distance - stop_distance) / (slow_distance - stop_distance)
