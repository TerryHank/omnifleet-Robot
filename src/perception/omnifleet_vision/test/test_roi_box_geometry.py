from pathlib import Path
from types import SimpleNamespace as NS
from collections import OrderedDict
import json,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/integration'))
from nanotrack_node import NanoTrackNode


class Tracker:
    def __init__(self,box):self.box=list(box);self.updates=0
    def update(self,image):self.updates+=1;return True,list(self.box)
    def getTrackingScore(self):return .95

def setup():
    emitted=[];created=[];observations=[]
    def create(image,box):
        tracker=Tracker(box);created.append(tracker);return tracker
    foreground=NS(prepare=lambda *args:None,calls=1,elapsed_ms=.1,depth=np.ones((1,1)),skew_ms=0.)
    def observe(image,item,box):
        observations.append(list(box))
        return image,dict(bbox=[100.,120.,160.,15.],center=[101.,121.],
            foreground=dict(available=foreground.depth is not None,
                depth_m=1.1 if foreground.depth is not None else None,
                bbox_xywh=[100.,120.,160.,15.]))
    node=NS(max_width=640,source_info_topic='/camera/color/camera_info',source_info=NS(width=640,height=480),
        foreground=foreground,foreground_cache={},color_cache={},cache=OrderedDict(),mode='roi',backend='nanotrack',
        pending_roi=NS(x_offset=100,y_offset=120,width=160,height=200),manual_tracker=None,manual_id=0,
        factory=NS(create=create,runtime='cpu'),observation=observe,
        output=NS(publish=lambda m:emitted.append(json.loads(m.data))),debug=None)
    message=NS(encoding='bgr8',width=640,height=480,step=1920,data=np.zeros((480,640,3),np.uint8).tobytes(),
        header=NS(stamp=NS(sec=100,nanosec=0),frame_id='test_optical'))
    return node,message,emitted,created,observations

def test_user_rectangle_initializes_template_and_is_not_replaced_by_depth_rim():
    node,message,emitted,created,observed=setup()
    NanoTrackNode.process_image(node,message)
    assert created[0].box==[100,120,160,200]
    assert created[0].updates==0,'Do not immediately infer the initialization frame again'
    assert emitted[-1]['tracks'][0]['bbox']==[100,120,160,200]
    assert emitted[-1]['tracks'][0]['center']==[180,220]
    assert observed==[[100,120,160,200]],'Range must be measured within the current visual target'

def test_tracker_motion_and_scale_are_preserved_despite_partial_depth():
    node,message,emitted,created,_=setup();NanoTrackNode.process_image(node,message)
    for i in range(25):
        created[0].box=[110+i,140+i,170,210]
        message.header.stamp.sec+=1
        NanoTrackNode.process_image(node,message)
        assert emitted[-1]['tracks'][0]['bbox']==created[0].box
        assert node.manual_box==created[0].box
        assert emitted[-1]['tracks'][0]['foreground']['bbox_xywh'][3]==15
    assert created[0].updates==25

def test_missing_depth_does_not_change_visual_rectangle_or_invent_distance():
    node,message,emitted,_,_=setup();node.foreground.depth=None
    NanoTrackNode.process_image(node,message)
    result=emitted[-1]['tracks'][0]
    assert result['bbox']==[100,120,160,200]
    assert result['foreground']['depth_m'] is None
