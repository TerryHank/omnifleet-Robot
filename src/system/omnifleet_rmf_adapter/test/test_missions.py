from concurrent.futures import Future
import math
from types import SimpleNamespace

import pytest

from omnifleet_rmf_adapter.missions import Missions, Trail, path_conflict, points, plan_route
from nav_msgs.msg import OccupancyGrid


class ImmediatePlanner:
    def submit(self, function, grid, start, targets, peers, transform):
        future = Future()
        future.set_result({'path': [start, targets[-1]['pose']], 'targets': targets})
        return future

    def shutdown(self, **kwargs): pass


@pytest.fixture
def fleet(tmp_path, monkeypatch):
    clock = [100.]
    monkeypatch.setattr('omnifleet_rmf_adapter.missions.time.monotonic', lambda: clock[0])
    robots = ['a', 'b', 'c']
    states = {r: {'online': True, 'fresh': dict.fromkeys(('map', 'navigation', 'control', 'pose', 'fleet_client'), True),
        'samples': {
            'navigation': {'value': {'local_ready': True, 'localization_epoch': r+'-epoch', 'navigation_active': False, 'fleet_lease_fresh': False}},
            'control': {'value': {'nav_active': False, 'manual_active': False, 'local_override': False, 'estop': False, 'control_gate_ready': True, 'stopped_seconds': 2., 'velocity':[0.,0.], 'velocity_age':0.}},
            'pose': {'value': {'x': 0., 'y': i*4., 'yaw': 0.}},
            'fleet_client': {'value': {'armed': False, 'busy': False, 'history': {}}},
        }} for i, r in enumerate(robots)}
    maps = SimpleNamespace(names={r:'/'+r for r in robots}, valid_robots=set(robots),
        alignment={r:[0.,0.,0.] for r in robots}, maps={r:None for r in robots}, obstacles={})
    config = {'robots': {r:{'motion_enabled':True} for r in robots}}
    sent = []

    def send(op, request, robot_id, **fields):
        sent.append((op, request, robot_id, fields))
        state = states[robot_id]
        client = state['samples']['fleet_client']['value']
        nav = state['samples']['navigation']['value']
        control = state['samples']['control']['value']
        if op == 'arm':
            client.update(armed=True); nav.update(fleet_lease_fresh=True)
            client['history'][request] = {'phase':'armed'}
        elif op == 'navigate':
            client.update(busy=True); nav.update(navigation_active=True); control.update(nav_active=True, stopped_seconds=0.)
            client['history'][request] = {'phase':'executing'}
        elif op == 'disarm':
            client.update(armed=False, busy=False); nav.update(navigation_active=False, fleet_lease_fresh=False)
            control.update(nav_active=False, stopped_seconds=1.)
        elif op == 'operator_stop':
            client.update(armed=False,busy=False);nav.update(navigation_active=False,fleet_lease_fresh=False,fleet_enabled=False)
            control.update(nav_active=False,stopped_seconds=1.,manual_active=False,local_override=False)
            client['history'][request]={'phase':'stopped','confirmed':True}
        elif op == 'prepare': client['history'][request] = {'phase':'prepared', 'point_count':len(fields['poses']), 'motion_sent':False}

    owner = Missions(config, maps, tmp_path, send)
    planner=ImmediatePlanner()
    owner.onboard_planner=lambda robot,targets,current:planner.submit(None,None,
        [current[robot]['samples']['pose']['value'][key] for key in ('x','y','yaw')],targets,None,None)

    def tick(count=1):
        for _ in range(count): clock[0] += .1; owner.tick(states, clock[0])

    def finish(robot, success=True):
        state = states[robot]; job = owner.jobs[robot]
        state['samples']['fleet_client']['value']['busy'] = False
        state['samples']['fleet_client']['value']['history'][job['request']] = {'phase':'completed' if success else 'failed', 'message':'blocked'}
        state['samples']['navigation']['value']['navigation_active'] = False
        state['samples']['control']['value'].update(nav_active=False, stopped_seconds=1.)

    return SimpleNamespace(owner=owner, states=states, maps=maps, config=config, sent=sent, tick=tick, finish=finish, clock=clock, root=tmp_path)


def save(fleet, robot, route):
    fleet.owner.command({'op':'route_save','robot_id':robot,'points':route,'id':'save-'+robot}, fleet.states)


def start(fleet, robot):
    fleet.owner.command({'op':'route_start','robot_id':robot,'id':'start-'+robot}, fleet.states)


def test_private_waypoints_persist_but_never_auto_restart(fleet):
    save(fleet, 'a', [[1.,0.,0.],[2.,0.,.5]])
    save(fleet, 'b', [[1.,4.,0.]])
    restored = Missions(fleet.config, fleet.maps, fleet.root, lambda *a,**k:None)
    assert len(restored.saved['routes']['a']['points']) == 2
    assert len(restored.saved['routes']['b']['points']) == 1
    assert not restored.jobs and not restored.follow['active']
    restored.close()


def test_two_point_route_is_one_onboard_queue_with_one_confirmed_result(fleet):
    save(fleet, 'a', [[1.,0.,0.],[2.,0.,.5]])
    start(fleet, 'a'); fleet.tick(4)
    assert [p[0] for p in fleet.sent].count('navigate') == 1
    request=next(p[3] for p in fleet.sent if p[0]=='navigate')
    assert request['poses']==[[1.,0.,0.],[2.,0.,.5]] and not request['single_point']
    fleet.finish('a'); fleet.tick(3)
    assert [p[0] for p in fleet.sent].count('navigate') == 1
    assert fleet.owner.jobs['a']['phase'] == 'COMPLETED'
    assert fleet.owner.jobs['a']['index'] == 2


def test_failed_navigation_stops_queue_instead_of_retrying(fleet):
    save(fleet, 'a', [[1.,0.,0.],[2.,0.,0.]])
    start(fleet, 'a'); fleet.tick(4); fleet.finish('a', False); fleet.tick(30)
    assert fleet.owner.jobs['a']['phase'] == 'FAILED'
    assert len([p for p in fleet.sent if p[0] == 'navigate']) == 1


def test_epoch_change_fences_queue_and_prevents_saved_route_reuse(fleet):
    save(fleet, 'a', [[1.,0.,0.]])
    start(fleet, 'a'); fleet.tick(4)
    fleet.states['a']['samples']['navigation']['value']['localization_epoch'] = 'new'
    fleet.tick(2)
    assert fleet.owner.jobs['a']['phase'] == 'INVALIDATED'
    with pytest.raises(ValueError, match='定位会话'): start(fleet, 'a')


def test_fixed_leader_loss_stops_follow_without_election_or_auto_resume(fleet):
    fleet.owner.command({'op':'follow_start','id':'follow','order':['a','b','c'],'distance':1.4}, fleet.states)
    for _ in range(7):
        fleet.states['a']['samples']['pose']['value']['x'] += .3; fleet.tick()
    fleet.tick(3)
    assert any(p[0]=='navigate' and p[2]=='b' for p in fleet.sent)
    fleet.states['a']['online']=False;fleet.tick(2)
    assert fleet.owner.follow['leader']=='a' and not fleet.owner.follow['active']
    assert fleet.owner.jobs['b']['phase']=='STOPPED'
    count=len([p for p in fleet.sent if p[0]=='navigate'])
    fleet.states['a']['online']=True;fleet.tick(10)
    assert fleet.owner.follow['leader']=='a' and not fleet.owner.follow['active']
    assert len([p for p in fleet.sent if p[0]=='navigate'])==count


def test_turning_trail_uses_walked_arc_length_without_extra_jump_gate():
    trail = Trail()
    for p in ([0.,0.,0.],[1.,0.,0.],[2.,0.,0.],[2.,1.,1.57],[2.,2.,1.57]): trail.add(p)
    distance, target = trail.target(3., 1.4)
    assert distance == pytest.approx(2.6)
    assert target == pytest.approx([2., .6, math.pi/2])
    trail.add([20.,2.,0.])
    assert trail.samples[-1][1]==[20.,2.,0.]


def test_motion_disabled_blocks_execution_but_allows_multigoal_prepare(fleet):
    fleet.config['robots']['a']['motion_enabled'] = False
    save(fleet, 'a', [[1.,0.,0.],[2.,0.,0.]])
    with pytest.raises(ValueError, match='执行开关'): start(fleet, 'a')
    fleet.owner.command({'op':'route_prepare','robot_id':'a','id':'precheck'}, fleet.states)
    fleet.tick(2)
    assert fleet.owner.prechecks['precheck']['phase'] == 'PREPARED'
    assert not any(p[0] in ('navigate','arm') for p in fleet.sent)


def test_crossing_routes_yield_in_request_order(fleet):
    fleet.states['b']['samples']['pose']['value'].update(x=1., y=-1.)
    save(fleet, 'a', [[2.,0.,0.]])
    save(fleet, 'b', [[1.,1.,0.]])
    start(fleet, 'a'); start(fleet, 'b'); fleet.tick(4)
    assert fleet.owner.jobs['a']['phase'] == 'EXECUTING'
    assert fleet.owner.jobs['b']['phase'] == 'YIELDING'
    assert not any(p[0] == 'navigate' and p[2] == 'b' for p in fleet.sent)


def test_manual_takeover_cancels_and_does_not_restart(fleet):
    save(fleet, 'a', [[1.,0.,0.]])
    start(fleet, 'a'); fleet.tick(4)
    fleet.states['a']['samples']['control']['value']['manual_active'] = True
    fleet.tick(10)
    assert fleet.owner.jobs['a']['phase'] == 'STOPPED'
    assert len([p for p in fleet.sent if p[0] == 'navigate']) == 1


@pytest.mark.parametrize('value', ([], [[True,0.,0.]], [[float('nan'),0.,0.]], [[1.,2.]]))
def test_rejects_invalid_waypoints(value):
    with pytest.raises(ValueError): points(value)


def test_path_reservation_checks_crossing_and_parallel_corridors():
    assert path_conflict([[0.,0.,0.],[1.,0.,0.],[2.,0.,0.]], [[1.,-1.,0.],[1.,0.,0.],[1.,1.,0.]])
    assert not path_conflict([[0.,0.,0.],[1.,0.,0.]], [[0.,2.,0.],[1.,2.,0.]])


def test_preflight_preserves_requested_one_centimeter_point_model():
    grid=OccupancyGrid();grid.info.width=grid.info.height=60;grid.info.resolution=.05;grid.info.origin.orientation.w=1.
    grid.data=[100]*3600
    for y in range(28,32):
        for x in range(60):grid.data[y*60+x]=0
    result=plan_route(grid,[.5,1.5,0.],[{'pose':[2.,1.5,0.]}],[],[0.,0.,0.])
    assert result['path'][-1] == [2.,1.5,0.]


def test_walked_part_of_leader_route_is_released_for_followers(fleet):
    path=[[i/10.,0.,0.] for i in range(101)]
    fleet.owner.enqueue('a',[{'pose':[10.,0.,0.]}],'route','a-epoch')
    job=fleet.owner.jobs['a'];job.update(phase='EXECUTING',path=path,reservation=path,path_index=0)
    follower=[[-1.,0.,0.],[1.5,0.,0.]]
    assert path_conflict(follower,job['path'])
    fleet.states['a']['samples']['pose']['value'].update(x=3.,y=0.)
    fleet.owner.refresh_reservations(fleet.states)
    assert job['path_index'] == 30
    assert not path_conflict(follower,job['path'])


def test_unavailable_fixed_leader_stops_group_instead_of_promoting_another(fleet):
    fleet.owner.command({'op':'follow_start','id':'follow','order':['a','b','c'],'distance':1.4},fleet.states)
    fleet.states['a']['samples']['control']['value']['control_gate_ready']=False
    fleet.tick()
    assert fleet.owner.follow['leader']=='a' and not fleet.owner.follow['active']


def test_fixed_leader_is_retained_while_map_alignment_refreshes(fleet):
    fleet.owner.command({'op':'follow_start','id':'follow','order':['a','b','c'],'distance':1.4},fleet.states)
    fleet.tick();fleet.maps.valid_robots.clear();saved=dict(fleet.maps.alignment);fleet.maps.alignment.clear();fleet.tick()
    assert fleet.owner.follow['leader']=='a' and fleet.owner.follow['phase']=='WAIT_MAP'
    fleet.maps.valid_robots.update(fleet.states);fleet.maps.alignment.update(saved);fleet.maps.alignment['a']=[2.,1.,.2]
    fleet.tick()
    assert fleet.owner.follow['leader']=='a'
    assert fleet.owner.trail.samples[-1]==(0.,[2.,1.,.2])
    assert len(fleet.owner.trail.samples)==2  # New-session joining leg, no old trail.


def test_handover_waits_for_all_online_old_follower_leases(fleet):
    fleet.owner.command({'op':'follow_start','id':'follow','order':['a','b','c'],'distance':1.4},fleet.states)
    fleet.tick();fleet.owner.handover=['b']
    fleet.states['b']['samples']['fleet_client']['value']['armed']=True
    fleet.tick()
    assert fleet.owner.follow['phase']=='HANDOVER'
    assert not any(p[0]=='navigate' for p in fleet.sent)
