from pathlib import Path
import yaml
import pytest
from nav2_parameter_store import SPECS, edited_yaml, save_changes, saved_values

SOURCE = Path('/home/iecme/omnifleet_ws/src/planning/omnifleet_planner/config/nav2_t2.yaml')

def test_linked_speed_is_atomic_and_keeps_yaml_comments(tmp_path):
    path = tmp_path / 'nav.yaml'
    original = SOURCE.read_text()
    path.write_text(original)
    install = tmp_path / 'installed.yaml'
    install.symlink_to(path)
    receipt = save_changes({'linear_speed': .25}, install, tmp_path / 'backups')
    assert saved_values(install)['linear_speed'] == {'max_vel_x': .25, 'max_speed_xy': .25}
    assert install.is_symlink()
    assert Path(receipt['backup']).read_text() == original
    before, after = yaml.safe_load(original), yaml.safe_load(path.read_text())
    before['controller_server']['ros__parameters']['FollowPath'].update(max_vel_x=.25, max_speed_xy=.25)
    assert before == after

@pytest.mark.parametrize('key', list(SPECS))
def test_double_type_roundtrip_for_every_control(key):
    text = edited_yaml(SOURCE.read_text(), {key: 1.})
    data = yaml.safe_load(text)
    for leaf in SPECS[key][1]:
        node = data
        for segment in SPECS[key][0] + (leaf,): node = node[segment]
        assert type(node) is float and node == 1.

@pytest.mark.parametrize('changes', [{'bad': .2}, {'linear_speed': float('nan')}, {'global_radius': -1}, {'linear_speed': True}, {'angular_speed': 99}])
def test_invalid_write_leaves_file_unchanged(tmp_path, changes):
    path = tmp_path / 'nav.yaml'; path.write_bytes(SOURCE.read_bytes()); before = path.read_bytes()
    with pytest.raises(ValueError): save_changes(changes, path, tmp_path / 'backups')
    assert path.read_bytes() == before

def test_missing_yaml_key_refuses_write(tmp_path):
    with pytest.raises(ValueError): edited_yaml('controller_server: {}', {'linear_speed': .2})

def test_shared_panel_submission_updates_both_costmaps_atomically(tmp_path):
    path = tmp_path / 'nav.yaml'
    path.write_bytes(SOURCE.read_bytes())
    receipt = save_changes({
        'local_radius': 1.0,
        'global_radius': 1.0,
        'local_scaling': 2.0,
        'global_scaling': 2.0,
        'local_padding': 0.05,
        'global_padding': 0.05,
    }, path, tmp_path / 'backups')
    saved = receipt['saved']
    assert saved['local_radius'] == {'inflation_radius': 1.0}
    assert saved['global_radius'] == {'inflation_radius': 1.0}
    assert saved['local_scaling'] == {'cost_scaling_factor': 2.0}
    assert saved['global_scaling'] == {'cost_scaling_factor': 2.0}
    assert saved['local_padding'] == {'footprint_padding': 0.05}
    assert saved['global_padding'] == {'footprint_padding': 0.05}
    assert Path(receipt['backup']).exists()
