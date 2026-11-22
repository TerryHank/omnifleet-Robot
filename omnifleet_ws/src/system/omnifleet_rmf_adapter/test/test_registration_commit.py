import json
import time

import pytest

from omnifleet_rmf_adapter.registration import commit_alignment, registration_pair


def fixture(tmp_path):
    report={'wall_time_seconds':time.time(),'robots':{public:{
        'connection_id':connection,'online':True,
        'fresh':dict.fromkeys(('map','pose','navigation','control'),True),
        'samples':{'navigation':{'value':{'local_ready':True,'localization_epoch':epoch}},
                   'control':{'value':{'velocity':[0.,0.],'stopped_seconds':10.,'velocity_age':0.}}}}
        for public,connection,epoch in [('alpha','link_a','boot_a'),('beta','link_b','boot_b')]}}
    result={'validated':True,'epochs':{'link_a':'boot_a','link_b':'boot_b'},
            'transforms':{'link_a':[0.,0.,0.],'link_b':[1.,2.,3.]}}
    (tmp_path/'connection_status.json').write_text(json.dumps(report))
    (tmp_path/'fleet_alignment.json').write_text('original')
    return report,result


def test_commit_new_sessions_with_arbitrary_public_names(tmp_path):
    _,result=fixture(tmp_path)
    commit_alignment(tmp_path,result,('link_a','link_b'))
    assert json.loads((tmp_path/'fleet_alignment.json').read_text())==result


@pytest.mark.parametrize('fault',('epoch','failed_match','moving','stale','central_dead','offline','manual_moving'))
def test_rejected_match_never_replaces_existing_alignment(tmp_path,fault):
    report,result=fixture(tmp_path)
    state=report['robots']['alpha']
    if fault=='epoch':state['samples']['navigation']['value']['localization_epoch']='rebooted'
    elif fault=='failed_match':result['validated']=False
    elif fault=='moving':state['samples']['control']['value']['velocity']=[.02,0.]
    elif fault=='stale':state['fresh']['map']=False
    elif fault=='central_dead':report['wall_time_seconds']-=10.
    elif fault=='offline':state['online']=False
    elif fault=='manual_moving':state['samples']['control']['value'].update(manual_active=True,velocity=[.02,0.])
    (tmp_path/'connection_status.json').write_text(json.dumps(report))
    with pytest.raises(ValueError):commit_alignment(tmp_path,result,('link_a','link_b'))
    assert (tmp_path/'fleet_alignment.json').read_text()=='original'


def test_reference_is_configured_without_fixed_vehicle_ids():
    config={'robots':{'socket_b':{'enabled':True},'socket_a':{'enabled':True}},
            'central':{'reference_robot':'socket_a'}}
    assert registration_pair(config)==('socket_b','socket_a')


def test_stopped_manual_mode_can_commit_validated_geometry(tmp_path):
    report,result=fixture(tmp_path)
    report['robots']['alpha']['samples']['control']['value'].update(manual_active=True,control_mode='MANUAL')
    (tmp_path/'connection_status.json').write_text(json.dumps(report))
    commit_alignment(tmp_path,result,('link_a','link_b'))
    assert json.loads((tmp_path/'fleet_alignment.json').read_text())==result
