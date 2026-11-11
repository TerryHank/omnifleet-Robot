from dataclasses import dataclass
import math
from typing import Iterable, Optional


@dataclass(frozen=True)
class VoiceCommand:
    command_id: int
    phrase: str
    kind: str
    target_x: float = 0.0
    speed: float = 0.0
    angular_z: float = 0.0
    duration_sec: float = 0.0
    segments: tuple = ()


@dataclass(frozen=True)
class DirectSegment:
    duration_sec: float
    linear_x: float = 0.0
    angular_z: float = 0.0
    steering_angle_rad: Optional[float] = None


TURN_ANGULAR_SPEED = 0.64
QUARTER_TURN_DURATION_SEC = math.pi / (2.0 * TURN_ANGULAR_SPEED)
HALF_TURN_DURATION_SEC = math.pi / TURN_ANGULAR_SPEED
FULL_TURN_DURATION_SEC = 2.0 * math.pi / TURN_ANGULAR_SPEED
DIRECT_MIN_SPEED = 0.40
DIRECT_MAX_SPEED = 0.55
DIRECT_SPEED_STEP = 0.05


def _drive(duration_sec, angular_z=0.0):
    return DirectSegment(
        duration_sec=duration_sec,
        linear_x=DIRECT_MIN_SPEED,
        angular_z=angular_z,
    )


def _reverse(duration_sec):
    return DirectSegment(duration_sec=duration_sec, linear_x=-DIRECT_MIN_SPEED)


def _pause(duration_sec=0.15):
    return DirectSegment(duration_sec=duration_sec)


def _steer(duration_sec, angle_deg):
    return DirectSegment(
        duration_sec=duration_sec,
        steering_angle_rad=math.radians(angle_deg),
    )


COMMANDS = {
    1: VoiceCommand(
        1, "前进", "drive_on_heading", target_x=0.4, speed=DIRECT_MIN_SPEED
    ),
    2: VoiceCommand(
        2, "后退", "backup", target_x=-0.4, speed=DIRECT_MIN_SPEED
    ),
    # REP-103: positive angular.z turns left/CCW; negative turns right/CW.
    3: VoiceCommand(
        3,
        "左转",
        "direct_twist",
        speed=DIRECT_MIN_SPEED,
        angular_z=TURN_ANGULAR_SPEED,
        duration_sec=QUARTER_TURN_DURATION_SEC,
    ),
    4: VoiceCommand(
        4,
        "右转",
        "direct_twist",
        speed=DIRECT_MIN_SPEED,
        angular_z=-TURN_ANGULAR_SPEED,
        duration_sec=QUARTER_TURN_DURATION_SEC,
    ),
    9: VoiceCommand(9, "停下", "stop"),
    0x0D: VoiceCommand(0x0D, "加速", "speed_up"),
    0x0E: VoiceCommand(0x0E, "减速", "speed_down"),
    0x1C: VoiceCommand(
        0x1C,
        "露一手",
        "direct_sequence",
        segments=(
            _drive(1.2, TURN_ANGULAR_SPEED),
            _drive(2.4, -TURN_ANGULAR_SPEED),
            _drive(1.2, TURN_ANGULAR_SPEED),
        ),
    ),
    0x1D: VoiceCommand(
        0x1D,
        "走两步",
        "drive_on_heading",
        target_x=0.8,
        speed=DIRECT_MIN_SPEED,
    ),
    0x1E: VoiceCommand(
        0x1E,
        "摇头",
        "direct_sequence",
        segments=(
            _steer(0.5, 30.0),
            _steer(1.0, -30.0),
            _steer(0.5, 30.0),
        ),
    ),
    0x1F: VoiceCommand(
        0x1F, "向前扑", "direct_sequence", segments=(_drive(0.6),)
    ),
    0x20: VoiceCommand(
        0x20, "向后扑", "direct_sequence", segments=(_reverse(0.6),)
    ),
    0x21: VoiceCommand(
        0x21,
        "战斗模式",
        "direct_sequence",
        segments=(
            _drive(0.5),
            _pause(),
            _reverse(0.5),
            _pause(),
            _drive(0.5),
            _pause(),
            _reverse(0.5),
        ),
    ),
    0x23: VoiceCommand(
        0x23,
        "抖一抖",
        "direct_sequence",
        segments=(
            _drive(0.25),
            _reverse(0.25),
            _drive(0.25),
            _reverse(0.25),
            _drive(0.25),
            _reverse(0.25),
        ),
    ),
    0x26: VoiceCommand(
        0x26,
        "转动舵机",
        "direct_sequence",
        segments=(_steer(0.8, 30.0), _steer(0.8, -30.0)),
    ),
    0x6C: VoiceCommand(
        0x6C,
        "跳舞",
        "direct_sequence",
        segments=(
            _drive(0.8, TURN_ANGULAR_SPEED),
            _drive(1.6, -TURN_ANGULAR_SPEED),
            _drive(0.8, TURN_ANGULAR_SPEED),
            _reverse(0.5),
            _drive(0.5),
            _drive(0.8, -TURN_ANGULAR_SPEED),
            _drive(1.6, TURN_ANGULAR_SPEED),
            _drive(0.8, -TURN_ANGULAR_SPEED),
        ),
    ),
    0x76: VoiceCommand(
        0x76,
        "原地踏步",
        "direct_sequence",
        segments=(
            _drive(0.4),
            _reverse(0.4),
            _drive(0.4),
            _reverse(0.4),
        ),
    ),
    0x78: VoiceCommand(
        0x78,
        "大摇大摆",
        "direct_sequence",
        segments=(
            _drive(1.0, TURN_ANGULAR_SPEED),
            _drive(2.0, -TURN_ANGULAR_SPEED),
            _drive(2.0, TURN_ANGULAR_SPEED),
            _drive(1.0, -TURN_ANGULAR_SPEED),
        ),
    ),
    0x7B: VoiceCommand(0x7B, "关闭玩法", "stop"),
    # The flashed table has no phrase named "自转一圈". Its reserved
    # "执行动作一" command sends protocol ID 0x80, used here for one
    # forward Ackermann circle (the chassis cannot rotate in place).
    0x80: VoiceCommand(
        0x80,
        "执行动作一",
        "direct_twist",
        speed=DIRECT_MIN_SPEED,
        angular_z=TURN_ANGULAR_SPEED,
        duration_sec=FULL_TURN_DURATION_SEC,
    ),
    0x81: VoiceCommand(
        0x81,
        "执行动作二",
        "direct_twist",
        speed=DIRECT_MIN_SPEED,
        angular_z=-TURN_ANGULAR_SPEED,
        duration_sec=FULL_TURN_DURATION_SEC,
    ),
    0x82: VoiceCommand(
        0x82,
        "执行动作三",
        "direct_sequence",
        segments=(
            _drive(FULL_TURN_DURATION_SEC, TURN_ANGULAR_SPEED),
            _drive(FULL_TURN_DURATION_SEC, -TURN_ANGULAR_SPEED),
        ),
    ),
    0x83: VoiceCommand(
        0x83,
        "执行动作四",
        "direct_twist",
        speed=DIRECT_MIN_SPEED,
        angular_z=TURN_ANGULAR_SPEED,
        duration_sec=HALF_TURN_DURATION_SEC,
    ),
    0x84: VoiceCommand(
        0x84,
        "执行动作五",
        "direct_twist",
        speed=DIRECT_MIN_SPEED,
        angular_z=-TURN_ANGULAR_SPEED,
        duration_sec=HALF_TURN_DURATION_SEC,
    ),
}


def direct_motion_profile(
    command: VoiceCommand, max_distance: float, cruise_speed=None
):
    configured_speed = (
        abs(float(command.speed))
        if cruise_speed is None
        else abs(float(cruise_speed))
    )
    if command.kind == "direct_twist":
        speed = math.copysign(configured_speed, command.speed)
        angular_z = float(command.angular_z)
        duration_sec = float(command.duration_sec)
        if speed == 0.0 or angular_z == 0.0 or duration_sec <= 0.0:
            raise ValueError("direct turn requires nonzero speed and duration")
        if not all(
            math.isfinite(value) for value in (speed, angular_z, duration_sec)
        ):
            raise ValueError("direct turn profile must be finite")
        return 0.0, speed, angular_z, duration_sec

    target_x = math.copysign(
        min(abs(command.target_x), float(max_distance)), command.target_x
    )
    speed = math.copysign(configured_speed, target_x)
    if speed == 0.0:
        raise ValueError("direct motion speed must not be zero")
    return target_x, speed, 0.0, abs(target_x) / abs(speed)


def direct_motion_segments(
    command: VoiceCommand, max_distance: float, cruise_speed: float
):
    cruise_speed = abs(float(cruise_speed))
    if not DIRECT_MIN_SPEED <= cruise_speed <= DIRECT_MAX_SPEED:
        raise ValueError("direct cruise speed is outside the safe range")
    if not command.segments:
        _, linear_x, angular_z, duration_sec = direct_motion_profile(
            command, max_distance, cruise_speed
        )
        return (
            DirectSegment(
                duration_sec=duration_sec,
                linear_x=linear_x,
                angular_z=angular_z,
            ),
        )

    result = []
    for segment in command.segments:
        values = (
            segment.duration_sec,
            segment.linear_x,
            segment.angular_z,
        )
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("direct sequence values must be finite")
        if (
            segment.steering_angle_rad is not None
            and not math.isfinite(float(segment.steering_angle_rad))
        ):
            raise ValueError("direct steering angle must be finite")
        if segment.duration_sec <= 0.0:
            raise ValueError("direct sequence duration must be positive")
        linear_x = 0.0
        if segment.linear_x != 0.0:
            linear_x = math.copysign(cruise_speed, segment.linear_x)
        result.append(
            DirectSegment(
                duration_sec=float(segment.duration_sec),
                linear_x=linear_x,
                angular_z=float(segment.angular_z),
                steering_angle_rad=(
                    None
                    if segment.steering_angle_rad is None
                    else float(segment.steering_angle_rad)
                ),
            )
        )
    if sum(segment.duration_sec for segment in result) > 20.0:
        raise ValueError("direct sequence duration exceeds 20 seconds")
    return tuple(result)


ACTIVE_ACTION_STATUSES = frozenset({1, 2, 3})
MONITORED_ACTIONS = (
    "navigate_to_pose",
    "navigate_through_poses",
    "follow_waypoints",
    "follow_path",
    "assisted_teleop",
    "drive_on_heading",
    "backup",
)
CONFLICTING_NAV_ACTIONS = frozenset(MONITORED_ACTIONS[:5])


def active_action_present(statuses: Iterable[int]) -> bool:
    return any(int(status) in ACTIVE_ACTION_STATUSES for status in statuses)


def voice_cancel_required(
    voice_busy: bool, action_name: str, statuses: Iterable[int]
) -> bool:
    return (
        bool(voice_busy)
        and action_name in CONFLICTING_NAV_ACTIONS
        and active_action_present(statuses)
    )


class CommandEdgeFilter:
    """Emit changing, non-zero result IDs and cool down repeated IDs."""

    def __init__(self, same_id_cooldown_sec: float, cooldown_exempt_ids=()):
        if same_id_cooldown_sec < 0.0:
            raise ValueError("same_id_cooldown_sec must not be negative")
        self._cooldown = float(same_id_cooldown_sec)
        self._cooldown_exempt_ids = frozenset(
            int(command_id) for command_id in cooldown_exempt_ids
        )
        self._armed = False
        self._previous_raw = 0
        self._last_emitted_at = {}

    def disarm(self) -> None:
        self._armed = False

    def observe(self, raw_id: int, now_sec: float) -> Optional[int]:
        raw_id = int(raw_id)
        if not 0 <= raw_id <= 255:
            raise ValueError("WonderEcho result ID must fit in one byte")

        if not self._armed:
            # A device can retain a result across a process restart. Treat the
            # first successful sample as a baseline so restart cannot move it.
            self._armed = True
            self._previous_raw = raw_id
            if raw_id in self._cooldown_exempt_ids:
                self._last_emitted_at[raw_id] = float(now_sec)
                return raw_id
            return None

        changed = raw_id != self._previous_raw
        self._previous_raw = raw_id
        if raw_id == 0 or not changed:
            return None

        last_emitted = self._last_emitted_at.get(raw_id)
        if (
            raw_id not in self._cooldown_exempt_ids
            and last_emitted is not None
            and now_sec - last_emitted < self._cooldown
        ):
            return None
        self._last_emitted_at[raw_id] = float(now_sec)
        return raw_id
