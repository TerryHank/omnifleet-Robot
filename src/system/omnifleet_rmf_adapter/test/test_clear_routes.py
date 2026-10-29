from concurrent.futures import Future
import pytest
from test_missions import fleet,save
from omnifleet_rmf_adapter.missions import Missions


def clear(f,robot=None):
    return f.owner.command({'op':'route_clear' if robot else 'routes_clear','robot_id':robot,'id':'clear'},f.states)


def test_clear_selected_route_keeps_other_vehicle_points_and_invalidates_precheck(fleet):
    f=fleet;save(f,'a',[[1.,0.,0.]]);save(f,'b',[[2.,4.,0.]])
    future=Future();f.owner.prechecks['old']={'robot_id':'a','phase':'PRECHECKING','future':future}
    before=f.owner.saved['routes']['a']['revision'];result=clear(f,'a')
    assert result['phase']=='cleared' and result['robots']==['a']
    assert f.owner.saved['routes']['a']['points']==[] and f.owner.saved['routes']['a']['revision']==before+1
    assert f.owner.saved['routes']['b']['points'] and future.cancelled() and f.owner.prechecks['old']['phase']=='INVALIDATED'
    assert f.owner.preview_paths['a']==[] and not f.sent


def test_clear_executing_queue_stops_and_never_sends_remaining_targets(fleet):
    f=fleet;save(f,'a',[[1.,0.,0.],[2.,0.,0.]])
    f.owner.command({'op':'route_start','id':'run','robot_id':'a'},f.states);f.tick(5)
    assert f.owner.jobs['a']['phase']=='EXECUTING';clear(f,'a');f.tick(10)
    assert f.owner.jobs['a']['phase']=='STOPPED'
    assert len([s for s in f.sent if s[0]=='navigate'])==1 and f.owner.saved['routes']['a']['points']==[]
    f.owner.command({'op':'route_add','robot_id':'a','point':{'pose':[3.,0.,0.]},'id':'new'},f.states);f.owner.command({'op':'route_start','robot_id':'a','id':'execute'},f.states);f.tick(5)
    assert f.owner.jobs['a']['index']==0 and [s[3]['pose'] for s in f.sent if s[0]=='navigate'][-1]==[3.,0.,0.]


def test_clear_all_works_offline_and_persists_across_restart(fleet):
    f=fleet;save(f,'a',[[1.,0.,0.]]);save(f,'b',[[2.,4.,0.]])
    for state in f.states.values():state['online']=False
    clear(f)
    assert all(not r['points'] for r in f.owner.saved['routes'].values())
    restored=Missions(f.config,f.maps,f.root,lambda *a,**k:None)
    assert restored.saved==f.owner.saved and not restored.jobs
    restored.close()


def test_clear_leader_cancels_active_follow_but_keeps_follower_saved_route(fleet):
    f=fleet;save(f,'a',[[1.,0.,0.]]);save(f,'b',[[2.,4.,0.]])
    f.owner.follow.update(active=True,leader='a',order=['a','b'])
    clear(f,'a')
    assert not f.owner.follow['active'] and f.owner.saved['routes']['b']['points']


def test_clear_blocks_old_drag_revision_and_completion_restart(fleet):
    f=fleet;f.owner.command({'op':'route_add','robot_id':'a','point':{'pose':[1.,0.,0.]},'id':'add'},f.states)
    f.owner.command({'op':'route_start','robot_id':'a','id':'execute'},f.states);f.tick(5);f.finish('a');f.tick()
    f.owner.command({'op':'route_add','robot_id':'a','point':{'pose':[2.,0.,0.]},'id':'append'},f.states)
    assert not f.owner.jobs['a'].get('restart_after_completion')
    clear(f,'a');f.tick(10)
    assert f.owner.jobs['a']['phase']=='STOPPED' and len([s for s in f.sent if s[0]=='navigate'])==1


def test_clear_unassigned_vehicle_is_rejected_without_mutation(fleet):
    f=fleet
    with pytest.raises(ValueError):clear(f,'retired')
    assert not f.owner.saved['routes'] and not f.sent


def test_new_point_after_offline_clear_binds_current_session_without_extra_save(fleet):
    f=fleet;f.states['a']['online']=False
    f.states['a']['samples']['navigation']['value']['localization_epoch']=None
    clear(f,'a')
    f.states['a']['online']=True;f.states['a']['samples']['navigation']['value']['localization_epoch']='new-epoch'
    f.owner.command({'op':'route_add','robot_id':'a','point':{'pose':[1.,0.,0.]},'id':'new'},f.states)
    assert f.owner.saved['routes']['a']['epoch']=='new-epoch' and not f.owner.jobs
