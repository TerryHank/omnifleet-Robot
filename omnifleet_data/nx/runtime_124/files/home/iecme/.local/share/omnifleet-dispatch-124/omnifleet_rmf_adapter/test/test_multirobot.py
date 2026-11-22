import json
from datetime import datetime
from types import SimpleNamespace
import pytest
import time
from std_msgs.msg import String
from omnifleet_rmf_adapter.client import RobotObserver
from nav_msgs.msg import OccupancyGrid
from omnifleet_rmf_adapter.map_hub import namespaces, prefix_frame, compose, inverse, peer_grid, MapHub
from omnifleet_rmf_adapter.coordination import grid_path, rmf_timing, timed_separation
from omnifleet_rmf_adapter.control_client import NavigationClient


def grid():
    value=OccupancyGrid();value.header.frame_id='map'
    value.info.width=value.info.height=100;value.info.resolution=.1;value.info.origin.orientation.w=1.
    value.data=[0]*10000
    return value


def test_central_names_are_unique_and_frames_follow_assignments():
    config={'central':{'assignments':{'a':{'namespace':'/alpha'},'b':{'namespace':'/bravo'}}},'robots':{'a':{'enabled':True},'b':{'enabled':True}}}
    assert namespaces(config)=={'a':'/alpha','b':'/bravo'}
    assert prefix_frame('/alpha','/base_link')=='alpha/base_link'
    config['central']['assignments']['b']['namespace']='/alpha'
    with pytest.raises(ValueError):namespaces(config)
    config['central']['assignments']['b']['namespace']='/fleet'
    with pytest.raises(ValueError):namespaces(config)


def test_peer_map_marks_only_peer_body_and_never_erases_source():
    source=grid();source.data[0]=100
    peer=peer_grid(source,[([5.,5.,0.],.39)])
    assert source.data[0]==100 and peer.data[0]==-1
    assert peer.data[50*100+50]==100 and set(peer.data)=={-1,100}
    assert all(v==-1 for v in peer_grid(source,[]).data)


def test_transform_roundtrip_preserves_targets():
    transform=[2.,-.5,3.]
    assert compose(inverse(transform),compose(transform,[1.,2.,.4]))==pytest.approx([1.,2.,.4])


def test_alignment_is_invalidated_by_either_vehicle_epoch(tmp_path):
    hub=MapHub.__new__(MapHub);hub.data=tmp_path;hub.reference='b';hub.names={'a':'/a','b':'/b'}
    states={r:{'online':True,'samples':{'navigation':{'value':{'localization_epoch':r+'-current'}}}} for r in hub.names}
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({'validated':True,'epochs':{'a':'a-current','b':'b-current'},'transforms':{'a':[1.,0.,0.],'b':[0.,0.,0.]}}))
    assert len(hub.transforms(states))==2
    states['a']['samples']['navigation']['value']['localization_epoch']='new-session'
    assert hub.transforms(states)=={'b':[0.,0.,0.]}


def test_plan_rejects_unknown_and_occupied_endpoint():
    source=grid();source.data[50*100+50]=100
    with pytest.raises(ValueError):grid_path(source,[1.,1.,0.],[5.,5.,0.])
    source.data=[-1]*10000
    with pytest.raises(ValueError):grid_path(source,[1.,1.,0.],[2.,2.,0.])


def test_actual_rmf_planner_returns_ordered_timing_and_goal_yaw():
    result=rmf_timing([[1.,1.,0.],[1.2,1.,0.],[1.2,1.,1.]],datetime.fromtimestamp(100))
    assert result[-1]['pose']==pytest.approx([1.2,1.,1.])
    assert all(a['time']<=b['time'] for a,b in zip(result,result[1:]))


def test_timed_collision_is_checked_between_path_samples():
    def plan(a,b):return [{'pose':a,'time':'2026-01-01T00:00:00'},{'pose':b,'time':'2026-01-01T00:00:02'}]
    assert timed_separation(plan([-1.,0.,0.],[1.,0.,0.]),plan([0.,-1.,0.],[0.,1.,0.]))<.2
    assert timed_separation(plan([-1.,0.,0.],[1.,0.,0.]),plan([-1.,2.,0.],[1.,2.,0.]))==pytest.approx(2.)


def test_motion_disabled_blocks_direct_arm_and_action_calls():
    events=[]
    client=SimpleNamespace(motion_enabled=False,event=lambda *a,**k:events.append((a,k)))
    NavigationClient.arm(client,'arm')
    NavigationClient.send_goal(client,{'id':'goal'})
    assert len(events)==2 and all(event[0][1]=='rejected' for event in events)


def test_wrong_vehicle_identity_never_becomes_assigned_state():
    records=[]
    observer=SimpleNamespace(robot_id='robot_113',record=lambda k,v:records.append((k,v)))
    RobotObserver.status(observer,'navigation',String(data=json.dumps({'robot_id':'robot_104','local_ready':True})))
    assert records==[('identity_error',{'received_robot':'robot_104'})]


def test_preparation_rejects_goal_from_previous_localization_session():
    packet={'schema':1,'sent_monotonic':time.monotonic(),'op':'prepare','id':'old','pose':[0.,0.,0.],'localization_epoch':'old'}
    packets=[json.dumps(packet).encode()]
    def receive(_):
        if packets:return packets.pop()
        raise BlockingIOError()
    events=[]
    client=SimpleNamespace(commands=SimpleNamespace(recv=receive),central_seen=time.monotonic(),motion_enabled=False,pending=None,
        samples={'navigation':(time.monotonic(),{'local_ready':True,'localization_epoch':'current'})},event=lambda *a,**k:events.append((a,k)))
    client.refresh_execution_permission=lambda:None
    NavigationClient.poll(client)
    assert events[0][0]==('old','rejected') and events[0][1]['message']=='localization epoch changed'
