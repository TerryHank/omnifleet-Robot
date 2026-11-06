from pathlib import Path
from types import SimpleNamespace
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/integration'))
from nanotrack_core import HybridTracks


class Factory:
    cuda=False
    def __init__(self):self.inputs=[];self.created=0
    def create(self,image,bbox):
        self.created+=1
        self.inputs.append(image.copy());owner=self
        class Tracker:
            def init(self,image,bbox):owner.inputs.append(image.copy())
            def update(self,image):owner.inputs.append(image.copy());return True,bbox
            def getTrackingScore(self):return .8
        return Tracker()


def test_expired_target_reuses_model_but_initializes_a_new_template_and_id():
    factory=Factory();core=HybridTracks(factory,'unused',foreground=observation,timeout=.5)
    image=np.full((100,160,3),30,np.uint8)
    item=dict(**{'class':'object'},confidence=.9,bbox=[10,10,90,80])
    core.detect([item],image,1,1,0)
    first=core.update(image,1,1,.1)[0]['track_id']
    assert core.update(image,1,1,.7)==[]
    core.detect([item],image,1,1,.8)
    second=core.update(image,1,1,.9)[0]['track_id']
    assert second!=first and len(core.retired)==0 and factory.created==1


def observation(image,item,bbox):
    prepared=np.full_like(image,127);prepared[20:60,30:60]=image[20:60,30:60]
    return prepared,dict(item,bbox=[30,20,30,40],center=[45,40],
        foreground=dict(available=True,source='test_semantic',depth_m=1.2))


def test_object_initialization_and_update_both_receive_foreground_pixels():
    factory=Factory();core=HybridTracks(factory,'unused',foreground=observation)
    image=np.full((100,160,3),30,np.uint8)
    core.detect([dict(**{'class':'object'},confidence=.9,bbox=[10,10,90,80])],image,1,1,0)
    result=core.update(image,1,1,.1)[0]
    assert len(factory.inputs)==2
    assert all(np.array_equal(frame[0,0],[127]*3) for frame in factory.inputs)
    assert all(np.array_equal(frame[30,40],[30]*3) for frame in factory.inputs)
    assert result['bbox']==[30,20,30,40] and result['center']==[45,40]


def test_person_observation_is_refined_before_botsort_and_gmc_keeps_raw_image():
    factory=Factory();core=HybridTracks(factory,'unused',foreground=observation)
    image=np.full((100,160,3),30,np.uint8);received=[]
    def update(boxes,frame):
        received.append((boxes.xyxy.copy(),frame))
        return np.array([[30,20,60,60,1,.9,0,0]],np.float32)
    core.person_tracker=SimpleNamespace(update=update,tracked_stracks=[],lost_stracks=[])
    core.detect([dict(**{'class':'person'},confidence=.9,bbox=[10,10,90,80])],image,1,1,0)
    assert factory.inputs==[]
    assert received[0][0].tolist()==[[30,20,60,60]]
    assert received[0][1] is image
