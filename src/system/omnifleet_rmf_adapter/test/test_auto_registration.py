from copy import deepcopy

import pytest

from omnifleet_rmf_adapter.registration import AutoRegistration


def states():
    return {robot: {
        'online': True,
        'fresh': dict.fromkeys(('map', 'pose', 'navigation', 'control'), True),
        'samples': {
            'navigation': {'value': {'local_ready': True, 'localization_epoch': robot+'-session', 'navigation_active': False}},
            'control': {'value': {'nav_active': False, 'manual_active': False, 'stopped_seconds': 10., 'velocity': [0., 0.], 'velocity_age':0.}},
        },
    } for robot in ('robot_104', 'robot_113')}


def test_stationary_boot_retries_failed_session_and_new_session_revalidates():
    policy = AutoRegistration()
    current = states()
    assert not policy.due(current, current, False, False, 0.)
    assert policy.due(current, current, False, False, 5.)
    assert not policy.due(current, current, False, False, 34.)
    assert not policy.due(current, current, False, False, 304.)
    assert policy.due(current, current, False, False, 305.)
    assert not policy.due(current, current, True, False, 500.)
    current['robot_113']['samples']['navigation']['value']['localization_epoch'] = 'rebooted'
    assert not policy.due(current, current, False, False, 501.)
    assert policy.due(current, current, False, False, 506.)


@pytest.mark.parametrize('fault', ('offline', 'map_stale', 'control_stale', 'navigation_not_ready', 'no_epoch', 'navigation_active', 'not_stopped', 'moving', 'nan'))
def test_waits_for_both_fresh_ready_stationary_vehicles(fault):
    current = states()
    original = deepcopy(current)
    bad = current['robot_104']
    nav = bad['samples']['navigation']['value']
    control = bad['samples']['control']['value']
    if fault == 'offline': bad['online'] = False
    elif fault == 'map_stale': bad['fresh']['map'] = False
    elif fault == 'control_stale': bad['fresh']['control'] = False
    elif fault == 'navigation_not_ready': nav['local_ready'] = False
    elif fault == 'no_epoch': nav['localization_epoch'] = ''
    elif fault == 'navigation_active': nav['navigation_active'] = True
    elif fault == 'not_stopped': control['stopped_seconds'] = 1.
    elif fault == 'moving': control['velocity'] = [.02, 0.]
    elif fault == 'nan': control['velocity'] = [float('nan'), 0.]
    policy = AutoRegistration()
    assert not policy.due(original, original, False, False, 0.)
    assert not policy.due(current, current, False, False, 6.)
    assert not policy.due(original, original, False, False, 7.)
    assert policy.due(original, original, False, False, 12.)


def test_no_duplicate_running_job_or_revalidation_of_valid_alignment():
    policy = AutoRegistration()
    current = states()
    assert not policy.due(current, current, True, False, 0.)
    assert not policy.due(current, current, True, False, 6.)
    assert not policy.due(current, current, False, True, 7.)
    assert policy.due(current, current, False, False, 8.)
    assert policy.due(current, current, False, False, 1000.)


def test_does_not_start_with_only_one_vehicle():
    policy = AutoRegistration()
    current = states()
    current.pop('robot_104')
    assert not policy.due(current, current, False, False, 0.)
    assert not policy.due(current, current, False, False, 10.)


def test_transient_empty_members_during_capture_retains_retry_interval():
    policy = AutoRegistration()
    current = states()
    assert not policy.due(current, current, False, False, 0.)
    assert policy.due(current, current, False, False, 5.)
    assert not policy.due(current, [], False, True, 10.)
    assert not policy.due(current, current, False, True, 20.)
    assert not policy.due(current, current, False, False, 155.)
    assert policy.due(current, current, False, False, 305.)


def test_released_manual_mode_with_zero_wheels_allows_automatic_recovery():
    current=states()
    current['robot_113']['samples']['control']['value'].update(manual_active=True,control_mode='MANUAL')
    policy=AutoRegistration()
    assert not policy.due(current,current,False,False,0.)
    assert policy.due(current,current,False,False,5.)
    current['robot_113']['samples']['control']['value']['velocity']=[.02,0.]
    assert not policy.due(current,current,False,False,40.)
