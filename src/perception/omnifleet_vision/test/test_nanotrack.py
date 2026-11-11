from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/integration'))
from nanotrack_core import HybridTracks, source_stamp


class Tracker:
    def __init__(self, bbox):self.box=list(bbox)
    def update(self,image):
        self.box[0]+=2
        return True, self.box
    def getTrackingScore(self):return .9


class Factory:
    cuda=False
    def __init__(self):self.created=0
    def create(self,image,bbox):
        self.created+=1
        return Tracker(bbox)


def detection(label,x=20):
    return dict(**{'class':label},confidence=.95,bbox=[x,20,30,40])


def test_dict_camera_stamp_is_preserved():
    assert source_stamp({'stamp':{'sec':10,'nanosec':250000000}},99)==10.25


def test_visual_prediction_keeps_detector_identity_and_expires():
    factory=Factory();core=HybridTracks(factory,'unused',timeout=1.)
    frame=np.zeros((100,160,3),np.uint8)
    core.detect([detection('red')],frame,1,1,0)
    first=core.update(frame,1,1,.1)
    core.detect([detection('red',22)],frame,1,1,.2)
    second=core.update(frame,1,1,.3)
    assert factory.created==1
    assert first[0]['track_id']==second[0]['track_id']
    assert second[0]['bbox'][0]>first[0]['bbox'][0]
    assert core.update(frame,1,1,1.3)==[]


def test_multiple_object_ids_do_not_mix_classes():
    factory=Factory();core=HybridTracks(factory,'unused')
    frame=np.zeros((100,160,3),np.uint8)
    core.detect([detection('red'),detection('blue',70)],frame,1,1,0)
    tracks=core.update(frame,1,1,.1)
    assert len({t['track_id'] for t in tracks})==2
    assert all(t['tracker']=='NanoTrack' for t in tracks)


def test_person_uses_real_botsort_without_nanotrack():
    pytest.importorskip('ultralytics')
    config=Path(__file__).resolve().parents[2]/'omnifleet_person_follow/config/botsort.yaml'
    factory=Factory();core=HybridTracks(factory,str(config))
    frame=np.zeros((100,160,3),np.uint8)
    core.detect([detection('person')],frame,1,1,0)
    first=core.update(frame,1,1,.1)
    core.detect([detection('person',22)],frame,1,1,.2)
    second=core.update(frame,1,1,.3)
    assert factory.created==0
    assert first[0]['tracker']==second[0]['tracker']=='BoT-SORT'
    assert first[0]['track_id']==second[0]['track_id']


def test_mixed_person_and_object_ids_are_distinct():
    pytest.importorskip('ultralytics')
    config=Path(__file__).resolve().parents[2]/'omnifleet_person_follow/config/botsort.yaml'
    factory=Factory();core=HybridTracks(factory,str(config))
    frame=np.zeros((100,160,3),np.uint8)
    core.detect([detection('person'),detection('chair',80)],frame,1,1,0)
    tracks=core.update(frame,1,1,.1)
    assert len(tracks)==2 and len({t['track_id'] for t in tracks})==2
    assert factory.created==1


def test_human_case_launches_keep_existing_person_package():
    launch=(Path(__file__).resolve().parents[1]/'launch/course_function.launch.py').read_text()
    for name in ['04_08_gesture_person_follow','04_09_body_tracking']:
        body=launch.split('"'+name+'": lambda:',1)[1].split('],',1)[0]
        assert 'omnifleet_person_follow' in body
        assert 'nanotrack_node' not in body
