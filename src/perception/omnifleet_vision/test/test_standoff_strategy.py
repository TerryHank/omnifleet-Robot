from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "integration"))
from standoff_strategy import StandoffStrategy


def target(identity=1, color="red", distance=1.2, x=280):
    return dict(track_id=identity, **{"class": color}, bbox=[x, 160, 80, 100], depth_m=distance)


def update(control, *items, now=0.):
    return control.update(dict(image_width=640, detections=list(items)), now)


def test_forward_hold_reverse_hysteresis():
    s = StandoffStrategy()
    assert update(s, target(distance=1.2))[0] > 0
    assert update(s, target(distance=.98))[0] > 0
    assert update(s, target(distance=.94))[0] == 0
    assert update(s, target(distance=.98))[0] == 0
    assert update(s, target(distance=.5))[0] < 0
    assert update(s, target(distance=.62))[0] < 0
    assert update(s, target(distance=.7))[0] == 0
    assert update(s, target(distance=.62))[0] == 0


def test_existing_id_wins_over_center_and_detection_order():
    s = StandoffStrategy()
    update(s, target())
    result = update(s, target(identity=2, x=280), target(x=370), now=.1)
    assert result[3]["locked_id"] == 1


def test_missing_id_does_not_jump_to_far_target():
    s = StandoffStrategy()
    update(s, target())
    result = update(s, target(identity=2, x=20), now=.2)
    assert result[:2] == (0., 0.)
    assert result[3]["locked_id"] == 1


def test_short_gap_rebinds_nearby_same_color():
    s = StandoffStrategy()
    update(s, target())
    update(s, now=.1)
    result = update(s, target(identity=8, x=285), now=.2)
    assert result[3]["locked_id"] == 8
    assert result[0] > 0


def test_other_color_cannot_take_lock_even_after_timeout():
    s = StandoffStrategy()
    update(s, target())
    assert update(s, target(identity=2, color="blue"), now=4.)[0] == 0
    assert s.locked_id == 1


def test_expired_lock_can_reacquire_same_color_elsewhere():
    s = StandoffStrategy()
    update(s, target())
    result = update(s, target(identity=9, x=190), now=2.)
    assert result[3]["locked_id"] == 9


def test_center_first_and_turn_hysteresis():
    s = StandoffStrategy()
    assert update(s, target(x=450))[3]["motion_state"] == "ALIGN"
    assert update(s, target(x=450))[0] == 0
    assert update(s, target(x=340))[0] == 0
    assert update(s, target(x=300))[0] > 0


@pytest.mark.parametrize("distance", [None, float("nan"), 0.])
def test_invalid_depth_does_not_command_translation(distance):
    s = StandoffStrategy()
    assert update(s, target(distance=distance))[0] == 0


def test_loss_resets_previous_distance_state():
    s = StandoffStrategy()
    update(s, target(distance=1.2))
    update(s, now=.1)
    assert update(s, target(distance=.98), now=.2)[0] == 0
