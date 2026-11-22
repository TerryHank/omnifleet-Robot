import json
from types import SimpleNamespace as NS

import pytest

from omnifleet_rmf_adapter.robot_names import RobotNames


def config():
    return {'central': {'assignments': {r: {'robot_name': r, 'namespace': '/' + r} for r in ('robot_104', 'robot_113')}}}


def test_names_persist_without_changing_robot_identity(tmp_path):
    settings = config()
    names = RobotNames(settings, tmp_path)
    result = names.rename('robot_113', ' 一号车 ')
    assert result['display_name'] == '一号车'
    assert settings['central']['assignments']['robot_113'] == {
        'robot_name': 'robot_113', 'namespace': '/robot_113', 'display_name': '一号车'}
    restored = config()
    RobotNames(restored, tmp_path)
    assert restored['central']['assignments']['robot_113']['display_name'] == '一号车'
    names.rename('robot_113', '')
    assert settings['central']['assignments']['robot_113']['display_name'] == '车辆 113'
    assert json.loads((tmp_path / 'robot_names.json').read_text())['names'] == {}


@pytest.mark.parametrize('robot,name', [('missing', '车'), ('robot_113', None), ('robot_113', 'x' * 41), ('robot_113', '一\n号车')])
def test_invalid_names_leave_existing_name_unchanged(tmp_path, robot, name):
    settings = config()
    names = RobotNames(settings, tmp_path)
    names.rename('robot_113', '一号车')
    with pytest.raises(ValueError):
        names.rename(robot, name)
    assert names.snapshot() == {'robot_113': '一号车'}


def test_failed_write_does_not_report_or_apply_success(tmp_path, monkeypatch):
    from pathlib import Path
    settings = config()
    names = RobotNames(settings, tmp_path)
    names.rename('robot_113', '一号车')
    def fail(*args, **kwargs):
        raise OSError('disk full')
    monkeypatch.setattr(Path, 'replace', fail)
    with pytest.raises(RuntimeError, match='Could not save'):
        names.rename('robot_113', '新名字')
    assert settings['central']['assignments']['robot_113']['display_name'] == '一号车'


def test_published_map_label_uses_real_assigned_id(tmp_path):
    from builtin_interfaces.msg import Time
    from omnifleet_rmf_adapter.map_hub import MapHub
    settings = config()
    settings['central']['reference_robot'] = 'robot_113'
    settings['robots'] = {r: {'enabled': True} for r in settings['central']['assignments']}
    names = RobotNames(settings, tmp_path)
    published = {}
    node = NS(create_publisher=lambda typ, topic, qos: NS(publish=lambda message: published.update({topic: message})),
              get_clock=lambda: NS(now=lambda: NS(to_msg=lambda: Time())))
    hub = MapHub(node, settings, tmp_path)
    states = {'robot_113': {'online': True, 'fresh': {}, 'samples': {'pose': {'value': {'x': 1., 'y': 2., 'yaw': 0.}}}}}
    names.rename('robot_113', '一号车')
    hub.tick(states)
    assert next(m for m in published['/fleet/robots'].markers if m.action == m.ADD).text == 'robot_113'
    settings['central']['assignments']['robot_113']['robot_name'] = 'car_1'
    hub.last_map_publish = 0.
    hub.tick(states)
    assert next(m for m in published['/fleet/robots'].markers if m.action == m.ADD).text == 'car_1'
