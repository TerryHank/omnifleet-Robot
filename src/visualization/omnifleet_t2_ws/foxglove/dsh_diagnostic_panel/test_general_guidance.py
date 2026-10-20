import json
from parameter_guidance import accepted_parameter_actions,build_parameter_details

def setup():
    keys=['turn','speed','obstacle','arrival','other_plugin']
    specs={k:(('controller_server','ros__parameters','Main' if k!='other_plugin' else 'Other'),('value',),'/controller_server',k+'.',0,100) for k in keys}
    algorithms={'local':{'current':('当前算法','Plugin','Main'),'other':('其他算法','OtherPlugin','Other')},'global':{}}
    snapshot={'parameter_catalog':{k:k for k in keys},'observations':{'/controller_selector':{'value':'Main'}},'saved_algorithms':{'local':'other'},'live_parameters':{'/controller_server':{k:5 for k in keys}},'parameter_evidence_paths':{k:['/live_parameters/~1controller_server/'+k] for k in keys},'reported_error':{'message':'故障证据'}}
    source='const parameterHelp = '+json.dumps({k:'功能说明 '+k for k in keys})+';'
    snapshot['parameter_details']=build_parameter_details(source,snapshot,specs,algorithms)
    return snapshot

def action(key,intent='inspect'):
    return {'id':key,'intent':intent,'reason':'模型根据用户意图选择的相关配置项','evidence_refs':['/live_parameters/~1controller_server/'+key]}

def test_model_selection_not_question_keywords():
    s=setup()
    for question,key in [('车头别歪着出发','turn'),('我希望慢一些','speed'),('离墙远一点','obstacle'),('停得精确一点','arrival')]:
        assert [a['id'] for a in accepted_parameter_actions({'parameter_actions':[action(key)]},question,s)]==[key]

def test_no_hardcoded_buttons_when_model_returns_none():
    assert accepted_parameter_actions({'parameter_actions':[]},'先转到航向再前进',setup())==[]

def test_current_binding_overrides_saved_algorithm():
    s=setup()
    assert s['parameter_details']['turn']['applicable'] is True
    assert s['parameter_details']['other_plugin']['applicable'] is False
    assert accepted_parameter_actions({'parameter_actions':[action('other_plugin')]},'哪项',s)==[]

def test_unknown_or_missing_evidence_rejected():
    s=setup()
    assert accepted_parameter_actions({'parameter_actions':[action('invented')]},'怎么改',s)==[]
    a=action('turn');a['evidence_refs']=['/missing']
    assert accepted_parameter_actions({'parameter_actions':[a]},'怎么改',s)==[]

def test_adjust_requires_actual_behavior_evidence():
    s=setup();a=action('turn','adjust')
    assert accepted_parameter_actions({'parameter_actions':[a]},'查故障',s)==[]
    a['evidence_refs'].append('/reported_error/message')
    assert accepted_parameter_actions({'parameter_actions':[a]},'查故障',s)

def test_all_real_panel_fields_have_descriptions():
    import sys,re
    from pathlib import Path
    root=Path('/home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/nav2_permanent_panel');sys.path.insert(0,str(root))
    import nav2_parameter_store as store
    source=(root/'Nav2PermanentPanel.js').read_text()
    catalog={m[0]:m[1] for m in re.findall(r'^\s*\[["\x27]([^"\x27]+)["\x27],\s*["\x27]([^"\x27]+)["\x27]',source,re.M)}
    s={'parameter_catalog':catalog,'saved_algorithms':store.selected_algorithms()}
    details=build_parameter_details(source,s,store.SPECS,store.ALGORITHMS)
    assert len(details)>70
    assert all(entry['description'] for entry in details.values())
