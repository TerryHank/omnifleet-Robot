from pathlib import Path
import pytest
import yaml
from nav2_parameter_store import CONTROL, SPECS, save_changes, saved_values

SOURCE = Path('/home/iecme/omnifleet_ws/src/planning/omnifleet_planner/config/nav2_t2.yaml')

def config(tmp_path):
    target = tmp_path / 'nav.yaml'
    target.write_bytes(SOURCE.read_bytes())
    return target

def test_minimums_preserve_other_configuration(tmp_path):
    target = config(tmp_path)
    before = yaml.safe_load(target.read_text())
    receipt = save_changes({'dwb_min_speed_xy': .15, 'dwb_min_speed_theta': .4, 'dwb_min_vel_x': -.15}, target, tmp_path/'backups')
    expected = before['controller_server']['ros__parameters']['FollowPath']
    expected.update(min_speed_xy=.15, min_speed_theta=.4, min_vel_x=-.15)
    assert yaml.safe_load(target.read_text()) == before
    assert saved_values(target)['dwb_min_speed_xy'] == {'min_speed_xy': .15}
    assert Path(receipt['backup']).exists()
    for key, leaf in [('dwb_min_speed_xy','min_speed_xy'),('dwb_min_speed_theta','min_speed_theta'),('dwb_min_vel_x','min_vel_x')]:
        assert SPECS[key][:4] == (CONTROL, (leaf,), '/controller_server', 'FollowPath.')

@pytest.mark.parametrize('changes', [
    {'dwb_min_speed_xy': -.1}, {'dwb_min_speed_theta': float('nan')},
    {'dwb_min_vel_x': -2.}, {'dwb_min_speed_xy': 1.4},
    {'dwb_min_speed_theta': 2.9}, {'dwb_min_vel_x': 1.4},
])
def test_invalid_minimums_do_not_write(tmp_path, changes):
    target=config(tmp_path);before=target.read_bytes()
    with pytest.raises(ValueError):save_changes(changes,target,tmp_path/'backups')
    assert target.read_bytes()==before
    assert not (tmp_path/'backups').exists()

def test_lowering_maximum_checks_existing_minimum(tmp_path):
    target=config(tmp_path)
    save_changes({'dwb_min_speed_xy': .3},target,tmp_path/'backups')
    before=target.read_bytes()
    with pytest.raises(ValueError):save_changes({'linear_speed': .2},target,tmp_path/'backups')
    assert target.read_bytes()==before

def test_joint_submission_can_lower_both_limits(tmp_path):
    target=config(tmp_path)
    save_changes({'linear_speed': .2,'dwb_min_speed_xy': .15},target,tmp_path/'backups')
    assert saved_values(target)['linear_speed']=={'max_vel_x':.2,'max_speed_xy':.2}
