import math

import pytest

from omnifleet_behaviors.voice_commands import (
    COMMANDS,
    CommandEdgeFilter,
    DIRECT_MAX_SPEED,
    DIRECT_MIN_SPEED,
    DIRECT_SPEED_STEP,
    FULL_TURN_DURATION_SEC,
    HALF_TURN_DURATION_SEC,
    MONITORED_ACTIONS,
    QUARTER_TURN_DURATION_SEC,
    active_action_present,
    direct_motion_profile,
    direct_motion_segments,
    voice_cancel_required,
)
from omnifleet_behaviors.wonderecho_device import (
    WonderEchoDevice,
    WonderEchoSerialDevice,
    WonderEchoSerialParser,
)


class FakeBus:
    def __init__(self, bus_number):
        self.bus_number = bus_number
        self.reads = [0]
        self.writes = []
        self.closed = False

    def read_i2c_block_data(self, address, register, length):
        assert length == 1
        return self.reads

    def write_i2c_block_data(self, address, register, values):
        self.writes.append((address, register, values))

    def close(self):
        self.closed = True


class FakeSerial:
    def __init__(self, data=b""):
        self.data = bytearray(data)
        self.closed = False

    @property
    def in_waiting(self):
        return len(self.data)

    def read(self, size):
        chunk = bytes(self.data[:size])
        del self.data[:size]
        return chunk

    def close(self):
        self.closed = True


def test_command_contract_uses_configured_motion_profiles():
    assert (COMMANDS[1].kind, COMMANDS[1].target_x, COMMANDS[1].speed) == (
        "drive_on_heading",
        0.4,
        0.40,
    )
    assert (COMMANDS[2].kind, COMMANDS[2].target_x, COMMANDS[2].speed) == (
        "backup",
        -0.4,
        0.40,
    )
    assert (COMMANDS[29].kind, COMMANDS[29].target_x, COMMANDS[29].speed) == (
        "drive_on_heading",
        0.8,
        0.40,
    )
    assert COMMANDS[9].kind == "stop"
    assert (COMMANDS[3].kind, COMMANDS[3].speed, COMMANDS[3].angular_z) == (
        "direct_twist",
        0.40,
        0.64,
    )
    assert (COMMANDS[4].kind, COMMANDS[4].speed, COMMANDS[4].angular_z) == (
        "direct_twist",
        0.40,
        -0.64,
    )
    assert (COMMANDS[0x80].phrase, COMMANDS[0x80].kind) == (
        "执行动作一",
        "direct_twist",
    )
    assert COMMANDS[0x0D].kind == "speed_up"
    assert COMMANDS[0x0E].kind == "speed_down"
    assert COMMANDS[0x7B].kind == "stop"
    assert COMMANDS[0x81].angular_z == -0.64
    assert COMMANDS[0x83].duration_sec == pytest.approx(
        HALF_TURN_DURATION_SEC
    )
    assert COMMANDS[0x84].duration_sec == pytest.approx(
        HALF_TURN_DURATION_SEC
    )
    assert (DIRECT_MIN_SPEED, DIRECT_MAX_SPEED, DIRECT_SPEED_STEP) == (
        0.40,
        0.55,
        0.05,
    )


@pytest.mark.parametrize(
    ("command_id", "expected"),
    [
        (1, (0.4, 0.4, 0.0, 1.0)),
        (2, (-0.4, -0.4, 0.0, 1.0)),
        (29, (0.8, 0.4, 0.0, 2.0)),
    ],
)
def test_direct_twist_profile_uses_bounded_duration(command_id, expected):
    assert direct_motion_profile(COMMANDS[command_id], 0.8) == expected


def test_direct_twist_profile_honors_distance_limit():
    assert direct_motion_profile(COMMANDS[29], 0.4) == (0.4, 0.4, 0.0, 1.0)


@pytest.mark.parametrize(
    ("command_id", "expected_angular", "expected_duration"),
    [
        (3, 0.64, QUARTER_TURN_DURATION_SEC),
        (4, -0.64, QUARTER_TURN_DURATION_SEC),
        (0x80, 0.64, FULL_TURN_DURATION_SEC),
    ],
)
def test_direct_turn_profiles(command_id, expected_angular, expected_duration):
    target_x, speed, angular_z, duration_sec = direct_motion_profile(
        COMMANDS[command_id], 0.8
    )
    assert target_x == 0.0
    assert speed == 0.40
    assert angular_z == expected_angular
    assert duration_sec == pytest.approx(expected_duration)


def test_direct_profile_uses_selected_cruise_speed():
    assert direct_motion_profile(COMMANDS[1], 0.8, 0.50) == (
        0.4,
        0.5,
        0.0,
        0.8,
    )
    assert direct_motion_profile(COMMANDS[2], 0.8, 0.50) == (
        -0.4,
        -0.5,
        0.0,
        0.8,
    )


def test_show_off_sequence_is_bounded_s_curve():
    segments = direct_motion_segments(COMMANDS[0x1C], 0.8, 0.40)
    assert len(segments) == 3
    assert [segment.angular_z for segment in segments] == [0.64, -0.64, 0.64]
    assert sum(segment.duration_sec for segment in segments) == pytest.approx(4.8)
    assert all(segment.linear_x == 0.40 for segment in segments)


def test_steering_sequences_keep_drive_wheels_stopped():
    for command_id in (0x1E, 0x26):
        segments = direct_motion_segments(COMMANDS[command_id], 0.8, 0.40)
        assert all(segment.linear_x == 0.0 for segment in segments)
        assert all(
            abs(segment.steering_angle_rad) == pytest.approx(math.radians(30.0))
            for segment in segments
        )


def test_figure_eight_is_one_left_and_one_right_circle():
    segments = direct_motion_segments(COMMANDS[0x82], 0.8, 0.40)
    assert [segment.angular_z for segment in segments] == [0.64, -0.64]
    assert sum(segment.duration_sec for segment in segments) == pytest.approx(
        2.0 * FULL_TURN_DURATION_SEC
    )


@pytest.mark.parametrize("speed", [0.39, 0.56])
def test_direct_sequences_reject_speed_outside_safe_range(speed):
    with pytest.raises(ValueError):
        direct_motion_segments(COMMANDS[0x1C], 0.8, speed)


def test_edge_filter_ignores_startup_value_and_held_register():
    edge = CommandEdgeFilter(2.0)
    assert edge.observe(1, 0.0) is None
    assert edge.observe(1, 0.1) is None
    assert edge.observe(0, 0.2) is None
    assert edge.observe(1, 0.3) == 1
    assert edge.observe(1, 0.4) is None


def test_edge_filter_applies_same_id_cooldown_after_zero_edge():
    edge = CommandEdgeFilter(2.0)
    assert edge.observe(0, 0.0) is None
    assert edge.observe(1, 0.1) == 1
    assert edge.observe(0, 0.2) is None
    assert edge.observe(1, 1.0) is None
    assert edge.observe(0, 1.1) is None
    assert edge.observe(1, 2.2) == 1


def test_stop_edge_is_never_suppressed_by_same_id_cooldown():
    edge = CommandEdgeFilter(2.0, cooldown_exempt_ids=(9, 0x7B))
    assert edge.observe(0, 0.0) is None
    assert edge.observe(9, 0.1) == 9
    assert edge.observe(0, 0.2) is None
    assert edge.observe(9, 0.3) == 9
    assert edge.observe(0, 0.4) is None
    assert edge.observe(0x7B, 0.5) == 0x7B


def test_stop_is_emitted_even_when_it_is_the_first_device_sample():
    edge = CommandEdgeFilter(2.0, cooldown_exempt_ids=(9,))
    assert edge.observe(9, 0.0) == 9
    assert edge.observe(9, 0.1) is None


def test_reconnect_disarm_treats_held_motion_as_a_new_baseline():
    edge = CommandEdgeFilter(2.0, cooldown_exempt_ids=(9,))
    assert edge.observe(0, 0.0) is None
    assert edge.observe(1, 0.1) == 1
    edge.disarm()
    assert edge.observe(1, 3.0) is None
    edge.disarm()
    assert edge.observe(9, 4.0) == 9


@pytest.mark.parametrize(
    "action_name",
    [
        "navigate_to_pose",
        "navigate_through_poses",
        "follow_waypoints",
        "follow_path",
        "assisted_teleop",
    ],
)
def test_new_navigation_activity_cancels_busy_voice_goal(action_name):
    assert voice_cancel_required(True, action_name, [2])
    assert not voice_cancel_required(False, action_name, [2])
    assert not voice_cancel_required(True, action_name, [4])


def test_only_nonterminal_action_states_block_motion():
    assert active_action_present([1])
    assert active_action_present([2])
    assert active_action_present([3])
    assert not active_action_present([0, 4, 5, 6])


def test_follow_path_is_monitored_for_gate_and_stop_cancellation():
    assert "follow_path" in MONITORED_ACTIONS
    assert voice_cancel_required(True, "follow_path", [2])


def test_device_uses_documented_result_and_speak_registers():
    fake = FakeBus(1)
    device = WonderEchoDevice(bus_factory=lambda number: fake)
    assert device.read_command() == 0
    device.speak_command(29)
    assert fake.writes == [(0x34, 0x6E, [0x00, 29])]
    device.close()
    assert fake.closed


def test_serial_parser_handles_fragmentation_noise_and_bad_tail():
    parser = WonderEchoSerialParser()
    assert parser.feed(b"\x10\xAA") == []
    assert parser.feed(b"\x55\x03\x00\xFB") == [(3, 0)]
    assert parser.feed(b"\xAA\x55\x00\x01\x00") == []
    assert parser.feed(b"\xAA\x55\x00\x09\xFB") == [(0, 9)]


@pytest.mark.parametrize(
    ("frame", "event"),
    [
        (b"\xAA\x55\x03\x00\xFB", (3, 0)),
        (b"\xAA\x55\x00\x01\xFB", (0, 1)),
        (b"\xAA\x55\x00\x09\xFB", (0, 9)),
        (b"\xAA\x55\x00\x0D\xFB", (0, 0x0D)),
        (b"\xAA\x55\x00\x1C\xFB", (0, 0x1C)),
        (b"\xAA\x55\x00\x7B\xFB", (0, 0x7B)),
        (b"\xAA\x55\x00\x80\xFB", (0, 0x80)),
        (b"\xAA\x55\x00\x84\xFB", (0, 0x84)),
        (b"\xAA\x55\x02\x00\xFB", (2, 0)),
    ],
)
def test_serial_parser_matches_generated_communication_table(frame, event):
    assert WonderEchoSerialParser().feed(frame) == [event]


def test_serial_device_returns_discrete_wake_and_command_events():
    fake = FakeSerial(
        b"\xAA\x55\x03\x00\xFB\xAA\x55\x00\x01\xFB"
    )
    device = WonderEchoSerialDevice(
        serial_factory=lambda **_kwargs: fake
    )
    assert device.read_event() == (3, 0)
    assert device.read_event() == (0, 1)
    assert device.read_event() is None
    device.close()
    assert fake.closed


@pytest.mark.parametrize("port", ["", "   "])
def test_serial_device_rejects_empty_port(port):
    with pytest.raises(ValueError):
        WonderEchoSerialDevice(port=port)


@pytest.mark.parametrize("address", [0x02, 0x78])
def test_device_rejects_invalid_i2c_address(address):
    with pytest.raises(ValueError):
        WonderEchoDevice(address=address, bus_factory=FakeBus)
