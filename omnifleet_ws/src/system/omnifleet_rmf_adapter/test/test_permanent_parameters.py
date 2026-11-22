import json
from types import SimpleNamespace as NS
from concurrent.futures import Future
import pytest
from omnifleet_rmf_adapter.permanent_parameters import ParameterClient,ParameterCommands,compact_receipt,validate_changes


class Service:
    def __init__(self):self.calls=[];self.future=Future();self.removed=[]
    def service_is_ready(self):return True
    def call_async(self,request):self.calls.append(request);return self.future
    def remove_pending_request(self,future):self.removed.append(future)


def client():
    services={};samples=[]
    def create(kind,name):services[name]=Service();return services[name]
    node=NS(profile={'observed_namespace':''},create_client=create,create_timer=lambda *a:None,record=lambda k,v:samples.append(v))
    return ParameterClient(node),services,samples


def test_selected_robot_uses_existing_onboard_service_and_links_both_costmaps():
    owner,services,_=client()
    owner.request({'op':'nav_parameters_save','id':'save','changes':{'geometry_local_inflation_radius':.6,'costmap_scaling':2.}})
    request=services['/omnifleet_t2/nav2/save_parameters'].calls[0]
    assert {p.name for p in request.parameters}=={'geometry_local_inflation_radius','geometry_global_inflation_radius','local_scaling','global_scaling'}
    assert all(p.value.type==3 for p in request.parameters)


def test_all_vehicle_sync_skips_unchanged_geometry_but_repairs_different_global_value():
    owner,services,_=client()
    owner.snapshot={'saved':{'geometry_local_robot_radius':{'robot_radius':.01},'geometry_global_robot_radius':{'robot_radius':.01},
        'geometry_local_inflation_radius':{'inflation_radius':.55},'geometry_global_inflation_radius':{'inflation_radius':.6}}}
    owner.request({'op':'nav_parameters_save','id':'save','changes':{'geometry_local_robot_radius':.01,'geometry_local_inflation_radius':.55}})
    assert {p.name for p in owner.writer.calls[0].parameters}=={'geometry_local_inflation_radius','geometry_global_inflation_radius'}


def test_saved_but_not_live_is_never_reported_as_live_confirmed():
    owner,services,samples=client();owner.request({'op':'nav_parameters_save','id':'save','changes':{'geometry_local_robot_radius':.02}})
    receipt={'saved':{'geometry_local_robot_radius':{'robot_radius':.02}},'runtime_confirmed':False,'runtime':{'geometry_local_robot_radius':'需重启'}}
    owner.writer.future.set_result(NS(results=[NS(successful=True,reason=json.dumps(receipt))]));owner.tick()
    assert samples[-1]['phase']=='saved' and samples[-1]['runtime_confirmed'] is False
    assert '重启' in samples[-1]['runtime']['geometry_local_robot_radius']


def test_single_car_save_error_does_not_hide_partial_results_for_other_car():
    sent=[];owner=ParameterCommands(lambda *a,**k:sent.append((a,k)) or True)
    states={r:{'transport_connected':True,'samples':{}} for r in ('connection_a','connection_b')}
    for r in states:owner.request({'op':'nav_parameters_save','id':r,'robot_id':r,'changes':{'geometry_local_inflation_radius':.6}},states)
    states['connection_a']['samples']['navigation_parameters']={'value':{'request_id':'connection_a','phase':'saved','runtime_confirmed':True}}
    states['connection_b']['samples']['navigation_parameters']={'value':{'request_id':'connection_b','phase':'failed','message':'本车拒绝'}}
    result={};owner.tick(states,result)
    assert result['connection_a']['phase']=='saved' and result['connection_b']['phase']=='failed'
    assert [entry[1]['robot_id'] for entry in sent]==list(states)


def test_native_validation_rejection_is_visible_and_does_not_report_saved():
    owner,_,samples=client();owner.request({'op':'nav_parameters_save','id':'save','changes':{'geometry_local_footprint':'invalid'}})
    owner.writer.future.set_result(NS(results=[NS(successful=False,reason='footprint 无效')]))
    owner.tick();assert samples[-1]['phase']=='failed' and 'footprint' in samples[-1]['message']


@pytest.mark.parametrize('changes',[{'mppi_vx_max':9.},{'geometry_local_robot_radius':True},{'geometry_local_inflation_radius':float('nan')},
    {'geometry_mppi_consider_footprint':'false'},{'__collision_model':'custom'},{'__collision_model':'point','costmap_scaling':2.}])
def test_unrelated_parameters_and_invalid_values_never_reach_vehicle(changes):
    with pytest.raises(ValueError):validate_changes(changes)


def test_read_includes_extended_navigation_parameters_and_exposes_common_scaling():
    result=compact_receipt({'saved':{'mppi_vx_max':{'vx_max':.3},'local_scaling':{'cost_scaling_factor':2.},'global_scaling':{'cost_scaling_factor':2.}},
        'parameter_links':{'large':'irrelevant'},'collision_model':{'mode':'point','restore_available':True,'details':{'unneeded':True}}})
    assert result['saved']['costmap_scaling']=={'cost_scaling_factor':2.}
    assert result['saved']['mppi_vx_max']=={'vx_max':.3} and 'parameter_links' not in result
    assert result['collision_model']=={'mode':'point','restore_available':True}


def test_timeout_reports_unknown_result_instead_of_saved(monkeypatch):
    clock=[100.];monkeypatch.setattr('omnifleet_rmf_adapter.permanent_parameters.time.monotonic',lambda:clock[0])
    owner,_,samples=client();owner.request({'op':'nav_parameters_save','id':'save','changes':{'costmap_scaling':2.}})
    clock[0]+=46.;owner.tick()
    assert samples[-1]['phase']=='failed' and '未确认' in samples[-1]['message'] and owner.writer.removed
