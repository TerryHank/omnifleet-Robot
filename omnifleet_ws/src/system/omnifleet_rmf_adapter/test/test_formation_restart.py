import pytest
from test_missions import fleet


@pytest.mark.parametrize('terminal', ['STOPPED', 'FAILED', 'INVALIDATED', 'COMPLETED'])
def test_explicit_restart_uses_a_new_follower_job(fleet, terminal):
    f=fleet.owner.formation
    f.capture(['a','b'],fleet.states)
    fleet.owner.jobs['b']={'id':'old','source':'formation','phase':terminal,'message':'previous run failed'}
    f.start(['a','b'],fleet.states)
    assert f.active
    assert f.phase=='PLANNING'
    fleet.tick(7)
    assert fleet.owner.jobs['b']['id']!='old'
    assert f.phase=='HOLDING'


def test_unconfirmed_stop_remains_ineligible_for_restart(fleet):
    f=fleet.owner.formation;f.capture(['a','b'],fleet.states)
    fleet.owner.jobs['b']={'id':'old','source':'formation','phase':'CANCEL_UNCONFIRMED'}
    with pytest.raises(ValueError): f.start(['a','b'],fleet.states)
