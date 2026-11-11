from types import SimpleNamespace as NS
from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import Marker
from omnifleet_person_follow.node import PersonFollowNode
from omnifleet_person_follow.following import StandoffGoal


def rig():
    node=PersonFollowNode.__new__(PersonFollowNode);published=[]
    node.global_frame='map';node.following=StandoffGoal(distance=.5)
    node.navigation=NS(handle=object(),canceling=False)
    node.goal_marker_pub=NS(publish=published.append)
    node.get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:PoseStamped().header.stamp))
    return node,published


def test_real_goal_has_visible_point_and_label_without_changing_navigation_height():
    node,published=rig();goal=PoseStamped();goal.pose.position.x=1.2;goal.pose.position.y=-.3
    node.publish_goal_markers(goal,[0.,0.,0.],'approach','TRACKING')
    markers=published[-1].markers
    assert all(m.action==Marker.ADD for m in markers)
    sphere=next(m for m in markers if m.type==Marker.SPHERE)
    assert sphere.pose.position.x==1.2 and sphere.pose.position.y==-.3 and sphere.pose.position.z>.1
    assert goal.pose.position.z==0.
    assert any(m.type==Marker.TEXT_VIEW_FACING and '取深度' in m.text for m in markers)


def test_hold_shows_no_moving_target_and_pause_clears_previous_markers():
    node,published=rig()
    node.publish_goal_markers(None,[.2,.3,0.],'follow','TRACKING')
    markers=published[-1].markers
    assert not any(m.type==Marker.SPHERE for m in markers)
    assert any('0.50m' in m.text and '无移动目标' in m.text for m in markers)
    node.publish_goal_markers(None,None,'follow','PAUSED')
    assert len(published[-1].markers)==1 and published[-1].markers[0].action==Marker.DELETEALL
