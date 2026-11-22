from types import SimpleNamespace as NS
import numpy as np
from omnifleet_person_follow.perception import Perception


def test_missing_hand_acquisition_is_person_crop_and_one_detector_call_per_frame():
    seen = []
    pipeline = Perception.__new__(Perception)
    pipeline.cached_hands, pipeline.acquisition_index = [], 0
    pipeline.palm = NS(infer=lambda image:(seen.append(image.shape) or []))
    tracks = [dict(id=1, bbox=[50,50,250,350], mask=np.ones((512,512),bool)),
              dict(id=2, bbox=[400,50,800,650], mask=np.ones((512,512),bool))]
    image = np.zeros((1280,1536,3),np.uint8)
    pipeline.hands(image, tracks, None)
    assert len(seen) == 1 and seen[0][:2] == (216,240)
    pipeline.hands(image, tracks, None)
    assert len(seen) == 2 and seen[1][0] <= 640
    pipeline.hands(image, tracks, 1)
    assert len(seen) == 3 and seen[-1][:2] == (216,240)


def test_small_person_alternates_magnified_upper_crop_with_whole_body():
    crops = []
    pipeline = Perception.__new__(Perception)
    pipeline.cached_hands, pipeline.acquisition_index = [], 0
    pipeline.palm = NS(infer=lambda image: (crops.append(image.shape[:2]) or []))
    image = np.zeros((480,640,3),np.uint8)
    track = dict(id=1, bbox=[240,100,340,320], mask=np.ones((512,512),bool))
    pipeline.hands(image, [track], None)
    pipeline.hands(image, [track], None)
    assert crops == [(316,240), (242,120)]


def test_small_palm_landmarks_return_to_camera_coordinates():
    pipeline = Perception.__new__(Perception)
    image = np.zeros((480,640,3),np.uint8)
    palm = np.array([290.,155.,310.,175.]+[300.,165.]*7+[.9])
    def infer(roi, local):
        assert roi.shape[:2] == (200,200)
        assert np.all(local[4:18].reshape(7,2) == [100.,100.])
        result = np.zeros(132)
        result[:4] = local[:4]
        result[4:67] = [100.,100.,20.]*21
        return result
    pipeline.hand = NS(infer=infer)
    result = pipeline.infer_hand(image,palm)
    assert np.all(result[:4] == palm[:4])
    assert np.all(result[4:67].reshape(21,3) == [300.,165.,10.])
