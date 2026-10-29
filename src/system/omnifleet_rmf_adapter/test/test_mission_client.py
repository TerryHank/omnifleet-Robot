from concurrent.futures import Future
import json
from types import SimpleNamespace as NS
import time

from builtin_interfaces.msg import Time
from omnifleet_rmf_adapter.control_client import NavigationClient


def test_action_events_preserve_armed_and_busy_readback():
    records=[]
    client=NS(motion_enabled=False,permission_error=None,events={},goal_handle=object(),inflight=None,pending=None,arm_pending=False,epoch='current',record=lambda *a:records.append(a))
    NavigationClient.event(client,'goal','executing')
    assert client.control['armed'] and client.control['busy']
    assert records[-1][1]['history']['goal']['phase'] == 'executing'


def test_late_goal_acceptance_is_cancelled_and_blocks_next_goal_until_drained():
    accepted, result = Future(), Future()
    events, goals, cancelled = [], [], []
    handle = NS(accepted=True, cancel_goal_async=lambda:cancelled.append(True), get_result_async=lambda:result)
    def send(goal, feedback_callback): goals.append(goal); return accepted
    client = NS(motion_enabled=True,generation=0,inflight=None,goal_handle=None,epoch='lease',task_id='task',revision=1,
        action=NS(send_goal_async=send),get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())),
        event=lambda *a,**k:events.append((a,k)))
    packet = {'id':'old','pose':[1.,0.,0.]}
    NavigationClient.send_goal(client, packet)
    assert client.inflight == 'old'
    client.generation += 1  # Cancel while the send-goal request is still in flight.
    accepted.set_result(handle)
    assert cancelled and client.goal_handle is None and client.inflight == 'old'
    NavigationClient.send_goal(client, {'id':'new','pose':[2.,0.,0.]})
    assert len(goals) == 1 and events[-1][1]['message'] == 'previous goal not drained'
    result.set_result(NS(status=5,result=NS(success=False,code='CANCELED',message='stopped')))
    assert client.inflight is None and client.goal_handle is None
    assert not any(args[1] == 'completed' for args, fields in events)


def test_disarm_remains_available_after_central_heartbeat_expiry():
    packet = json.dumps({'schema':1,'sent_monotonic':time.monotonic(),'op':'disarm','id':'stop'}).encode()
    packets = [packet]
    def receive(size):
        if packets:return packets.pop()
        raise BlockingIOError()
    events = []
    client = NS(commands=NS(recv=receive),central_seen=0.,motion_enabled=False,generation=0,pending=None,
        arm_pending=False,goal_handle=None,epoch='old',enable=NS(service_is_ready=lambda:False),
        stopped=lambda:True,event=lambda *a,**k:events.append((a,k)))
    client.refresh_execution_permission=lambda:None
    client.cancel=lambda request,disarm=False:NavigationClient.cancel(client,request,disarm)
    NavigationClient.poll(client)
    assert client.epoch is None and client.generation == 1
    assert events == [(('stop','stopped'),{'confirmed':True})]


def test_multi_point_prepare_never_arms_or_sends_goals():
    packet = json.dumps({'schema':1,'sent_monotonic':time.monotonic(),'op':'prepare','id':'prepare',
        'poses':[[1.,0.,0.],[2.,0.,0.]],'localization_epoch':'current'}).encode()
    packets = [packet]
    def receive(size):
        if packets:return packets.pop()
        raise BlockingIOError()
    events=[]
    client=NS(commands=NS(recv=receive),central_seen=time.monotonic(),motion_enabled=False,pending=None,
        samples={'navigation':(time.monotonic(),{'local_ready':True,'localization_epoch':'current'})},
        profile={'domain_id':104},event=lambda *a,**k:events.append((a,k)))
    client.refresh_execution_permission=lambda:None
    client.cancel=lambda request,disarm=False:NavigationClient.cancel(client,request,disarm)
    NavigationClient.poll(client)
    assert events[0][0] == ('prepare','prepared')
    assert events[0][1]['point_count'] == 2 and events[0][1]['motion_sent'] is False


def test_expired_onboard_lease_discards_local_epoch_instead_of_rearming():
    events=[]
    client=NS(motion_enabled=False,permission_error=None,samples={'navigation':(time.monotonic(),{'fleet_enabled':False,'fleet_lease_fresh':False})},
        epoch='stale',armed_since=0.,generation=0,pending=('old',1.),goal_handle=None,inflight=None,
        arm_pending=False,control={},central_seen=0.,record=lambda *a:events.append(a))
    NavigationClient.renew(client)
    assert client.epoch is None and client.pending is None and client.generation == 1
    assert not client.control['armed']
