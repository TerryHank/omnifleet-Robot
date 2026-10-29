import asyncio
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


def test_formation_endpoint_forces_fleet_admission_and_existing_lease_policy():
    from omnifleet_local_navigation.runtime import LocalNavigation
    recorded=[]
    async def admit(*args,**kwargs):recorded.append((args,kwargs));return 'checked'
    request=ExecuteFormation.Goal(task_id='formation-task',command_epoch='lease',revision=9)
    node=NS(admit=admit);handle=NS(request=request)
    assert asyncio.run(LocalNavigation.execute_formation(node,handle))=='checked'
    args,kwargs=recorded[0]
    assert args[2].source=='FLEET' and args[2].command_epoch=='lease'
    assert kwargs['backend']=='formation_follow' and args[4] is True
