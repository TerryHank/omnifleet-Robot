import copy,json
import pytest
from test_missions import fleet,save

def test_first_new_point_archives_old_session_and_later_points_append(fleet):
    f=fleet;save(f,'a',[[99.,88.,0.]])
    f.owner.saved['routes']['a']['epoch']='old-session'
    old=copy.deepcopy(f.owner.saved['routes']['a'])
    result=f.owner.command({'op':'route_add','robot_id':'a','point':[1.,0.,0.]},f.states)
    route=f.owner.saved['routes']['a']
    assert route['epoch']=='a-epoch' and [p['pose'] for p in route['points']]==[[1.,0.,0.]]
    assert not f.owner.jobs and not f.sent
    archives=list((f.owner.file.parent/'route_archive').glob('*.json'))
    assert len(archives)==1 and json.loads(archives[0].read_text())['route']==old
    assert '已备份' in result['message']
    f.owner.command({'op':'route_add','robot_id':'a','point':[2.,0.,0.]},f.states)
    assert [p['pose'] for p in f.owner.saved['routes']['a']['points']]==[[1.,0.,0.],[2.,0.,0.]]
    assert len(list((f.owner.file.parent/'route_archive').glob('*.json')))==1

def test_invalid_new_point_keeps_the_old_session_unchanged(fleet):
    f=fleet;save(f,'a',[[99.,88.,0.]])
    f.owner.saved['routes']['a']['epoch']='old-session';old=copy.deepcopy(f.owner.saved)
    with pytest.raises(ValueError):f.owner.command({'op':'route_add','robot_id':'a','point':[float('nan'),0.,0.]},f.states)
    assert f.owner.saved==old and not (f.owner.file.parent/'route_archive').exists()

def test_finished_old_job_does_not_replay_archived_points(fleet):
    f=fleet;save(f,'a',[[99.,88.,0.]])
    f.owner.saved['routes']['a']['epoch']='old-session'
    f.owner.jobs['a']={'phase':'COMPLETED','source':'route','index':10}
    f.owner.command({'op':'route_add','robot_id':'a','point':[1.,0.,0.]},f.states)
    assert f.owner.jobs['a']['index']==10
    f.owner.command({'op':'route_start','robot_id':'a','id':'execute'},f.states)
    assert f.owner.jobs['a']['index']==0 and len(f.owner.jobs['a']['points'])==1
