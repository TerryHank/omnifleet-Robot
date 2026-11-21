import copy
import math
from types import SimpleNamespace as NS
import pytest

from test_missions import fleet,save
from test_operator_controls import controls
from omnifleet_rmf_adapter.operator_controls import OperatorControls
from geometry_msgs.msg import PoseStamped


def populated(f):
    message=PoseStamped();message.header.frame_id='fleet_map';message.pose.position.x=2.;message.pose.position.y=4.;message.pose.orientation.w=1.
    f.operator.waypoint('connection',message)
    message.pose.position.y=5.;f.operator.waypoint('connection',message)
    f.owner.missions.jobs.clear()  # Drag edits are tested after operator stop, independently of automatic start.
    route=f.owner.missions.saved['routes']['connection']
    command={'op':'route_update','id':'drag','robot_id':'connection','route_revision':route['revision'],
        'localization_epoch':'epoch','map_transform':[2.,3.,math.pi/2],'index':1,'position':[4.,5.]}
    return command


def test_drag_updates_only_selected_point_and_preserves_heading_and_order(controls):
    f=controls;command=populated(f);before=copy.deepcopy(f.owner.missions.saved['routes']['connection'])
    result=f.operator.update_waypoint(command,f.states)
    after=f.owner.missions.saved['routes']['connection']
    assert result['phase']=='saved' and after['revision']==before['revision']+1
    assert after['points'][0]['pose']==pytest.approx([2.,-2.,-math.pi/2])
    assert after['points'][0]['name']==before['points'][0]['name'] and after['points'][1]==before['points'][1]
    assert not f.sent and not f.owner.missions.jobs
    with pytest.raises(ValueError,match='队列已变化'):f.operator.update_waypoint(command,f.states)


@pytest.mark.parametrize('field,value', [('localization_epoch','old'),('map_transform',[0.,0.,0.]),('index',0),('index',True),('position',[float('nan'),1.])])
def test_stale_or_invalid_drag_never_changes_saved_points(controls,field,value):
    f=controls;command=populated(f);before=copy.deepcopy(f.owner.missions.saved)
    command[field]=value
    with pytest.raises(ValueError):f.operator.update_waypoint(command,f.states)
    assert f.owner.missions.saved==before and not f.sent


def test_navigation_active_blocks_drag(controls):
    f=controls;command=populated(f);before=copy.deepcopy(f.owner.missions.saved)
    f.states['connection']['samples']['navigation']['value']['navigation_active']=True
    with pytest.raises(ValueError,match='导航执行中'):f.operator.update_waypoint(command,f.states)
    assert f.owner.missions.saved==before


def batch_operator(f):
    return NS(stopped=False,owner=NS(missions=f.owner,maps=f.maps,execution_permissions=lambda _:({},{},{r:True for r in f.maps.names})))


def test_batch_starts_both_multigoal_routes_and_skips_vehicle_without_route(fleet):
    f=fleet;save(f,'a',[[1.,0.,0.],[2.,0.,0.]]);save(f,'b',[[1.,4.,0.],[2.,4.,0.]])
    result=OperatorControls.start_routes(batch_operator(f),{'id':'batch'},f.states)
    assert result['phase']=='accepted' and set(f.owner.jobs)=={'a','b'}
    assert result['vehicles']['c']=={'phase':'skipped','message':'未安排航点'}
    assert all(len(j['points'])==2 and j['source']=='route' for j in f.owner.jobs.values())
    assert not f.sent


def test_empty_saved_route_is_unassigned_and_cannot_start(fleet):
    f=fleet;save(f,'a',[[1.,0.,0.]])
    previous=f.owner.saved['routes']['a']['revision'];save(f,'a',[])
    assert f.owner.saved['routes']['a']['revision']==previous+1
    result=OperatorControls.start_routes(batch_operator(f),{'id':'batch'},f.states)
    assert all(v['phase']=='skipped' for v in result['vehicles'].values()) and not f.owner.jobs
    with pytest.raises(ValueError,match='保存.*航点'):f.owner.command({'op':'route_start','id':'single','robot_id':'a'},f.states)


def test_unready_vehicle_is_reported_without_blocking_other_assigned_vehicle(fleet):
    f=fleet;save(f,'a',[[1.,0.,0.]]);save(f,'b',[[1.,4.,0.]])
    f.states['b']['online']=False
    result=OperatorControls.start_routes(batch_operator(f),{'id':'batch'},f.states)
    assert set(f.owner.jobs)=={'a'} and result['vehicles']['b']['phase']=='rejected' and result['vehicles']['c']['phase']=='skipped'


def test_batch_cannot_overlap_following(fleet):
    f=fleet;save(f,'a',[[1.,0.,0.]]);f.owner.follow['active']=True
    with pytest.raises(ValueError,match='停止跟随'):OperatorControls.start_routes(batch_operator(f),{'id':'batch'},f.states)
    assert not f.owner.jobs and not f.sent
