import pytest
from test_missions import fleet

@pytest.mark.parametrize('distance',[0.,.01,.3,1.39,1.4,5.01,10.,1000.])
def test_operator_distance_is_preserved_without_fixed_range(fleet,distance):
    result=fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':distance},fleet.states)
    assert result['phase']=='accepted'
    assert fleet.owner.follow['distance']==distance
    assert not any(p[0] in ('arm','navigate') for p in fleet.sent)

@pytest.mark.parametrize('distance',[-.01,float('nan'),float('inf'),True,None,'0.3'])
def test_invalid_distance_is_rejected_before_start(fleet,distance):
    with pytest.raises(ValueError,match='非负数'):
        fleet.owner.command({'op':'follow_start','order':['a','b'],'distance':distance},fleet.states)
    assert not fleet.owner.follow['active'] and not fleet.sent
