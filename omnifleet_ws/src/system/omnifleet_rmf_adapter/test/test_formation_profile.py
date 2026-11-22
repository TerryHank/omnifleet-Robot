from concurrent.futures import Future
from types import SimpleNamespace as NS
import json

import pytest
from rclpy.parameter import Parameter
from omnifleet_rmf_adapter.formation_profile import FormationProfile


@pytest.mark.parametrize('kind',['default','old_mppi','ackermann','navfn','rpp'])
def test_effective_acceleration_source_preserves_default_and_ackermann_queries(monkeypatch,kind):
    monkeypatch.setattr('omnifleet_rmf_adapter.formation_profile.time.monotonic',lambda:100.)
    raw={'FollowPath.vx_max':.18,'FollowPath.vx_min':-.12,'FollowPath.wz_max':.7,
         'FollowPath.motion_model':'Ackermann' if kind=='ackermann' else 'DiffDrive',
         'footprint':json.dumps([[-.1,-.1],[.1,-.1],[.1,.1],[-.1,.1]]),'footprint_padding':.01,'robot_radius':.12,
         'GridBased.allow_unknown':True,'GridBased.max_planning_time':3.}
    if kind=='default':raw.update({'FollowPath.ax_max':.3,'FollowPath.ax_min':-.6,'FollowPath.az_max':1.})
    else:raw.update({'max_accel':[.3,0.,1.],'max_decel':[-.6,0.,-1.]})
    if kind=='ackermann':raw.update({'FollowPath.AckermannConstraints.min_turning_r':1.05,'GridBased.minimum_turning_radius':1.05})
    if kind in ('navfn','rpp'):raw.pop('GridBased.max_planning_time')
    if kind=='rpp':
        raw.update({'FollowPath.desired_linear_vel':.18,'FollowPath.allow_reversing':False,'max_velocity':[.18,0.,.7],'min_velocity':[-.12,0.,-.7]})
    calls=[];records=[]
    def create(typ,path):
        def get(request):
            calls.append((path,request.names));future=Future()
            future.set_result(NS(values=[Parameter(name,value=raw[name]).get_parameter_value() for name in request.names]))
            return future
        return NS(service_is_ready=lambda:True,call_async=get)
    profile={'acceleration_source':'velocity_smoother'} if kind=='old_mppi' else {'vehicle_type':'ackermann'} if kind=='ackermann' else {}
    if kind=='navfn':profile={'acceleration_source':'velocity_smoother','planner_type':'navfn'}
    if kind=='rpp':profile={'controller_type':'rpp','vehicle_type':'diff_drive','planner_type':'navfn'}
    node=NS(profile=profile,selected_algorithms={'controller':'FollowPath','planner':'GridBased'},
            create_client=create,record=lambda key,value:records.append(value))
    reader=FormationProfile(node);reader.tick();reader.tick()
    assert records[0]['limits']=={'forward':.18,'reverse':0. if kind=='rpp' else .12,'angular':.7,'accel':.3,'decel':.6,'angular_accel':1.}
    assert records[0]['limits_source']=='onboard_parameters'
    assert any('velocity_smoother' in path for path,_ in calls)==(kind!='default')
    if kind=='ackermann':assert records[0]['minimum_turning_radius']==1.05
