import json
import pytest
import mola_sampling as module

def runtime(tmp_path):
    path=tmp_path/'runtime.json'
    path.write_text(json.dumps({'MOLA_DECIMATED_POINTS_MAP':'8000','MOLA_DECIMATED_POINTS_ICP':'2000','other':'preserve'}))
    return path

def test_save_roundtrip_preserves_other_settings(tmp_path):
    path=runtime(tmp_path);old=path.read_bytes()
    result=module.save({'mola_icp_points':2500},tmp_path/'backup',path)
    assert json.loads(path.read_text())=={'MOLA_DECIMATED_POINTS_MAP':'8000','MOLA_DECIMATED_POINTS_ICP':'2500','other':'preserve'}
    assert module.values(path)['mola_icp_points']['MOLA_DECIMATED_POINTS_ICP']==2500
    assert result['restart_required'] and not result['runtime_confirmed']
    from pathlib import Path
    assert Path(result['backup']).read_bytes()==old

@pytest.mark.parametrize('changes',[{'mola_icp_points':True},{'mola_icp_points':2.5},{'mola_map_points':0},{'mola_map_points':-1},{'mola_map_points':1000001},{'unknown':2000},{}])
def test_invalid_saves_leave_file_unchanged(tmp_path,changes):
    path=runtime(tmp_path);old=path.read_bytes()
    with pytest.raises(ValueError):module.save(changes,tmp_path/'backup',path)
    assert path.read_bytes()==old

def test_noop_save_keeps_exact_bytes(tmp_path):
    path=runtime(tmp_path);old=path.read_bytes()
    result=module.save({'mola_map_points':8000,'mola_icp_points':2000},tmp_path/'backup',path)
    assert path.read_bytes()==old and result['backup'] is None

def test_replace_failure_keeps_original(tmp_path,monkeypatch):
    path=runtime(tmp_path);old=path.read_bytes()
    def fail(*args):raise OSError('test failure')
    monkeypatch.setattr(module.os,'replace',fail)
    with pytest.raises(OSError):module.save({'mola_map_points':8100},tmp_path/'backup',path)
    assert path.read_bytes()==old and not list(tmp_path.glob('.mola-sampling-*'))
