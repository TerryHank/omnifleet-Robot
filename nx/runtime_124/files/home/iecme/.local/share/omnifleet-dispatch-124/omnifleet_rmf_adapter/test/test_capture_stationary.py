import ast
import json
import math
from pathlib import Path
import time

import pytest

from omnifleet_rmf_adapter.registration import run_stage
from omnifleet_rmf_adapter.state import connection_states


def capture_check(tmp_path, control, navigation=None, script='capture_clouds.py'):
    source=Path(__file__).resolve().parents[1]/'scripts'/script
    tree=ast.parse(source.read_text())
    function=next(node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef) and node.name=='stationary')
    report={'wall_time_seconds':time.time(),'robots':{'renamed_car':{
        'connection_id':'link_a','online':True,'fresh':dict.fromkeys(('map','pose','navigation','control'),True),
        'samples':{'control':{'value':control},'navigation':{'value':navigation or {}}}}}}
    (tmp_path/'connection_status.json').write_text(json.dumps(report))
    namespace={'data':tmp_path,'robot':'link_a','connection_states':connection_states,'time':time,'math':math,'json':json}
    exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
    return namespace['stationary']


@pytest.mark.parametrize('manual',[False,True])
@pytest.mark.parametrize('script',['capture_clouds.py','capture_keyframe_maps.py'])
def test_capture_accepts_stopped_wheels_in_both_modes(tmp_path,manual,script):
    check=capture_check(tmp_path,{'manual_active':manual,'nav_active':False,'stopped_seconds':10.,'velocity':[0.,0.]},script=script)
    assert check()['connection_id']=='link_a'


@pytest.mark.parametrize('velocity',[[.02,0.],[0.,.02],[],[0.],[float('nan'),0.]])
@pytest.mark.parametrize('script',['capture_clouds.py','capture_keyframe_maps.py'])
def test_capture_rejects_moving_or_invalid_wheels_in_manual_mode(tmp_path,velocity,script):
    check=capture_check(tmp_path,{'manual_active':True,'nav_active':False,'stopped_seconds':10.,'velocity':velocity},script=script)
    with pytest.raises(AssertionError,match='wheels are moving or feedback is invalid'):check()


def test_capture_rejects_active_navigation_even_with_zero_feedback(tmp_path):
    check=capture_check(tmp_path,{'manual_active':True,'stopped_seconds':10.,'velocity':[0.,0.]},{'navigation_active':True})
    with pytest.raises(AssertionError,match='navigation is active'):check()


def test_stage_error_keeps_original_cause_instead_of_generic_exit_code(tmp_path,capsys):
    script=tmp_path/'capture_example.py'
    script.write_text("raise RuntimeError('link_a: wheels are moving')")
    with pytest.raises(RuntimeError,match='capture_example.py: RuntimeError: link_a: wheels are moving'):
        run_stage(script)
    assert 'link_a: wheels are moving' in capsys.readouterr().out
