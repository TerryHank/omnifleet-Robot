import json
import threading
import time
from types import SimpleNamespace as NS
from omnifleet_person_follow.node import PersonFollowNode
from omnifleet_person_follow.core import FollowManager
from omnifleet_person_follow.following import StandoffGoal,ImageCentering,VisualApproach
from omnifleet_person_follow.recovery import SearchRecovery


def rig():
    node=PersonFollowNode.__new__(PersonFollowNode)
    node.tros=None
    node.lock=threading.RLock();node.manager=FollowManager()
    node.tracks=[dict(id=7)];node.last_frame=time.monotonic()
    node.following,node.centering,node.approach,node.recovery=StandoffGoal(),ImageCentering(),VisualApproach(),SearchRecovery()
    stopped=[];node.navigation=NS(update=stopped.append)
    node.get_logger=lambda:NS(info=lambda text:None)
    return node,stopped


def test_panel_target_selection_is_explicit_and_not_a_fabricated_gesture():
    node,stopped=rig()
    assert node.manager.state=='IDLE'
    node.on_operator_control(NS(data=json.dumps(dict(op='lock',track_id=7))))
    assert (node.manager.state,node.manager.track_id,node.lock_source)==('TRACKING',7,'fox_operator')
    assert stopped==[None]
    node.on_operator_control(NS(data=json.dumps(dict(op='pause'))))
    assert node.manager.state=='PAUSED' and stopped==[None,None]


def test_invalid_or_no_longer_visible_selection_does_not_start_following():
    node,stopped=rig()
    node.on_operator_control(NS(data=json.dumps(dict(op='lock',track_id=8))))
    assert node.manager.state=='IDLE' and not stopped


def test_pause_before_first_detection_prevents_automatic_start():
    node,stopped=rig()
    node.on_operator_control(NS(data=json.dumps(dict(op='pause'))))
    assert node.manager.state=='PAUSED' and stopped==[None]
    assert node.manager.auto_lock(node.tracks,time.monotonic(),1536) is None
