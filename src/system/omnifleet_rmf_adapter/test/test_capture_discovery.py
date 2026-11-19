import ast
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPTS = ('capture_clouds.py', 'capture_keyframe_maps.py')


def capture_settings(tmp_path, monkeypatch):
    config = tmp_path/'framework.json'
    config.write_text(json.dumps({'robots': {'robot_104': {
        'enabled': True, 'domain_id': 104, 'rmw': 'rmw_fastrtps_cpp',
        'observed_namespace': '', 'fastdds_config': 'old-static.json5'}}}))
    monkeypatch.setenv('OMNIFLEET_CONFIG', str(config))
    monkeypatch.setenv('OMNIFLEET_DATA', str(tmp_path))
    runtime = tmp_path/'run/discovery/robot_104.json'
    return config, runtime


@pytest.mark.parametrize('script', SCRIPTS)
@pytest.mark.parametrize('profile', [None, {}], ids=['not-discovered', 'missing-session'])
def test_missing_discovery_exits_with_specific_message_before_ros(tmp_path, monkeypatch, script, profile):
    _, runtime = capture_settings(tmp_path, monkeypatch)
    if profile is not None:
        runtime.parent.mkdir(parents=True)
        runtime.write_text(json.dumps(profile))
    source = Path(__file__).resolve().parents[1]/'scripts'/script
    result = subprocess.run([sys.executable, str(source), 'robot_104'],
                            capture_output=True, text=True, timeout=5)
    assert result.returncode != 0
    expected = '车辆未发现' if profile is None else '发现配置缺少fastdds_config'
    assert 'robot_104' in result.stderr and expected in result.stderr
    assert 'Traceback' not in result.stderr and 'KeyError' not in result.stderr


@pytest.mark.parametrize('script', SCRIPTS)
def test_capture_uses_discovered_domain_and_session_before_ros(tmp_path, monkeypatch, script):
    _, runtime = capture_settings(tmp_path, monkeypatch)
    runtime.parent.mkdir(parents=True)
    session = runtime.with_suffix('.fastdds.xml')
    session.write_text('{}')
    runtime.write_text(json.dumps({'domain_id': 111, 'rmw': 'rmw_fastrtps_cpp',
                                   'fastdds_config': str(session), 'observed_namespace': ''}))
    source = Path(__file__).resolve().parents[1]/'scripts'/script
    tree = ast.parse(source.read_text())
    branch = next(n for n in tree.body if isinstance(n, ast.If))
    index = next(i for i, n in enumerate(branch.orelse)
                 if isinstance(n, ast.Import) and any(a.name == 'rclpy' for a in n.names))
    branch.orelse = branch.orelse[:index]
    monkeypatch.setattr(sys, 'argv', [str(source), 'robot_104'])
    for key in ('ROS_DOMAIN_ID', 'RMW_IMPLEMENTATION', 'ROS_LOCALHOST_ONLY', 'FASTRTPS_DEFAULT_PROFILES_FILE'):
        monkeypatch.setenv(key, '')
    exec(compile(tree, str(source), 'exec'), {'__file__': str(source)})
    assert os.environ['ROS_DOMAIN_ID'] == '111'
    assert os.environ['RMW_IMPLEMENTATION'] == 'rmw_fastrtps_cpp'
    assert os.environ['FASTRTPS_DEFAULT_PROFILES_FILE'] == str(session)
