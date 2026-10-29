from test_missions import fleet


def executing(fleet):
    fleet.owner.enqueue('a', [{'pose': [1., 0., 0.]}], 'single', 'a-epoch')
    fleet.tick(5)
    job = fleet.owner.jobs['a']
    assert job['phase'] == 'EXECUTING'
    return job


def test_onboard_failure_is_not_overwritten_by_later_lease_withdrawal(fleet):
    job = executing(fleet)
    client = fleet.states['a']['samples']['fleet_client']['value']
    client['history'][job['request']] = {'phase': 'failed', 'message': 'follow target update timed out'}
    client['armed'] = False
    fleet.states['a']['samples']['navigation']['value']['fleet_lease_fresh'] = False
    fleet.tick()
    assert job['message'] == 'follow target update timed out'
    assert job['phase'] in ('STOPPING', 'FAILED')


def test_real_lease_loss_without_onboard_failure_keeps_lease_error(fleet):
    job = executing(fleet)
    fleet.states['a']['samples']['fleet_client']['value']['armed'] = False
    fleet.states['a']['samples']['navigation']['value']['fleet_lease_fresh'] = False
    fleet.tick()
    assert job['message'] == '车端租约失效'
