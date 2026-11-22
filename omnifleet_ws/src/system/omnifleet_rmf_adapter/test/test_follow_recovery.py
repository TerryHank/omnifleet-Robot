from test_missions import fleet

def test_genuine_follow_failure_is_failed_not_waiting_for_unimplemented_retry(fleet):
    fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':.4},fleet.states)
    fleet.tick(5)
    fleet.owner.jobs['b'].update(phase='FAILED',message='controller failed')
    fleet.tick()
    assert not fleet.owner.follow['active'] and fleet.owner.follow['phase']=='FAILED'
    assert 'controller failed' in fleet.owner.follow['message']

def test_waiting_for_onboard_replanning_has_real_active_task(fleet):
    fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':.4},fleet.states)
    fleet.tick(5)
    fleet.states['b']['samples']['navigation']['value']['follow_stream']={'blocked':True}
    fleet.tick()
    assert fleet.owner.follow['active'] and fleet.owner.follow['phase']=='BLOCKED'
    assert fleet.owner.jobs['b']['phase']=='EXECUTING'
