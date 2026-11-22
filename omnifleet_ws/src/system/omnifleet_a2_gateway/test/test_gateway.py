import json
from types import SimpleNamespace as NS
from rclpy.task import Future
from omnifleet_a2_gateway.gateway import A2Gateway
from collections import deque


def test_follow_identity_and_sequence():
    request = NS(follow_trail=True, source=1, FLEET=1, task_id='test', command_epoch='lease', revision=2)
    n = NS(active=NS(request=request), lease=NS(matches=lambda *_:True), epoch='map',
           follow_sequence=-1, follow_updates=0)
    data = dict(task_id='test', epoch='lease', revision=2, localization_epoch='map', sequence=1, poses=[[1.,2.,.3]])
    A2Gateway.follow_update(n, NS(data=json.dumps(data)))
    assert n.follow_updates == 1 and n.follow_target.pose.position.x == 1.
    A2Gateway.follow_update(n, NS(data=json.dumps(data)))
    assert n.follow_updates == 1
    for key, value in [('epoch','wrong'), ('localization_epoch','wrong'), ('revision',3), ('poses',[[float('nan'),0.,0.]])]:
        invalid = {**data, 'sequence':2, key:value}
        A2Gateway.follow_update(n, NS(data=json.dumps(invalid)))
        assert n.follow_updates == 1


def test_lifecycle_timeout_retries_and_ignores_late_reply():
    removed = []
    old = Future()
    new = Future()
    client = NS(service_is_ready=lambda:True, remove_pending_request=removed.append, call_async=lambda _:new)
    n = NS(state_clients={'planner':client}, state_pending={'planner':(old,0.)}, states={})
    A2Gateway.poll_states(n)
    assert removed == [old] and n.state_pending['planner'][0] is new
    new.set_result(NS(current_state=NS(id=3)))
    assert n.states['planner'][0] == 3 and not n.state_pending


def test_stationary_pose_velocity_jitter_does_not_reset_stop_time():
    n = NS(velocity_history=deque([[0.,0.]]*5,maxlen=5),stopped_at=0.)
    for value in [.014,-.015,.011,-.012,.013,-.014,.011]:
        message = NS(twist=NS(twist=NS(linear=NS(x=value),angular=NS(z=0.))))
        A2Gateway.speed(n,message)
        assert n.stopped_at == 0.
    A2Gateway.speed(n,NS(twist=NS(twist=NS(linear=NS(x=.12),angular=NS(z=0.)))))
    assert n.stopped_at > 0.


def test_control_uses_encoders_while_navigation_keeps_lio_velocity(monkeypatch):
    monkeypatch.setenv('OMNIFLEET_ROBOT_ID','robot_111')
    control, status = [], []
    n = NS(owned_uuid=None, statuses={}, enabled=False, active=None,
           ready=lambda:True, velocity=[.018,0.], wheel_velocity=[0.,0.],
           velocity_at=0., wheel_at=0., stopped_at=0., pose_at=0., epoch='map',
           lease=NS(fresh=lambda _:False, sequence=-1, task_id='', revision=0),
           phase='idle', message='', follow_updates=0, follow_sequence=-1,
           follow_blocked=False, follow_at=0.,
           hold_pub=NS(publish=lambda _:None), traffic_paused=False, stop_holding=False,
           control_pub=NS(publish=lambda m:control.append(json.loads(m.data))),
           status_pub=NS(publish=lambda m:status.append(json.loads(m.data))))
    A2Gateway.tick(n)
    assert control[-1]['velocity'] == [0.,0.]
    assert status[-1]['velocity'] == [.018,0.]
    A2Gateway.wheel_speed(n,NS(linear=NS(x=.12),angular=NS(z=.03)))
    A2Gateway.tick(n)
    assert control[-1]['velocity'] == [.12,.03] and n.stopped_at > 0.
    assert status[-1]['velocity'] == [.018,0.]
