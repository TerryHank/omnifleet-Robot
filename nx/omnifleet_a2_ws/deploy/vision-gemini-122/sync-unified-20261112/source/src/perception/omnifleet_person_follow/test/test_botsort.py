from pathlib import Path
from types import SimpleNamespace
import cv2
import numpy as np
import yaml
from ultralytics.engine.results import Boxes
from ultralytics.trackers.bot_sort import BOTSORT


def configured():
    settings=yaml.safe_load((Path(__file__).parents[1]/'config/botsort.yaml').read_text())
    return BOTSORT(SimpleNamespace(**settings))


def detections(score, x=60.):
    return Boxes(np.array([[x,40,x+60,180,score,0]],dtype=np.float32),(240,320))


def test_low_confidence_continues_existing_id_but_cannot_create_one():
    image=np.zeros((240,320,3),np.uint8)
    tracker=configured()
    assert not len(tracker.update(detections(.2),image))
    tracker=configured()
    initial=tracker.update(detections(.9),image)
    continued=tracker.update(detections(.2,62),image)
    assert len(initial)==len(continued)==1
    assert initial[0,4]==continued[0,4] and continued[0,5] < .7


def test_sparse_flow_compensates_camera_shift():
    rng=np.random.default_rng(17)
    gray=(rng.random((240,320))*255).astype(np.uint8)
    image=cv2.cvtColor(cv2.GaussianBlur(gray,(3,3),0),cv2.COLOR_GRAY2BGR)
    tracker=configured()
    first=tracker.update(detections(.9),image)
    # Incremental camera displacement crosses an object's original width.
    for shift in [12,24,36,48,60,72]:
        moved=cv2.warpAffine(image,np.array([[1.,0.,shift],[0.,1.,0.]]),(320,240))
        result=tracker.update(detections(.9,60+shift),moved)
        assert len(result)==1 and result[0,4]==first[0,4]
    assert tracker.gmc.method=='sparseOptFlow' and tracker.encoder is None
