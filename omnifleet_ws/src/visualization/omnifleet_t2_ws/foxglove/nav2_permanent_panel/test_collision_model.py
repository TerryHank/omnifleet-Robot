from pathlib import Path
import json

import pytest
import yaml

import collision_model as model


@pytest.fixture
def config(tmp_path):
    path = tmp_path / 'nav2.yaml'
    source = Path('/home/iecme/omnifleet_ws/src/planning/omnifleet_planner/config/nav2_t2.yaml')
    data = yaml.safe_load(source.read_text())
    for scope in ('local', 'global'):
        p = data[scope + '_costmap'][scope + '_costmap']['ros__parameters']
        p['footprint'] = '[[0.25,0.185],[0.25,-0.185],[-0.25,-0.185],[-0.25,0.185]]'
        p.pop('robot_radius', None)
        p['footprint_padding'] = .05
        p['inflation_layer']['inflation_radius'] = .4
    for p in model.model_paths(data):
        if p[-1] == 'consider_footprint':
            model.parent_at(data, p)[p[-1]] = True
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    return path


def save(path, mode, **overrides):
    guard = dict(navigation_active=False, state_age=.1, motion_age=3)
    guard.update(overrides)
    return model.save_mode(mode, path, path.parent / 'backups', **guard)


def test_point_model_changes_all_collision_fields_and_restores_only_them(config):
    original = yaml.safe_load(config.read_text())
    result = save(config, 'point')
    assert result['collision_model']['mode'] == 'point'
    assert result['runtime_confirmed'] is False
    assert result['applies_to'] == 'next_restart'
    point = yaml.safe_load(config.read_text())
    for scope in ('local', 'global'):
        p = point[scope + '_costmap'][scope + '_costmap']['ros__parameters']
        assert p['footprint'] == '[]' and p['robot_radius'] == .01
        assert p['footprint_padding'] == 0 and p['inflation_layer']['inflation_radius'] == .01
    for path in model.model_paths(point):
        if path[-1] == 'consider_footprint':
            assert model.parent_at(point, path)[path[-1]] is False
    point['controller_server']['ros__parameters']['FollowPathMPPI']['vx_max'] = .19
    config.write_text(yaml.safe_dump(point, sort_keys=False))
    save(config, 'body')
    original['controller_server']['ros__parameters']['FollowPathMPPI']['vx_max'] = .19
    assert yaml.safe_load(config.read_text()) == original


def test_repeated_point_does_not_overwrite_original_body(config):
    save(config, 'point')
    profile = model.profile_path(config).read_bytes()
    save(config, 'point')
    assert model.profile_path(config).read_bytes() == profile


def test_custom_changes_can_restore_the_original_body(config):
    original = yaml.safe_load(config.read_text())
    save(config, 'point'); save(config, 'body')
    data = yaml.safe_load(config.read_text())
    data['local_costmap']['local_costmap']['ros__parameters']['footprint_padding'] = .027
    config.write_text(yaml.safe_dump(data, sort_keys=False))
    assert model.state(config)['mode'] == 'custom'
    save(config, 'body')
    assert yaml.safe_load(config.read_text()) == original
    save(config, 'point'); save(config, 'body')
    assert yaml.safe_load(config.read_text()) == original


@pytest.mark.parametrize('mode', ['bad', '', None])
def test_invalid_mode_does_not_write(config, mode):
    before = config.read_bytes()
    with pytest.raises(ValueError):
        save(config, mode)
    assert config.read_bytes() == before and not model.profile_path(config).exists()


@pytest.mark.parametrize('guard', [dict(navigation_active=True), dict(navigation_active=None),
                                 dict(state_age=3), dict(motion_age=.2)])
def test_navigation_state_does_not_block_model_save(config, guard):
    save(config, 'point', **guard)
    assert model.state(config)['mode'] == 'point'


def test_missing_profile_prevents_inventing_a_body(config):
    save(config, 'point'); model.profile_path(config).unlink()
    before = config.read_bytes()
    with pytest.raises(ValueError):
        save(config, 'body')
    assert config.read_bytes() == before


def test_read_and_noop_body_leave_config_and_profile_untouched(config):
    before = config.read_bytes()
    assert model.state(config)['mode'] == 'body'
    assert not model.state(config)['restore_available']
    save(config, 'body')
    assert config.read_bytes() == before and not model.profile_path(config).exists()


def test_corrupt_profile_rejected_before_yaml_write(config):
    save(config, 'point'); before = config.read_bytes()
    model.profile_path(config).write_text(json.dumps({'version': 1, 'body': []}))
    with pytest.raises(ValueError):
        save(config, 'body')
    assert config.read_bytes() == before


def test_failed_yaml_write_preserves_original_config(config, monkeypatch):
    before = config.read_bytes(); original_write = model.atomic_write
    def fail(path, data):
        if path == config:
            raise OSError('read only')
        original_write(path, data)
    monkeypatch.setattr(model, 'atomic_write', fail)
    with pytest.raises(OSError):
        save(config, 'point')
    assert config.read_bytes() == before
