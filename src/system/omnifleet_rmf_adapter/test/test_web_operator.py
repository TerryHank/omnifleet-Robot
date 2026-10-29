import math
from types import SimpleNamespace as NS
import pytest
from test_operator_controls import controls
from omnifleet_rmf_adapter.permanent_parameters import validate_changes,ParameterClient

def test_web_single_goal_uses_same_vehicle_navigation_and_fleet_transform(controls):
    f=controls
    result=f.operator.web_command({'op':'web_goal','id':'goal','robot_id':'connection','pose':[2.,4.,0.]},f.states)
    assert result['phase']=='accepted'
    job=f.owner.missions.jobs['connection']
    assert job['source']=='single' and job['points'][0]['pose']==pytest.approx([1.,0.,-math.pi/2])
    assert not f.sent

def test_web_multi_additions_preserve_queue_and_ordinary_executor(controls):
    f=controls
    for i in (4.,5.):f.operator.web_command({'op':'web_goal','id':'add','robot_id':'connection','pose':[2.,i,0.],'multi':True},f.states)
    assert len(f.owner.missions.saved['routes']['connection']['points'])==2
    assert f.owner.missions.jobs['connection']['source']=='route'

def test_web_manual_rejects_follower_but_zero_still_reaches_native_owner(controls):
    f=controls;f.owner.missions.follow.update(active=True,leader='other')
    with pytest.raises(ValueError):f.operator.web_command({'op':'web_manual','id':'drive','robot_id':'connection','velocity':[.15,0.]},f.states)
    f.operator.web_command({'op':'web_manual','id':'stop','robot_id':'connection','velocity':[0.,0.]},f.states)
    assert f.sent[-1][1]['velocity']==[0.,0.]

def test_web_pause_and_release_never_resume_an_old_goal(controls):
    f=controls;f.operator.web_command({'op':'web_stop','stopped':True},f.states);f.sent.clear()
    f.operator.web_command({'op':'web_stop','stopped':False},f.states)
    assert not f.sent and not f.owner.missions.follow['active']

@pytest.mark.parametrize('value',[float('nan'),float('inf'),True,'1'])
def test_web_invalid_pose_never_creates_a_native_job(controls,value):
    with pytest.raises(ValueError):controls.operator.web_command({'op':'web_goal','id':'bad','robot_id':'connection','pose':[value,1.,0.]},controls.states)
    assert not controls.owner.missions.jobs

def test_extended_permanent_fields_use_real_types_and_original_limits():
    assert validate_changes({'mppi_vx_max':.5,'follow_gap_gain':1.,'follow_speed_damping':.35})
    assert validate_changes({'local_controller_algorithm':'mppi'})
    with pytest.raises(ValueError):validate_changes({'local_controller_algorithm':'not_registered'})
    with pytest.raises(ValueError):validate_changes({'follow_gap_gain':True})
    with pytest.raises(ValueError):validate_changes({'__stack_status':'arbitrary'})

def test_integer_and_boolean_parameter_serialization_uses_vehicle_service():
    from test_permanent_parameters import client
    owner,services,_=client()
    owner.request({'op':'nav_parameters_save','id':'typed','changes':{'mppi_time_steps':56,'automatic_replanning':True}})
    values={p.name:p.value for p in owner.writer.calls[0].parameters}
    assert values['mppi_time_steps'].type==2 and values['automatic_replanning'].type==1

def test_shared_costmap_controls_are_read_back_under_their_panel_ids():
    from omnifleet_rmf_adapter.permanent_parameters import compact_receipt
    result=compact_receipt({'saved':{'local_radius':{'inflation_radius':.55},'global_radius':{'inflation_radius':.55},
                                   'local_padding':{'footprint_padding':0.},'global_padding':{'footprint_padding':0.}}})
    assert result['saved']['costmap_radius']=={'inflation_radius':.55}
    assert result['saved']['costmap_padding']=={'footprint_padding':0.}
