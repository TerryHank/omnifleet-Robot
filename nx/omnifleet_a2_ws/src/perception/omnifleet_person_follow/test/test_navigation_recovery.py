import threading
import time
from types import SimpleNamespace as NS
from omnifleet_person_follow.core import FollowManager
from omnifleet_person_follow.node import PersonFollowNode
from omnifleet_person_follow.recovery import SearchRecovery
from geometry_msgs.msg import PoseStamped
from omnifleet_person_follow.following import StandoffGoal,ImageCentering,VisualApproach


def test_node_sends_search_leg_then_resumes_follow_after_new_id_relock():
    now = time.monotonic()
    manager = FollowManager()
    manager.gesture('thumbs_up', 7)
    manager.observe([dict(id=7,world=[1.,0.,0.])], now-2.)
    manager.observe([dict(id=7,world=[1.1,0.,0.])], now-1.5)
    manager.observe([], now)
    node = PersonFollowNode.__new__(PersonFollowNode)
    node.lock, node.manager = threading.RLock(), manager
    node.last_frame, node.tracks = now, []
    node.recovery, node.last_recovery_phase = SearchRecovery(), 'OFF'
    node.following = StandoffGoal()
    node.centering = ImageCentering()
    node.approach = VisualApproach()
    node.info, node.costmap, node.global_frame = None, None, 'map'
    node.coordinate_error = ''
    pose = NS(translation=NS(x=0.,y=0.), rotation=NS(x=0.,y=0.,z=0.,w=1.))
    node.tf = NS(lookup_transform=lambda *args:NS(transform=pose))
    goals, calls = [], []
    node.goal_pub = NS(publish=goals.append)
    node.goal_marker_pub = NS(publish=lambda markers:None)
    node.navigation = NS(failed=False,completed=False,task='follow',task_key=None,outcome='aborted',
                         handle=None,canceling=False,
                         update=lambda goal,**kwargs:calls.append((goal,kwargs)))
    node.get_logger = lambda:NS(info=lambda message:None)
    node.get_clock = lambda:NS(now=lambda:NS(to_msg=lambda:PoseStamped().header.stamp))
    node.navigation_tick()
    assert calls[-1][1]['task'] == 'search'
    assert goals[-1].pose.position.x > 1.1
    assert manager.state == 'LOST' and node.recovery.phase == 'NAV_PREDICTED'
    # A completed/failed search leg must not put the newly recovered person in PAUSED.
    for stamp, x in [(now+.1,1.2),(now+.7,1.5)]:
        node.tracks = [dict(id=8,world=[x,0.,0.],position_time=stamp,confidence=.9)]
        manager.observe(node.tracks, stamp)
    node.navigation.task, node.navigation.failed = 'search', True
    node.navigation_tick()
    assert manager.track_id == 8 and manager.state == 'TRACKING'
    assert calls[-1][1] == dict(task='follow',token=8)
    assert node.recovery.phase == 'OFF'


def test_auto_locked_person_centers_then_approaches_for_depth_instead_of_history_search():
    now=time.monotonic();node=PersonFollowNode.__new__(PersonFollowNode)
    node.lock=threading.RLock();node.manager=FollowManager()
    node.last_frame=now;node.tracks=[dict(id=7,bbox=[0,0,20,100])]
    node.manager.auto_lock(node.tracks,now,100)
    node.recovery,node.last_recovery_phase=SearchRecovery(),'OFF'
    node.following,node.centering,node.approach=StandoffGoal(),ImageCentering(),VisualApproach()
    node.info=NS(width=100,k=[100,0,50,0,100,50,0,0,1]);node.costmap=None;node.global_frame='map'
    pose=NS(translation=NS(x=0.,y=0.),rotation=NS(x=0.,y=0.,z=0.,w=1.))
    node.tf=NS(lookup_transform=lambda *args:NS(transform=pose))
    calls=[];node.goal_pub=NS(publish=lambda message:None)
    node.goal_marker_pub=NS(publish=lambda markers:None)
    node.navigation=NS(failed=False,completed=False,task='follow',task_key=None,outcome='',
                       handle=None,canceling=False,
                       update=lambda goal,**kwargs:calls.append((goal,kwargs)))
    node.get_logger=lambda:NS(info=lambda message:None)
    node.get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:PoseStamped().header.stamp))
    node.navigation_tick()
    assert calls[-1][1]['task']=='center'
    assert calls[-1][0].pose.position.x==calls[-1][0].pose.position.y==0.
    assert calls[-1][1]['spin_angle']>0 and node.recovery.phase=='OFF'
    node.tracks[0]['bbox']=[45,0,55,100]
    node.navigation_tick()
    assert calls[-1][1]['task']=='approach'
    assert abs(calls[-1][0].pose.position.x-.2)<1e-9
    assert node.following.mode=='APPROACH_FOR_DEPTH' and node.recovery.phase=='OFF'
    node.manager.state='TRACKING'
    node.tracks[0].update(world=[1.,0.,0.],position_time=time.monotonic())
    node.navigation_tick()
    assert calls[-1][0] is None and calls[-1][1]['task']=='follow'
    assert node.following.mode=='HOLD' and node.approach.goal is None
    node.tracks[0].update(world=[.6,0.,0.],position_time=now+2.)
    node.navigation_tick()
    assert calls[-1][1]['task']=='backoff'
    assert calls[-1][0].pose.position.x<0
    assert node.following.mode=='BACKOFF'
    node.manager.history.append((now,node.tracks[0]['world']))
    node.manager.state='LOST';node.tracks[0].pop('world');node.tracks[0].pop('position_time')
    node.navigation_tick()
    assert calls[-1][1]['task']=='approach' and calls[-1][0].pose.position.x>0
    assert node.following.mode=='APPROACH_FOR_DEPTH'
    pose.translation.x=-.4
    node.navigation.task_key=('approach',node.approach.token);node.navigation.completed=True
    node.navigation_tick()
    assert calls[-1][0].pose.position.x>pose.translation.x
    assert node.following.mode=='APPROACH_FOR_DEPTH'
