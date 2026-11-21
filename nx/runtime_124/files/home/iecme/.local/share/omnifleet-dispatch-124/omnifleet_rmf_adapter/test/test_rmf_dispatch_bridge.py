import json
from types import SimpleNamespace as NS
from unittest.mock import Mock

from rmf_task_msgs.msg import BidNotice, DispatchCommand
from omnifleet_rmf_adapter.rmf_dispatch import RmfDispatch


def fixture():
    publishers = {}
    def publisher(kind, topic, qos):
        result = Mock();result.get_subscription_count.return_value = 1;publishers[topic] = result;return result
    mission = NS(jobs={}, current_rmf_task_id=None, command=Mock(return_value={'phase':'accepted'}), traffic=NS(order=lambda:['a','b'],rank=lambda r:['a','b'].index(r)))
    owner = NS(create_publisher=publisher, create_subscription=Mock(), ui_results={}, missions=mission,
               maps=NS(names={'a':'/alpha','b':'/beta'},state={'poses':{}}), config={'central':{'assignments':{'a':{'robot_name':'alpha'},'b':{'robot_name':'beta'}}}}, snapshots=lambda:{})
    return RmfDispatch(owner), owner, publishers


def test_fast_appended_goals_are_queued_without_losing_second_request():
    bridge, owner, publishers = fixture()
    for identifier in ('first','second'):bridge.submit({'op':'route_add','robot_id':'a','id':identifier}, {})
    bridge.send_next();bridge.send_next()
    assert publishers['/task_api_requests'].publish.call_count == 1
    first = bridge.pending['first'];first.update(task_id='compose.dispatch-1');bridge.tasks[first['task_id']] = first
    bridge.award(DispatchCommand(fleet_name='omnifleet_a',task_id=first['task_id'],dispatch_id=1,type=1))
    bridge.send_next()
    assert publishers['/task_api_requests'].publish.call_count == 2
    assert json.loads(publishers['/task_api_requests'].publish.call_args.args[0].json_msg)['request']['description']['phases'][0]['activity']['description']['description']['id'] == 'second'


def test_cancelled_queued_award_never_executes_vehicle_command():
    bridge, owner, publishers = fixture()
    bridge.submit({'op':'single_goal','robot_id':'a','id':'cancel-me'}, {})
    record=bridge.pending['cancel-me'];record['task_id']='compose.dispatch-2';bridge.tasks[record['task_id']]=record
    bridge.cancel_pending(robot='a')
    bridge.award(DispatchCommand(fleet_name='omnifleet_a',task_id=record['task_id'],dispatch_id=2,type=1))
    owner.missions.command.assert_not_called()
    assert not publishers['/rmf_task/dispatch_ack'].publish.call_args.args[0].success


def test_route_stop_does_not_cancel_a_queued_formation():
    bridge, owner, publishers = fixture()
    bridge.submit({'op':'formation_start','order':['a','b'],'id':'formation'}, {})
    bridge.submit({'op':'route_start','robot_id':'a','id':'route'}, {})
    bridge.cancel_pending(routes_only=True)
    assert bridge.pending['route']['phase']=='STOPPED'
    assert bridge.pending['formation']['phase']=='QUEUED'


def test_repeated_dispatch_award_does_not_duplicate_navigation():
    bridge, owner, publishers = fixture()
    bridge.submit({'op':'single_goal','robot_id':'a','id':'once'}, {})
    record=bridge.pending['once'];record['task_id']='compose.dispatch-3';bridge.tasks[record['task_id']]=record
    award=DispatchCommand(fleet_name='omnifleet_a',task_id=record['task_id'],dispatch_id=3,type=1)
    bridge.award(award);bridge.award(award)
    assert owner.missions.command.call_count==1


def test_rmf_removal_stops_the_whole_formation():
    bridge, owner, publishers = fixture()
    bridge.submit({'op':'formation_start','order':['a','b'],'id':'group'}, {})
    record=bridge.pending['group'];record.update(task_id='compose.dispatch-4',robot='a',phase='EXECUTING');bridge.tasks[record['task_id']]=record
    bridge.award(DispatchCommand(fleet_name='omnifleet_a',task_id=record['task_id'],dispatch_id=4,type=2))
    owner.missions.command.assert_called_once_with({'op':'formation_stop'}, {})
    assert record['phase']=='STOPPED'


def test_equal_cost_automatic_assignment_prefers_leader_order():
    bridge,owner,publishers=fixture()
    owner.snapshots=lambda:{'a':{'online':True},'b':{'online':True}}
    owner.maps.state['poses']={'a':[0.,0.,0.],'b':[0.,0.,0.]}
    bridge.submit({'op':'route_start','id':'auto','shared_points':[{'pose':[1.,0.,0.]}]},owner.snapshots())
    packet=bridge.pending['auto']['packet']
    request={'description':{'category':'omnifleet','phases':[{'activity':{'description':{
        'description':packet}}}]}}
    bridge.bid(BidNotice(task_id='compose.dispatch-priority',request=json.dumps(request)))
    proposals=[call.args[0].proposal for call in publishers['/rmf_task/bid_response'].publish.call_args_list]
    costs={proposal.fleet_name:proposal.new_cost for proposal in proposals}
    assert costs['omnifleet_a']<costs['omnifleet_b']
