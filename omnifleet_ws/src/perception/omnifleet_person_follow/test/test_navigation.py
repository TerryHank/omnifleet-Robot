from types import SimpleNamespace as NS
from omnifleet_person_follow import navigation
from builtin_interfaces.msg import Time


class Future:
    def __init__(self, value=None, immediate=False):
        self.value, self.immediate = value, immediate
    def result(self):
        return self.value
    def add_done_callback(self, callback):
        if self.immediate:
            callback(self)


def rig(monkeypatch, enabled=True, delayed=False):
    sent, updates, cancels = [], [], []
    handle = NS(accepted=True, get_result_async=lambda:Future(), cancel_goal_async=lambda:cancels.append(True))
    future = Future(handle, not delayed)
    client = NS(server_is_ready=lambda:True, send_goal_async=lambda goal:(sent.append(goal) or future))
    monkeypatch.setattr(navigation, 'ActionClient', lambda *args:client)
    node = NS(create_publisher=lambda *args:NS(publish=updates.append),
              get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time(sec=123))))
    nav = navigation.DynamicNavigation(node, '/navigate_to_pose', '/goal_update', '/test.xml', enabled)
    return nav, sent, updates, cancels, future


def test_many_updates_only_start_one_public_navigation_action(monkeypatch):
    nav, sent, updates, cancels, _ = rig(monkeypatch)
    for _ in range(50):
        nav.update(navigation.PoseStamped())
    assert len(sent) == 1 and len(updates) == 1 and not cancels
    for _ in range(10):
        nav.update(None)
    assert len(cancels) == 1


def test_perception_only_never_publishes_nav_or_starts_action(monkeypatch):
    nav, sent, updates, cancels, _ = rig(monkeypatch, enabled=False)
    for _ in range(50):
        nav.update(navigation.PoseStamped())
    assert not sent and not updates and not cancels


def test_pause_while_acceptance_pending_cancels_own_late_goal(monkeypatch):
    nav, sent, updates, cancels, future = rig(monkeypatch, delayed=True)
    nav.update(navigation.PoseStamped())
    nav.update(None)
    nav.accepted(future, 0)
    assert len(sent) == 1 and len(cancels) == 1 and not updates


def test_finished_navigation_does_not_flood_repeated_actions(monkeypatch):
    nav, sent, updates, cancels, _ = rig(monkeypatch)
    nav.update(navigation.PoseStamped())
    handle = nav.handle
    nav.finished(Future(), handle)
    for _ in range(20):
        nav.update(navigation.PoseStamped())
    assert len(sent) == 1 and nav.failed
    nav.update(None)
    nav.update(navigation.PoseStamped())
    assert len(sent) == 2


def test_search_uses_finite_navigation_and_success_is_not_failure(monkeypatch):
    nav, sent, updates, cancels, _ = rig(monkeypatch)
    nav.update(navigation.PoseStamped(), task='search', token=1)
    assert sent[0].behavior_tree == '' and not updates
    nav.finished(Future(NS(status=4)), nav.handle)
    assert nav.completed and not nav.failed and nav.outcome == 'succeeded'
    for _ in range(10):
        nav.update(navigation.PoseStamped(), task='search', token=1)
    assert len(sent) == 1
    nav.update(navigation.PoseStamped(), task='search', token=2)
    assert len(sent) == 2


def test_search_transition_waits_for_own_follow_cancellation(monkeypatch):
    nav, sent, updates, cancels, _ = rig(monkeypatch)
    nav.update(navigation.PoseStamped())
    follow_handle = nav.handle
    nav.update(navigation.PoseStamped(), task='search', token=1)
    assert len(cancels) == 1 and len(sent) == 1
    nav.finished(Future(NS(status=5)), follow_handle)
    nav.update(navigation.PoseStamped(), task='search', token=1)
    assert len(sent) == 2 and sent[-1].behavior_tree == ''
    assert not nav.failed


def test_updates_coalesce_to_latest_target_at_2_5_hz(monkeypatch):
    clock=[0.]
    monkeypatch.setattr(navigation.time,'monotonic',lambda:clock[0])
    nav,sent,updates,_,_=rig(monkeypatch)
    for index in range(101):
        clock[0]=index*.01
        pose=navigation.PoseStamped();pose.pose.position.x=index*.01;pose.pose.orientation.w=1.
        nav.update(pose)
    assert len(sent)==1 and len(updates)==3
    assert updates[-1].pose.position.x == .8
    clock[0]=1.3;nav.update(pose)
    assert updates[-1].pose.position.x==1. and len(updates)==4


def test_nav2_obstacle_abort_retries_but_external_cancel_does_not(monkeypatch):
    clock=[0.]
    monkeypatch.setattr(navigation.time,'monotonic',lambda:clock[0])
    nav,sent,_,_,_=rig(monkeypatch)
    pose=navigation.PoseStamped();nav.update(pose)
    nav.finished(Future(NS(status=6)),nav.handle)
    clock[0]=1.;nav.update(pose);assert len(sent)==1
    clock[0]=2.1;nav.update(pose);assert len(sent)==2
    nav.finished(Future(NS(status=5)),nav.handle)
    clock[0]=20.;nav.update(pose);assert len(sent)==2


def test_goal_updater_uses_dispatch_time_after_local_navigation_restamps_initial_goal(monkeypatch):
    nav,_,updates,_,_=rig(monkeypatch)
    pose=navigation.PoseStamped();pose.header.stamp.sec=1
    nav.update(pose)
    assert updates[-1].header.stamp.sec==123


def test_centering_uses_nav2_spin_without_a_translation_controller(monkeypatch,tmp_path):
    import xml.etree.ElementTree as ET
    monkeypatch.setattr(navigation.Path,'home',lambda:tmp_path)
    nav,sent,updates,_,_=rig(monkeypatch)
    nav.update(navigation.PoseStamped(),task='center',token=1,spin_angle=.3)
    tree=ET.parse(sent[0].behavior_tree)
    assert float(tree.find('.//Spin').get('spin_dist'))>0
    assert tree.find('.//FollowPath') is None and not updates


def test_direction_reversal_stops_forward_once_then_updates_one_reverse_action(monkeypatch):
    clock=[0.]
    monkeypatch.setattr(navigation.time,'monotonic',lambda:clock[0])
    nav,sent,updates,cancels,_=rig(monkeypatch)
    forward=navigation.PoseStamped();forward.pose.position.x=1.;forward.pose.orientation.w=1.
    nav.update(forward,task='follow',token=7)
    old=nav.handle
    reverse=navigation.PoseStamped();reverse.pose.position.x=-.2;reverse.pose.orientation.w=1.
    for _ in range(30):
        nav.update(reverse,task='backoff',token=7)
    assert len(cancels)==1 and len(sent)==1
    nav.finished(Future(NS(status=5)),old)
    for index in range(90):
        clock[0]=index/30.
        pose=navigation.PoseStamped();pose.pose.position.x=-.2-index*.002;pose.pose.orientation.w=1.
        nav.update(pose,task='backoff',token=7)
    assert len(sent)==2 and len(cancels)==1
    assert sent[-1].behavior_tree=='/test.xml'
    assert updates[-1].pose.position.x<-.3 and len(updates)<=9
    assert '后退' in nav.message
