from concurrent.futures import Future
from types import SimpleNamespace as NS

from omnifleet_navigation_interfaces.action import ExecuteNavigation,ExecuteFormation
from omnifleet_navigation_interfaces.msg import NavigationPoint
from rclpy.serialization import serialize_message,deserialize_message


def test_new_action_roundtrips_without_changing_existing_navigation_schema():
    assert 'follow_formation' not in ExecuteNavigation.Goal.get_fields_and_field_types()
    p=NavigationPoint();p.pose.header.frame_id='map';p.pose.pose.orientation.w=1.
    goal=ExecuteFormation.Goal(task_id='formation-task',command_epoch='lease',revision=9,waypoints=[p])
    restored=deserialize_message(serialize_message(goal),ExecuteFormation.Goal)
    assert restored.task_id=='formation-task' and restored.revision==9
    assert restored.waypoints[0].pose.header.frame_id=='map'


def test_formation_client_sends_typed_goal_with_existing_lease_and_task_version():
    from omnifleet_rmf_adapter.control_client import NavigationClient
    from builtin_interfaces.msg import Time
    sent=[];events=[]
    def send(goal,feedback_callback):sent.append(goal);return Future()
    node=NS(motion_enabled=True,goal_handle=None,inflight=None,generation=0,epoch='lease',
            task_id='formation-task',revision=9,formation_action=NS(send_goal_async=send),
            get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())),event=lambda *a,**k:events.append(a))
    NavigationClient.send_goal(node,{'id':'formation-task','poses':[[1.,2.,.3]],'follow_formation':True})
    assert isinstance(sent[0],ExecuteFormation.Goal)
    assert sent[0].command_epoch=='lease' and sent[0].revision==9 and sent[0].task_id=='formation-task'
    assert sent[0].waypoints[0].pose.header.frame_id=='map'
    assert sent[0].waypoints[0].pose.pose.position.x==1.
    assert node.inflight=='formation-task' and not events
