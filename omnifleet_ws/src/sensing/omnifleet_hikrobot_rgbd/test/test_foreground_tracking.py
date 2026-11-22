import numpy as np
import pytest
from omnifleet_hikrobot_rgbd.foreground_tracking import ForegroundQuery, summary


def query():
    q=ForegroundQuery(.2,3.5)
    q.depth=np.full((120,160),3000,np.uint16)
    q.depth[30:90,50:100]=1400
    q.rgb_size=(320,240)
    q.depth_k=np.array([[100.,0,80],[0,100.,60],[0,0,1.]])
    q.rgb_k=np.array([[200.,0,160],[0,200.,120],[0,0,1.]])
    q.transform=np.eye(4)
    return q


def test_same_component_conditions_appearance_refines_box_and_supplies_range():
    q=query();result=q.query([60,30,200,180])
    image=np.full((240,320,3),(25,70,200),np.uint8)
    conditioned=q.appearance(image,result)
    assert np.array_equal(conditioned[120,150],image[120,150])
    assert np.array_equal(conditioned[40,70],[127,127,127])
    assert result['bbox_xywh'][2]<120
    value=summary(result,10.,10.)
    assert value['depth_m']==pytest.approx(1.4) and value['sampled_count']<=256
    assert value['native_depth_mm_range']==[1400,1400]
    assert value['ambiguous']  # geometry alone is not semantic proof


def test_semantics_without_depth_refine_observation_but_never_invent_range():
    q=query();q.depth=None
    mask=np.zeros((240,320),bool);mask[60:180,100:200]=True
    result=q.query([60,30,200,180],mask)
    value=q.describe(result)
    assert value['available'] and value['source']=='semantic_only'
    assert value['depth_m'] is None and value['sampled_count']==0
    assert not value['ambiguous'] and value['bbox_xywh'][2]<120


def test_empty_depth_without_semantics_is_explicitly_unavailable():
    q=query();q.depth[:]=0
    assert q.describe(q.query([60,30,200,180]))==dict(available=False,source='unavailable',depth_m=None)
