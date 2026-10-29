from copy import deepcopy
import json
import time

from test_auto_registration import states
from omnifleet_rmf_adapter.registration import AutoRegistration, registration_members, commit_alignment


def test_new_member_registers_while_unrelated_old_member_is_offline():
    current=states()
    current['new_rover']=deepcopy(current['robot_104'])
    current['new_rover']['samples']['navigation']['value']['localization_epoch']='new-session'
    current['robot_104']['online']=False
    members=registration_members(current,current,'robot_113',{'robot_113'})
    assert members==['robot_113','new_rover']
    p=AutoRegistration()
    assert not p.due(current,members,False,False,0.)
    assert p.due(current,members,False,False,5.)


def test_already_aligned_busy_peer_does_not_block_new_member():
    current=states()
    current['new_rover']=deepcopy(current['robot_104'])
    current['robot_104']['samples']['navigation']['value']['navigation_active']=True
    assert registration_members(current,current,'robot_113',{'robot_113','robot_104'})==['robot_113','new_rover']
    assert registration_members(current,current,'robot_113',set(current))==[]


def test_reference_must_remain_available_and_stationary():
    current=states();current['robot_113']['online']=False
    assert registration_members(current,current,'robot_113')==[]


def test_rejoining_pending_member_restarts_the_stability_window():
    current=states();policy=AutoRegistration()
    members=registration_members(current,current,'robot_113',{'robot_113'})
    assert not policy.due(current,members,False,False,0.)
    assert policy.due(current,members,False,False,5.)
    current['robot_104']['online']=False
    assert registration_members(current,current,'robot_113',{'robot_113'})==[]
    assert not policy.due(current,[],True,False,50.)
    current['robot_104']['online']=True
    assert not policy.due(current,members,False,False,100.)
    assert policy.due(current,members,False,False,105.)
    current['robot_113']['online']=True
    current['robot_113']['samples']['control']['value']['velocity_age']=3.
    assert registration_members(current,current,'robot_113')==[]


def test_pair_commit_preserves_current_peers_but_drops_old_sessions(tmp_path):
    robots=['anchor','old','new','rebooted']
    report={'wall_time_seconds':time.time(),'robots':{r:{'connection_id':r,'online':True,
        'fresh':dict.fromkeys(('map','pose','navigation','control'),True),
        'samples':{'navigation':{'value':{'local_ready':True,'localization_epoch':r+'-epoch'}},
                   'control':{'value':{'stopped_seconds':10.,'velocity':[0.,0.],'velocity_age':0.}}}}
        for r in robots}}
    report['robots']['old']['online']=False
    (tmp_path/'connection_status.json').write_text(json.dumps(report))
    old={'validated':True,'epochs':{'anchor':'anchor-epoch','old':'old-epoch','rebooted':'previous-epoch'},
         'transforms':{'anchor':[0,0,0],'old':[1,0,0],'rebooted':[2,0,0]}}
    (tmp_path/'fleet_alignment.json').write_text(json.dumps(old))
    pair={'validated':True,'reference_robot':'anchor','epochs':{'anchor':'anchor-epoch','new':'new-epoch'},
          'transforms':{'anchor':[0,0,0],'new':[3,0,0]}}
    commit_alignment(tmp_path,pair,['anchor','new'])
    saved=json.loads((tmp_path/'fleet_alignment.json').read_text())
    assert set(saved['transforms'])=={'anchor','old','new'}
    assert saved['transforms']['old']==[1,0,0]


def test_changed_anchor_never_preserves_transforms_from_old_world(tmp_path):
    current=states()
    report={'wall_time_seconds':time.time(),'robots':{r:{**s,'connection_id':r} for r,s in current.items()}}
    (tmp_path/'connection_status.json').write_text(json.dumps(report))
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({'validated':True,'epochs':{'robot_113':'old','foreign':'f'},
        'transforms':{'robot_113':[0,0,0],'foreign':[5,0,0]}}))
    pair={'validated':True,'reference_robot':'robot_113','epochs':{r:s['samples']['navigation']['value']['localization_epoch'] for r,s in current.items()},
          'transforms':{'robot_113':[0,0,0],'robot_104':[1,0,0]}}
    commit_alignment(tmp_path,pair,list(current))
    assert 'foreign' not in json.loads((tmp_path/'fleet_alignment.json').read_text())['transforms']


def test_automatic_subset_pipeline_commits_good_new_member_even_when_another_fails(tmp_path,monkeypatch):
    import os
    import omnifleet_rmf_adapter.registration as module
    template=states()['robot_104']
    current={r:deepcopy(template) for r in ('anchor','arriving_good','arriving_bad','retired')}
    for r,s in current.items():s['samples']['navigation']['value']['localization_epoch']=r+'-epoch'
    current['retired']['online']=False
    config={'robots':{r:{'enabled':True} for r in current},'central':{'reference_robot':'anchor'}}
    config_path=tmp_path/'framework.json';config_path.write_text(json.dumps(config))
    report={'wall_time_seconds':time.time(),'robots':{r:{**s,'connection_id':r} for r,s in current.items()}}
    (tmp_path/'connection_status.json').write_text(json.dumps(report))
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({'validated':True,'epochs':{'anchor':'anchor-epoch','retired':'retired-epoch'},
        'transforms':{'anchor':[0,0,0],'retired':[9,0,0]}}))
    monkeypatch.setenv('OMNIFLEET_REGISTRATION_SOURCE','')
    monkeypatch.setenv('OMNIFLEET_CONFIG',str(config_path));monkeypatch.setenv('OMNIFLEET_DATA',str(tmp_path))
    members=registration_members(current,current,'anchor',{'anchor'})
    assert members==['anchor','arriving_good','arriving_bad']
    monkeypatch.setenv('OMNIFLEET_REGISTRATION_ROBOTS',json.dumps(members))
    calls=[]
    def stage(script,timeout):
        source=os.environ.get('OMNIFLEET_REGISTRATION_SOURCE')
        calls.append((script.name,source))
        if script.name!='register_clouds.py':return
        pair={'validated':source=='arriving_good','epochs':{'anchor':'anchor-epoch',source:source+'-epoch'},
              'transforms':{'anchor':[0,0,0],source:[1,2,.3]},
              'best':{'fitness':.9,'reverse_fitness':.4 if source=='arriving_bad' else .9,'inlier_rmse_m':.02},
              'distinct_candidate_margin':.2}
        (tmp_path/'alignment/cloud-registration.json').write_text(json.dumps(pair))
    monkeypatch.setattr(module,'run_stage',stage)
    module.main()
    status=json.loads((tmp_path/'registration-job.json').read_text())
    saved=json.loads((tmp_path/'fleet_alignment.json').read_text())
    assert status['phase']=='partial' and set(status['errors'])=={'arriving_bad'}
    assert set(saved['transforms'])=={'anchor','retired','arriving_good'}
    assert 'arriving_bad' not in saved['epochs']
    assert registration_members(current,current,'anchor',{'anchor','arriving_good'})==['anchor','arriving_bad']
    assert not any(source=='retired' for _,source in calls)
