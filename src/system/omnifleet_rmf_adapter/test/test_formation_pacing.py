from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
from test_missions import fleet
from omnifleet_rmf_adapter.control_client import NavigationClient


def test_wide_formation_keeps_native_limits_and_stops_all_members(fleet):
    f=fleet.owner.formation;f.capture(['a','b'],fleet.states);f.start(['a','b'],fleet.states)
    fleet.tick(7)
    f.command({'op':'single_goal','point':[1.,2.,0.]},fleet.states);fleet.tick(3)
    assert f.rate>.9 and all(m['limits']['forward']==.4 for m in f.trajectory.models)
    fleet.states['b']['samples']['pose']['value']['x']=-.4;fleet.tick()
    assert 0<f.rate<.3
    assert not any(p[0]=='formation_speed' for p in fleet.sent)
    f.stop()
    assert not f.active and f.rate==0.
    assert {p[2] for p in fleet.sent if p[0]=='disarm'}=={'a','b'}


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
    fleet.tick(7)
    f.command({'op':'single_goal','point':[1.,.5,0.]},fleet.states);fleet.tick(3)
    assert f.rate>.9 and not any(p[0]=='formation_speed' for p in fleet.sent)
    fleet.states['b']['samples']['pose']['value']['x']+=.4
    fleet.tick()
    assert 0<f.rate<.5
