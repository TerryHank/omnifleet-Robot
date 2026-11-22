import pytest
from omnifleet_rmf_adapter.cloud_quality import registration_valid

@pytest.mark.parametrize('forward,reverse,rms,margin,accepted',[
    (.56,.93,.069,.17,False),
    (.9814,.9619,.0506,.677,True),
    (.6,.6,.089,.081,True),
    (.99,.99,.09,.9,False),
    (.99,.99,.01,.08,False),
    (.99,float('nan'),.01,.9,False),
])
def test_same_overlap_rms_and_ambiguity_gates_remain_enforced(forward,reverse,rms,margin,accepted):
    assert bool(registration_valid({'fitness':forward,'reverse_fitness':reverse,'inlier_rmse_m':rms},margin)) is accepted
