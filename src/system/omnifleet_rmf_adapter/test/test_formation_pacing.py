from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
from test_missions import fleet
from omnifleet_rmf_adapter.control_client import NavigationClient


def test_wide_formation_slows_only_the_leader_and_restores_on_stop(fleet):
    f=fleet.owner.formation;f.capture(['a','b'],fleet.states);f.start(['a','b'],fleet.states)
    pace=[p for p in fleet.sent if p[0]=='formation_speed'][-1]
    assert pace[2]=='a' and pace[3]['percentage']==25.
    fleet.states['b']['samples']['pose']['value']['x']=.2;f.tick(fleet.states)
    reduced=[p for p in fleet.sent if p[0]=='formation_speed'][-1][3]['percentage']
    assert reduced==pytest.approx(15.)
    f.stop()
    assert [p for p in fleet.sent if p[0]=='formation_speed'][-1][3]['percentage']==100.


@pytest.mark.parametrize('central_age,pace_age,expected', [(0.,0.,10.),(.6,0.,100.),(0.,.6,100.)])
def test_stale_formation_context_restores_normal_speed(monkeypatch,central_age,pace_age,expected):
    monkeypatch.setattr('omnifleet_rmf_adapter.control_client.time.monotonic',lambda:100.)
    node=NS(formation_speed=10.,formation_speed_seen=100.-pace_age,central_seen=100.-central_age,
            formation_speed_applied=10.,formation_speed_output=Mock(),get_clock=Mock(),
            samples={},epoch=None,control={},goal_handle=None,inflight=None,pending=None,
            arm_pending=False,motion_enabled=True,permission_error=None,record=Mock())
    node.get_clock.return_value.now.return_value.to_msg.return_value=None
    # Use a real ROS time message for the generated SpeedLimit header.
    from builtin_interfaces.msg import Time
    node.get_clock.return_value.now.return_value.to_msg.return_value=Time()
    NavigationClient.renew(node)
    assert node.formation_speed_output.publish.call_args.args[0].speed_limit==expected


def test_close_formation_uses_the_permanent_limit_without_a_fixed_ten_percent_cap(fleet):
    fleet.states['b']['samples']['pose']['value']['y']=1.
    f=fleet.owner.formation;f.capture(['a','b'],fleet.states);f.start(['a','b'],fleet.states)
    pace=[p for p in fleet.sent if p[0]=='formation_speed'][-1]
    assert pace[3]['percentage']==100.
    fleet.states['b']['samples']['pose']['value']['x']+=.4
    f.tick(fleet.states)
    assert [p for p in fleet.sent if p[0]=='formation_speed'][-1][3]['percentage']==25.
