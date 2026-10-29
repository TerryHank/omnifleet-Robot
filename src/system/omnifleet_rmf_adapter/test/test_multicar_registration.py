import copy

import pytest

from test_auto_registration import states
from omnifleet_rmf_adapter.registration import AutoRegistration, merge_registrations, registration_pair


def test_five_vehicles_can_enter_the_existing_stationary_registration_gate():
    current=states()
    for name in ['third','fourth','fifth']:
        current[name]=copy.deepcopy(current['robot_104'])
        current[name]['samples']['navigation']['value']['localization_epoch']=name
    p=AutoRegistration()
    assert not p.due(current,current,False,False,0)
    assert p.due(current,current,False,False,5)


def test_each_pair_is_bound_to_the_configured_reference(monkeypatch):
    config={'robots':{r:{'enabled':True} for r in ['a','b','c']},'central':{'reference_robot':'a'}}
    monkeypatch.setenv('OMNIFLEET_REGISTRATION_SOURCE','c')
    assert registration_pair(config)==('c','a')
    monkeypatch.setenv('OMNIFLEET_REGISTRATION_SOURCE','unassigned')
    with pytest.raises(ValueError):registration_pair(config)


def test_multiple_validated_pair_transforms_commit_as_one_fleet():
    results=[(r,{'validated':True,'transforms':{'a':[0,0,0],r:[i,0,0]},'epochs':{'a':'a-map',r:r+'-map'},'best':{'fitness':.9}}) for i,r in enumerate(['b','c'],1)]
    saved=merge_registrations(results,['a','b','c'],'a')
    assert saved['transforms']=={'a':[0,0,0],'b':[1,0,0],'c':[2,0,0]}
    results[1][1]['epochs']['a']='changed'
    with pytest.raises(ValueError,match='localization changed'):merge_registrations(results,['a','b','c'],'a')
