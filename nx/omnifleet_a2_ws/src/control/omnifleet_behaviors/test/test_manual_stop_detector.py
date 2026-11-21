from omnifleet_behaviors.foxglove_nav_bridge import HoldToStopDetector


def test_direction_release_single_zero_does_not_stop_stack():
    detector = HoldToStopDetector(required_messages=3, window_sec=0.35)

    assert detector.observe(True, 1.0) is False


def test_center_hold_triggers_once_after_repeated_zero_messages():
    detector = HoldToStopDetector(required_messages=3, window_sec=0.35)

    assert detector.observe(True, 1.0) is False
    assert detector.observe(True, 1.1) is False
    assert detector.observe(True, 1.2) is True
    assert detector.observe(True, 1.3) is False


def test_nonzero_command_resets_the_hold_detector():
    detector = HoldToStopDetector(required_messages=3, window_sec=0.35)

    assert detector.observe(True, 1.0) is False
    assert detector.observe(True, 1.1) is False
    assert detector.observe(False, 1.15) is False
    assert detector.observe(True, 1.2) is False
    assert detector.observe(True, 1.3) is False
    assert detector.observe(True, 1.4) is True


def test_slow_zero_messages_do_not_form_a_center_hold():
    detector = HoldToStopDetector(required_messages=3, window_sec=0.35)

    assert detector.observe(True, 1.0) is False
    assert detector.observe(True, 1.5) is False
    assert detector.observe(True, 2.0) is False
