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
    assert len(seen) == 1 and seen[0][:2] == (330,240)
    pipeline.hands(image, tracks, None)
    assert len(seen) == 2 and seen[1][0] <= 640
    pipeline.hands(image, tracks, 1)
    assert len(seen) == 3 and seen[-1][:2] == (330,240)
