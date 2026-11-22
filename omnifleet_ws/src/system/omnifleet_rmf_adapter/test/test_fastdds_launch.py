import json
from pathlib import Path
import pytest
from omnifleet_rmf_adapter import launch


@pytest.mark.parametrize('role,expected', [('central', 'rmw_fastrtps_cpp'), ('robot_test', 'rmw_fastrtps_cpp')])
def test_central_fastdds_and_discovered_robot_keep_separate_environments(tmp_path, monkeypatch, role, expected):
    config = tmp_path / 'framework.json'
    config.write_text(json.dumps({
        'central': {'domain_id': 42, 'rmw': 'rmw_fastrtps_cpp', 'fastdds_config': 'fastdds-central.xml'},
        'robots': {'robot_test': {'enabled': True, 'domain_id': 101, 'rmw': 'rmw_fastrtps_cpp', 'fastdds_config': 'robot.xml'}}
    }))
    runtime = tmp_path / 'runtime.json'
    runtime.write_text(json.dumps({'robot_id': 'robot_test', 'domain_id': 101}))
    monkeypatch.setenv('OMNIFLEET_DISCOVERY_PROFILE', str(runtime))
    monkeypatch.setenv('FASTRTPS_DEFAULT_PROFILES_FILE', '/inherited/wrong.xml')
    monkeypatch.setenv('RMW_FASTRTPS_USE_QOS_FROM_XML', '1')
    monkeypatch.setenv('ZENOH_SESSION_CONFIG_URI', '/inherited/wrong.json5')
    monkeypatch.setattr('sys.argv', ['launch', role, '--config', str(config), '--data', str(tmp_path / 'data')])
    captured = {}
    def execute(program, args, env):
        captured.update(env)
        raise SystemExit(0)
    monkeypatch.setattr(launch.os, 'execvpe', execute)
    with pytest.raises(SystemExit):
        launch.main()
    assert captured['RMW_IMPLEMENTATION'] == expected
    if role == 'central':
        assert captured['FASTRTPS_DEFAULT_PROFILES_FILE'] == str(tmp_path / 'fastdds-central.xml')
        assert captured['RMW_FASTRTPS_USE_QOS_FROM_XML'] == '1'
        assert 'ZENOH_SESSION_CONFIG_URI' not in captured
        assert captured['ROS_LOCALHOST_ONLY'] == '1'
    else:
        assert 'ZENOH_SESSION_CONFIG_URI' not in captured
        assert captured['FASTRTPS_DEFAULT_PROFILES_FILE'] == str(tmp_path / 'robot.xml')
        assert captured['RMW_FASTRTPS_USE_QOS_FROM_XML'] == '1'
        assert captured['OMNIFLEET_ROBOT_ID'] == 'robot_test'
        assert captured['ROS_DOMAIN_ID'] == '101'
