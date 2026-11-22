from unittest.mock import Mock
import pytest
from test_missions import fleet


def dispatcher(fleet):
    bridge=Mock();bridge.api.get_subscription_count.return_value=1
    bridge.submit.return_value={'phase':'queued'};fleet.owner.rmf_dispatch=bridge
    return bridge


def test_explicit_single_goal_does_not_bid_and_targets_only_selected_robot(fleet):
    bridge=dispatcher(fleet)
    result=fleet.owner.command({'op':'single_goal','id':'manual-point','robot_id':'b','point':{'pose':[1.,4.,0.]}},fleet.states)
    assert result['phase']=='accepted'
    bridge.submit.assert_not_called()
    fleet.tick(6)
    goals=[p for p in fleet.sent if p[0]=='navigate']
    assert len(goals)==1 and goals[0][2]=='b'


def test_unassigned_single_goal_keeps_automatic_dispatch(fleet):
    bridge=dispatcher(fleet)
    result=fleet.owner.command({'op':'single_goal','id':'automatic','point':{'pose':[1.,0.,0.]}},fleet.states)
    assert result['phase']=='queued'
    bridge.submit.assert_called_once()


def test_explicit_single_goal_still_obeys_traffic_admission(fleet):
    bridge=dispatcher(fleet)
    traffic=Mock();traffic.admit.return_value=(False,'traffic wait');fleet.owner.rmf_traffic=traffic
    fleet.owner.command({'op':'single_goal','id':'manual-point','robot_id':'a','point':{'pose':[1.,0.,0.]}},fleet.states)
    fleet.tick(6)
    bridge.submit.assert_not_called();traffic.admit.assert_called()
    assert not any(p[0]=='navigate' for p in fleet.sent)


def test_unknown_selected_vehicle_is_rejected_instead_of_reassigned(fleet):
    bridge=dispatcher(fleet)
    with pytest.raises(ValueError,match='车辆'):
        fleet.owner.command({'op':'single_goal','id':'invalid','robot_id':'unknown','point':{'pose':[1.,0.,0.]}},fleet.states)
    bridge.submit.assert_not_called()
