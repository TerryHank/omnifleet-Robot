import importlib.util,json,math,sys
from pathlib import Path

import pytest
import yaml

HERE=Path(__file__).parent
LIVE=Path('/home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/nav2_permanent_panel')
sys.path.insert(0,str(LIVE))
def module(name,filename,live):
    path=HERE/filename
    if not path.exists():path=LIVE/live
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec)
    sys.modules[name]=result;spec.loader.exec_module(result);return result
model=module('collision_model','model-after.py','collision_model.py')
links=module('parameter_links','links-after.py','parameter_links.py')
store=module('_geometry_store','store-after.py','nav2_parameter_store.py')


@pytest.fixture
def config(tmp_path):
    data=yaml.safe_load(store.YAML_FILE.read_text())
    for scope in ('local','global'):
        p=data[scope+'_costmap'][scope+'_costmap']['ros__parameters']
        p['footprint']='[[0.25,0.185],[0.25,-0.185],[-0.25,-0.185],[-0.25,0.185]]'
        p.pop('robot_radius',None);p['footprint_padding']=.05;p['inflation_layer']['inflation_radius']=.4
    for path in model.model_paths(data):
        if path[-1]=='consider_footprint':model.parent_at(data,path)[path[-1]]=True
    path=tmp_path/'nav2.yaml';path.write_text(yaml.safe_dump(data,sort_keys=False))
    return path


def save(path,changes):return store.save_changes(changes,path,path.parent/'backups')


def values():
    result={'geometry_local_resolution':.01,'geometry_mppi_consider_footprint':False}
    for scope in ('local','global'):
        result.update({f'geometry_{scope}_footprint':'[]',f'geometry_{scope}_robot_radius':.01,
                       f'geometry_{scope}_footprint_padding':0.,f'geometry_{scope}_inflation_radius':.01})
    return result


def test_nine_fields_persist_with_correct_types_and_restart_policy(config):
    desired=values();receipt=save(config,desired)
    actual=store.saved_values(config)
    for key,value in desired.items():
        read=next(iter(actual[key].values()));assert read==value and type(read)==type(value)
    assert (set(desired)-{'geometry_local_inflation_radius','geometry_global_inflation_radius'})<=store.RESTART_ONLY
    assert not {'geometry_local_inflation_radius','geometry_global_inflation_radius'} & store.RESTART_ONLY
    assert receipt['collision_model']['mode']=='point'
    assert yaml.safe_load(config.read_text())['local_costmap']['local_costmap']['ros__parameters']['footprint']=='[]'


def test_local_global_fields_are_independent(config):
    before=yaml.safe_load(config.read_text())
    save(config,{'geometry_local_footprint_padding':.02,'geometry_global_inflation_radius':.7})
    after=yaml.safe_load(config.read_text())
    before['local_costmap']['local_costmap']['ros__parameters']['footprint_padding']=.02
    before['global_costmap']['global_costmap']['ros__parameters']['inflation_layer']['inflation_radius']=.7
    assert after==before


@pytest.mark.parametrize('value',['garbage','{}','null','[[1,1],[2,2]]','[[0,0],[1,1],[2,2]]',
                                 '[[true,0],[1,0],[0,1]]','[[0,0],[1,0],[0,NaN]]','[[0,0,0],[1,0],[0,1]]'])
def test_invalid_polygon_never_changes_saved_configuration(config,value):
    old=config.read_bytes()
    with pytest.raises((ValueError,TypeError)):save(config,{'geometry_local_footprint':value})
    assert config.read_bytes()==old and not model.profile_path(config).exists()


@pytest.mark.parametrize('key,value',[('geometry_local_robot_radius',0.),('geometry_global_robot_radius',float('nan')),
                                     ('geometry_local_footprint_padding',-.1),('geometry_global_inflation_radius',True),
                                     ('geometry_local_resolution',.001),
                                     ('geometry_mppi_consider_footprint','false')])
def test_invalid_scalar_or_boolean_is_rejected(config,key,value):
    old=config.read_bytes()
    with pytest.raises(ValueError):save(config,{key:value})
    assert config.read_bytes()==old


def test_manual_edit_becomes_custom_and_body_restore_keeps_other_tuning(config):
    original=yaml.safe_load(config.read_text())
    save(config,{'geometry_local_footprint':'[]','geometry_local_robot_radius':.08})
    assert model.state(config)['mode']=='custom'
    save(config,{'mppi_vx_max':.19})
    model.save_mode('body',config,config.parent/'backups',navigation_active=False,state_age=.1,motion_age=3)
    original['controller_server']['ros__parameters']['FollowPathMPPI']['vx_max']=.19
    assert yaml.safe_load(config.read_text())==original


def test_existing_body_backup_survives_custom_then_point_switch(config):
    save(config,{'geometry_local_robot_radius':.03});body=model.profile_path(config).read_bytes()
    model.save_mode('point',config,config.parent/'backups',navigation_active=False,state_age=.1,motion_age=3)
    assert model.profile_path(config).read_bytes()==body
    save(config,{'geometry_global_inflation_radius':.02})
    assert model.state(config)['mode']=='point'


def test_absent_radius_reads_default_and_config_links_still_work(config,tmp_path,monkeypatch):
    saved=store.saved_values(config)
    assert saved['geometry_local_robot_radius']['robot_radius']==.1
    height=tmp_path/'height.json';height.write_text(json.dumps({'slice_z_min':-.03,'slice_z_max':.5}))
    selected=tmp_path/'selected.json';selected.write_text(json.dumps({'global':'smac_2d','local':'mppi'}))
    pwm=tmp_path/'pwm.yaml';pwm.write_text('pwm_compensation_m1: 0\npwm_compensation_m2: 0\n')
    monkeypatch.setattr(links,'PWM_VIEW',pwm)
    catalog=links.catalog(store.SPECS,config,height,selected)
    for key in values():assert catalog[key]['targets'] and catalog[key]['docs']['url']
    assert '缺省' in catalog['geometry_local_robot_radius']['targets'][0]['label']
    save(config,{'geometry_local_robot_radius':.12})
    updated=links.catalog(store.SPECS,config,height,selected)
    assert '缺省' not in updated['geometry_local_robot_radius']['targets'][0]['label']


def test_same_values_do_not_rewrite_the_config(config):
    key='geometry_local_footprint';value=store.saved_values(config)[key]['footprint'];old=config.read_bytes()
    save(config,{key:value});assert config.read_bytes()==old and not model.profile_path(config).exists()
