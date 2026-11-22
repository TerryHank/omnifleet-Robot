import importlib.util
import sys
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).parents[1] / "scripts" / "integration" / "gesture_person_follow_node.py"
spec = importlib.util.spec_from_file_location("gesture_person_follow", SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def hand_with_extended(count):
    points = np.zeros((21, 3), dtype=np.float32)
    points[0, :2] = (0, 0)
    points[9, :2] = (0, 10)
    thumb_open = count >= 5
    points[1, :2], points[2, :2] = (1, 3), (2, 5)
    points[3, :2] = (2, 7 if thumb_open else 4)
    points[4, :2] = (2, 10 if thumb_open else 3)
    for index, chain in enumerate(module.FINGER_CHAINS[1:], 1):
        _, pip, dip, tip = chain
        is_open = index <= count
        points[pip, :2] = (index + 1, 5)
        points[dip, :2] = (index + 1, 7 if is_open else 4)
        points[tip, :2] = (index + 1, 10 if is_open else 3)
    return points


def test_gesture_counts():
    assert module.classify_hand(hand_with_extended(0))[0] == "fist"
    assert module.classify_hand(hand_with_extended(1))[0] == "1"
    assert module.classify_hand(hand_with_extended(2))[0] == "2"
    assert module.classify_hand(hand_with_extended(3))[0] == "3"
    assert module.classify_hand(hand_with_extended(5))[0] == "open_palm"


def test_state_machine_follow_cancel_and_manual_modes():
    state = module.GestureState()
    for gesture, expected in (("open_palm", "follow_started"), ("fist", "follow_cancelled"),
                              ("1", "forward"), ("2", "reverse"), ("3", "rotate")):
        state.last_confirmed = "unknown"
        state.candidate = "unknown"
        assert state.update(gesture, 2) is None
        assert state.update(gesture, 2) == expected


def test_depth_median_and_range_filter():
    depth = np.zeros((4, 4), dtype=np.uint16)
    depth[1:3, 1:3] = ((800, 900), (1000, 2000))
    assert module.median_depth_m(depth, 2, 2, (4, 4), radius=1) == 0.9


def test_numeric_gesture_velocity_mapping():
    assert module.manual_velocity("forward") == (0.20, 0.0)
    assert module.manual_velocity("reverse") == (-0.15, 0.0)
    assert module.manual_velocity("rotate") == (0.0, 0.50)
    assert module.manual_velocity("idle") == (0.0, 0.0)


def test_first_recognized_fist_stops_and_cancels_follow():
    state = module.GestureState(mode="follow")
    assert state.update("fist") == "follow_cancelled"
    assert state.mode == "idle"
    assert state.update("open_palm") == "follow_started"


def test_wholebody_preprocess_normalizes_only_model_sized_image():
    blob, center, scale = module.SingleWholebodyPipeline.preprocess(np.zeros((1280, 1536, 3), np.uint8))
    assert blob.shape == (1, 3, 256, 192)
    assert blob.dtype == np.float32 and blob.flags.c_contiguous
    np.testing.assert_allclose(center, [768, 640])
    np.testing.assert_allclose(scale, [1920, 2560])
    np.testing.assert_allclose(blob[0, :, 128, 96], -np.array([123.675, 116.28, 103.53]) /
                               np.array([58.395, 57.12, 57.375]), rtol=1e-6)


def test_wholebody_one_forward_returns_body_and_both_hand_outputs():
    x = np.zeros((1, 133, 384), np.float32)
    y = np.zeros((1, 133, 512), np.float32)
    for index in range(133):
        x[0, index, 160 + index % 40] = .8
        y[0, index, 200 + index % 60] = .9

    class Session:
        calls = 0

        def run(self, names, inputs):
            self.calls += 1
            assert inputs['input'].shape == (1, 3, 256, 192)
            return x, y

    pipeline = module.SingleWholebodyPipeline.__new__(module.SingleWholebodyPipeline)
    pipeline.session, pipeline.input_name = Session(), 'input'
    person, pose, hand = pipeline.infer(np.zeros((256, 192, 3), np.uint8))
    assert pipeline.session.calls == pipeline.calls_last_frame == 1
    assert person.shape == (4,) and pose[1].shape == (17, 5) and hand.shape == (67,)
    points, scores = pipeline.decode([x, y], np.array([96., 128.]), np.array([240., 320.]))
    np.testing.assert_allclose(points[0], [76., 93.])
    np.testing.assert_allclose(scores, .8)
    x.fill(0)
    y.fill(0)
    assert pipeline.infer(np.zeros((256, 192, 3), np.uint8)) == (None, None, None)
    assert pipeline.session.calls == 2 and pipeline.calls_last_frame == 1
