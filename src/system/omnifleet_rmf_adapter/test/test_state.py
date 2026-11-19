from omnifleet_rmf_adapter.state import summarize


def sample():
    return {'sample_monotonic': 100.0, 'samples': {
        key: {'age_seconds': 0.2, 'value': {}} for key in ('pose', 'navigation', 'control')
    }}


def test_live_read_only_robot_is_online_but_not_dispatchable():
    result = summarize(sample(), 101.0, 3.0)
    assert result['online']
    assert result['transport_connected']
    assert not result['dispatch_enabled']
    assert not result['rmf_registered']


def test_ipc_loss_expires_cached_state():
    result = summarize(sample(), 104.0, 3.0)
    assert not result['online']
    assert not result['transport_connected']
    assert not any(result['fresh'].values())


def test_topic_loss_and_missing_control_do_not_report_online():
    payload = sample()
    payload['samples']['pose']['age_seconds'] = 10.0
    assert not summarize(payload, 101.0, 3.0)['online']
    del payload['samples']['control']
    assert not summarize(payload, 101.0, 3.0)['online']


def test_previous_boot_snapshot_is_not_live():
    assert not summarize(sample(), 10.0, 3.0)['online']
