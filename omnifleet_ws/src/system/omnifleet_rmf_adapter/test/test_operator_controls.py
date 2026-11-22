import math
import time
from types import SimpleNamespace as NS

import pytest
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import Bool
from omnifleet_rmf_adapter.missions import Missions
from omnifleet_rmf_adapter.operator_controls import OperatorControls
from omnifleet_rmf_adapter.control_client import NavigationClient


@pytest.fixture
def controls(tmp_path):
    states={'connection':{'online':True,'fresh':{'map':True,'fleet_client':True},'samples':{
        'navigation':{'value':{'localization_epoch':'epoch','local_ready':True}},
        'control':{'value':{'control_gate_ready':True,'stopped_seconds':2.}},'fleet_client':{'value':{'busy':False}}}}}
    maps=NS(names={'connection':'/car_new'},valid_robots={'connection'},alignment={'connection':[2.,3.,math.pi/2]})
    config={'robots':{'connection':{'motion_enabled':True}},'central':{'assignments':{'connection':{'robot_name':'car_new'}}}}
    sent=[];subscriptions=[];destroyed=[];published=[]
    owner=NS(data=tmp_path,config=config,maps=maps,identities=NS(revision=9),snapshots=lambda:states,
        create_subscription=lambda cls,topic,callback,qos:subscriptions.append((topic,callback)) or topic,
        destroy_subscription=destroyed.append,create_publisher=lambda *a:NS(publish=published.append),create_timer=lambda *a:None,
        send_command=lambda *a,**k:sent.append((a,k)),execution_permissions=lambda _:({},{},{'connection':True}))
    owner.missions=Missions(config,maps,tmp_path,owner.send_command)
    operator=OperatorControls(owner)
    yield NS(operator=operator,owner=owner,sent=sent,states=states,subscriptions=subscriptions,destroyed=destroyed,published=published)
    owner.missions.close()


def test_shared_map_click_stages_queue_and_appends_local_coordinates(controls):
    f=controls;m=PoseStamped();m.header.frame_id='fleet_map';m.pose.position.x=2.;m.pose.position.y=4.;m.pose.orientation.w=1.
    f.operator.waypoint('connection',m);f.operator.waypoint('connection',m)
    route=f.owner.missions.saved['routes']['connection']
    assert len(route['points'])==2 and route['epoch']=='epoch'
    assert route['points'][0]['pose']==pytest.approx([1.,0.,-math.pi/2])
    assert not f.sent and not f.owner.missions.jobs and f.operator.receipt['count']==2
    assert f.operator.receipt['phase']=='saved'
    f.operator.publish_waypoints()
    assert f.published[-1].markers[-1].text=='car_new / 航点2'


def test_wrong_frame_rejects_and_new_session_click_starts_a_fresh_queue(controls):
    f=controls;m=PoseStamped();m.header.frame_id='map';m.pose.orientation.w=1.
    f.operator.waypoint('connection',m)
    assert f.operator.receipt['phase']=='rejected' and not f.owner.missions.saved['routes']
    f.owner.missions.saved['routes']['connection']={'epoch':'old','points':[{'name':'航点1','pose':[1.,0.,0.]}]};m.header.frame_id='fleet_map'
    f.operator.waypoint('connection',m)
    assert f.operator.receipt['phase']=='saved' and f.operator.receipt['count']==1
    route=f.owner.missions.saved['routes']['connection']
    assert route['epoch']=='epoch' and len(route['points'])==1 and route['points'][0]['name']=='航点1'
    assert len(list((f.owner.missions.file.parent/'route_archive').glob('*.json')))==1


def test_rebind_removes_retired_prefix_and_revision_subscriptions(controls):
    f=controls;f.owner.maps.names['connection']='/leader_new';f.owner.identities.revision=10
    f.operator.bind()
    assert '/car_new/ui/r9/waypoint' in f.destroyed and '/car_new/ui/r9/cmd_vel' in f.destroyed
    assert [s[0] for s in f.subscriptions][-2:]==['/leader_new/ui/r10/waypoint','/leader_new/ui/r10/cmd_vel']


def test_teleop_uses_requested_connection_but_not_active_follower(controls):
    f=controls;m=Twist();m.linear.x=.15
    f.operator.manual('connection',m)
    assert f.sent[-1][0][0]=='manual' and f.sent[-1][1]=={'robot_id':'connection','velocity':[.15,0.]}
    f.sent.clear();f.owner.missions.follow.update(active=True,leader='other')
    f.operator.manual('connection',m)
    assert not f.sent
    m.linear.x=0.;f.operator.manual('connection',m)
    assert f.sent[-1][1]['velocity']==[0.,0.]


def test_operator_stop_stops_jobs_and_blocks_held_direction_without_auto_resume(controls):
    f=controls;f.operator.pause(Bool(data=True));f.sent.clear();m=Twist();m.linear.x=.15
    f.operator.manual('connection',m);assert not f.sent
    f.operator.pause(Bool(data=False));assert not f.sent and not f.owner.missions.follow['active']


def test_vehicle_manual_watchdog_zeroes_velocity_and_never_acquires_fleet():
    published=[]
    client=NS(motion_enabled=True,manual_publisher=NS(publish=published.append),manual_until=0.)
    NavigationClient.manual(client,{'velocity':[.15,0.]})
    assert published[-1].linear.x==.15 and client.manual_until>time.monotonic()
    NavigationClient.stop_manual(client)
    assert published[-1].linear.x==0. and client.manual_until==0.
    NavigationClient.manual(client,{'velocity':[float('nan'),0.]})
    NavigationClient.manual(client,{'velocity':[.31,0.]})
    client.motion_enabled=False;NavigationClient.manual(client,{'velocity':[.15,0.]})
    assert len(published)==2
